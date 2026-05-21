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

## Citation chain

- Image copyright → § 2(1) Nr. 5 UrhG (Lichtbildwerke) + § 72 UrhG (einfache Lichtbilder)
- Attribution for CC-BY → § 13 UrhG (Anerkennung der Urheberschaft) + the CC license terms themselves
- Personality rights of depicted person → § 22 KUG, § 23 KUG (carve-outs)
- AI-image disclosure → Art. 50(2) + Art. 50(4) AI Act (binding 02.08.2026)
- Takedown / damages → § 97 + § 97a UrhG
