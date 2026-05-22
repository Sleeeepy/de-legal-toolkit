---
phase: 1
name: Static external resources
tags: [cookies, fonts, third-party-trackers, browser-side]
applies_when_compliance_yaml: { static_resources: true }
---

# Phase 1 — Static external resources

**Goal:** Find any external network resource that fires from the **browser**. Only browser-visible resources are detectable by mass-Abmahn scrapers; server-to-server calls are out of scope for this phase (see Phase 4).

## What to check

Grep across `src/`, `public/`, and project root (NOT `node_modules`, NOT `.next`, NOT `dist`):

### High-priority patterns (wave-trigger relevant)

| Pattern | Why | Mitigation |
|---------|-----|------------|
| `fonts.googleapis.com`, `fonts.gstatic.com` | Google Fonts wave (LG München I 03 O 17493/20, 2022) | Self-host via `next/font/google` (auto-inlined) or `next/font/local` |
| `maps.googleapis.com`, `maps.google.com/embed` | Google Maps embed wave (OLG Köln 6 U 58/22) | Replace with OSM/Leaflet or click-to-load shim |
| `google-analytics.com`, `googletagmanager.com`, `gtag` | Pre-consent tracking | Move behind explicit opt-in |
| `connect.facebook.net`, `facebook.com/tr` | Meta Pixel pre-consent | Move behind explicit opt-in |
| `hotjar.com`, `mixpanel.com`, `intercom.io`, `crisp.chat` | Session/behavioural tracking | Move behind explicit opt-in or replace |
| `youtube.com/embed`, `vimeo.com/video` (iframe) | Third-party iframe before consent | Click-to-load shim |
| `instagram.com/embed`, embedded TikTok/X widgets | Same | Click-to-load shim |

### Medium-priority

| Pattern | Why | Mitigation |
|---------|-----|------------|
| `picsum.photos`, `placeholder.com`, `unsplash.com` (runtime fetch, not curated download) | Third-party CDN for placeholders — usually low-risk but third-country transfer with no contract | Replace with local placeholders |
| External CDN script tags (`cdnjs`, `unpkg`, `jsdelivr`) | Should be bundled, not CDN-loaded | Move to `package.json` dependency |
| `fonts.adobe.com`, `use.typekit` | Adobe Fonts subscription embed | If used, ensure compliant per Adobe DPA |

### Configuration to check

- `next.config.ts` / `next.config.js` → `images.remotePatterns` — every entry is a third-party image host. Each is an Art. 13(1)(e) DSGVO recipient.
- `src/app/**/layout.tsx` `<head>` — confirm fonts loaded via `next/font/*` (safe) and not via `<link href="fonts.googleapis.com">` (unsafe).
- All `*.css` files — grep for `@import url(http...)`.

## How to execute

```
1. Recursive grep src/ public/ for each pattern in the tables above.
2. Read next.config.* and extract images.remotePatterns.
3. Read src/app/layout.tsx and src/app/[locale]/layout.tsx (if i18n).
4. Build the report: file:line for each hit, classified as
   [FUNCTIONAL] (acceptable, e.g. Supabase auth call from your own infra)
   [SELF-HOSTED] (e.g. next/font/google inlining; Vercel Insights proxied first-party)
   [FLAG] (potential Abmahn risk)
```

## Output schema

```markdown
## Phase 1 — Static external resources

Status: PASS | PASS-WITH-NOTES | FAIL

### Browser-side third-party domains found

| File:line | Pattern | Domain | Classification | Citation |
|-----------|---------|--------|----------------|----------|
| ...       | ...     | ...    | [FLAG]         | LG München I 03 O 17493/20 (2022) |

### next.config.ts remotePatterns

- domain.example.com — [purpose, classification]

### Fonts loading mechanism

- next/font/google (Inter, DM Sans, ...) — [SELF-HOSTED]
- OR: `<link href="fonts.googleapis.com/...">` — [FLAG]

### Verdict

One paragraph. Pass = no [FLAG] entries on a brower-rendered route. Fail = any [FLAG] on a public route.
```

## Close gate

Lifted verbatim by the sink into each phase-1 issue's "Close gate" section. A phase-1 finding may only be closed when ALL apply:

- [ ] Recursive grep across `src/` + `public/` (excluding `node_modules`, `.next`, `dist`) matches zero of the high-priority patterns listed above.
- [ ] Every `<head>` font load goes through `next/font/google` (with inlining) or `next/font/local`; no `<link href="fonts.googleapis.com">` and no `@import url(...fonts.googleapis.com...)` anywhere reachable from a production-rendered route.
- [ ] Every entry in `next.config.*` `images.remotePatterns` is justified by a documented purpose (comment, README row, or compliance note); zombie entries removed.
- [ ] Build-time validator (regression guard) committed: a CI step or script that re-runs the grep above and fails the build on any hit. Name the script in the close comment.
- [ ] Re-audit of phase 1 with the toolkit at HEAD: this finding no longer detected.

## Citation chain

When raising a finding, always cite from `findings/_current.md`. If the pattern matches a finding, use its citation. If no finding matches but the pattern is on the high-priority list, cite the underlying ruling/statute referenced in `checks/` itself. If no finding and no ruling can be cited, mark "speculative — surface to legal-research for verification".
