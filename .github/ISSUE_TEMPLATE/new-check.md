---
name: New audit check (code pattern)
about: Propose a static-scrapable pattern that the audit should detect but currently doesn't
title: "check: phase-N [pattern] (e.g. 'check: phase-1 google maps embed')"
labels: ["new-check", "needs-discussion"]
---

## The pattern

<!-- What's the code-level pattern that creates Abmahn risk? Give a concrete example. -->

Pattern: 

Example file path or code snippet:

```
// example
```

## Which audit phase

- [ ] Phase 1 — static resources
- [ ] Phase 2 — runtime Playwright
- [ ] Phase 3 — legal docs
- [ ] Phase 4 — sub-processors
- [ ] Phase 5 — music-library copyright
- [ ] Phase 6 — image attribution
- [ ] Phase 7 — e-commerce
- [ ] Phase 8 — AI Act Art. 50
- [ ] New phase (justify below)

## Why this is checkable

Static-scrapable means a scraper can detect it from outside the site without needing accounts. Examples:
- Substring in HTML (`fonts.googleapis.com`)
- Button text in checkout form
- Cookie name in Set-Cookie header
- Specific Datenschutz section missing

Explain why this pattern is detectable from public surface:

## Linked finding (existing or proposed)

<!-- Every check should be enforceable from a finding/ruling. Link an existing FIND-* ID or attach a New Finding issue. -->

Finding ID: 

OR: opens a new finding issue (link it):

## Proposed Abmahn-relevance

- [ ] HIGH — this is a known wave-trigger pattern
- [ ] MEDIUM — emerging pattern, fewer cases but documented
- [ ] LOW — theoretical concern, no documented enforcement yet

## False-positive risk

<!-- How likely is this check to flag innocent code? E.g. matching `email` is too broad; matching `fonts.googleapis.com` in an HTML attribute is sharp. -->

## Suggested mitigation

<!-- What should a project DO when this check fires? -->
