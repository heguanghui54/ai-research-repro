"""Local Evaluate-compatible accuracy metric for offline BabyLM probes."""

from __future__ import annotations

import datasets
import evaluate


_DESCRIPTION = "Simple token-level accuracy for offline compatibility probes."
_KWARGS_DESCRIPTION = "Computes the fraction of predictions equal to references."


class Accuracy(evaluate.Metric):
    def _info(self):
        return evaluate.MetricInfo(
            description=_DESCRIPTION,
            citation="",
            inputs_description=_KWARGS_DESCRIPTION,
            features=datasets.Features(
                {
                    "predictions": datasets.Value("int64"),
                    "references": datasets.Value("int64"),
                }
            ),
        )

    def _compute(self, predictions, references):
        if len(references) == 0:
            return {"accuracy": 0.0}
        correct = sum(int(pred == ref) for pred, ref in zip(predictions, references))
        return {"accuracy": correct / len(references)}
