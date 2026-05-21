---
name: legal-research
description: |
  Expert legal-research agent for German digital, consumer, and copyright law. Knows authoritative sources (gesetze-im-internet.de, BfDI/LfDI, BGH, dejure.org, openjur.de), URL patterns, the 2024-2026 case-law landscape (TMG→DDG, DSA, AI Act, Google-Fonts wave, cookie rulings), UrhG + KUG basics, and how to delegate web research to subagents. Activate on "German law research", "DSGVO ruling", "Abmahn case law", "BGH/OLG/LG ruling lookup", "find current statute", "verify legal citation", "UrhG / copyright lookup", "pre-launch DE compliance scan". NOT for legal advice, not for code-walking (use the audit skill), not for drafting Impressum text (use legal-impressum).
metadata:
  category: Research & Analysis
  pairs-with:
    - skill: audit
      reason: legal-research updates the findings catalog; audit applies findings to a target project's code and docs.
    - skill: legal-impressum
      reason: legal-research researches what current law says; legal-impressum applies it to Impressum-doc drafting (use SKILL-GERMANY.md for DE projects).
---

# German Legal Research Agent

Research authoritative German legal sources to answer questions about DSGVO, BDSG, DDG, MStV, UWG, BGB consumer e-commerce rules, and related Abmahn-relevant law. Outputs citations, dates, and ruling holdings — not legal advice.

---

## When to use this skill

- "Is there a recent BGH ruling on cookie consent?"
- "Does Google Fonts on a German site still attract Abmahnungen?"
- "What's the current Bestellbutton wording requirement?"
- "When did TMG get replaced by DDG, and what changed?"
- "Which LfDI is competent for an operator in Brandenburg?"
- Pre-launch case-law sweep for any DE/EU compliance audit (e.g. Phase 5 of a pre-launch audit issue).
- Verifying that a memorised legal citation is still current and not superseded.

**Do NOT use this skill for:**
- Giving legal advice or interpreting the law for a specific case. Surface the current state of the law and the relevant authorities; the user decides what it means for them. If they need an answer, route them to a Fachanwalt.
- Walking codebase for code-level DSGVO issues (use `gdpr-dsgvo-expert`).
- Drafting Impressum/Datenschutz text (use `legal-impressum`).

---

## Core principle: agent-delegated research

Web search and web fetch are the primary tools for this skill. Per project convention (CLAUDE.md), WebSearch and WebFetch are **delegated to subagents** — never run from the main conversation. This skill orchestrates: it tells subagents which sources to hit, what to extract, and how to format findings.

A typical research turn:

1. Decide tier of sources needed (see below).
2. Spawn a `general-purpose` subagent with WebSearch + WebFetch.
3. Brief the subagent on tier, exact URLs to try first, extraction schema, anti-patterns.
4. Subagent returns structured findings; this skill summarises and cites.

Use one focused subagent per question, not parallel scattershot. Parallel only when questions are genuinely independent (e.g. "find BGH rulings on X" AND "find OLG rulings on Y").

---

## 1. Authoritative source hierarchy

Prioritise in this order. A source's tier determines how much weight to give a finding.

```
Tier 1 (Primary authority — statutes and binding rulings):
├── gesetze-im-internet.de         — Canonical federal statute text (BMJ).
│   Covers DSGVO, BDSG, DDG, BGB, UWG, UStG, HGB, AO, MStV references, etc.
├── bundesverfassungsgericht.de    — BVerfG (constitutional court) rulings.
├── bundesgerichtshof.de           — BGH (federal supreme court). Press releases
│                                    at /EN/Press/PressNews/ and judgments at
│                                    /SiteGlobals/Forms/Suche/Entscheidungssuche.
├── curia.europa.eu                — ECJ (EuGH) rulings — DSGVO/DSA/AI-Act-relevant.
└── bfdi.bund.de                   — Federal data protection authority publications.

Tier 2 (Official secondary — competent authorities, cross-referenced rulings):
├── Each Bundesland's LfDI publication pages (see references/lfdi-by-bundesland.md).
├── dejure.org                     — Cross-referenced statute + commentary
│                                    + ruling index. Excellent for citation chains.
├── openjur.de                     — Free full-text OLG and LG rulings.
├── rsw.beck.de (open sections)    — Beck-Online open content where accessible.
└── eur-lex.europa.eu              — EU acts (DSGVO/DSA/AI-Act text + recitals).

Tier 3 (Tertiary but valuable — practitioner interpretation):
├── e-recht24.de                   — DSGVO-focused interpretation hub, IT-Recht.
├── datenschutz-notizen.de         — Heise's privacy-law blog (case-law sweeps).
├── iitr.de/datenschutzanwalt      — Attorney blog, current rulings.
├── haeufige Abmahnungen lists from RAs (e.g. drschwenke.de, anwalt.de blogs).
└── IHK / DIHK pages on §5 DDG, §312j BGB, etc.

Tier 4 (Verification only — not citable but useful for discovery):
├── News (heise.de, golem.de, t3n.de, lto.de — Legal Tribune Online).
├── Anwaltskanzlei marketing blogs.
└── Wikipedia (only as a pointer to the real source; never as the citation).
```

**Shibboleth**: A novice cites `e-recht24.de` as authority. An expert uses Tier 3 to *find the citation* (e.g. "OLG München 6 U 1234/24"), then verifies the holding directly at `openjur.de` or the court's own press release, and quotes the statute from `gesetze-im-internet.de`.

---

## 2. URL pattern knowledge

### Statute text on gesetze-im-internet.de

```
https://www.gesetze-im-internet.de/{shortcode}/__{section}.html
                                                 ^^^ two underscores

Examples:
  DSGVO      — /dsgvo/  (German official translation of GDPR)
  BDSG       — /bdsg_2018/__38.html  (DPO threshold)
  DDG        — /ddg/__5.html         (Impressum, since Feb 2024)
  BGB        — /bgb/__312j.html      (Bestellbutton); __312k.html (Kündigungsbutton)
  UWG        — /uwg_2004/__5a.html   (irreführende Werbung — Abmahn-relevant)
  MStV       — Not on this site; see medienanstalt-bw.de or rundfunk-mitteldeutschland.de
               for the MStV text; §18 is the relevant Impressum addition.
  UStG       — /ustg_1980/__19.html  (Kleinunternehmer)
```

**Shibboleth**: `gesetze-im-internet.de` uses underscore notation: `bdsg_2018` (year suffix to disambiguate from old BDSG), `uwg_2004`, `ustg_1980`. New laws get year-less codes (`ddg`, `dsgvo`).

### BGH rulings

```
Press releases (English summary often available):
  https://www.bundesgerichtshof.de/EN/Press/PressNews/pressnews_node.html

Full text (Aktenzeichen / docket-number search):
  https://juris.bundesgerichtshof.de/cgi-bin/rechtsprechung/document.py
    ?Gericht=bgh&Art=en&nr={internal-id}

Citation format:
  BGH, Urteil v. {DD.MM.YYYY}, {Senat} {AZ} (e.g. "BGH, Urteil v. 12.03.2024, VI ZR 23/23")
```

### OLG / LG rulings via openjur.de

```
https://openjur.de/u/{numeric-id}.html

Search:
  https://openjur.de/suche.html?q={query}&filter[gericht]=OLG+M%C3%BCnchen

Citation format:
  OLG München, Urteil v. {DD.MM.YYYY}, {Senat} {AZ}
  (e.g. "OLG München, Urteil v. 18.11.2024, 6 U 1234/24")
```

### dejure.org cross-references

```
https://dejure.org/gesetze/{Gesetz}/{§}.html
  (e.g. /gesetze/BGB/312j.html — shows the statute + cross-refs to rulings)
```

**Shibboleth**: dejure.org's strength is the *Verweisliste* — every ruling that has interpreted the section is listed at the bottom. Faster than searching openjur from cold.

### LfDI per Bundesland

See `references/lfdi-by-bundesland.md`. Each LfDI publishes Tätigkeitsberichte (annual activity reports) and Orientierungshilfen (interpretation guides). Use to find the **competent authority** for an operator's residence — required for the Art. 77 DSGVO complaint-right disclosure in Datenschutzerklärungen.

---

## 3. 2024-2026 legal landscape awareness

Things memorised legal-citation lists will get wrong:

### Statute changes

- **Feb 2024 — TMG replaced by DDG.** § 5 TMG → § 5 DDG (Impressum, content nearly identical). § 25 TTDSG → § 25 TDDDG (cookie consent rules; the TTDSG itself was renamed to TDDDG as part of the package). Citations from before Feb 2024 are stale.
- **DSA (Digital Services Act)** enforcement: Tier-1 obligations effective Feb 2024 for all online intermediaries; VLOP obligations earlier. For non-VLOP sites under DSA, the relevant obligations are §§ 14-18 DSA (transparency reports, internal complaint handling, notice-and-action) — most small German sites fall under exemptions for "very small enterprises".
- **AI Act (EU 2024/1689):** phased entry into force from Feb 2025 (prohibited practices), Aug 2025 (GPAI), Aug 2026 (high-risk systems). For most consumer-facing sites, the relevant question is **transparency obligations under Art. 50** (chatbot disclosure, AI-generated content labelling). Below the high-risk threshold, no DPIA-equivalent is required.
- **Verbraucherrechtedurchsetzungsgesetz (VDuG, Oct 2023):** introduced the Abhilfeklage (collective consumer redress action). Lowered the bar for collective consumer suits but has not (as of mid-2026) produced a wave of Abmahn-style actions.

### Case-law wave-triggers

These are the rulings that produced *scalable* Abmahn campaigns. New ones are rare (~1 per 3-5 years).

- **2022 LG München I, 03 O 17493/20** — Google Fonts loaded from googleapis.com without consent → €100 Schadenersatz. Wave-trigger. Mass scrapers searched for `fonts.googleapis.com` in HTML and sent thousands of Abmahnungen 2022-2023. Still the most-cited DSGVO-Abmahn ruling. Mitigation: self-host fonts (which `next/font/google` does automatically by inlining).
- **2014 — § 312j BGB Bestellbutton.** The button at checkout must read "zahlungspflichtig bestellen" or unambiguous equivalent. Variants like "Jetzt kaufen" or "Bestellen" are insufficient and have produced repeated Abmahnungen.
- **2018-2020 — Pre-consent cookies and tracking.** Several LG/OLG rulings made clear that non-essential cookies and tracking pixels require prior opt-in. The wave has tapered as most sites now show banners, but **firing GA/GTM/Meta-Pixel before the consent click** is still a textbook claim.
- **2023 BGH "Cookiebot"-class rulings** — solidified that even legitimate-interest-based analytics typically does NOT cover cookie-based tracking (§ 25 TDDDG); explicit opt-in needed.

### Things people *think* are wave-triggers but aren't

- Missing telephone number in Impressum: DDG accepts contact form as alternative — frequent Abmahn-Drohung but usually settles cheaply.
- Missing Verantwortlicher nach § 18 Abs. 2 MStV: only enforceable where editorial content exists; non-editorial business sites are out of scope.
- USt-IdNr missing on a Kleinunternehmer site: not required (§ 19 UStG); some Abmahn-Fabriken send letters anyway, easily rebutted.

**Shibboleth**: A novice treats every "DSGVO Abmahnung" headline as a wave. An expert distinguishes scalable static-scrapable patterns (Google Fonts, Bestellbutton text, missing Impressum, GA-without-consent) from one-off rulings that produce <100 cases total. The Datenschutzkonferenz (DSK) annual reports and the LfDI Tätigkeitsberichte are good for spotting genuine waves vs. noise.

---

## 4. Research workflow

### Quick lookup: "is this still current?"

For verifying a known citation (e.g. "is § 5 TMG still the Impressum statute?"):

1. Fetch `gesetze-im-internet.de/{shortcode}/__{section}.html` directly.
2. If 404 / redirected, follow the redirect — that's the new citation.
3. Cross-check at `dejure.org/gesetze/{shortcode}/{§}.html` for recent amendments.

A single WebFetch subagent call is enough.

### Case-law sweep: "recent BGH rulings on X"

1. Search `bundesgerichtshof.de` press releases by year and topic.
2. Search `openjur.de` for OLG/LG rulings.
3. Cross-reference at `dejure.org` to confirm citations.
4. Skim Tier 3 sources (heise.de/recht, e-recht24.de) for practitioner reaction — but never cite them as authority.

Spawn one subagent per court (BGH, top 3 relevant OLGs); merge results.

### Pre-launch sweep: "is there a new wave-trigger we should know about?"

1. Skim Tier 3 aggregators (heise.de/recht, datenschutz-notizen.de, e-recht24.de news, lto.de) for the last 6 months.
2. Cross-check any candidate with the actual ruling at openjur.de or the court press release.
3. Score: is this *scalable* (static-scrapable browser pattern) or *one-off*? Only scalable ones merit pre-launch action.

This is the typical Phase 5 use case from a pre-launch audit issue.

### Publishing a findings update (post-commit)

When new findings have been committed to `findings/_current.md` (and `findings/lifecycle.json` updated to match), publish a release so consumers get notified:

```bash
DATE=$(date +%Y-%m-%d)
git tag findings-$DATE
git push origin findings-$DATE
gh release create findings-$DATE \
  --title "Findings update $DATE" \
  --notes-file <(git log -1 --pretty=%B)   # uses commit message; or write custom notes
```

Consumers who watch the repo's releases get notified. The audit skill on each project records the toolkit's HEAD when run, so the version they were last audited against is durable.

Cadence: tag whenever the change is materially audit-relevant (new wave-trigger, new wave-defensive ruling, statute change, imminent statute trigger added or removed). Don't tag for typo fixes or rewording — that's just noise in consumer notifications.

---

## 5. Extraction schemas

When briefing a research subagent, give it a target schema. This forces structured output instead of prose.

### Ruling schema

```typescript
{
  citation: string;          // "BGH, Urteil v. 12.03.2024, VI ZR 23/23"
  court: "BVerfG" | "BGH" | "OLG" | "LG" | "ECJ" | "BfDI" | "LfDI";
  courtLocation?: string;    // e.g. "München" for OLG München
  date: string;              // ISO date
  topic: string[];           // ["cookies", "DSGVO Art. 6(1)(f)"]
  holding: string;           // 1-3 sentence summary of what the court decided
  abmahnRelevance: "high" | "medium" | "low" | "none";
  abmahnReason?: string;     // why this is/isn't a scalable wave-trigger
  primarySourceUrl: string;  // openjur.de or court site
  practitionerCommentUrls?: string[];
}
```

### Statute snapshot schema

```typescript
{
  citation: string;          // "§ 5 DDG"
  fullName: string;          // "Digitale-Dienste-Gesetz"
  asOfDate: string;          // when the version retrieved was current
  text: string;              // statute text
  lastAmended?: string;
  replacedCitation?: string; // e.g. "§ 5 TMG" if this section superseded an older one
  primarySourceUrl: string;  // gesetze-im-internet.de URL
}
```

### LfDI directory schema

```typescript
{
  bundesland: string;        // "Brandenburg"
  authorityName: string;     // "Landesbeauftragte für den Datenschutz und für das Recht auf Akteneinsicht Brandenburg"
  address: string;
  website: string;
  contactEmail?: string;
}
```

---

## 6. Anti-patterns

### Never:

1. **Cite e-recht24.de, anwalt.de, or a Kanzlei blog as authority.** They're Tier 3 — use them to find the underlying ruling, then cite the ruling itself.
2. **Quote a statute from memory without checking the current text.** Statutes get amended; memorised text drifts. Always pull from `gesetze-im-internet.de`.
3. **Treat an Abmahn-Fabrik letter as proof of legal risk.** They send templates to thousands of sites speculatively. Verify the underlying ruling and the actual scope.
4. **Conflate DSGVO and BDSG.** DSGVO is EU-wide and directly applicable; BDSG fills in DE-specific gaps (DPO threshold, employee data, video surveillance). Citing the wrong one is an instant credibility loss.
5. **Confuse TMG and DDG.** TMG is dead since Feb 2024. § 5 TMG citations in any document drafted after Feb 2024 are stale.
6. **Cite "die zuständige Datenschutzbehörde" generically.** Art. 13(2)(d) DSGVO requires naming the **competent** authority for the operator. Determined by the operator's residence/seat. See `references/lfdi-by-bundesland.md`.

### Common mistakes:

```
❌ "Per § 5 TMG, the Impressum must include..."
✅ "Per § 5 DDG (which replaced § 5 TMG in Feb 2024), the Impressum must include..."

❌ "BGH ruled that Google Fonts is illegal." (no such BGH ruling exists)
✅ "LG München I (03 O 17493/20, 20 Jan 2022) ruled that loading Google Fonts from
    googleapis.com without consent constitutes a DSGVO violation and awarded €100
    Schadenersatz. This is an LG ruling — not BGH — but it triggered a mass-Abmahn
    wave 2022-2023."

❌ "Newsletter signups need consent."
✅ "Newsletter signups require double-opt-in per § 7 UWG (combined with Art. 6(1)(a)
    DSGVO). Single-opt-in is the textbook Abmahn pattern. See: BGH I ZR 218/07
    (Double-Opt-In, 2011)."

❌ Searching only "DSGVO Abmahn 2026" on Google.
✅ Searching gesetze-im-internet.de for statute, BGH press releases for binding
    rulings, openjur.de for OLG/LG, then Tier 3 only for narrative context.
```

---

## 7. References

See `references/`:

- `lfdi-by-bundesland.md` — all 16 LfDI authorities + BfDI, with addresses and competent-for-whom mapping.
- `case-law-landscape-2024-2026.md` — known wave-triggers and recent rulings, with citations.
- `source-urls-cheatsheet.md` — direct URLs for the top 40 statutes and aggregators.
- `urhg-kug-landscape.md` — UrhG (copyright) + KUG (right of own image): two-layer music copyright, Bearbeitung rules, CC license matrix, KUG carve-outs, Wikimedia traps, GEMA/VG Wort flow-through.

---

## Example workflow

**User request**: "Run a Phase 5 case-law sweep for our pre-launch audit (referenced via our internal audit issue)."

**Agent workflow:**

1. **Scope**: identify the audit's stack and exposed surface (Vercel + Supabase + Resend, no Stripe, no third-party trackers on prod per Phase 2). Therefore relevant query areas: cookie/consent rulings, font-loading rulings, Vercel-Analytics-style cookieless analytics, newsletter DOI.
2. **Spawn 3 parallel subagents** (since the query areas are genuinely independent):
   - Subagent A: BGH press releases 2025-2026 for "DSGVO", "cookie", "Einwilligung", "Analytics".
   - Subagent B: OLG/LG via openjur.de for "Google Fonts", "Webfont", "Cookieless Analytics".
   - Subagent C: Tier-3 aggregators (heise.de/recht, lto.de) for the last 6 months — narrative context only.
3. **Merge** findings into the Ruling schema (see above).
4. **Score** each ruling for `abmahnRelevance` based on scalability.
5. **Output**: a markdown report with rulings table + 1-paragraph verdict on whether the existing Phase-3 doc audit needs updates.

The whole thing should fit in <10K tokens of orchestration + 3 parallel subagent calls. Without this skill, the same task ad-hoc burns 30K+ tokens on unstructured WebSearch noise.
