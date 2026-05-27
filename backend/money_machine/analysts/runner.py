from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..settings import settings


_DASHBOARD_DATA = Path(__file__).resolve().parents[3] / "dashboard" / "data"


def load_prompts() -> dict[str, str]:
    with (_DASHBOARD_DATA / "prompts.json").open() as f:
        return json.load(f)["templates"]


def load_personas() -> list[dict[str, Any]]:
    with (_DASHBOARD_DATA / "analysts.json").open() as f:
        return json.load(f)["personas"]


def render_prompt(persona_id: str, inputs: dict[str, str]) -> str:
    prompts = load_prompts()
    template = prompts.get(persona_id)
    if not template:
        raise KeyError(f"No prompt template for persona '{persona_id}'")
    rendered = template
    for k, v in inputs.items():
        rendered = rendered.replace("{{" + k + "}}", str(v))
    return rendered


def run_analyst(persona_id: str, inputs: dict[str, str]) -> str:
    """Render the prompt and call the configured LLM. Falls back to dry-run echo."""
    prompt = render_prompt(persona_id, inputs)
    if not settings.anthropic_key:
        return f"[DRY RUN — no ANTHROPIC_API_KEY]\n\n{prompt}"

    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError:
        return "anthropic SDK not installed. `pip install anthropic`"

    client = Anthropic(api_key=settings.anthropic_key)
    msg = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in msg.content if hasattr(block, "text"))
