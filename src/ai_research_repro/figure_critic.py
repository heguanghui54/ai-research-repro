from __future__ import annotations

from pathlib import Path

from .llm import chat_vision_text


FIGURE_CRITIC_SYSTEM = """You are a strict scientific figure reviewer.
Check whether figures are readable, correctly labeled, and support only the claims stated by the experiment logs."""


def critique_figures(
    *,
    image_paths: list[Path],
    claim_context: str,
    model: str | None = None,
) -> str:
    def _fallback() -> str:
        names = ", ".join(path.name for path in image_paths) or "no figures"
        return (
            f"Fallback figure critique for {names}: verify axis labels, legends, captions, "
            "and whether the plotted quantities directly support the stated claims."
        )

    prompt = f"""Review these scientific figures against the claim context.

Claim context:
{claim_context}

Return concise bullet points covering:
- readability defects,
- label/caption problems,
- unsupported or overstated claims,
- concrete fixes before paper submission.
"""
    return chat_vision_text(
        system=FIGURE_CRITIC_SYSTEM,
        user=prompt,
        image_paths=image_paths,
        model=model,
        fallback=_fallback,
    ).text
