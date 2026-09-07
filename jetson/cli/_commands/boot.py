"""``jetson boot`` — noun group for Jetson boot-mode knowledge.

The first domain noun on this CLI: its verbs answer a Jetson question rather
than describe the agent. ``boot mode`` renders the sourced ``boot-mode`` topic
from :mod:`jetson.knowledge.boot_mode`; ``boot overview`` describes what the
noun knows (the rubric's noun-overview rule, same shape as ``cli overview``).

Read-only and offline: nothing here inspects the running machine or shells out,
so the output is identical on a Jetson, on a workstation, and in CI. The
commands it prints are what the reader runs on the board.
"""

from __future__ import annotations

import argparse

from jetson.cli._commands.overview import emit_overview
from jetson.cli._output import emit_result
from jetson.knowledge import boot_mode

_JSON_HELP = "Emit structured JSON."


def boot_sections() -> list[dict[str, object]]:
    """Sections describing what the ``boot`` noun knows."""
    return [
        {
            "title": "Verbs",
            "items": [
                "boot mode — desktop (GUI) vs console boot, with sources",
                "boot overview — this description of the noun",
            ],
        },
        {
            "title": "Topic: boot-mode",
            "items": [f"{claim['id']} — {claim['statement']}" for claim in boot_mode.CLAIMS],
        },
        {
            "title": "Field notes (not claims)",
            "items": [
                f"[{', '.join(str(c) for c in note['sources']) or 'unsourced'}] {note['note']}"
                for note in boot_mode.FIELD_NOTES
            ],
        },
        {
            "title": "Sources",
            "items": [f"{src['title']} — {src['url']}" for src in boot_mode.SOURCES.values()],
        },
        {"title": "Known gaps", "items": list(boot_mode.GAPS)},
    ]


def cmd_boot_mode(args: argparse.Namespace) -> int:
    json_mode = bool(getattr(args, "json", False))
    if json_mode:
        emit_result(boot_mode.as_dict(), json_mode=True)
    else:
        emit_result(boot_mode.render_text(), json_mode=False)
    return 0


def cmd_boot_overview(args: argparse.Namespace) -> int:
    emit_overview(
        "jetson boot",
        boot_sections(),
        json_mode=bool(getattr(args, "json", False)),
    )
    return 0


def _no_verb(args: argparse.Namespace) -> int:
    # `jetson boot` with no sub-verb prints the noun's overview.
    return cmd_boot_overview(args)


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "boot",
        help="Jetson boot-mode knowledge (see 'jetson boot mode').",
    )
    p.add_argument("--json", action="store_true", help=_JSON_HELP)
    p.set_defaults(func=_no_verb, json=False)
    # Propagate the parser class so nested parse errors keep the structured
    # error contract (see _commands/cli.py for the same pattern).
    noun_sub = p.add_subparsers(dest="boot_command", parser_class=type(p))

    m = noun_sub.add_parser(
        "mode",
        help="Desktop (GUI) vs console boot: the systemd default target, with sources.",
    )
    # default=SUPPRESS so `jetson boot --json mode` keeps the parent's True:
    # a child default would otherwise overwrite it on the shared `json` dest.
    m.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=_JSON_HELP)
    m.set_defaults(func=cmd_boot_mode)

    ov = noun_sub.add_parser("overview", help="Describe what the boot noun knows.")
    ov.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help=_JSON_HELP)
    ov.set_defaults(func=cmd_boot_overview)
