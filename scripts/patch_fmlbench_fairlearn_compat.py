#!/usr/bin/env python3
"""Patch the official FML-bench Fairlearn task runner for API compatibility.

The official Fairness_fairlearn task runner imports fairlearn.reductions and
the DeepSeek-generated code can pass `random_state=` into
ExponentiatedGradient. Some installed Fairlearn versions do not accept that
keyword argument, so this helper patches the task runner to ignore it.
"""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = """warnings.filterwarnings('ignore')\n\n# Add the ml_tasks directory to path so we can import algorithm\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\nfrom algorithm import FairnessAlgorithm\n"""

NEW = """warnings.filterwarnings('ignore')\n\n# Add the ml_tasks directory to path so we can import algorithm\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n\n# ---------------------------------------------------------------------------\n# Compatibility shim\n# ---------------------------------------------------------------------------\n# Some installed Fairlearn versions do not accept a random_state keyword in\n# ExponentiatedGradient.__init__. The benchmark-generated code may pass it,\n# so we patch the class to ignore that extra argument when necessary.\ntry:\n    import inspect\n    from fairlearn import reductions as _fairlearn_reductions\n\n    if 'random_state' not in inspect.signature(_fairlearn_reductions.ExponentiatedGradient.__init__).parameters:\n        _OriginalExponentiatedGradient = _fairlearn_reductions.ExponentiatedGradient\n\n        class _PatchedExponentiatedGradient(_OriginalExponentiatedGradient):\n            def __init__(self, *args, random_state=None, **kwargs):\n                super().__init__(*args, **kwargs)\n\n        _fairlearn_reductions.ExponentiatedGradient = _PatchedExponentiatedGradient\nexcept Exception:\n    pass\n\nfrom algorithm import FairnessAlgorithm\n"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="Path to the official FML-bench repo root")
    args = parser.parse_args()

    path = Path(args.repo) / "ml_tasks" / "Fairness_fairlearn" / "train_eval_baseline.py"
    text = path.read_text()
    if NEW in text:
        print(f"Compatibility shim already present in {path}")
        return
    if OLD not in text:
        raise SystemExit(f"Target block not found in {path}")
    path.write_text(text.replace(OLD, NEW))
    print(f"Patched {path}")


if __name__ == "__main__":
    main()
