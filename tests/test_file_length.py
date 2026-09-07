"""Every source and doc file stays under a hard line cap.

A 1000-line file is past the point where a reader — human or agent — can hold it
in one pass, and past the point where `explain`-style prose stays coherent. The
cap is a trip-wire, not a style rule: when a file hits it, split it (a knowledge
topic per module, a doc per subject) rather than raising the number.

Scope: tracked `.py` and `.md` files. The vendored skill kit under
`.claude/skills/` is excluded — it is cited verbatim from upstream and must not
be edited here (see CLAUDE.md, "Vendored means vendored").

Note for whoever trips this first: `CHANGELOG.md` grows monotonically and will
reach the cap eventually. The fix there is to archive older releases into a
`docs/` history file, not to raise MAX_LINES.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

MAX_LINES = 1000

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXCLUDED_PREFIXES = (".claude/skills/",)


def _tracked_sources() -> list[str]:
    """Tracked `.py` / `.md` paths, or an empty list outside a git checkout."""
    try:
        out = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "ls-files", "--", "*.py", "*.md"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - no git/checkout
        return []
    return [line for line in out.splitlines() if line and not line.startswith(_EXCLUDED_PREFIXES)]


_SOURCES = _tracked_sources()


@pytest.mark.skipif(not _SOURCES, reason="not a git checkout — nothing tracked to measure")
@pytest.mark.parametrize("relpath", _SOURCES)
def test_file_is_under_the_line_cap(relpath: str) -> None:
    path = _REPO_ROOT / relpath
    if not path.is_file():  # pragma: no cover - tracked but deleted in the worktree
        pytest.skip(f"{relpath} is tracked but not present")
    lines = path.read_text(encoding="utf-8").count("\n") + 1
    assert lines <= MAX_LINES, (
        f"{relpath} is {lines} lines (cap {MAX_LINES}) — split it rather than "
        f"raising the cap; see this test's docstring."
    )
