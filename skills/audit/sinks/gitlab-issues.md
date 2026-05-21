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

Identical to GitHub-issues sink. GitLab Markdown renders the same.

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
