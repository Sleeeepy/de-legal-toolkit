---
phase: 6
name: Image attribution
tags: [urhg, kug, image-license, attribution, bildnachweise]
applies_when_compliance_yaml: { image_attribution: true }
---

# Phase 6 — Image attribution

**Goal:** Every image displayed on the site has a verifiable license + source + (where applicable) creator attribution. The `/bildnachweise` page accurately reflects what's on disk.

Risk vectors:
1. **UrhG infringement**: copying a copyrighted image without licence → § 97 UrhG claim from the photographer / agency / heir.
2. **KUG infringement**: showing a recognisable person without their consent → § 22 KUG claim from the depicted person.
3. **CC license violation**: using a CC-BY image without attribution → automatic licence termination → de-facto unlicensed use.
4. **Wikimedia "public domain" trap**: many Wikimedia images are PD in country of origin but not in DE (different PD rules), or PD only for non-commercial use.

## Common license types and their requirements

| License | Attribution required? | Commercial OK? | Derivative OK? | Notes |
|---------|----------------------|----------------|----------------|-------|
| Public Domain | No (but recommended) | Yes | Yes | Verify PD in DE/EU specifically |
| CC0 | No | Yes | Yes | Effectively PD; safest |
| CC-BY | **Yes** | Yes | Yes | Attribution must be machine-AND-human-readable |
| CC-BY-SA | **Yes** | Yes | Yes (must inherit SA) | Don't combine with proprietary works |
| CC-BY-NC | **Yes** | **No** | Yes | Bans commercial use — most websites are commercial |
| CC-BY-ND | **Yes** | Yes | **No** (no derivatives) | Cropping is borderline derivative |
| GFDL | **Yes** | Yes | Yes (must inherit GFDL) | Older Wikimedia images; rare now |
| Editorial use only | **Yes** | Limited | No | Stock photo trap |

## What to check

### 1. Sidecar metadata for every image

For each image directory (e.g. `public/images/composers/`, `public/images/genres/`, `public/images/instruments/`, `public/images/blog/`), every `.webp` / `.jpg` / `.png` must have a sibling `.meta.json` or `.attribution.md`:

```json
{
  "filename": "brahms.webp",
  "source_url": "https://commons.wikimedia.org/wiki/File:Johannes_Brahms_1.jpg",
  "license": "Public Domain",
  "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
  "creator": "Carl Brasch (photographer, d. 1903)",
  "depicted": "Johannes Brahms",
  "depicted_consent": "n/a — historical figure, KUG § 23(1)(1) Bildnis der Zeitgeschichte",
  "verified_on": "2026-05-20"
}
```

Missing sidecars are a launch blocker.

### 2. Recognisable persons → KUG check

For each image of a recognisable person:
- Pre-1900s historical figures: § 23(1)(1) KUG carve-out (Bildnisse der Zeitgeschichte) applies — no consent needed
- Living public figures performing public functions: same carve-out, but case-by-case
- Private individuals: **consent required (§ 22 KUG)** — must be documented in the sidecar
- Children: written consent of guardian + child if old enough

If a sidecar exists but says `depicted_consent: "missing"` or doesn't address it, FAIL.

### 3. /bildnachweise page accuracy

Read the public attribution page. Cross-reference with on-disk sidecars:
- Every CC-BY / CC-BY-SA / CC-BY-NC image on disk must have its creator credited on /bildnachweise OR adjacent to the image at display time
- Every license category in use should be listed with its terms
- Generic "Bilder von Pixabay / Unsplash" is NOT enough — modern Pixabay and Unsplash require attribution per their terms even though they say "free for commercial use"

### 4. Stock photo provenance

For stock photos sourced through any of the `stock-photo-finder`-style skills:
- Confirm the URL on the sidecar still resolves
- Confirm the license on the source page still matches the sidecar (sites can change licensing retroactively for new uses)
- Sample 10 images, fetch their source pages, compare

### 5. AI-generated images

Per Art. 50(2) AI Act (binding 02.08.2026), AI-generated images should be marked machine-readable as synthetic. The marking obligation is on the **provider** (DALL-E, Midjourney, Stable Diffusion service), but the **deployer** (the site) should:
- Ensure the sidecar records `ai_generated: true` + the model used
- Display "KI-generiert" near AI images if the image is published in a public-interest context (Art. 50(4) — likely doesn't apply to decorative images but does apply to news/illustration of factual events)

## Output schema

```markdown
## Phase 6 — Image attribution

Status: PASS | PASS-WITH-NOTES | FAIL

### Sidecar coverage

| Directory | Total images | Sidecars present | Missing |
|-----------|--------------|------------------|---------|
| public/images/composers | 130 | 95 | 35 |
| public/images/genres | 23 | 18 | 5 |
| ... | ... | ... | ... |

### Sidecar quality (sample N)

For a random sample of N sidecars:
- license present
- source_url resolves
- creator field populated where required
- KUG fields populated where person depicted
- verified_on within 12 months

### /bildnachweise page status

Exists: yes/no
Covers each license category in use: yes/no/partial
Names creators where CC-BY required: yes/no

### Findings list

Per finding: file, what's missing, citation, action.

### Verdict
```

## Close gate

Lifted verbatim by the sink into each phase-6 issue's "Close gate" section. This is the canonical example of a phase where lifecycle markers and infra-only closes are the dominant failure mode — the bullets below exist to make those closes impossible.

A phase-6 finding may only be closed when ALL apply:

- [ ] Every image file (`.webp` / `.jpg` / `.png`) in every audited directory has a sibling `.meta.json` (or `.attribution.md`). Sidecar coverage is **100%**, not "100% of new uploads" or "100% of in-scope assets".
- [ ] Sample 10 random sidecars: for **each**, the `source_url` resolves AND the license stated on the source page matches the sidecar's `license` field AND the `creator` is named (where the license requires it) AND `verified_on` is within the last 12 months. The sample is executed manually and the result captured in the close comment — not derived from "the schema validates".
- [ ] Zero sidecars with `creator: null`, `source_url: null`, `license: "unknown"`, `license: "tbd"`, or `status` in (`pending-verification`, `pending-re-source`, `provisional`, `unverified`). If lifecycle markers were used during remediation, a deploy-time gate rejects them at release (see lifecycle-loophole subsection).
- [ ] For every image of a recognisable person: `depicted_consent` populated with either (a) a § 23(1) KUG carve-out citation, or (b) a documented consent reference. `depicted_consent: "missing"` or absent counts as FAIL.
- [ ] `/bildnachweise` page renders an entry for every CC-BY / CC-BY-SA / CC-BY-NC image on disk (or the image displays attribution adjacent to it at render time). Generic "Bilder von Pixabay/Unsplash" is not acceptable.
- [ ] Re-audit of phase 6 with the toolkit at HEAD: sidecar coverage 100%, sample 10 passes, `/bildnachweise` complete.

### Infrastructure vs data — mandatory split for this phase

Phase 6 findings of the form "N user-facing assets, 0 attribution sidecars" almost always bundle infrastructure + data. The close gate splits them:

- [ ] **Infrastructure**: sidecar JSON schema landed; a validator script (e.g. `scripts/validate-sidecars.mjs`) exits 0 on the current tree; an agent or generator exists to populate new sidecars on upload. Name the script + the agent in the close comment.
- [ ] **Data**: every one of the N existing assets has a sidecar with **non-placeholder** values. Specifically: `source_url` resolves, `license` matches the source page, `creator` is populated when required. A sidecar that validates the schema but holds placeholders does NOT satisfy this bullet.

Closing infrastructure alone is not closing. The Bildnachweise aggregator page renders against on-disk content — placeholder sidecars become a public self-incrimination document.

### Lifecycle-state loophole

The sidecar schema permits `status: pending-*` to support a remediation lifecycle. That permission is a closing loophole unless paired with a deploy-time gate:

- [ ] CI / release script asserts: no sidecar in `public/images/**` has `status` in any `pending-*` / `provisional` / `unverified` value AND no sidecar has `creator: null` or `source_url: null`. Release blocks on any hit. Name the script in the close comment.

### Regression guard (HIGH)

- [ ] `scripts/validate-sidecars.mjs` (or equivalent) committed AND wired into CI on every PR AND wired into the release pipeline as a blocking step. The validator checks both schema conformity AND non-placeholder content (the two are independent — schema-valid placeholders are exactly the failure mode this phase exists to prevent).

## Citation chain

- Image copyright → § 2(1) Nr. 5 UrhG (Lichtbildwerke) + § 72 UrhG (einfache Lichtbilder)
- Attribution for CC-BY → § 13 UrhG (Anerkennung der Urheberschaft) + the CC license terms themselves
- Personality rights of depicted person → § 22 KUG, § 23 KUG (carve-outs)
- AI-image disclosure → Art. 50(2) + Art. 50(4) AI Act (binding 02.08.2026)
- Takedown / damages → § 97 + § 97a UrhG
