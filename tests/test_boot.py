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


def test_boot_mode_json_shape(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["boot", "mode", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["topic"] == "boot-mode"
    assert payload["claims"] and payload["sources"] and payload["gaps"]
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
