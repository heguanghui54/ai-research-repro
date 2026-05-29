from __future__ import annotations

import argparse
import json
from pathlib import Path

from .orchestrator import PipelineConfig, run_pipeline
from .templates.nanogpt_lite import default_config, train_and_evaluate
from .reviewer import review_report
from .writer import save_report


def _cmd_run(args: argparse.Namespace) -> None:
    result = run_pipeline(
        PipelineConfig(
            workspace=Path(args.workspace),
            num_ideas=args.ideas,
            gpt_model=args.model,
            run_baseline=not args.no_baseline,
        )
    )
    print(json.dumps(
        {
            "workspace": result["workspace"],
            "summary_metrics": result["summary_metrics"],
            "report_path": result["report_path"],
            "review": result["review"],
        },
        indent=2,
    ))


def _cmd_baseline(args: argparse.Namespace) -> None:
    out_dir = Path(args.workspace) / "baseline"
    result = train_and_evaluate(default_config(), out_dir=out_dir)
    print(json.dumps(result["metrics"], indent=2))


def _cmd_review(args: argparse.Namespace) -> None:
    report = Path(args.report).read_text(encoding="utf-8")
    review = review_report(report, metrics={}, model=args.model)
    print(json.dumps(review, indent=2))


def _cmd_web(_: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run("ai_research_repro.webapp.app:app", host="127.0.0.1", port=8000, reload=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-research-repro")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the full idea-to-paper pipeline.")
    run.add_argument("--workspace", required=True)
    run.add_argument("--ideas", type=int, default=3)
    run.add_argument("--model", default="gpt-4o-mini")
    run.add_argument("--no-baseline", action="store_true")
    run.set_defaults(func=_cmd_run)

    baseline = sub.add_parser("baseline", help="Run the NanoGPT-lite baseline only.")
    baseline.add_argument("--workspace", required=True)
    baseline.set_defaults(func=_cmd_baseline)

    review = sub.add_parser("review", help="Review a report markdown file.")
    review.add_argument("--report", required=True)
    review.add_argument("--model", default="gpt-4o-mini")
    review.set_defaults(func=_cmd_review)

    web = sub.add_parser("web", help="Start the web workspace.")
    web.set_defaults(func=_cmd_web)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
