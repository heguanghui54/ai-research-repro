#!/usr/bin/env python3
"""Small offline BabyLM causal-LM eval used for compatibility probing."""

from __future__ import annotations

import json
import math
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer


def main() -> None:
    env_dir = Path(__file__).resolve().parents[1] / "env"
    run_dir = env_dir.parent
    output_dir = env_dir / "output"
    dataset_script = env_dir / "babyLM_for_hf.py"
    tokenizer = AutoTokenizer.from_pretrained(run_dir.parent / "gpt2_assets")
    model = AutoModelForCausalLM.from_pretrained(output_dir)
    model.eval()

    block_size = 64
    max_chunks = 64
    raw = load_dataset(str(dataset_script), "babyLM-10M", split="test")

    token_buffer: list[int] = []
    for row in raw:
        text = row.get("text", "")
        if not isinstance(text, str):
            continue
        token_buffer.extend(tokenizer(text, add_special_tokens=False)["input_ids"])
        if len(token_buffer) >= block_size * max_chunks:
            break

    chunks = [
        token_buffer[start : start + block_size]
        for start in range(0, min(len(token_buffer), block_size * max_chunks), block_size)
        if len(token_buffer[start : start + block_size]) == block_size
    ]
    if not chunks:
        raise SystemExit("no evaluation chunks were produced")

    losses: list[float] = []
    with torch.no_grad():
        for chunk in chunks:
            input_ids = torch.tensor([chunk], dtype=torch.long)
            out = model(input_ids=input_ids, labels=input_ids)
            losses.append(float(out.loss.detach().cpu()))

    mean_loss = sum(losses) / len(losses)
    metrics = {
        "eval_loss": mean_loss,
        "perplexity": math.exp(mean_loss) if mean_loss < 100 else float("inf"),
        "eval_chunks": len(chunks),
        "block_size": block_size,
        "scope": "tiny_offline_compatibility_eval_not_full_babylm_benchmark",
    }
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
