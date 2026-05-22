---
phase: 5
name: Music library copyright
tags: [urhg, music-library, license-metadata, public-domain]
applies_when_compliance_yaml: { music_library: true }
---

# Phase 5 — Music library copyright

**Goal:** Every piece in the music library has a verifiable license + source attribution, and no copyrighted compositions are being served without licence regardless of transcription license.

This phase is **UrhG-driven**, not DSGVO. The risk vector is a copyright Anwalt from a publisher/heir scanning the catalogue and sending a cease-and-desist or damages claim under §§ 97, 97a UrhG.

## Key copyright concepts

### Two-layer copyright

A music piece on the library is **two works**:
1. The **underlying composition** (Komposition) — copyright runs **70 years pma** (post mortem auctoris, § 64 UrhG). A composition by Brahms (d. 1897) is public domain in DE. A composition by Bartók (d. 1945) became public domain on 01.01.2016. A composition by Britten (d. 1976) is still copyrighted until 01.01.2047.
2. The **engraved/transcribed edition** (Notensatz / Bearbeitung) — has its own copyright if it has the required Schöpfungshöhe (§ 2(2) UrhG), but for a faithful modern engraving of a PD work, that's increasingly questionable. The Wikimedia/IMSLP community treats faithful PD engravings as PD.

The trap: "CC0-licensed transcription" does NOT release the underlying composition. PDMX and similar datasets often have CC0 metadata on the *file* but the *composition* may still be copyrighted.

### Bearbeitungen (arrangements)

A composer's arrangement of a PD work creates a NEW copyrighted work (§ 3 UrhG). Bach's arrangements of Vivaldi are PD because Bach is PD; a Reger arrangement of Bach is still under copyright depending on Reger's death date (d. 1916 → PD since 1987).

## What to check

### 1. Every piece has license metadata

Query the project's DB (likely Supabase, table `works` / `pieces` / similar):

```sql
SELECT COUNT(*) FILTER (WHERE license IS NULL) AS null_license,
       COUNT(*) FILTER (WHERE source_url IS NULL) AS null_source,
       COUNT(*) FILTER (WHERE composer_death_year IS NULL) AS null_composer_death,
       COUNT(*) AS total
FROM works;
```

NULL on any of these is a **launch blocker** finding. The audit reports the count + 5 sample IDs.

### 2. CC0 transcription of post-1955 composition

```sql
SELECT id, title, composer_name, composer_death_year, license, source_url
FROM works
WHERE license LIKE '%CC0%' OR license LIKE '%public domain%'
  AND composer_death_year IS NOT NULL
  AND composer_death_year > 1955  -- 70 years before 2026
LIMIT 50;
```

These are flagged: the transcription may be CC0 but the underlying composition is still copyrighted. Each row is a potential takedown claim.

### 3. Bearbeitung / arrangement detection

Look for titles containing: "arr.", "arranged", "Arrangement", "transcribed", "transcription of". Cross-reference with the arranger's death year. Aggregate count + sample IDs.

### 4. Source-URL validity (spot-check)

For a random sample of 20 rows: confirm `source_url` resolves to a page that actually shows the piece's license (IMSLP works page, Mutopia entry, Wikimedia Commons file page).

### 5. Attribution policy

Project's public-facing `/bildnachweise` or `/quellen` page should:
- List the upstream sources (IMSLP, Mutopia, PDMX, etc.) with their licenses
- For non-PD pieces (rare in classical libraries), name the right-holder or publisher

If `/bildnachweise` doesn't exist or doesn't cover the music sources, that's a finding.

## Edge cases

### EU-PD ≠ US-PD ≠ rest-of-world

A composition by Bartók (d. 1945) became PD in EU/UK on 01.01.2016 (70 years pma). In the US, it became PD on 01.01.2026 (95 years from publication for pre-1978 works). A library serving German users should apply DE/EU rules; if the library is also accessed from the US, the more restrictive jurisdiction governs the source — typically the **country of upload** for IMSLP-style libraries.

### GEMA / VG Wort flow-through

If the library streams audio (not just sheet music), and the composer's heirs/estate is GEMA-affiliated, royalty flow-through obligations apply even for transcriptions. Sheet-music-only libraries are typically out of GEMA's scope but **not out of UrhG's scope**.

### "Editions" with proprietary editorial markup

A modern critical edition (e.g. Henle Urtext) of a PD composition has its OWN copyright on the editorial markings/fingering/preface. Scanning a Henle and uploading as CC0 is infringement of the editorial layer, not the composition layer.

## Output schema

```markdown
## Phase 5 — Music library copyright

Status: PASS | PASS-WITH-NOTES | FAIL

### License metadata coverage

| Field | NULL count | Sample IDs |
|-------|------------|------------|
| license | 12,043 | a3f, 4d2, 8b1, ... |
| source_url | 4 | ... |
| composer_death_year | 234 | ... |

### Potentially-copyrighted compositions with CC0 transcriptions

Count: 187. Sample 10 IDs. Each is a launch blocker — the underlying composition is still copyrighted regardless of transcription license.

### Bearbeitung / arrangement entries

Count: 412. Sample 10 with arranger death year. Each needs arranger-PD verification.

### /bildnachweise status

Exists / Missing / Incomplete. List of upstream sources covered vs missing.

### Verdict

PASS = zero NULL-license rows, zero post-1955-composer CC0 entries, valid /bildnachweise.
FAIL = any of the above outstanding.
```

## Close gate

Lifted verbatim by the sink into each phase-5 issue's "Close gate" section. A phase-5 finding may only be closed when ALL apply:

- [ ] DB query: `SELECT COUNT(*) FROM works WHERE license IS NULL OR source_url IS NULL OR composer_death_year IS NULL` returns **0**. No null-license, null-source, or null-composer-death-year rows remain.
- [ ] DB query: zero rows with `license LIKE '%CC0%' OR license LIKE '%public domain%'` AND `composer_death_year > 1955`. Each pre-existing row resolved (re-licensed, re-sourced, or removed) — not marked with a placeholder status.
- [ ] Bearbeitungen (entries with `arr.`, `arranged`, etc. in title): each verified against arranger death year + 70 years, or removed.
- [ ] Sample of 20 random rows: each `source_url` resolves, and the source page's stated license matches the row's `license` field. Sample executed manually and timestamped.
- [ ] `/bildnachweise` (or `/quellen`) page lists every upstream source (IMSLP, Mutopia, PDMX, etc.) and the corresponding license.
- [ ] Re-audit of phase 5: zero blocker rows.

### Infrastructure vs data

Most phase-5 findings split cleanly. Infrastructure-only close is NOT a close.

- [ ] Infrastructure: schema columns + validator + ingest pipeline reject rows lacking license / source / composer death year going forward.
- [ ] Data: every one of the N existing rows flagged by the audit re-checked by hand or by a verified script; placeholder values (`license = "unknown"`, `source_url = null`) do not count as resolved.

### Lifecycle-state loophole

- [ ] No row has `license = 'unknown'`, `source_url IS NULL`, or `status IN ('pending-verification', 'provisional', 'placeholder')` in production. If such markers were introduced during ingest, a release-blocking script asserts they are zero before deploy.

### Regression guard (HIGH)

- [ ] CI step that re-runs the NULL-license + CC0-post-1955 queries against a production-mirror DB on every release candidate and fails the release on any hit. Name the script in the close comment.

## Citation chain

- 70-years-pma rule → § 64 UrhG
- Bearbeitung copyright → § 3 UrhG
- Edition copyright (Notensatz) → § 70 UrhG (older case law treats it as Lichtbild-adjacent; modern engravings on the borderline of Schöpfungshöhe per § 2(2))
- Takedown procedure if violation found → § 97 UrhG (Unterlassung), § 97a UrhG (Abmahnung)
- Damages → § 97(2) UrhG (lizenzanaloge Schadenersatzberechnung)

## Notes for the executing subagent

- Access the project's DB via MCP postgres (LOCAL only) or via `psql` with credentials from `.env.local`.
- Memory note (for music projects): "MCP postgres targets LOCAL only" — never trust `mcp__postgres__execute_sql` for remote state; use temporary credentials for remote verification.
- Do not fix or modify rows. This phase reports only.
