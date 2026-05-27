from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..analysts.runner import load_personas, run_analyst


_OUT_DIR = Path(__file__).resolve().parents[3] / "dashboard" / "data" / "dreams"


# Nightly dream plan: which personas fire and with what canned inputs.
# This is a starting point — the Orchestrator can re-rank this list weekly based on hit-rate.
DREAM_PLAN = [
    ("mckinsey_macro", {"holdings": "core ETF basket", "biggest_concern": "Fed policy + China tariffs"}),
    ("bridgewater_risk", {"holdings": "current portfolio", "total_value": "100000"}),
    ("quant_regime", {"asset": "SPY"}),
    ("quant_alpha", {"market": "US equities"}),
    ("renaissance_patterns", {"ticker": "SPY", "time_period": "trailing 12 months"}),
    ("bain_competitive", {"sector": "AI infrastructure"}),
]


def run_dream() -> dict:
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    personas = {p["id"]: p for p in load_personas()}
    out: dict = {"started_at": ts, "results": []}
    for persona_id, inputs in DREAM_PLAN:
        meta = personas.get(persona_id, {})
        try:
            text = run_analyst(persona_id, inputs)
            out["results"].append({
                "persona_id": persona_id,
                "firm": meta.get("firm"),
                "title": meta.get("title"),
                "inputs": inputs,
                "output": text,
                "ok": True,
            })
        except Exception as e:  # noqa: BLE001
            out["results"].append({
                "persona_id": persona_id,
                "error": str(e),
                "ok": False,
            })
    out["finished_at"] = datetime.now(timezone.utc).isoformat()
    path = _OUT_DIR / f"dream_{ts.replace(':', '-')}.json"
    path.write_text(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    result = run_dream()
    print(f"Dream finished — {len(result['results'])} analyst runs written to /dashboard/data/dreams/")
