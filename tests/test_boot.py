"""Tests for the `boot` noun group — the first domain verbs on this CLI."""

from __future__ import annotations

import json

import pytest

from jetson.cli import main
from jetson.knowledge import boot_mode

# --- boot mode ------------------------------------------------------------


def test_boot_mode_text(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot", "mode"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "graphical.target" in out
    assert "multi-user.target" in out
    assert "systemctl set-default" in out
    # The repair asks display-manager.service rather than hard-coding a unit —
    # a gdm3-only fix strands a lightdm image, and on R38 `gdm3` is only an
    # alias for `gdm` (PR #3 review + observation on this board).
    assert "display-manager.service" in out
    # gdm3 survives only in the unsourced field note about the alias, never in a
    # command the reader is told to run.
    commands = [str(cmd) for claim in boot_mode.CLAIMS for cmd in claim["commands"]]
    assert not any("gdm3" in cmd for cmd in commands)
    # The runlevel spelling jetson-containers documents.
    assert "init 3" in out


def test_boot_mode_json_shape(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot", "mode", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["topic"] == "boot-mode"
    assert payload["claims"]
    assert payload["sources"]
    assert payload["gaps"]
    assert payload["field_notes"]
    for claim in payload["claims"]:
        assert {"id", "statement", "commands", "sources", "confidence"} <= set(claim)


def test_every_claim_cites_a_known_source() -> None:
    """The sourcing contract: no claim may cite a source id that does not exist."""
    for claim in boot_mode.CLAIMS:
        assert claim["sources"], f"{claim['id']} cites no source"
        for source_id in claim["sources"]:
            assert source_id in boot_mode.SOURCES, f"{claim['id']} cites unknown {source_id}"


def test_every_source_has_a_title_and_url() -> None:
    for source_id, source in boot_mode.SOURCES.items():
        assert source["title"], f"{source_id} has no title"
        assert source["url"].startswith("https://"), f"{source_id} has no https url"


def test_vendor_specifics_are_field_notes_not_claims() -> None:
    """Unsourced vendor/release detail must not ride along inside a sourced claim.

    The gdm3-vs-lightdm mapping has no recorded citation, so it lives in
    FIELD_NOTES and is rendered under its own "unsourced" heading — never as part
    of a claim's statement (PR #3 review).
    """
    statements = " ".join(str(claim["statement"]) for claim in boot_mode.CLAIMS).lower()
    assert "gdm3" not in statements
    assert "lightdm" not in statements
    assert any("gdm3" in note for note in boot_mode.FIELD_NOTES)
    assert "unsourced" in boot_mode.render_text().lower()


def test_jetson_specific_practice_credits_jetson_containers() -> None:
    """Borrowed knowledge is cited, not restated as ours.

    The init 3 / init 5 pair and the desktop's memory cost come from
    dusty-nv/jetson-containers; the mission is to credit the projects the
    knowledge comes from, so both claims must cite that source and the source
    must name the project.
    """
    source = boot_mode.SOURCES["jetson-containers-setup"]
    assert "jetson-containers" in source["title"]
    assert "dusty-nv/jetson-containers" in source["url"]
    borrowed = {"init-3-and-5-toggle-the-desktop", "desktop-costs-memory"}
    for claim in boot_mode.CLAIMS:
        if claim["id"] in borrowed:
            assert "jetson-containers-setup" in claim["sources"], claim["id"]
            borrowed.discard(claim["id"])
    assert not borrowed, f"claims went missing: {borrowed}"


def test_a_live_target_is_not_a_live_screen() -> None:
    """The headless trap gets its own claim — it is what actually bites people."""
    claim = next(
        c for c in boot_mode.CLAIMS if c["id"] == "target-says-nothing-about-a-connected-display"
    )
    assert any("/sys/class/drm" in str(cmd) for cmd in claim["commands"])
    assert "disconnected" in str(claim["statement"])


# --- --json in either position -------------------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["boot", "mode", "--json"],
        ["boot", "--json", "mode"],
        ["boot", "overview", "--json"],
        ["boot", "--json", "overview"],
        ["cli", "--json", "overview"],
    ],
)
def test_json_flag_honoured_in_either_position(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    """A noun-level --json must survive the verb parser's default (PR #3 review)."""
    rc = main(argv)
    assert rc == 0
    json.loads(capsys.readouterr().out)  # raises if the handler emitted text


# --- boot overview --------------------------------------------------------


def test_boot_overview_text(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot", "overview"])
    assert rc == 0
    assert "# jetson boot" in capsys.readouterr().out


def test_boot_overview_json_shape(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot", "overview", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["subject"] == "jetson boot"
    titles = [section["title"] for section in payload["sections"]]
    assert "Sources" in titles
    assert "Known gaps" in titles


def test_boot_noun_bare_is_non_empty(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot"])
    assert rc == 0
    assert capsys.readouterr().out.strip()


def test_boot_unknown_flag_structured_error(capsys: pytest.CaptureFixture[str]) -> None:
    # Nested parse errors must keep the structured contract (error:/hint:, exit 1).
    with pytest.raises(SystemExit) as exc:
        main(["boot", "mode", "--bogus"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert err.startswith("error:")
    assert "hint:" in err
