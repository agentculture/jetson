# Jetson boot mode — desktop (GUI) vs console

**Topic id:** `boot-mode` · **CLI:** `jetson boot mode` (add `--json` for the
machine-readable form, with per-claim sources, confidence, and gaps).

Jetson Linux (L4T) is an Ubuntu userspace running systemd, so which mode a board
boots into is the **systemd default target** — sources
[`systemd-special`](#sources), [`systemctl`](#sources):

| Target | What boots |
|--------|------------|
| `graphical.target` | Pulls in a display manager — the desktop. |
| `multi-user.target` | Multi-user text console, no GUI. |

Every heading below names the source ids backing it; the full URLs are in
[Sources](#sources), and `jetson boot mode --json` carries the claim → source
mapping with per-claim confidence.

## Change it persistently (takes effect next boot) — `systemctl`, `systemd-special`

```bash
systemctl get-default                          # what it is set to now
sudo systemctl set-default graphical.target    # GUI on boot
sudo systemctl set-default multi-user.target   # console on boot
```

`set-default` repoints the `default.target` symlink. It needs root, and it does
not change the running system — reboot, or use `isolate` below.

## Change it for this boot only — `systemctl`, `jetson-containers-setup`

```bash
sudo systemctl isolate graphical.target    # bring the GUI up now
sudo systemctl isolate multi-user.target   # drop to console now

sudo init 3    # the runlevel spelling: stop the desktop
sudo init 5    # ...and restart it
```

`isolate` stops units the new target does not want, so do not run it over work
you care about in the desktop session. `init 3` / `init 5` — the pair
jetson-containers documents — is the same switch: systemd maps `runlevel3.target`
to `multi-user.target` and `runlevel5.target` to `graphical.target`.

## What it costs to leave the desktop on — `jetson-containers-setup`

jetson-containers puts the desktop's memory at **~800 MB for Unity/GNOME** and
**~250 MB for LXDE** — the reason console boot is standard advice on a
memory-constrained Jetson. That is their stated figure, not one measured here;
`free -h` before and after tells you what it is on your board.

## "The target is right and I still see nothing" — `observed-r38`, `systemctl`

`graphical.target` being the default **and** active does not mean anything is on
screen. The display manager can be running, with Xorg and a greeter alive, while
every output reads `disconnected` — no monitor attached, nothing to show. Check
the two things separately:

```bash
systemctl get-default && systemctl is-active graphical.target
systemctl is-active display-manager.service
grep -H . /sys/class/drm/*/status   # 'connected' on at least one output?
```

A headless board over SSH looks identical to a broken desktop if you only look at
`systemctl`. Seeing that desktop from another machine is a remote-desktop
question (VNC/RDP), not a boot-target one.

## If the GUI still does not come up — `systemctl`

The display manager unit itself may be disabled or masked — a masked unit cannot
be started, and `graphical.target` comes up without a desktop. Find which display
manager unit the image actually has, then unmask and enable **that** one;
repairing a unit the image does not use changes nothing.

Do not guess the unit name — Debian/Ubuntu (L4T included) point
`/etc/systemd/system/display-manager.service` at whichever one the image
installed, so ask that symlink and repair the unit it names:

```bash
systemctl status display-manager.service            # resolves to the real unit
ls -l /etc/systemd/system/display-manager.service   # names it directly

sudo systemctl unmask <unit> && sudo systemctl enable --now <unit>
```

## Field notes (unsourced — not claims)

No recorded source supports these, so they are kept out of the claim set and are
never rendered as sourced:

- NVIDIA's desktop L4T images are generally reported to ship `gdm3`, with
  `lightdm` on some images and older releases. Which display manager ships with
  which JetPack release is not verified here — which is why the step above tells
  you to look rather than assume.
- On one L4T R38.2.2 / Ubuntu 24.04.3 board, `gdm3.service` is an **alias** and
  the real unit is `gdm.service` (with `display-manager.service` symlinked to
  it). A command hard-coding `gdm3` leans on an alias a future image need not
  keep. Observed on a single board; not checked across releases.

## Sources

| Id | Source |
|----|--------|
| `systemd-special` | [systemd.special(7) — special systemd units](https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html) |
| `systemctl` | [systemctl(1) — control the systemd system and service manager](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) |
| `jetson-containers-setup` | [dusty-nv/jetson-containers — "Disabling the Desktop GUI"](https://github.com/dusty-nv/jetson-containers/blob/master/docs/setup.md#disabling-the-desktop-gui) — Dustin Franklin and contributors |
| `observed-r38` | Direct observation on a Jetson AGX Thor dev kit — L4T R38.2.2, Ubuntu 24.04.3, 2026-09-07 (`systemctl` / `loginctl` / DRM sysfs output) |
| `jetson-linux-docs` | [NVIDIA Jetson documentation hub](https://docs.nvidia.com/jetson/) (entry point only — not evidence for a claim) |

The Jetson-specific practice on this page — the `init 3` / `init 5` pair and what
the desktop costs in memory — is documented by
[**dusty-nv/jetson-containers**](https://github.com/dusty-nv/jetson-containers)
and is cited, not restated as if it were ours.

Claim → source mapping, and each claim's confidence, live in
[`jetson/knowledge/boot_mode.py`](../../jetson/knowledge/boot_mode.py) and are
emitted by `jetson boot mode --json`.

## Known gaps

- No NVIDIA-published citation is recorded for any claim here. The generic
  mechanism is sourced to the systemd manuals, the Jetson-specific practice to
  dusty-nv/jetson-containers (a community project, not a vendor document), and
  two claims partly to direct observation on a single R38 board.
- Which display manager ships per JetPack release (`gdm3` vs `lightdm`, and from
  which L4T version) is not verified release-by-release. It is recorded as a
  field note, not a claim.
- The memory figure is jetson-containers' stated number, not a measurement taken
  here, and no per-release or per-board measurement has been recorded.
- Remote access to the desktop (VNC, RDP, or a streaming host) is named as what a
  headless board actually needs, but no setup for it is documented here — that is
  a separate topic.
- Headless/serial-console specifics (`nvgetty`, the dev kit's serial console
  header) are a neighbouring topic and are not covered.

## How this topic is stored

The content above is data in
[`jetson/knowledge/boot_mode.py`](../../jetson/knowledge/boot_mode.py) — summary,
claims (each with commands, source ids, and a confidence), a source table, an
unsourced field-note list, and an explicit gap list. That shape is the smallest thing that lets a first topic carry
real citations; it is **not** a repo-wide citation schema yet. When a schema
lands, this module is what it has to fit.
