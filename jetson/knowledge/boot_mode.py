"""Topic: Jetson boot mode — desktop (GUI) vs console.

Answers "how do I make my Jetson boot to the desktop again?" and its inverse.
Everything here is knowledge, not measurement: nothing in this module inspects
the running machine or shells out, so it reads the same on a Jetson, on a
laptop, and in CI. To see what a given board is *currently* set to, run the
``systemctl get-default`` command the claims below cite.
"""

from __future__ import annotations

TOPIC = "boot-mode"
TITLE = "Jetson boot mode — desktop (GUI) vs console"

SUMMARY = (
    "Jetson Linux (L4T) is an Ubuntu userspace running systemd, so which mode a "
    "board boots into is the systemd default target: graphical.target boots the "
    "desktop, multi-user.target boots to a text console. Switch it persistently "
    "with 'systemctl set-default', or for the current boot only with "
    "'systemctl isolate'."
)

SOURCES: dict[str, dict[str, str]] = {
    "systemd-special": {
        "title": "systemd.special(7) — special systemd units",
        "url": "https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html",
        "kind": "upstream-manual",
    },
    "systemctl": {
        "title": "systemctl(1) — control the systemd system and service manager",
        "url": "https://www.freedesktop.org/software/systemd/man/latest/systemctl.html",
        "kind": "upstream-manual",
    },
    "jetson-linux-docs": {
        "title": "NVIDIA Jetson documentation hub (Jetson Linux / JetPack)",
        "url": "https://docs.nvidia.com/jetson/",
        "kind": "vendor-docs-index",
    },
}

CLAIMS: list[dict[str, object]] = [
    {
        "id": "default-target-selects-mode",
        "statement": (
            "The boot mode is the systemd default target: graphical.target pulls in a "
            "display manager and boots to the desktop; multi-user.target boots to a "
            "multi-user text console with no GUI."
        ),
        "commands": ["systemctl get-default"],
        "sources": ["systemd-special", "systemctl"],
        "confidence": "high",
    },
    {
        "id": "set-default-persists",
        "statement": (
            "'systemctl set-default' changes the mode for every subsequent boot by "
            "repointing the default.target symlink. It needs root and takes effect on "
            "the next reboot, not immediately."
        ),
        "commands": [
            "sudo systemctl set-default graphical.target   # GUI on boot",
            "sudo systemctl set-default multi-user.target   # console on boot",
        ],
        "sources": ["systemctl", "systemd-special"],
        "confidence": "high",
    },
    {
        "id": "isolate-switches-now",
        "statement": (
            "'systemctl isolate' switches the running system to a target immediately, "
            "without touching the default. Use it to start or drop the desktop for the "
            "current boot only; it stops units the new target does not want, so do not "
            "run it over work you care about on the desktop session."
        ),
        "commands": [
            "sudo systemctl isolate graphical.target    # bring the GUI up now",
            "sudo systemctl isolate multi-user.target   # drop to console now",
        ],
        "sources": ["systemctl"],
        "confidence": "high",
    },
    {
        "id": "display-manager-may-be-disabled",
        "statement": (
            "If graphical.target is the default but no desktop appears, the display "
            "manager unit itself may be disabled or masked — a masked unit cannot be "
            "started, and graphical.target comes up without a desktop. Find which "
            "display manager unit the image actually has, then unmask and enable that "
            "one. Repairing a unit the image does not use changes nothing."
        ),
        "commands": [
            "systemctl list-unit-files 'gdm3.service' 'lightdm.service'   # which one exists",
            "sudo systemctl unmask gdm3 && sudo systemctl enable --now gdm3        # if gdm3",
            "sudo systemctl unmask lightdm && sudo systemctl enable --now lightdm  # if lightdm",
        ],
        "sources": ["systemctl"],
        "confidence": "high",
    },
]

# Unsourced field notes. Deliberately NOT claims: no recorded source supports
# them, so they are rendered under their own heading and never presented as
# sourced. Promote one to CLAIMS only when it gains a citation.
FIELD_NOTES: list[str] = [
    "NVIDIA's desktop L4T images are generally reported to ship gdm3, with lightdm on "
    "some images and older releases. Which display manager ships with which JetPack "
    "release is not verified here — that is why the claim above tells you to look "
    "rather than assume.",
]

GAPS: list[str] = [
    "No NVIDIA-published citation is recorded for any claim here. The mechanism is "
    "generic systemd on L4T's Ubuntu userspace, sourced to the systemd manuals; the "
    "vendor docs hub is listed only as an entry point, not as evidence for a claim.",
    "Which display manager ships per JetPack release (gdm3 vs lightdm, and from which "
    "L4T version) is not verified release-by-release. It is recorded as a FIELD_NOTE, "
    "not a claim, so it is never rendered as sourced.",
    "The widely repeated advice that booting to multi-user.target frees a useful amount "
    "of RAM on a Jetson dev kit is deliberately not stated as a claim: no measured, "
    "citable figure has been recorded here yet.",
    "Headless/serial-console specifics (nvgetty, the serial console on the dev kit "
    "header) are a neighbouring topic and are not covered.",
]


def as_dict() -> dict[str, object]:
    """The whole topic as a JSON-serialisable payload."""
    return {
        "topic": TOPIC,
        "title": TITLE,
        "summary": SUMMARY,
        "claims": [dict(c) for c in CLAIMS],
        "sources": {k: dict(v) for k, v in SOURCES.items()},
        "field_notes": list(FIELD_NOTES),
        "gaps": list(GAPS),
    }


def render_text() -> str:
    """Human/agent-readable markdown for the whole topic, citations included."""
    lines = [f"# {TITLE}", "", SUMMARY, ""]
    for claim in CLAIMS:
        cites = ", ".join(str(s) for s in claim["sources"])  # type: ignore[union-attr]
        lines.append(f"## {claim['id']}  [{claim['confidence']}; sources: {cites}]")
        lines.append("")
        lines.append(str(claim["statement"]))
        lines.append("")
        for cmd in claim["commands"]:  # type: ignore[union-attr]
            lines.append(f"    {cmd}")
        lines.append("")
    lines.append("## Field notes (unsourced — not claims)")
    lines.append("")
    for note in FIELD_NOTES:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    for sid, src in SOURCES.items():
        lines.append(f"- `{sid}` — {src['title']}: {src['url']}")
    lines.append("")
    lines.append("## Known gaps")
    lines.append("")
    for gap in GAPS:
        lines.append(f"- {gap}")
    return "\n".join(lines).rstrip()
