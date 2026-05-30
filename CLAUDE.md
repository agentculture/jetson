# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is (read first)

There is a real split in this repo's identity, and you need to know it before you
touch anything:

- The **packaging metadata** (`pyproject.toml` name/description, the `README.md`
  title, the workspace-level `CLAUDE.md`) frames `jetson` as *"an agent and CLI
  for NVIDIA Jetson edge-AI ops — device setup, container builds, on-device
  deployment."*
- The **actual code** does none of that. It was scaffolded from
  `culture-agent-template` and the CLI's own strings still call it *"a clonable
  template for AgentCulture mesh agents"* (see `jetson/cli/_commands/learn.py`,
  `jetson/explain/catalog.py`, the parser `description` in `jetson/cli/__init__.py`).
  Every verb is generic identity/introspection — `whoami`, `learn`, `explain`,
  `overview`, `doctor`, `cli`. **No Jetson domain functionality exists yet.**

So this is a freshly-minted-but-not-yet-specialized agent. The core work is
replacing the template's self-description and introspection-only surface with
real Jetson ops verbs. Don't assume Jetson features are present — grep first.
(Also: the workspace `CLAUDE.md` lists the command as `jetson-jolt` — that's
stale. The real entry point is `jetson`, per `[project.scripts]`.)

## Two things in one repo: a CLI and a mesh agent

- **A Python CLI** — package `jetson/`, console script `jetson` →
  `jetson.cli:main`. This is what humans and other agents invoke.
- **A Culture mesh agent** — declared by `culture.yaml` (`suffix: jetson`,
  `backend: claude`). A Claude backend on the IRC-based
  [Culture](https://github.com/agentculture/culture) mesh loads **this very
  `CLAUDE.md` as its runtime prompt** when acting as the `jetson` agent.

That dual role matters: `CLAUDE.md` is both Claude Code guidance and the agent's
mesh persona, and it is **load-bearing** — `jetson doctor` and the CI rubric gate
(`teken cli doctor . --strict`) both fail if the `backend: claude` ↔ `CLAUDE.md`
pairing is broken. Don't delete or rename it.

## Commands

Uses **uv**. No system Python has the deps — always go through `uv run`.

```bash
uv sync                                      # install (runtime + dev groups)

uv run pytest -n auto                         # full suite (xdist parallel)
uv run pytest tests/test_cli.py::test_whoami_json   # a single test
uv run pytest -n auto --cov=jetson --cov-report=term # with coverage (CI uses xml)

uv run jetson whoami                          # run the CLI (also: python -m jetson)
uv run jetson explain jetson                  # browse the docs catalog
```

Lint stack is **black + isort + flake8 + bandit** (no ruff, no mypy). Run exactly
what CI runs:

```bash
uv run black --check jetson tests
uv run isort --check-only jetson tests        # profile=black, line length 100
uv run flake8 jetson tests                     # E203/W503 ignored to agree with black
uv run bandit -c pyproject.toml -r jetson
uv run teken cli doctor . --strict             # the agent-first rubric gate (see below)
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
```

## The agent-first contract (the core design constraint)

Every command is built to be driven by another agent, and `teken cli doctor .
--strict` enforces this in CI. The rules are spread across a few files — honor
them in any new command:

- **`--json` on every verb.** Text for humans, `--json` for machines.
- **Strict stream split** (`jetson/cli/_output.py`): results → stdout,
  errors/diagnostics → stderr, *never mixed*, even in JSON mode.
- **Structured errors** (`jetson/cli/_errors.py`): every failure raises
  `CliError(code, message, remediation)`. Text mode renders `error:` + `hint:`
  lines; JSON mode emits `{code, message, remediation}`. No Python traceback may
  ever reach stderr — `_dispatch` wraps unknown exceptions into a `CliError`.
- **Exit-code policy:** `0` success, `1` user error, `2` environment error,
  `3+` reserved. Centralized as constants in `_errors.py`.
- **`learn` and `explain` are part of the contract**, not decoration. `learn`
  must stay ≥200 chars and mention purpose/commands/exit-codes/`--json`/`explain`.
  Every registered noun/verb needs an `explain` catalog entry — a test
  (`test_every_catalog_path_resolves`) checks every catalog path resolves.

## How the CLI is wired (add a command the right way)

`jetson/cli/__init__.py` is the spine. Each command lives in
`jetson/cli/_commands/<name>.py` and exposes a `register(sub)` function;
`_build_parser()` calls them in turn (there's a marked spot to add yours).

Non-obvious plumbing to preserve when extending:

- **`_CliArgumentParser`** overrides argparse's `.error()` so even *parse-time*
  errors (unknown verb, bad flag) produce the `error:`/`hint:` format and exit
  `1` — not argparse's default stderr-dump + exit `2`. `main()` pre-scans raw
  argv for `--json` into a class attr (`_json_hint`) because parse errors happen
  before `args.json` exists.
- **`parser_class` must propagate to sub-subparsers.** When you add a noun group
  with its own verbs, pass `parser_class=type(p)` to `add_subparsers` (see
  `jetson/cli/_commands/cli.py`) or that group's parse errors bypass the contract.
- **Descriptive verbs never hard-fail on a bad target** — `overview` accepts and
  ignores a stray positional so `overview /bogus` still exits 0 (rubric rule).

## Conventions that block merge

- **Zero runtime dependencies.** `pyproject.toml` has `dependencies = []` and it
  stays that way — `culture.yaml` is parsed by hand (no PyYAML) precisely to keep
  it empty. `teken` is dev-only. Don't add a runtime dep without a hard reason.
- **Version bump on every PR** — even docs/config/CI-only changes. The
  `version-check` CI job fails a PR whose `pyproject.toml` version equals
  `origin/main`. The single source of truth is `pyproject.toml`; `__version__`
  is derived from installed package metadata (`importlib.metadata`), so there's
  nothing to hand-sync in `__init__.py`. Use the `version-bump` skill (bumps
  `pyproject.toml` + prepends a Keep-a-Changelog entry to `CHANGELOG.md`).
- **CI = three jobs** in `.github/workflows/tests.yml`: `test` (pytest, coverage,
  and optional SonarCloud gated on `SONAR_TOKEN`), `lint` (the stack above plus
  the rubric gate), and `version-check`. `publish.yml` ships to TestPyPI on
  internal PRs and to PyPI (Trusted Publishing) on push to `main`.

## Packaging note

Distribution name is **`jetson-cli`** (the bare `jetson` was already taken on
PyPI by an unrelated package that reached 0.7.0 — hence our 0.1.x → 0.8.0 jump to
sort above it; see `CHANGELOG.md`). The **import** package and the command are
both `jetson`: `pip install jetson-cli`, then `import jetson` / run `jetson`.
`requires-python = ">=3.12"`.

## Vendored skills

`.claude/skills/` carries 11 skills vendored **cite-don't-import** from
`guildmaster` (provenance + re-sync procedure in `docs/skill-sources.md`). Edit
them here only via that procedure — lift real changes upstream first. The `cicd`
and `communicate` skills need `agex` / `agtag` on `PATH`.
