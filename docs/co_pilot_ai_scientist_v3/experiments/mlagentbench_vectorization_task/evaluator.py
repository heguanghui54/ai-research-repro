#!/usr/bin/env python3
"""Evaluator for the MLAgentBench vectorization task.

The official MLAgentBench task scores the runtime written to submission.csv.
For research-paper evidence, we add a small correctness check before accepting
the runtime score. This keeps the benchmark machine-gradeable while avoiding
trivial invalid speedups.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np


def _load_module(program_path: Path):
    spec = importlib.util.spec_from_file_location("candidate_vectorization", program_path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"Could not load {program_path}")
    spec.loader.exec_module(module)
    return module


def _reference_forward(layer: Any, features_batch: np.ndarray) -> np.ndarray:
    padding_size = layer.padding if isinstance(layer.padding, int) else 0
    batch_size, h_old, w_old, _ = features_batch.shape
    filter_size = layer.kernel_matrices.shape[0]
    num_of_filters_new = layer.kernel_matrices.shape[-1]
    h_new = int((h_old + (2 * padding_size) - filter_size) / layer.stride) + 1
    w_new = int((w_old + (2 * padding_size) - filter_size) / layer.stride) + 1

    padded_batch = np.pad(
        features_batch,
        ((0, 0), (padding_size, padding_size), (padding_size, padding_size), (0, 0)),
        mode="constant",
        constant_values=0,
    )
    output = np.zeros((batch_size, h_new, w_new, num_of_filters_new))
    for index in range(batch_size):
        padded_feature = padded_batch[index]
        for h in range(h_new):
            for w in range(w_new):
                vertical_start = h * layer.stride
                vertical_end = vertical_start + filter_size
                horizontal_start = w * layer.stride
                horizontal_end = horizontal_start + filter_size
                image_portion = padded_feature[
                    vertical_start:vertical_end, horizontal_start:horizontal_end, :
                ]
                for filter_index in range(num_of_filters_new):
                    kernel_matrix = layer.kernel_matrices[:, :, :, filter_index]
                    bias = layer.biases[:, :, :, filter_index]
                    output[index, h, w, filter_index] = (
                        np.sum(image_portion * kernel_matrix) + bias.astype("float")
                    )
    if layer.activation == "relu":
        return output * (output > 0)
    return output


def _check_correctness(program_path: Path) -> tuple[bool, str]:
    module = _load_module(program_path)
    if not hasattr(module, "Conv2DLayer"):
        return False, "candidate does not define Conv2DLayer"

    np.random.seed(123)
    layer = module.Conv2DLayer(3, 4, 3, 2, 1, "relu")
    features = np.random.randn(2, 8, 7, 3)
    expected = _reference_forward(layer, features)
    actual = layer.forward(features)
    if not isinstance(actual, np.ndarray):
        return False, "forward did not return a numpy array"
    if actual.shape != expected.shape:
        return False, f"shape mismatch: got {actual.shape}, expected {expected.shape}"
    if not np.allclose(actual, expected, rtol=1e-8, atol=1e-8):
        return False, "numerical mismatch against reference convolution"
    return True, ""


def _run_script_once(program_path: Path, timeout: int) -> float:
    with tempfile.TemporaryDirectory(prefix="mlagentbench_vectorization_") as tmp_name:
        tmp = Path(tmp_name)
        train_path = tmp / "train.py"
        shutil.copy2(program_path, train_path)
        start = time.time()
        completed = subprocess.run(
            [sys.executable, str(train_path)],
            cwd=tmp,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False,
        )
        wall_time = time.time() - start
        if completed.returncode != 0:
            raise RuntimeError(
                json.dumps(
                    {
                        "returncode": completed.returncode,
                        "stdout": completed.stdout[-1000:],
                        "stderr": completed.stderr[-1000:],
                    }
                )
            )
        submission = tmp / "submission.csv"
        if not submission.exists():
            raise RuntimeError("candidate did not write submission.csv")
        first_line = submission.read_text(encoding="utf-8").strip().splitlines()[0]
        try:
            reported_time = float(first_line.split(";")[0])
        except ValueError as exc:
            raise RuntimeError(f"invalid submission time: {first_line!r}") from exc
        if reported_time <= 0:
            raise RuntimeError(f"non-positive submission time: {reported_time}")
        if reported_time > wall_time + 2.0:
            raise RuntimeError(
                f"reported time {reported_time} exceeds observed wall time {wall_time}"
            )
        return reported_time


def evaluate(path: str) -> dict[str, float | int | str | bool]:
    program_path = Path(path)
    try:
        correct, reason = _check_correctness(program_path)
        if not correct:
            return {
                "combined_score": 0.0,
                "score": 0.0,
                "runtime_seconds": 1e9,
                "correct": False,
                "error": reason,
            }
        times = [_run_script_once(program_path, timeout=30) for _ in range(3)]
        median_seconds = float(np.median(times))
        return {
            "combined_score": float(1.0 / (median_seconds + 1e-9)),
            "score": float(1.0 / (median_seconds + 1e-9)),
            "runtime_seconds": median_seconds,
            "best_runtime_seconds": float(min(times)),
            "mean_runtime_seconds": float(np.mean(times)),
            "num_runs": len(times),
            "correct": True,
            "error": "",
        }
    except Exception as exc:
        return {
            "combined_score": 0.0,
            "score": 0.0,
            "runtime_seconds": 1e9,
            "correct": False,
            "error": str(exc)[:1000],
        }


if __name__ == "__main__":
    print(json.dumps(evaluate(sys.argv[1]), indent=2))
