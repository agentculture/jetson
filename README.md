# jetson

A verified, sourced knowledge base of everything known about NVIDIA Jetson
devices — usable as a CLI, an MCP server, and a multilingual static site. Every
claim cites its source, gaps are stated honestly, and existing projects and
contributors are credited.

## Status — scaffold

That paragraph is the **mission**, not a description of what is built. This repo
was scaffolded from
[`culture-agent-template`](https://github.com/agentculture/culture-agent-template)
on 2026-09-05 and, apart from renaming, is still the unmodified template: a
working agent-first CLI whose verbs are all *introspective*, a mesh identity, the
vendored skill kit, and a green CI/publish baseline.

Not built yet — no Jetson knowledge-base content, no sourcing/citation model, no
MCP server, no static site, and no CLI verb that answers a Jetson question. Some
scaffold prose (the `learn` text, the `explain` catalog, `overview`) still
describes the repo as a template; rewriting it for this agent's domain is
unclaimed work. See [`CLAUDE.md`](CLAUDE.md) for the full mission-vs-reality
breakdown.

## What is here today

- **An agent-first CLI** cited from [teken](https://github.com/agentculture/teken)
  (`afi-cli`) — the runtime package has no third-party dependencies.
- **A mesh identity** — `culture.yaml` (`suffix: jetson`, `backend: colleague`)
  and its resident prompt file `AGENTS.colleague.md`.
- **The vendored skill kit** under `.claude/skills/`, cite-don't-import from
  guildmaster, devague, and colleague. See
  [`docs/skill-sources.md`](docs/skill-sources.md).
- **A build + deploy baseline** — pytest, lint, the agent-first rubric gate, and
  PyPI Trusted Publishing wired into GitHub Actions.

## Quickstart

```bash
uv sync
uv run pytest -n auto                 # run the test suite
uv run jetson whoami                  # identity from culture.yaml
uv run jetson learn                   # self-teaching prompt (add --json)
uv run teken cli doctor . --strict    # the agent-first rubric gate CI runs
```

## CLI

| Verb | What it does |
|------|--------------|
| `whoami` | Report this agent's nick, version, backend, and model from `culture.yaml`. |
| `learn` | Print a structured self-teaching prompt. |
| `explain <path>` | Markdown docs for any noun/verb path. |
| `overview` | Read-only descriptive snapshot of the agent. |
| `doctor` | Check the agent-identity invariants (prompt-file-present, backend-consistency). |
| `cli overview` | Describe the CLI surface itself. |

Every command supports `--json`. Results go to stdout, errors/diagnostics to
stderr (never mixed). Exit codes: `0` success, `1` user error, `2` environment
error, `3+` reserved.

## Contributing

Read [`CLAUDE.md`](CLAUDE.md) first — it carries the conventions:
version-bump-on-every-PR (CI enforces it), the `cicd` PR lane, the worktree
location rule, and the hands-off policy for the vendored `.claude/skills/` tree.

## License

Apache 2.0 — see [`LICENSE`](LICENSE).
