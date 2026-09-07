"""``jetson learn`` — the learnability affordance.

Prints a structured self-teaching prompt. Must satisfy the agent-first rubric:
>=200 chars and mention purpose, command map, exit codes, --json, and explain.
"""

from __future__ import annotations

import argparse

from jetson import __version__
from jetson.cli._output import emit_result

_TEXT = """\
jetson — an AgentCulture mesh agent whose domain is NVIDIA Jetson devices.

Purpose
-------
A verified, sourced knowledge base about Jetson hardware, JetPack, and the
surrounding ecosystem: every claim cites its source and gaps are stated rather
than papered over. Most of that is still unbuilt — the CLI carries the
agent-first introspection verbs it was scaffolded with (cited from the teken
`python-cli` reference), plus one sourced domain topic so far, `boot mode`.

Commands
--------
  jetson whoami             Identity from culture.yaml.
  jetson learn              This self-teaching prompt.
  jetson explain <path>...  Markdown docs for any noun/verb path.
  jetson overview           Descriptive snapshot of the agent.
  jetson doctor             Check the agent-identity invariants.
  jetson cli overview       Describe the CLI surface itself.
  jetson boot mode          Desktop (GUI) vs console boot, with sources.
  jetson boot overview      What the boot noun knows (claims, sources, gaps).

Machine-readable output
-----------------------
Every command supports --json. Errors in JSON mode emit
{"code", "message", "remediation"} to stderr. Stdout and stderr never mix.

Exit-code policy
----------------
  0 success
  1 user-input error (bad flag, bad path, missing arg)
  2 environment / setup error
  3+ reserved

More detail
-----------
  jetson explain jetson
"""


def _as_json_payload() -> dict[str, object]:
    return {
        "tool": "jetson",
        "version": __version__,
        "purpose": "Sourced knowledge about NVIDIA Jetson devices, as an agent-first CLI.",
        "commands": [
            {"path": ["whoami"], "summary": "Identity probe from culture.yaml."},
            {"path": ["learn"], "summary": "Self-teaching prompt."},
            {"path": ["explain"], "summary": "Markdown docs by path."},
            {"path": ["overview"], "summary": "Descriptive snapshot of the agent."},
            {"path": ["doctor"], "summary": "Check the agent-identity invariants."},
            {"path": ["cli", "overview"], "summary": "Describe the CLI surface."},
            {
                "path": ["boot", "mode"],
                "summary": "Desktop (GUI) vs console boot, with sources.",
            },
            {
                "path": ["boot", "overview"],
                "summary": "What the boot noun knows (claims, sources, gaps).",
            },
        ],
        "exit_codes": {
            "0": "success",
            "1": "user-input error",
            "2": "environment/setup error",
        },
        "json_support": True,
        "explain_pointer": "jetson explain <path>",
    }


def cmd_learn(args: argparse.Namespace) -> int:
    if getattr(args, "json", False):
        emit_result(_as_json_payload(), json_mode=True)
    else:
        emit_result(_TEXT, json_mode=False)
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "learn",
        help="Print a structured self-teaching prompt for agent consumers.",
    )
    p.add_argument("--json", action="store_true", help="Emit structured JSON.")
    p.set_defaults(func=cmd_learn)
