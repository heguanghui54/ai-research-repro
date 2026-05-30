from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path
from typing import Any


SCORE_FIELDS = [
    "overall_quality",
    "scientific_validity",
    "claim_grounding",
    "reproducibility",
    "novelty_calibration",
    "overclaim_risk",
]


def _read_packet(packet_path: Path) -> list[dict[str, Any]]:
    with packet_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    artifacts: list[dict[str, Any]] = []
    for row in rows:
        artifacts.append(
            {
                "annotation_order": int(row.get("annotation_order") or len(artifacts) + 1),
                "artifact_id": row.get("artifact_id", ""),
                "domain": row.get("domain", ""),
                "task_id": row.get("task_id", ""),
                "question": row.get("question", ""),
                "related_work_trap": row.get("related_work_trap", ""),
                "required_evidence": row.get("required_evidence", "[]"),
                "expected_artifacts": row.get("expected_artifacts", "[]"),
                "answer": row.get("answer", ""),
            }
        )
    return artifacts


def _write_html(artifacts: list[dict[str, Any]], output_path: Path) -> None:
    payload = json.dumps(artifacts, ensure_ascii=False)
    score_inputs = "\n".join(
        f"""
        <label>{field.replace('_', ' ')}
          <select id="{field}" required>
            <option value=""></option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
        </label>
        """
        for field in SCORE_FIELDS
    )
    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI Research Human Evaluation</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #17202a; background: #f6f7f9; }}
    header {{ position: sticky; top: 0; background: #ffffff; border-bottom: 1px solid #d9dee7; padding: 14px 22px; z-index: 2; }}
    main {{ display: grid; grid-template-columns: 1fr 360px; gap: 18px; padding: 18px 22px 28px; }}
    section, aside {{ background: #ffffff; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; }}
    h1 {{ font-size: 18px; margin: 0 0 4px; }}
    h2 {{ font-size: 16px; margin: 0 0 12px; }}
    .meta {{ color: #5f6b7a; font-size: 13px; }}
    .prompt {{ white-space: pre-wrap; line-height: 1.45; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #111827; color: #f9fafb; padding: 14px; border-radius: 6px; max-height: 56vh; overflow: auto; }}
    label {{ display: block; margin: 10px 0; font-size: 14px; }}
    select, textarea {{ width: 100%; box-sizing: border-box; margin-top: 4px; }}
    select {{ height: 32px; }}
    textarea {{ min-height: 90px; }}
    button {{ height: 34px; padding: 0 12px; margin-right: 8px; border: 1px solid #9aa4b2; background: #fff; border-radius: 6px; cursor: pointer; }}
    button.primary {{ background: #1f6feb; border-color: #1f6feb; color: #fff; }}
    .bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
    .status {{ font-weight: 600; }}
    .warn {{ color: #9a3412; }}
    .done {{ color: #116329; }}
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div>
        <h1>AI Research Artifact Human Evaluation</h1>
        <div class="meta">Blinded packet. Do not infer method identity from length alone.</div>
      </div>
      <div class="status" id="status"></div>
    </div>
  </header>
  <main>
    <section>
      <h2 id="title"></h2>
      <div class="meta" id="domain"></div>
      <h2>Task</h2>
      <div class="prompt" id="question"></div>
      <h2>Related-Work Trap</h2>
      <div class="prompt" id="trap"></div>
      <h2>Required Evidence</h2>
      <div class="prompt" id="evidence"></div>
      <h2>Expected Artifacts</h2>
      <div class="prompt" id="artifacts"></div>
      <h2>Generated Answer</h2>
      <pre id="answer"></pre>
    </section>
    <aside>
      <h2>Scores</h2>
      <form id="form">
        {score_inputs}
        <label>notes
          <textarea id="notes" placeholder="One concise reason for the scores."></textarea>
        </label>
      </form>
      <p class="meta">1 is low/poor, 5 is high/strong. For overclaim risk, 1 is low risk and 5 is high risk.</p>
      <button id="prev">Previous</button>
      <button id="next" class="primary">Save + Next</button>
      <button id="download">Download CSV</button>
      <button id="downloadJson">Download JSON</button>
      <p id="completion" class="meta"></p>
    </aside>
  </main>
  <script>
    const artifacts = {payload};
    const scoreFields = {json.dumps(SCORE_FIELDS)};
    let index = Number(localStorage.getItem("humanEvalIndex") || "0");
    const saved = JSON.parse(localStorage.getItem("humanEvalScores") || "{{}}");

    function current() {{ return artifacts[index]; }}
    function parseList(value) {{
      try {{ return JSON.parse(value).join("\\n"); }} catch {{ return value; }}
    }}
    function load() {{
      const item = current();
      document.getElementById("title").textContent = `${{item.annotation_order}} / ${{artifacts.length}} · ${{item.artifact_id}} · ${{item.task_id}}`;
      document.getElementById("domain").textContent = item.domain;
      document.getElementById("question").textContent = item.question;
      document.getElementById("trap").textContent = item.related_work_trap;
      document.getElementById("evidence").textContent = parseList(item.required_evidence);
      document.getElementById("artifacts").textContent = parseList(item.expected_artifacts);
      document.getElementById("answer").textContent = item.answer;
      const row = saved[item.artifact_id] || {{}};
      for (const field of scoreFields) document.getElementById(field).value = row[field] || "";
      document.getElementById("notes").value = row.notes || "";
      updateStatus();
    }}
    function save() {{
      const item = current();
      const row = {{}};
      for (const field of scoreFields) row[field] = document.getElementById(field).value;
      row.notes = document.getElementById("notes").value.replace(/\\r?\\n/g, " ");
      saved[item.artifact_id] = row;
      localStorage.setItem("humanEvalScores", JSON.stringify(saved));
      localStorage.setItem("humanEvalIndex", String(index));
      updateStatus();
    }}
    function updateStatus() {{
      let complete = 0;
      for (const item of artifacts) {{
        const row = saved[item.artifact_id] || {{}};
        if (scoreFields.every(field => row[field])) complete += 1;
      }}
      document.getElementById("status").textContent = `${{complete}} / ${{artifacts.length}} complete`;
      document.getElementById("completion").textContent = complete === artifacts.length ? "All artifacts scored. Download CSV." : "Progress is saved in this browser.";
      document.getElementById("completion").className = complete === artifacts.length ? "done" : "warn";
    }}
    function csvCell(value) {{
      return `"${{String(value || "").replace(/"/g, '""')}}"`;
    }}
    function downloadCsv() {{
      save();
      const fields = ["artifact_id", ...scoreFields, "notes"];
      const lines = [fields.join(",")];
      for (const item of artifacts) {{
        const row = saved[item.artifact_id] || {{}};
        lines.push(fields.map(field => csvCell(field === "artifact_id" ? item.artifact_id : row[field])).join(","));
      }}
      const blob = new Blob([lines.join("\\n") + "\\n"], {{type: "text/csv"}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "human_eval_completed.csv";
      a.click();
      URL.revokeObjectURL(url);
    }}
    function downloadJson() {{
      save();
      const rows = artifacts.map(item => ({{artifact_id: item.artifact_id, ...(saved[item.artifact_id] || {{}})}}));
      const blob = new Blob([JSON.stringify(rows, null, 2) + "\\n"], {{type: "application/json"}});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "human_eval_completed.json";
      a.click();
      URL.revokeObjectURL(url);
    }}
    document.getElementById("prev").onclick = () => {{ save(); index = Math.max(0, index - 1); load(); }};
    document.getElementById("next").onclick = () => {{ save(); index = Math.min(artifacts.length - 1, index + 1); load(); }};
    document.getElementById("download").onclick = downloadCsv;
    document.getElementById("downloadJson").onclick = downloadJson;
    load();
  </script>
</body>
</html>
"""
    output_path.write_text(html_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifacts = _read_packet(args.packet)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_html(artifacts, args.output)
    print(json.dumps({"output": str(args.output), "artifact_count": len(artifacts)}, indent=2))


if __name__ == "__main__":
    main()
