"""Markdown catalog for ``jetson explain <path>``.

Each entry is verbatim markdown. Keys are command-path tuples. The empty tuple
and ``("jetson",)`` both resolve to the root entry.

Keep bodies self-contained: an agent reading one entry should get enough
context without chaining reads.
"""

from __future__ import annotations

_ROOT = """\
# jetson

An AgentCulture mesh agent whose domain is NVIDIA Jetson devices. The goal is a
verified, sourced knowledge base — every claim citing its source, gaps stated
rather than papered over. Most of that is still unbuilt: the CLI carries the
agent-first introspection verbs it was scaffolded with, plus one sourced domain
topic (`boot mode`).

## Verbs

- `jetson whoami` — identity probe from `culture.yaml`.
- `jetson learn` — structured self-teaching prompt.
- `jetson explain <path>` — markdown docs for any noun/verb.
- `jetson overview` — descriptive snapshot of the agent.
- `jetson doctor` — check the agent-identity invariants.
- `jetson cli overview` — describe the CLI surface.
- `jetson boot mode` — desktop (GUI) vs console boot, with sources.

## Exit-code policy

- `0` success
- `1` user-input error
- `2` environment / setup error
- `3+` reserved

## See also

- `jetson explain whoami`
- `jetson explain doctor`
- `jetson explain boot mode`
"""

_WHOAMI = """\
# jetson whoami

Reports the agent's identity from `culture.yaml`: nick (`suffix`), backend,
served model, and the package version. Read-only.

## Usage

    jetson whoami
    jetson whoami --json
"""

_LEARN = """\
# jetson learn

Prints a structured self-teaching prompt covering purpose, command map,
exit-code policy, `--json` support, and the `explain` pointer.

## Usage

    jetson learn
    jetson learn --json
"""

_EXPLAIN = """\
# jetson explain <path>

Prints markdown documentation for any noun/verb path. Unlike `--help` (terse,
positional), `explain` is global and addressable by path.

## Usage

    jetson explain jetson
    jetson explain whoami
    jetson explain --json <path>
"""

_OVERVIEW = """\
# jetson overview

Read-only descriptive snapshot of the agent: identity (from `culture.yaml`), the
verb surface, and the sibling-pattern artifacts the template carries. Accepts an
ignored `target` so a stray path never hard-fails.

## Usage

    jetson overview
    jetson overview --json
"""

_DOCTOR = """\
# jetson doctor

Checks the agent-identity invariants `steward doctor` verifies:
prompt-file-present and backend-consistency (`colleague` → `AGENTS.colleague.md`), plus a
skills-present check. Exits 1 when unhealthy.

## Usage

    jetson doctor
    jetson doctor --json
"""

_CLI = """\
# jetson cli

Noun group for CLI-surface introspection. `cli overview` describes the CLI
itself (distinct from the global `overview`, which describes the agent).

## Usage

    jetson cli overview
    jetson cli overview --json
"""

_BOOT = """\
# jetson boot

Noun group for Jetson boot-mode knowledge — the first domain noun on this CLI
(its verbs answer a Jetson question rather than describe the agent).

`boot overview` lists what the noun knows: every claim in the `boot-mode` topic,
its sources, and its recorded gaps. `boot mode` renders the topic itself.

Read-only and offline: nothing under this noun inspects the running machine or
shells out, so it reads the same on a Jetson, on a workstation, and in CI.

## Usage

    jetson boot overview
    jetson boot mode
    jetson boot mode --json
"""

_BOOT_MODE = """\
# jetson boot mode

Desktop (GUI) versus console boot on a Jetson, with the source behind each
claim.

Jetson Linux (L4T) is an Ubuntu userspace running systemd, so the mode a board
boots into is the **systemd default target**: `graphical.target` pulls in a
display manager and boots the desktop; `multi-user.target` boots to a text
console with no GUI.

## Persistently (takes effect next boot)

    systemctl get-default                          # what it is set to now
    sudo systemctl set-default graphical.target    # GUI on boot
    sudo systemctl set-default multi-user.target   # console on boot

## For this boot only

    sudo systemctl isolate graphical.target    # bring the GUI up now
    sudo systemctl isolate multi-user.target   # drop to console now

    sudo init 3    # the runlevel spelling of the same switch
    sudo init 5    # ...and back to the desktop

`isolate` stops units the new target does not want, so do not run it over work
you care about in the desktop session. `init 3` / `init 5` is the pair
jetson-containers documents; systemd maps `runlevel3.target` to
`multi-user.target` and `runlevel5.target` to `graphical.target`.

## The target can be right and the screen still blank

`graphical.target` being default *and* active does not mean anything is on
screen — the display manager can be up, Xorg and a greeter running, while every
output reads `disconnected`. Check the two things separately:

    systemctl get-default && systemctl is-active graphical.target
    grep -H . /sys/class/drm/*/status   # 'connected' on at least one output?

A headless board over SSH looks exactly like a broken desktop if you only read
`systemctl`. Seeing the desktop from another machine is a remote-desktop question
(VNC/RDP), not a boot-target one.

## What the desktop costs

jetson-containers puts it at ~800 MB for Unity/GNOME and ~250 MB for LXDE — the
reason console boot is standard advice on a memory-constrained Jetson. That is
their figure, not one measured here.

## If the GUI still does not come up

The display manager unit itself may be disabled or masked — a masked unit cannot
be started, and `graphical.target` comes up without a desktop. Find which unit
the image actually has, then unmask and enable **that** one:

    systemctl status display-manager.service            # resolves to the real unit
    ls -l /etc/systemd/system/display-manager.service   # names it directly
    sudo systemctl unmask <unit> && sudo systemctl enable --now <unit>

Do not hard-code the unit name. Debian/Ubuntu (L4T included) point
`display-manager.service` at whichever manager the image installed — on one
R38 / Ubuntu 24.04 board `gdm3.service` is merely an alias for `gdm.service`.
Which manager a given JetPack release ships is *not* verified here; it is an
unsourced field note, not a claim.

## Sources and gaps

The generic mechanism cites the systemd manuals (`systemd.special(7)`,
`systemctl(1)`); the Jetson-specific practice cites
[dusty-nv/jetson-containers](https://github.com/dusty-nv/jetson-containers)'
`docs/setup.md`; two claims cite direct observation on a single R38 board. No
NVIDIA-published citation is recorded yet. `jetson boot mode --json` carries the
full source list, per-claim confidence, the unsourced field notes, and the
recorded gaps.

## Usage

    jetson boot mode
    jetson boot mode --json
"""


ENTRIES: dict[tuple[str, ...], str] = {
    (): _ROOT,
    ("jetson",): _ROOT,
    ("whoami",): _WHOAMI,
    ("learn",): _LEARN,
    ("explain",): _EXPLAIN,
    ("overview",): _OVERVIEW,
    ("doctor",): _DOCTOR,
    ("cli",): _CLI,
    ("cli", "overview"): _CLI,
    ("boot",): _BOOT,
    ("boot", "overview"): _BOOT,
    ("boot", "mode"): _BOOT_MODE,
}
