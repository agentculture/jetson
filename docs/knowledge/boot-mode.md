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

## Change it for this boot only — `systemctl`

```bash
sudo systemctl isolate graphical.target    # bring the GUI up now
sudo systemctl isolate multi-user.target   # drop to console now
```

`isolate` stops units the new target does not want, so do not run it over work
you care about in the desktop session.

## If the GUI still does not come up — `systemctl`

The display manager unit itself may be disabled or masked — a masked unit cannot
be started, and `graphical.target` comes up without a desktop. Find which display
manager unit the image actually has, then unmask and enable **that** one;
repairing a unit the image does not use changes nothing.

```bash
systemctl list-unit-files 'gdm3.service' 'lightdm.service'   # which one exists

sudo systemctl unmask gdm3 && sudo systemctl enable --now gdm3          # if gdm3
sudo systemctl unmask lightdm && sudo systemctl enable --now lightdm    # if lightdm
```

## Field notes (unsourced — not claims)

No recorded source supports these, so they are kept out of the claim set and are
never rendered as sourced:

- NVIDIA's desktop L4T images are generally reported to ship `gdm3`, with
  `lightdm` on some images and older releases. Which display manager ships with
  which JetPack release is not verified here — which is why the step above tells
  you to look rather than assume.

## Sources

| Id | Source |
|----|--------|
| `systemd-special` | [systemd.special(7) — special systemd units](https://www.freedesktop.org/software/systemd/man/latest/systemd.special.html) |
| `systemctl` | [systemctl(1) — control the systemd system and service manager](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) |
| `jetson-linux-docs` | [NVIDIA Jetson documentation hub](https://docs.nvidia.com/jetson/) (entry point only — not evidence for a claim) |

Claim → source mapping, and each claim's confidence, live in
[`jetson/knowledge/boot_mode.py`](../../jetson/knowledge/boot_mode.py) and are
emitted by `jetson boot mode --json`.

## Known gaps

- No NVIDIA-published citation is recorded for any claim here. The mechanism is
  generic systemd on L4T's Ubuntu userspace, sourced to the systemd manuals.
- Which display manager ships per JetPack release (`gdm3` vs `lightdm`, and from
  which L4T version) is not verified release-by-release. It is recorded as a
  field note, not a claim.
- The widely repeated advice that booting to `multi-user.target` frees a useful
  amount of RAM on a Jetson dev kit is deliberately **not** stated as a claim: no
  measured, citable figure has been recorded here yet.
- Headless/serial-console specifics (`nvgetty`, the dev kit's serial console
  header) are a neighbouring topic and are not covered.

## How this topic is stored

The content above is data in
[`jetson/knowledge/boot_mode.py`](../../jetson/knowledge/boot_mode.py) — summary,
claims (each with commands, source ids, and a confidence), a source table, an
unsourced field-note list, and an explicit gap list. That shape is the smallest thing that lets a first topic carry
real citations; it is **not** a repo-wide citation schema yet. When a schema
lands, this module is what it has to fit.
