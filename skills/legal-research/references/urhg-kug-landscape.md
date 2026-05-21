# UrhG + KUG copyright landscape

Reference material for the `legal-research` skill, covering the German copyright (UrhG) and personality-rights (KUG) law relevant to web apps that publish images, music, audio, video, or text content from third-party sources.

## Legal framework — the four key statutes

| Statute | Scope |
|---------|-------|
| **UrhG** (Urheberrechtsgesetz) | Core copyright law. Protects "Werke" — original creations of authorship in literature, art, science. |
| **KUG** (Kunsturhebergesetz) | "Right of one's own image" — § 22-24 KUG. Protects depicted persons from publication of their image without consent. |
| **UrhDaG** (Urheberrechts-Diensteanbieter-Gesetz) | DE implementation of EU DSM-Directive Art. 17. Platform liability for user-uploaded content. Mostly applies to OCSSPs (large platforms). |
| **VG-Wahrnehmungsgesetz** | Collecting societies (GEMA, VG Wort, etc.) — flow-through royalty obligations. |

## Core concepts

### 70 years post mortem auctoris (§ 64 UrhG)

Copyright in a Werk expires 70 years after the author's death, computed from end of the year. For multi-author works (co-creation), 70 years after the last surviving author's death.

```
Composer born 1810, died 1890 → public domain since 01.01.1961
Composer died 1955 → public domain since 01.01.2026
Composer died 1960 → public domain on 01.01.2031
```

The death year is what matters. Country of origin doesn't, for works published in DE/EU. **EU-PD ≠ US-PD ≠ UK-PD** — different durations and trigger events.

### Two-layer copyright in music

A piece on a sheet-music site is two separate copyrighted works (or non-copyrighted, depending):

1. **The composition** (Komposition) — runs 70 years pma of the composer
2. **The engraved edition / transcription** (Notensatz / Bearbeitung) — has its own copyright IF it has Schöpfungshöhe (§ 2(2) UrhG)

For modern engravings of PD works, the second layer is increasingly questioned. The IMSLP community treats faithful PD engravings as PD. A *critical edition* (Urtext with editorial markings, fingering, preface) does have its own copyright on the editorial layer.

### Bearbeitung / arrangement (§ 3 UrhG)

An arrangement creates a NEW copyrighted work. The arranger's copyright runs independently. A Reger arrangement of Bach is copyrighted until Reger goes PD (Reger d. 1916 → PD 1987).

### Lichtbildwerke vs Lichtbilder (§ 2(1) Nr. 5 + § 72 UrhG)

Photographs are protected in two tiers:
- **Lichtbildwerk** — artistic photograph with Schöpfungshöhe — 70 years pma
- **Lichtbild** — every other photo (including documentary, snapshots) — 50 years from first publication or from creation if unpublished

Both require licensing if used commercially.

## Wikimedia Commons traps

Wikimedia is the most common source of "free" images. Common traps:

| Trap | Reality |
|------|---------|
| "PD in US" label | Often means published before 1929 in the US. Doesn't establish DE-PD. |
| "PD-self" | Uploader's self-declaration as PD. If wrong, downstream user is still infringing. |
| "{{PD-old}}" | Tags pre-1923 PD work — usually safe but verify the version (modern edition can be copyrighted even if the work is PD) |
| GFDL-only | Older Wikimedia images. GFDL requires inheriting GFDL on derivative works — incompatible with most modern sites. |
| CC-BY without crediting | The image is *uploaded* as CC-BY but the actual creator is not the uploader. Must credit the original creator, not just "via Wikimedia Commons" |

**Safest pattern:** for any Wikimedia image, record `creator` (real photographer / painter / engraver), `creator_death_year` (for PD verification), `wikimedia_license`, `source_url`, `verified_on` in the sidecar.

## KUG — Right of one's own image

§ 22 KUG: "Bildnisse dürfen nur mit Einwilligung des Abgebildeten verbreitet oder öffentlich zur Schau gestellt werden."

§ 23 KUG carve-outs (no consent needed):
1. Bildnisse aus dem Bereich der Zeitgeschichte (historical / public-interest figures, including modern public figures in their public function)
2. Bilder, auf denen die Personen nur als Beiwerk neben einer Landschaft erscheinen
3. Bilder von Versammlungen / Aufzügen
4. Bildnisse, die nicht auf Bestellung angefertigt werden, sofern die Verbreitung einem höheren Interesse der Kunst dient

### Practical rules for websites

- **Historical figures** (composers d. 1900s, etc.): Zeitgeschichte applies. No consent needed.
- **Living public figures performing public function**: Zeitgeschichte applies. Public function only. A musician on stage at a concert is "performing public function"; the same person grocery shopping is not.
- **Private individuals** (e.g. stock photo models): § 22 consent required. Stock photos typically include model releases — verify by checking the source's terms or release URL.
- **Children**: § 22 consent of *both* parents/guardians required, plus the child's assent if old enough. Stock libraries occasionally fail this; check carefully.
- **Crowd shots**: § 23(2) carve-out, but only if person is genuinely "Beiwerk". A face fills frame ≠ Beiwerk.

Violation: § 33 KUG penalty + § 823 + § 1004 BGB Unterlassungsanspruch + EUR 5,000-25,000 typical damages for non-consensual publication.

## CC license matrix

| License | Attribution | Commercial use | Derivatives | Site-use friendly? |
|---------|-------------|----------------|-------------|--------------------|
| CC0 | Optional | Yes | Yes | ✓ Best |
| CC-BY 4.0 | Required (machine + human readable) | Yes | Yes | ✓ Good |
| CC-BY-SA 4.0 | Required | Yes | Yes (must inherit SA) | ⚠ Viral — doesn't combine with proprietary |
| CC-BY-NC 4.0 | Required | **No** | Yes | ✗ Most websites are commercial |
| CC-BY-ND 4.0 | Required | Yes | **No** (cropping is derivative) | ⚠ Cropping for thumbnails risky |
| CC-BY-NC-SA / CC-BY-NC-ND | Various | **No** | Various | ✗ Don't use |

### CC-BY attribution requirements

Per the license text, attribution must include:
- Name (or pseudonym) of the creator
- Title of the work
- Source URL (link to the license-stated source)
- The license name + URL (e.g. "CC BY 4.0" linked to creativecommons.org/licenses/by/4.0/)
- Indication of any modifications

Generic "Image: Wikimedia Commons" is **not** enough.

## GEMA / VG Wort flow-through

Collecting societies represent rights-holders. For a site that:
- Streams audio of GEMA-affiliated composers/arrangers → GEMA license required (even for "free" use)
- Streams audio of post-1972 sound recordings → label/producer rights apply separately
- Distributes sheet music of compositions in GEMA's repertoire — sheet music alone is typically out of GEMA's narrow scope (GEMA handles performance + mechanical rights, not print) — but the publisher's distribution rights still apply via Musikverlag licensing.

Sheet music PDFs of PD compositions are typically safe; sheet music of post-1955 compositions need publisher license regardless of GEMA.

## Common Abmahn vectors specific to copyright

| Vector | Trigger pattern | Mitigation |
|--------|----------------|------------|
| Stock photo without licence | Lawyer subscribes to reverse-image-search alerts on agency catalogues | Buy licences from established stock sites only; keep receipts; sidecar every image |
| Lyrics on a fan / lyrics site without label permission | Search bots from labels' agencies | Don't publish lyrics |
| Album cover used as illustration | Same | Don't use album covers without label permission |
| Concert poster reproduction | Photographer Abmahn | Same — original photographer holds copyright |
| Wikipedia photo without proper CC-BY credit | Photographers actively check for unsourced reuse | Always credit per CC-BY full requirements |
| Composition still in copyright on a "PD library" | Publisher's legal team checks | Verify composer death year before serving any score |

## Practical pre-launch checklist

- [ ] Every image on disk has a sidecar with `license`, `source_url`, `creator`, `verified_on`
- [ ] Every CC-BY image displays attribution somewhere reachable from the image (in caption, on /bildnachweise, or in alt-text-adjacent text)
- [ ] No CC-BY-NC images used
- [ ] No images of recognisable private individuals without documented consent (§ 22 KUG)
- [ ] Music library: every piece has composer_death_year filled; no entries for composers d. after (current_year - 70)
- [ ] Music library: every transcription has source_url to a verifiable upstream (IMSLP, Mutopia, PDMX) and a license that's actually granted by the upstream
- [ ] `/bildnachweise` page is current and matches what's actually displayed

## Sources

- UrhG full text — `https://www.gesetze-im-internet.de/urhg/`
- KUG full text — `https://www.gesetze-im-internet.de/kunsturhg/`
- UrhDaG — `https://www.gesetze-im-internet.de/urhdag/`
- IMSLP license summary — `https://imslp.org/wiki/IMSLP:Copyright_Made_Simple`
- Wikimedia Commons licensing guide — `https://commons.wikimedia.org/wiki/Commons:Licensing`
- GEMA scope — `https://www.gema.de/musikurheber/musik-anmelden/`
