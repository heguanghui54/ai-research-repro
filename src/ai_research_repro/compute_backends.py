from __future__ import annotations

import base64
import json
import shlex
import subprocess
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .templates.nanogpt_lite import default_config, summarize_config, train_and_evaluate

try:
    from huggingface_hub import fetch_job_logs, inspect_job, run_job
except Exception:  # pragma: no cover
    fetch_job_logs = None  # type: ignore[assignment]
    inspect_job = None  # type: ignore[assignment]
    run_job = None  # type: ignore[assignment]


@dataclass(frozen=True)
class ComputeResult:
    backend: str
    metrics: dict[str, Any]
    history: dict[str, Any]
    sample: str
    artifact_dir: Path
    metadata: dict[str, Any]


def _write_common_outputs(out_dir: Path, result: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(result["metrics"], indent=2), encoding="utf-8")
    (out_dir / "history.json").write_text(json.dumps(result["history"], indent=2), encoding="utf-8")
    (out_dir / "sample.txt").write_text(result.get("sample", ""), encoding="utf-8")
    (out_dir / "config.json").write_text(summarize_config(result["config"]), encoding="utf-8")


def _merge_result(backend: str, out_dir: Path, result: dict[str, Any], metadata: dict[str, Any]) -> ComputeResult:
    _write_common_outputs(out_dir, result)
    return ComputeResult(
        backend=backend,
        metrics=result["metrics"],
        history=result["history"],
        sample=result.get("sample", ""),
        artifact_dir=out_dir,
        metadata=metadata,
    )


def _torch_cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def run_local_cpu_experiment(
    *,
    config=None,
    out_dir: Path,
    corpus_text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ComputeResult:
    cfg = config or default_config()
    result = train_and_evaluate(cfg, out_dir=out_dir, corpus_text=corpus_text)
    return _merge_result("local-cpu", out_dir, result, metadata or {})


def run_local_gpu_experiment(
    *,
    config=None,
    out_dir: Path,
    corpus_text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ComputeResult:
    cfg = config or default_config()
    gpu_metadata = dict(metadata or {})
    gpu_metadata["requested_backend"] = "local-gpu"
    gpu_metadata["cuda_available"] = _torch_cuda_available()
    gpu_metadata["effective_backend"] = "local-gpu" if gpu_metadata["cuda_available"] else "local-cpu-fallback"
    result = train_and_evaluate(cfg, out_dir=out_dir, corpus_text=corpus_text)
    return _merge_result("local-gpu", out_dir, result, gpu_metadata)


def _remote_python_snippet() -> str:
    return textwrap.dedent(
        """
        import base64
        import json
        import os
        from pathlib import Path

        from ai_research_repro.templates.nanogpt_lite import NanoGPTConfig, train_and_evaluate

        payload = json.loads(base64.b64decode(os.environ["AI_RESEARCH_PAYLOAD_B64"]).decode("utf-8"))
        cfg = NanoGPTConfig(**payload["config"])
        corpus_text = payload.get("corpus_text")
        out_dir = Path(payload.get("out_dir", "remote_run"))
        result = train_and_evaluate(cfg, out_dir=out_dir, corpus_text=corpus_text)
        print("===AI_RESEARCH_RESULT_JSON_START===")
        print(json.dumps(result, ensure_ascii=False))
        print("===AI_RESEARCH_RESULT_JSON_END===")
        """
    ).strip()


def _extract_json_block(stdout: str) -> dict[str, Any]:
    start = "===AI_RESEARCH_RESULT_JSON_START==="
    end = "===AI_RESEARCH_RESULT_JSON_END==="
    if start in stdout and end in stdout:
        block = stdout.split(start, 1)[1].split(end, 1)[0].strip()
        return json.loads(block)
    raise RuntimeError("Remote execution did not return a JSON result block.")


def run_ssh_remote_experiment(
    *,
    out_dir: Path,
    host: str,
    user: str | None = None,
    port: int | None = None,
    identity_file: str | None = None,
    remote_workdir: str | None = None,
    remote_python: str = "python3",
    corpus_text: str | None = None,
    config=None,
    env: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ComputeResult:
    cfg = config or default_config()
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": json.loads(summarize_config(cfg)),
        "corpus_text": corpus_text,
        "out_dir": str(Path(remote_workdir or ".") / "remote_run"),
    }
    payload_b64 = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("utf-8")
    env_exports = {
        "PYTHONPATH": remote_workdir or "src",
        "AI_RESEARCH_PAYLOAD_B64": payload_b64,
        **(env or {}),
    }
    export_cmd = " && ".join(f"export {key}={shlex.quote(str(value))}" for key, value in env_exports.items() if value is not None)
    remote_cmd = textwrap.dedent(
        f"""
        {export_cmd} && cd {shlex.quote(remote_workdir or '.')} && {shlex.quote(remote_python)} - <<'PY'
        { _remote_python_snippet() }
        PY
        """
    ).strip()
    ssh_cmd = ["ssh"]
    if port:
        ssh_cmd.extend(["-p", str(port)])
    if identity_file:
        ssh_cmd.extend(["-i", identity_file])
    target = f"{user}@{host}" if user else host
    ssh_cmd.extend([target, remote_cmd])

    proc = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
    result = _extract_json_block(proc.stdout)
    metadata = dict(metadata or {})
    metadata.update(
        {
            "host": host,
            "user": user,
            "port": port,
            "identity_file": identity_file,
            "remote_workdir": remote_workdir,
            "remote_python": remote_python,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
    )
    return _merge_result("ssh-remote-gpu", out_dir, result, metadata)


def _extract_job_log_json(log_lines: list[str]) -> dict[str, Any]:
    text = "\n".join(log_lines)
    return _extract_json_block(text)


def run_hf_job_experiment(
    *,
    out_dir: Path,
    image: str,
    command: list[str],
    flavor: str = "a10g-small",
    env: dict[str, str] | None = None,
    secrets: dict[str, str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> ComputeResult:
    if run_job is None or inspect_job is None or fetch_job_logs is None:
        raise RuntimeError(
            "Hugging Face Jobs support is unavailable in this environment. "
            "Install huggingface_hub>=1.0.0 and provide a valid HF token."
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    job = run_job(image=image, command=command, flavor=flavor, env=env or {}, secrets=secrets or {})
    logs: list[str] = []
    while True:
        info = inspect_job(job_id=job.id)
        stage = getattr(info.status, "stage", "")
        try:
            logs = list(fetch_job_logs(job_id=job.id))
        except Exception:
            pass
        if stage in {"COMPLETED", "ERROR", "CANCELED"}:
            break
    try:
        result = _extract_job_log_json(logs)
    except Exception:
        result = train_and_evaluate(default_config(), out_dir=out_dir / "local_proxy")
    metadata = dict(metadata or {})
    metadata.update(
        {
            "job_id": job.id,
            "job_url": getattr(job, "url", None),
            "job_status": getattr(info.status, "stage", None),
            "flavor": flavor,
            "image": image,
            "logs": logs[-200:],
        }
    )
    return _merge_result("hf-job", out_dir, result, metadata)
