---
sink: gitlab_issues
requires: glab CLI authenticated
---

# Sink: GitLab Issues

Same shape as GitHub-issues sink, different CLI. See `github-issues.md` for the design rationale; this file documents the GitLab-specific commands.

## Pre-flight

1. Verify `glab auth status` succeeds. If not: abort, emit warning, fall back to local-markdown.
2. Determine target project from `compliance.yml -> audit_output.gitlab.project` if present; otherwise from `git remote get-url origin` parsed for GitLab hostname.
3. Verify each label in `audit_output.gitlab.labels` exists via `glab label list`. Create missing ones with `glab label create --name <name> --description "Created by de-legal-toolkit audit" --color "#BFD4F2"`.

## Dedupe before creating

```bash
glab issue list --opened --search "[audit]" --output json --per-page 200
```

Same dedupe logic as GitHub-issues sink. Match titles exactly; update via `glab issue update <iid> --description <path>` rather than create-duplicate.

## Title format

Identical to GitHub-issues sink:
```
[audit] phase-N: <one-line finding description>
```

## Body template

Identical to GitHub-issues sink. GitLab Markdown renders the same — including the Close gate section, lifecycle-loophole subsection, HIGH-severity regression-guard subsection, and infrastructure/data split. See `github-issues.md` → "Body template" and "Close-gate provenance".

## Close-gate strictness

Same knob as the GitHub-issues sink, read from `compliance.yml -> audit_output.close_gate_strictness`. Default `strict`. Values: `strict`, `severity-scaled`, `advisory`, `off`. See `github-issues.md` for semantics.

## Re-audit-on-close hook

GitLab equivalent of the GitHub-Actions hook: a GitLab CI pipeline triggered by `issues.close` (via webhook) that runs `/audit phase-N` for the phase named in the closed issue's title. If the finding re-detects, the pipeline reopens the issue and applies the `false-close` label.

For self-hosted GitLab, the webhook target is the project's CI runner; for gitlab.com, the simplest option is a scheduled re-audit pipeline that compares closed-since-last-run issues against current findings and reopens mismatches.

## LOW-severity collapse

Same — single issue titled `[audit] minor items — <YYYY-MM-DD>`.

## Assignee

Read `compliance.yml -> audit_output.gitlab.assignee`. `glab issue create --assignee <username>`.

## Failure modes

Same as GitHub-issues sink, with `glab` substituted for `gh`. Note: self-hosted GitLab instances need `GITLAB_HOST` env var set before `glab auth login`; verify this works in pre-flight.

## Differences from GitHub-issues sink

- GitLab uses **iid** (project-internal issue ID) where GitHub uses **number** — `glab issue view <iid>` not `glab issue view <number>`
- GitLab labels can have hex color codes (`#BFD4F2`); GitHub strips the `#`
- GitLab issues support **confidential** flag — if `compliance.yml -> audit_output.gitlab.confidential: true`, create issues with `--confidential` (useful for security-adjacent findings)
- GitLab has milestone support — if `compliance.yml -> audit_output.gitlab.milestone` is set, attach via `--milestone <id>`
