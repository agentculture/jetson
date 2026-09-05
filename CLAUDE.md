# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`jetson` is an AgentCulture mesh agent whose **domain is NVIDIA Jetson
devices**. Its goal: a verified, sourced knowledge base of everything known
about Jetson hardware, JetPack, and the surrounding ecosystem — where every
claim cites its source, gaps are stated honestly rather than papered over, and
the existing projects and contributors the knowledge comes from are credited.

**Read the next section before you plan any work.** The domain above is the
*mission*; almost none of it is built yet.

## State of the repo — mission vs. reality

This repo was scaffolded from
[`culture-agent-template`](https://github.com/agentculture/culture-agent-template)
(commit `4681e62`, 2026-09-05) and, apart from the renaming sweep, is still the
**unmodified template**. What exists on disk today:

- a working agent-first CLI whose verbs are all **introspective** (`whoami`,
  `learn`, `explain`, `overview`, `doctor`) — they describe the agent, not
  Jetson;
- a mesh identity (`culture.yaml` + `AGENTS.colleague.md`);
- the vendored skill kit under `.claude/skills/`;
- a green CI/lint/publish baseline.

What does **not** exist yet — treat every one of these as *(planned)*, and do
not write docs, tests, or `explain` entries that speak of them in the present
tense:

| Planned | Status |
|---------|--------|
| Any Jetson knowledge-base content | Nothing. No data files, no schema, no sourcing/citation model. |
| The MCP server surface | Nothing. No MCP dependency, no server module. |
| The multilingual static site | Nothing. No site generator, no `docs/site/`, no i18n. |
| Verbs that answer Jetson questions | Nothing. The CLI has no domain verbs. |

The package docstrings, `learn` text, `overview` artifacts, `explain` catalog,
and `README.md` still describe the repo as "a clonable template for AgentCulture
mesh agents" — inherited scaffold prose that has not been rewritten for this
agent's domain. Rewriting it is real, unclaimed work; when you touch one of
those surfaces, fix its prose rather than propagating the template wording.

**Keep this file grounded in checked-in reality.** When a section drifts ahead
of what is on disk, mark it `(planned)` or move it under a `## Roadmap` heading
— never state an intention in the present tense.

## Identity

Declared in `culture.yaml`:

```yaml
agents:
- suffix: jetson
  backend: colleague
  model: sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP
```

`backend: colleague` fixes the resident prompt file to **`AGENTS.colleague.md`**
— this agent runs as a colleague resident served by a local Qwen model, so the
mesh runtime reads `AGENTS.colleague.md`, while `CLAUDE.md` (this file) is the
Claude Code guidance file and is *not* the resident prompt. Together the
declaration and its resident prompt satisfy the two invariants `steward doctor`
verifies: **prompt-file-present** and **backend-consistency** (`colleague` ↔
`AGENTS.colleague.md`). `jetson doctor` checks the same invariants locally.

The seed `CLAUDE.md` this file replaced claimed `culture.yaml` declares
`backend: claude`. It does not, and never did in this repo — if you see that
claim resurface anywhere, it is stale.

Sibling repos in the AgentCulture mesh:
[`guildmaster`](https://github.com/agentculture/guildmaster) (skills supplier),
[`steward`](https://github.com/agentculture/steward) (alignment —
`steward doctor`), [`teken`](https://github.com/agentculture/teken) (the
`afi-cli` agent-first-interface scaffolder this CLI is cited from),
[`devague`](https://github.com/agentculture/devague) (the spec/plan method),
and [`colleague`](https://github.com/agentculture/colleague) (the second-mind
CLI). They are checked out beside this repo as `../guildmaster`, `../steward`,
and so on — the skill re-sync procedures assume those paths.

## Commands

```bash
uv sync                                   # create/refresh .venv from uv.lock
uv run pytest -n auto                     # full suite (parallel)
uv run pytest tests/test_cli.py -q        # one file
uv run pytest -k whoami -q                # one test by name
uv run pytest --cov=jetson --cov-report=term   # with coverage (CI gate: 60%)

uv run jetson whoami                      # identity from culture.yaml
uv run jetson learn --json                # self-teaching prompt
uv run jetson explain jetson              # markdown docs for a noun/verb path
uv run jetson doctor                      # agent-identity invariants
```

Lint — CI runs each of these; run them before opening a PR:

```bash
uv run black --check jetson tests         # line length 100
uv run isort --check-only jetson tests
uv run flake8 jetson tests
uv run bandit -c pyproject.toml -r jetson
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
uv run teken cli doctor . --strict        # the agent-first rubric gate
```

The rubric gate is the one that surprises people: `teken cli doctor . --strict`
enforces the agent-first contract (a `learn` verb of a certain shape, an
`explain` entry per registered path, `--json` everywhere, the `overview` noun
rule, the structured error format). Adding a verb without its `explain` entry
fails CI.

## The CLI

Cited (cite-don't-import) from teken's `python-cli` reference via
`teken cli cite`, so the **runtime package has no third-party dependencies** —
`teken` is a dev dependency only. Keep it that way: a knowledge-base
dependency added to `[project.dependencies]` is a deliberate decision, not an
incidental one. `culture.yaml` is even parsed by hand in
`jetson/cli/_commands/whoami.py` rather than pulling in PyYAML.

Structure and the contracts that hold it together:

- `jetson/cli/__init__.py` — `main()` → `_build_parser()` → `_dispatch()`.
  Every verb module under `jetson/cli/_commands/` exposes `register(sub)` and
  is wired in `_build_parser()`; new noun groups follow the same pattern (there
  is a marked spot in the file).
- `jetson/cli/_errors.py` — **every failure raises `CliError`**
  (`{code, message, remediation}`). `_dispatch()` wraps any other exception into
  one, so no Python traceback ever reaches stderr. Exit codes: `0` success,
  `1` user error, `2` environment error, `3+` reserved.
- `jetson/cli/_output.py` — **results to stdout, errors and diagnostics to
  stderr, never mixed**, in both text and `--json` mode. Agents parse on this
  invariant; do not print progress to stdout.
- Argparse errors route through the same contract:
  `_CliArgumentParser.error()` emits `error:` / `hint:` and exits `1` instead of
  argparse's default `2`. Because parse errors happen before `args.json`
  exists, `main()` pre-scans raw argv and sets the class-level `_json_hint`.
  Any new subparser must be created with `parser_class=_CliArgumentParser`
  (the top-level subparsers pass it down; a hand-built nested group must
  propagate it — see `_commands/cli.py` for the pattern).
- `jetson/explain/catalog.py` — markdown keyed by command-path tuples. **Every
  registered noun/verb needs an entry**, and bodies are self-contained (a reader
  should not have to chain reads).
- Descriptive verbs (`overview`, `cli overview`) never hard-fail on a bad
  target — `overview /no/such/path` exits `0`. That is a rubric contract with a
  test guarding it.

## Skills

`.claude/skills/` vendors skills **cite-don't-import**. Provenance, per-skill
notes, and the re-sync procedure live in
[`docs/skill-sources.md`](docs/skill-sources.md) — read it before touching
anything under `.claude/skills/`.

Two upstreams:

- **guildmaster** (the skills supplier) — `cicd`, `communicate`, `version-bump`,
  `agent-config`, `doc-test-alignment`, `pypi-maintainer`, `run-tests`,
  `sonarclaude`.
- **devague** (vendored directly, a tracked divergence) — the eight-leg method
  chain, in flow order:

  ```text
  scope -> think -> challenge -> spec-to-plan -> assign-to-workforce ->
  deviate -> validate-delivery -> summarize-delivery
  ```

- **colleague** (vendored directly, a tracked divergence) — `ask-colleague`.
- Plus `recall` / `remember` (the `eidetic` memory store).

**Vendored means vendored.** Do not reformat, patch, or "fix" a vendored
`SKILL.md` or script — including in response to a review comment. Fix it
upstream in its origin repo and re-sync; a local patch is silently reverted by
the next sync and destroys the `diff -r` check the ledger depends on. The
vendored tree is excluded from markdownlint and from Sonar analysis for the same
reason.

One known upstream wart, left verbatim on purpose: `assign-to-workforce` names
the PR CLI `agex` in two prose lines; the binary is called `devex`. See the
`agex` → `devex` section in `docs/skill-sources.md`.

Tooling prerequisites: **`devex`** (>=0.21) and **`agtag`** (>=0.1) on PATH
(`cicd` and `communicate` shell out to them); **`colleague`** on PATH is
optional — only `ask-colleague` needs it, and it exits with an install hint if
absent.

## Conventions

- **Reach for `ask-colleague` reflexively.** Treat it as the teammate at the
  next desk, not a last resort — its value is a *second, independent mind* (a
  different backend/model), not a stronger one. Before presenting or opening a
  PR on a non-trivial committed diff, run `review`; for a fresh read of an
  unfamiliar area whose answer is independent of your current context, run
  `explore`. Both are read-only (a throwaway worktree, zero side effects), so
  the reflex is always safe. The side-effecting `write --apply` / `write --pr`
  needs the user's go-ahead. Its output is a second opinion to verify and own,
  never authority.
- **Every PR bumps the version** — even docs/config/CI-only PRs. Use the
  `version-bump` skill; the `version-check` CI job comments on and blocks any PR
  whose `pyproject.toml` version matches `main`.
- **PRs go through the `cicd` skill** (`devex pr` + SonarCloud gating). Sign
  online posts as `- jetson (Claude)`; the `cicd` / `communicate` scripts
  resolve the nick from `culture.yaml` and append it themselves, so do not sign
  the body by hand when using them.
- **Deploy**: pushing to `main` publishes to PyPI via Trusted Publishing
  (`.github/workflows/publish.yml`); PRs do a TestPyPI dry-run (skipped on fork
  PRs, which have no OIDC context). The `pypi` / `testpypi` GitHub environments
  and a PyPI Trusted Publisher must be configured for those jobs to succeed.
- **SonarCloud** project key `agentculture_jetson`. The scan step is guarded by
  `if: env.SONAR_TOKEN != ''`, so a token-less repo and fork PRs stay green
  rather than failing.

## Git worktrees

**Every worktree you create by hand lives in `../.worktrees.jetson/<name>/`** —
one repo-named directory beside the checkout, one subfolder per worktree:

```bash
git worktree add ../.worktrees.jetson/<name> -b <branch>
```

Never a shared `../worktrees/`. This workspace holds many sibling projects, and
a generic shared folder accumulates orphaned trees from several repos at once
with nothing indicating who owns which — someone clearing stale trees cannot
tell yours from junk, and an `rm -rf` on the shared folder takes your lane with
it.

Use a branch prefix scoped to the work (`kb/t2`, not `agent/t2`): plain
`agent/*` names collide with leftovers from earlier fan-outs and
`git worktree add -b` fails on an existing branch.

**Following the vendored `assign-to-workforce` skill:** its fan-out example uses
both the shared `../worktrees/` path and `agent/<task-id>` branch names — the
two things above say not to. That skill is cited verbatim and must not be
edited, so override *both* when you follow it.

Remove a worktree with `git worktree remove <path>`, which deletes the directory
and its bookkeeping together. `git worktree prune` only clears metadata for
directories that are *already* gone. Never `rm -rf` a worktree you did not
create.

**Exception — tool-managed throwaways.** `ask-colleague`'s `explore` / `review`
/ `write`-preview verbs create their own detached worktree under
`${TMPDIR:-/tmp}` and reap it on an EXIT trap. Those never persist and need no
owner, so they are outside this rule. Expect `git worktree list` to show one
while such a command is in flight.

## Memory — recall before, remember after

This repo's eidetic memory is **in-repo and public**: a plain `/remember` lands
in `<repo-root>/.eidetic/memory` — committed, shared with the team and mesh
peers (the `claude` and `colleague` backends both resolve the `jetson` scope
from `culture.yaml`), so memory travels with the repo rather than a private
home-dir store. Note that the vendored `remember`/`recall` `SKILL.md` prose
still describes a *private* default; the wrappers' actual policy override
(`scripts/remember.sh`) is public-in-repo, and the script is what runs.

- **`/recall` before you start** a non-trivial task — prior decisions, gotchas,
  "have we done this before?" — so you build on what is known instead of
  re-deriving it.
- **`/remember` when something worth keeping surfaces** — a non-obvious decision
  and its rationale, a constraint, a fix and *why*, a gotcha that cost time.
  Capture it as it happens.

Keep something out of the committed store with `--visibility private` (routes to
`$HOME/.eidetic/memory`); `/recall` reads both and merges. In-repo routing needs
`eidetic >= 0.10.0`. Do not store what the repo already records (code structure,
git history, this file, `CHANGELOG.md`) — store what you would otherwise have to
re-derive.

## Layout

```text
jetson/                   agent-first CLI (cited from teken's python-cli reference)
  cli/                    parser, error/output contract, _commands/ (verbs)
  explain/                markdown catalog for `explain`
tests/                    pytest smoke + introspection tests
.claude/skills/           vendored skill kit (cite-don't-import) — never edit in place
docs/skill-sources.md     skill provenance ledger + re-sync procedures
culture.yaml              mesh identity (suffix + backend)
AGENTS.colleague.md       the resident prompt (backend: colleague)
.github/workflows/        tests + lint + rubric gate + version check; PyPI publish
```
