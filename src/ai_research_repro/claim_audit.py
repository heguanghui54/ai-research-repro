from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RISK_TERMS = ("fallback", "planned", "simulated", "placeholder", "pilot only", "not final")


@dataclass
class AuditFinding:
    severity: str
    method: str
    seed: int
    task_id: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "method": self.method,
            "seed": self.seed,
            "task_id": self.task_id,
            "message": self.message,
        }


def load_results(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_results(summary: dict[str, Any]) -> dict[str, Any]:
    findings: list[AuditFinding] = []
    for method_result in summary.get("results", []):
        method = method_result.get("method", "unknown")
        for seed_result in method_result.get("seeds", []):
            seed = int(seed_result.get("seed", -1))
            for task_result in seed_result.get("tasks", []):
                task_id = task_result.get("task", {}).get("task_id", "unknown")
                answer = task_result.get("answer", {})
                text = json.dumps(answer, ensure_ascii=False).lower()
                claim_table = answer.get("claim_evidence_table", [])
                commands = answer.get("reproducibility_commands", [])

                if not commands:
                    findings.append(AuditFinding("error", method, seed, task_id, "Missing reproducibility commands."))
                if not claim_table:
                    findings.append(AuditFinding("error", method, seed, task_id, "Missing claim-evidence table."))
                if any(term in text for term in RISK_TERMS):
                    findings.append(
                        AuditFinding(
                            "warning",
                            method,
                            seed,
                            task_id,
                            "Contains planning/fallback language; do not present as completed empirical evidence.",
                        )
                    )
                for row in claim_table if isinstance(claim_table, list) else []:
                    status = str(row.get("status", "")).lower() if isinstance(row, dict) else ""
                    if status and status not in {"observed", "measured", "verified", "completed"}:
                        findings.append(
                            AuditFinding(
                                "warning",
                                method,
                                seed,
                                task_id,
                                f"Claim row has non-final status `{status}`.",
                            )
                        )

    errors = [item for item in findings if item.severity == "error"]
    warnings = [item for item in findings if item.severity == "warning"]
    return {
        "status": "fail" if errors else "pass_with_warnings" if warnings else "pass",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": [item.to_dict() for item in findings],
    }


def write_audit(audit: dict[str, Any], workspace: Path) -> dict[str, str]:
    json_path = workspace / "claim_audit.json"
    md_path = workspace / "claim_audit.md"
    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    lines = [
        "# Claim And Evidence Audit",
        "",
        f"- Status: `{audit['status']}`",
        f"- Errors: {audit['error_count']}",
        f"- Warnings: {audit['warning_count']}",
        "",
    ]
    if audit["findings"]:
        lines.extend(["| Severity | Method | Seed | Task | Message |", "| --- | --- | ---: | --- | --- |"])
        for finding in audit["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['method']}` | {finding['seed']} | "
                f"`{finding['task_id']}` | {finding['message']} |"
            )
    else:
        lines.append("No unsupported-claim findings were detected by the automated audit.")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def audit_results_file(results_path: Path) -> dict[str, Any]:
    summary = load_results(results_path)
    audit = audit_results(summary)
    paths = write_audit(audit, results_path.parent)
    audit["paths"] = paths
    return audit

