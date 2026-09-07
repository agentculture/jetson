"""Topic: Jetson boot mode — desktop (GUI) vs console.

Answers "how do I make my Jetson boot to the desktop again?" and its inverse.

Credit: the Jetson-specific practice here (the init 3 / init 5 pair and the
memory the desktop costs) is documented by **dusty-nv/jetson-containers**, and
is cited as ``jetson-containers-setup`` rather than restated as if it were ours.
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
    "jetson-containers-setup": {
        "title": (
            'dusty-nv/jetson-containers — "Disabling the Desktop GUI" in docs/setup.md '
            "(Dustin Franklin and contributors)"
        ),
        "url": (
            "https://github.com/dusty-nv/jetson-containers/blob/master/docs/setup.md"
            "#disabling-the-desktop-gui"
        ),
        "kind": "community-project-docs",
    },
    "observed-r38": {
        "title": (
            "Direct observation on a Jetson AGX Thor dev kit — L4T R38.2.2, Ubuntu 24.04.3, "
            "2026-09-07 (systemctl/loginctl/DRM sysfs output)"
        ),
        "url": "https://developer.nvidia.com/embedded/jetson-linux",
        "kind": "direct-observation",
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
        "id": "init-3-and-5-toggle-the-desktop",
        "statement": (
            "'init 3' and 'init 5' are the runlevel-compatibility spelling of the same "
            "switch — systemd maps runlevel3.target to multi-user.target and "
            "runlevel5.target to graphical.target. jetson-containers documents this pair "
            "as the way to stop and restart the desktop on a Jetson. Like isolate, it "
            "changes the running system only; the default target is untouched."
        ),
        "commands": [
            "sudo init 3   # stop the desktop",
            "sudo init 5   # restart the desktop",
        ],
        "sources": ["jetson-containers-setup", "systemd-special"],
        "confidence": "high",
    },
    {
        "id": "desktop-costs-memory",
        "statement": (
            "Turning the desktop off frees the memory the window manager and desktop hold. "
            "jetson-containers puts the figure at around 800 MB for Unity/GNOME and around "
            "250 MB for LXDE — the reason console boot is standard advice on a "
            "memory-constrained Jetson. That is their stated figure, not one measured here, "
            "and it will vary by release and desktop."
        ),
        "commands": ["free -h   # before and after, to see it on your own board"],
        "sources": ["jetson-containers-setup"],
        "confidence": "medium",
    },
    {
        "id": "target-says-nothing-about-a-connected-display",
        "statement": (
            "graphical.target being the default AND active does not mean anything is on "
            "screen. The display manager can be running, with Xorg and a greeter alive, "
            "while every output reads 'disconnected' — no monitor attached, nothing to "
            "show. Check the boot target and the outputs separately before concluding the "
            "GUI is broken: a headless board over SSH looks identical to a broken desktop "
            "if you only look at systemctl. Seeing that desktop from another machine is a "
            "remote-desktop question (VNC/RDP), not a boot-target one."
        ),
        "commands": [
            "systemctl get-default && systemctl is-active graphical.target",
            "systemctl is-active display-manager.service",
            "grep -H . /sys/class/drm/*/status   # 'connected' on at least one output?",
        ],
        "sources": ["observed-r38", "systemctl"],
        "confidence": "high",
    },
    {
        "id": "display-manager-may-be-disabled",
        "statement": (
            "If graphical.target is the default but no desktop appears, the display "
            "manager unit itself may be disabled or masked — a masked unit cannot be "
            "started, and graphical.target comes up without a desktop. Do not guess the "
            "unit name: Debian/Ubuntu (L4T included) point "
            "/etc/systemd/system/display-manager.service at whichever one the image "
            "installed, so ask that symlink first. Note the trap in the masked case: "
            "masking display-manager.service *replaces* that symlink with one to "
            "/dev/null, destroying the only thing that named the unit. Fall back to "
            "/etc/X11/default-display-manager, which Debian writes with the chosen "
            "manager's binary and which masking does not touch, or list the installed "
            "units. Then unmask and enable the real unit — and display-manager.service "
            "too, if that is what was masked."
        ),
        "commands": [
            "ls -l /etc/systemd/system/display-manager.service   # names the unit...",
            "#   ...unless it points at /dev/null — that means it is masked:",
            "cat /etc/X11/default-display-manager      # e.g. /usr/sbin/gdm3",
            "systemctl list-unit-files --type=service | grep -Ei 'gdm|lightdm|sddm|xdm'",
            "sudo systemctl unmask <unit> && sudo systemctl enable --now <unit>",
            "sudo systemctl unmask display-manager.service   # if the alias was masked",
        ],
        "sources": ["systemctl", "observed-r38"],
        "confidence": "high",
    },
]

# Unsourced field notes. Deliberately NOT claims: no recorded source supports
# them, so they are rendered under their own heading and never presented as
# sourced. Promote one to CLAIMS only when it gains a citation.
FIELD_NOTES: list[dict[str, object]] = [
    {
        "note": (
            "NVIDIA's desktop L4T images are generally reported to ship gdm3, with "
            "lightdm on some images and older releases. Which display manager ships with "
            "which JetPack release is not verified here — that is why the claim above "
            "tells you to look rather than assume."
        ),
        "sources": [],
    },
    {
        "note": (
            "Both outputs read 'disconnected' with the whole desktop stack up, and "
            "attaching a KVM-over-IP capture device (JetKVM) on HDMI was what made an "
            "output appear and the desktop show — the boot target was never the problem. "
            "Such a device only presents an EDID once it is powered, so an unpowered "
            "capture dongle looks exactly like no cable at all."
        ),
        "sources": ["observed-r38"],
    },
    {
        "note": (
            "'gdm3.service' is an *alias* and the real unit is 'gdm.service' (with "
            "display-manager.service symlinked to it, and "
            "/etc/X11/default-display-manager reading /usr/sbin/gdm3). A command written "
            "against a hard-coded 'gdm3' therefore leans on an alias a future image need "
            "not keep. One board, one release — not checked across releases."
        ),
        "sources": ["observed-r38"],
    },
]

GAPS: list[str] = [
    "No NVIDIA-published citation is recorded for any claim here. The generic mechanism "
    "is sourced to the systemd manuals, the Jetson-specific practice to "
    "dusty-nv/jetson-containers (a community project, not a vendor document), and two "
    "claims partly to direct observation on a single R38 board. The NVIDIA docs hub is "
    "listed only as an entry point, not as evidence for a claim.",
    "Which display manager ships per JetPack release (gdm3 vs lightdm, and from which "
    "L4T version) is not verified release-by-release. It is recorded as a FIELD_NOTE, "
    "not a claim, so it is never rendered as sourced.",
    "The memory figure in desktop-costs-memory is jetson-containers' stated number "
    "(~800 MB GNOME / ~250 MB LXDE), not a measurement taken here, and no per-release or "
    "per-board measurement has been recorded.",
    "Remote access to the desktop (VNC, RDP, or a streaming host) is named in "
    "target-says-nothing-about-a-connected-display as the thing a headless board actually "
    "needs, but no setup for it is documented here — that is a separate topic.",
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
        "field_notes": [dict(n) for n in FIELD_NOTES],
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
    lines.append("## Field notes (not claims)")
    lines.append("")
    for note in FIELD_NOTES:
        cites = note["sources"]
        tag = f"[sources: {', '.join(str(c) for c in cites)}]" if cites else "[unsourced]"
        lines.append(f"- {tag} {note['note']}")
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
