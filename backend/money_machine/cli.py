from __future__ import annotations

import argparse
import json

from .analysts.runner import load_personas, run_analyst
from .dream.nightly import run_dream
from .orchestrator import Orchestrator
from .strategies import registry  # noqa: F401
from .strategies import multi_factor, news_butterfly, pol_latency, macro_regime  # noqa: F401


def cmd_status(_: argparse.Namespace) -> None:
    o = Orchestrator()
    snap = o.snapshot()
    print(json.dumps(snap, indent=2, default=str))


def cmd_refresh_state(_: argparse.Namespace) -> None:
    o = Orchestrator()
    o.write_state(extra_log=[{"ts": "now", "msg": "State refreshed via CLI."}])
    print("State refreshed.")


def cmd_list_strategies(_: argparse.Namespace) -> None:
    for s in registry.all_strategies():
        m = s.meta
        print(f"- {m.id} :: {m.title} ({m.category}) — needs {m.needs_data}")


def cmd_list_personas(_: argparse.Namespace) -> None:
    for p in load_personas():
        print(f"- {p['id']:>26}  {p['firm']:<22} {p['title']}")


def cmd_run_analyst(args: argparse.Namespace) -> None:
    inputs = dict(item.split("=", 1) for item in args.inputs or [])
    out = run_analyst(args.persona, inputs)
    print(out)


def cmd_dream(_: argparse.Namespace) -> None:
    res = run_dream()
    print(f"Dream finished. {len(res['results'])} analyst runs.")


def main() -> None:
    p = argparse.ArgumentParser(prog="money-machine")
    sub = p.add_subparsers(required=True)

    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("refresh-state").set_defaults(func=cmd_refresh_state)
    sub.add_parser("strategies").set_defaults(func=cmd_list_strategies)
    sub.add_parser("personas").set_defaults(func=cmd_list_personas)
    sub.add_parser("dream").set_defaults(func=cmd_dream)

    ra = sub.add_parser("analyst")
    ra.add_argument("persona")
    ra.add_argument("inputs", nargs="*", help="key=value pairs")
    ra.set_defaults(func=cmd_run_analyst)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
