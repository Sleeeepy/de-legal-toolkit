---
name: audit
description: |
  User-invocable only via /audit — not auto-triggered. Pre-launch and ongoing DSGVO/Abmahn/UrhG compliance audit for German web apps. Walks the target project's codebase, docs, and runtime against a curated findings file from the de-legal-toolkit. Eight phases cover static resources, runtime behaviour, legal docs (Impressum/Datenschutz/AGB/Widerruf), sub-processors, music-library copyright, image attribution, e-commerce (Bestellbutton + Kündigungsbutton + Widerrufsbutton), and AI Act Art. 50.
metadata:
  category: Compliance & Audit
  invocation: user-only
  pairs-with:
    - skill: legal-research
      reason: legal-research updates the findings catalog; audit applies it to a project.
---

# Compliance Audit Skill

Run a pre-launch or refresh audit for German web apps against the curated findings in `findings/_current.md`. Each finding maps to one or more **check files** under `checks/`. The skill orchestrates: discovers the target project, applies the relevant checks, produces a structured report.

This skill is *static check catalog, dynamic priority* (per the toolkit's design ADR). Findings update the priority and reference rulings for existing checks; they do not declare new executable check specs. If a new ruling demands a fundamentally new check pattern, that's a PR to this skill's `checks/` directory, not a runtime mutation.

---

## When to use

- Pre-launch audit of a new project ("Phase 1-6 sweep")
- Re-audit triggered by a new finding from `legal-research` (e.g. issue labelled `ready-for-agent` saying "Re-audit triggered by finding X")
- Targeted re-check of one or two phases after a relevant code change
- Pre-deploy verification when an audit-relevant area changed in the PR diff

**Do NOT use for:**
- Legal-research questions (use the `legal-research` skill)
- Implementing fixes (the audit identifies; the fixes are a separate PR)
- Code review of unrelated changes (use `review` / `simplify`)

---

## Core principles

### 1. Read findings first, always

Before any check executes, read `findings/_current.md` (or the project-pinned snapshot if specified). The findings tell you:
- Which checks are currently `high-severity` vs `medium` vs `low`
- Which rulings to cite when an issue is found
- Which checks are temporarily *defensive* (i.e. the ruling has narrowed the obligation; do NOT raise a finding the user has to chase)

A check without a current finding citation is a check whose underlying legal basis we haven't verified recently. Run it but note "no current finding citation" in the output — flag for the next legal-research sweep.

### 2. Project applicability gate

Before each phase, check the project's `compliance.yml` (or `CLAUDE.md` derived facts) for which phases apply:

```yaml
# project root: compliance.yml
applies:
  static_resources: true    # phase 1
  runtime_playwright: true  # phase 2
  legal_docs: true          # phase 3
  sub_processors: true      # phase 4
  music_library: true       # phase 5 — only for music/library-style sites
  image_attribution: true   # phase 6
  e_commerce: false         # phase 7 (Stripe / checkout) — opt-in
  ai_features: true         # phase 8 (Art. 50 AI Act labelling)
```

A project that's `ai_features: false` skips Phase 8 entirely, no need to walk the codebase looking for AI surfaces.

### 3. Subagent parallelism per phase

Each phase is independent. Spawn one focused subagent per phase, run them in parallel, merge results. Each subagent gets:
- The phase's check file (`checks/phase-N-X.md`) verbatim
- The applicable findings section (filtered to the phase's tags)
- The project root and any project-specific config

### 4. Output format

Single markdown report with one section per phase:

```markdown
## Phase N — {name}

### Status: PASS | PASS-WITH-NOTES | FAIL | NOT-APPLICABLE

| Check | Status | Citation | File / location | Action |
|-------|--------|----------|-----------------|--------|
| ...   | ...    | ...      | ...             | ...    |

### Notes
- {anything that doesn't fit the table}
```

Final section: aggregated punch list ranked by severity (`high` → `low`) with file paths and one-line action per item, **followed by a structured `close_when:` block per finding** so the sink can lift conditions verbatim without paraphrasing.

````markdown
- [ ] **<finding>** — <one-line action> *<citation>* → #<issue>

  ```yaml
  close_when:
    - check: <playbook bullet, verbatim from checks/phase-N-*.md>
    - validator: <scripts/path-or-CI-step>
      expect: exit-0
    - sample:
        n: 10
        check: <what each sampled item must satisfy>
    - re_audit:
        phase: <N>
        expect: finding-not-detected
    # HIGH-severity findings additionally require:
    - regression_guard:
        artifact: <path/to/validator|CI-step|playwright-spec>
        why: prevents silent re-emergence on next audit run
    # When a lifecycle marker is introduced as part of remediation:
    - deploy_gate:
        rejects: [pending-*, provisional, unverified, draft]
        location: <CI-step or runtime-assertion file>
    # When infrastructure and data are both involved:
    - infrastructure: <named artifact landed>
    - data:
        total: <count>
        remediated_with_non_placeholder: <count>
        sample_n: <N>
        sample_clean: true
  ```
````

The punch list is the audit-run's source of truth. Every issue body is one rendering of one row, and the `close_when:` block is what the sink lifts into the issue's Close gate section. This is why the orchestrator emits the block at report time, not the sink at create time — the report is reproducible; the sink is incidental.

**Required:** the report must also include a fixed-bucket "Catalogue does NOT cover" section near the verdict, so the report stays honest about its scope. The catalogue is deliberately violation-driven; absence of findings ≠ absence of risk. Five fixed lines:

```markdown
## Catalogue does NOT cover (verify separately)

- **Defensive evidence trails for not-yet-precedented regulations.** Postures
  marked `FIND-POSTURE-*` in findings/_current.md describe expected
  infrastructure (e.g. Art. 50 AI Act editorial-responsibility evidence) that
  the audit checks for. Verify any AI / e-commerce / health-data surface added
  since the last audit re-triggers its posture check.
- **Case-law sweep since {date of findings/_current.md last update}.** The
  audit applies the findings catalogue as-of the toolkit's last release.
  Run /legal-research — case-law sweep — to refresh before
  treating "no current finding" as authoritative.
- **Paid-launch items deferred to checkout milestone.** PAngV pricing rules,
  § 356(4) BGB digital-service withdrawal exception, Stripe AVV, electronic
  Widerrufsbutton (19.06.2026) — only triggered when checkout flow ships.
- **Pre-engagement Fachanwalt review for high-stakes documents.** AVV
  templates, ToS final pass before paid SaaS launch, Datenschutz post-launch
  fitness review. Toolkit identifies; toolkit does not bless.
- **Industry- or jurisdiction-specific obligations.** BaFin (FinTech), HDPI
  (HealthTech), UStG OSS/MOSS (cross-EU sellers), § 26 BDSG (operators
  with employees) — not in the catalogue.
```

This section is non-negotiable in the output. It keeps the verdict honest without inflating finding counts.

### 5. Lifecycle states are loopholes

Any schema field, status enum, or contract value with a `pending-*`, `provisional`, `unverified`, `draft`, or similar lifecycle marker MUST be paired with a deploy-time gate that rejects those values in production. Otherwise the marker is a closing loophole: an AC like "all N items have a sidecar conforming to the schema" can be satisfied by N placeholders with `status: pending-verification`, the original finding stays present, and the issue closes green.

This is broadly applicable — same shape as TODO comments without dated owners, feature flags without expiry, draft documents linked from production navigation.

How to surface this as a finding:
- When a phase check observes a remediation pattern that introduces a lifecycle value (e.g. Phase 6 sidecars with `status: pending-re-source`), the phase MUST also check for a corresponding deploy-time gate.
- If no gate exists: raise as a finding in its own right — title `lifecycle-state without deploy-time gate at <file:line>`, severity HIGH (it nullifies the remediation it accompanies).
- If a gate exists: cite it in the Close gate's lifecycle-loophole subsection so the closer can verify it's still wired in.

### 6. Infrastructure findings vs data findings

A finding like *"N existing assets lack attribution sidecars"* is actually two pieces of work bundled into one row:

- **Infrastructure**: schema, validator, generator script, agent prompt.
- **Data**: back-populate sidecars for each of the N existing items with verified provenance.

Infrastructure is small, visible, tempting to ship first. Data is grindy, easy to defer, easy to satisfy with placeholders. Bundling them into one issue with one AC almost always closes against the infrastructure layer alone.

**Heuristic for the orchestrator**: when emitting a finding, if both of these hold —
- existing-items count > 0
- current-coverage = 0 (or the remediation requires per-item work, not a schema fix)

— split into two issues, OR emit a single issue whose Close gate has separate `infrastructure:` and `data:` bullets with independently-tickable criteria. The sink renders both; the closer cannot tick the issue closed by addressing only one.

### 7. PASS-WITH-NOTES vs FAIL — operational weight

The per-phase verdict (`PASS / PASS-WITH-NOTES / FAIL / NOT-APPLICABLE`) carries operational weight that the per-finding row should inherit. A finding raised within a `FAIL` phase should ship with stricter close-gate templates (regression guard required, infrastructure/data split required when applicable) than a finding within a `PASS-WITH-NOTES` phase. The orchestrator carries this forward by setting the `close_gate_strictness_override:` field on `FAIL`-phase findings to `strict` regardless of the project's default.

### 8. Sink routing

After producing the aggregated report, route per-finding output to the configured sink. Read `compliance.yml -> audit_output.sink`:

- `github_issues` — one issue per HIGH/MEDIUM finding, LOW items collapsed into one "audit notes" issue. Dedupe against existing open issues; update rather than duplicate. See `sinks/github-issues.md`.
- `gitlab_issues` — same shape, GitLab CLI. See `sinks/gitlab-issues.md`.
- `local_markdown` — write dated markdown files to `audit_output.local_markdown.output_dir`. Default fallback when no issue tracker is configured. See `sinks/local-markdown.md`.
- `single_report` — emit only the aggregated markdown report; no per-finding artifacts.

If the configured sink fails its pre-flight (e.g. `gh auth status` doesn't succeed), fall back to `local_markdown` and emit a warning in the final report. Never silently swallow findings.

### 9. Over-collection is a finding too (missing vs. excess compliance)

The catalogue's centre of gravity is *missing-obligation* findings — no Impressum field, a pre-consent cookie, an absent Bestellbutton. These share a property: more compliance UI is safer, so an auditor's bias toward "add the thing" is aligned with the law.

There is an opposite, easily-missed failure mode: **excess compliance theatre that is itself non-compliant.** A consent that shouldn't exist (an Art. 13 information duty or an Art. 6(1)(b) contract step modelled as a gating, recorded Art. 6(1)(a) consent — see FIND-2026-005) is as much a finding as a consent that's missing. It is *harder* to catch because every symmetry check passes: the doc mentions it, the code records it, the box looks conservative. Rubber-stamping it because "more consent = safer" is the exact error.

When auditing any consent gate, acceptance tick, or "compliance" checkbox, do not stop at "is it present and symmetric?" Ask **"should this exist at all, and is it the right legal instrument?"** A required tick on something that is not a freely-given, withdrawable Art. 6(1)(a)/9(2)(a) consent is over-collection — FAIL it, don't bless it. This applies beyond consent: any UI added in the name of compliance that mis-states the legal basis or couples a non-consent step to a gate is a finding in its own right.

---

## Phases

| # | Phase | Check file | Applies when |
|---|-------|------------|--------------|
| 1 | Static external resources | `checks/phase-1-static-resources.md` | always |
| 2 | Runtime Playwright sweep | `checks/phase-2-runtime.md` | site has a public web surface |
| 3 | Legal document checklists | `checks/phase-3-docs.md` | has Impressum/Datenschutz/AGB/Widerruf docs |
| 4 | Sub-processor reconciliation | `checks/phase-4-sub-processors.md` | uses any external API |
| 5 | Music library copyright | `checks/phase-5-copyright-music.md` | has music/library content (`music_library: true`) |
| 6 | Image attribution | `checks/phase-6-image-attribution.md` | has stock or sourced imagery (`image_attribution: true`) |
| 7 | E-commerce (Bestellbutton + Kündigungsbutton + Widerrufsbutton) | `checks/phase-7-ecommerce.md` | `e_commerce: true` or `subscription: true` |
| 8 | AI Act Art. 50 labelling | `checks/phase-8-ai-act.md` | `ai_features: true` |

Phases 1-4 cover the standard pre-launch checks (static resources, runtime, legal docs, sub-processors). Phases 5-8 added 2026-05-21 to cover copyright, e-commerce, and AI Act features.

---

## Workflow

### Full pre-launch audit

```
1. Read project's compliance.yml (or infer from CLAUDE.md + heuristics)
2. Read findings/_current.md from the toolkit (resolved via the audit skill's own symlink target). Record the toolkit's HEAD short-SHA or latest release tag into compliance.yml:findings_pinned_version so future audits know which baseline was used.
3. Determine applicable phases
4. Spawn one subagent per applicable phase, in parallel
5. Each subagent applies the phase's checks and returns a structured section
6. Aggregate. Output single markdown report.
7. Optionally: post as a GitHub issue or as a PR description.
```

Total cost: 1 orchestration round + N parallel subagent calls. Typical full audit: 7-10 minutes wall-clock.

### Refresh audit (single finding)

```
1. Take the new finding (citation + topic + tags) as input
2. Determine which phase(s) the finding's tags map to (each check file lists tags it covers in frontmatter)
3. Run only those phases against the project
4. Output a delta report: what's new since the previous audit
```

Saves time when only one phase needs re-running.

### Phase-targeted

```
User: "re-run phase 3"
1. Read project's compliance.yml
2. Skip findings file lookup if user says "just check the current docs"
3. Run only phase 3
4. Output single-phase report
```

---

## Anti-patterns

### Never:

1. **Raise findings without a citation.** Every issue surfaced must point at a check rule (in `checks/`) which itself cites the underlying ruling / statute from the findings catalog. "This is bad" is not actionable; "This violates § 312k BGB per LG München I 3 HK O 13796/24 (12.01.2026)" is.
2. **Modify the project's code.** This skill identifies. Fixes are out of scope. Output is a punch list; PR author (human or agent) handles the implementation.
3. **Run a phase whose `applies: false` in `compliance.yml`.** Trust the project to know whether it has Stripe / music library / AI features. Don't second-guess.
4. **Cite a finding marked `status: superseded` or `status: withdrawn` in `findings/lifecycle.json`.** Even if the original check file still references it. Stale citations damage credibility.
5. **Re-run all 8 phases when only 1 is relevant.** Refresh audits should target only the phases the new finding affects.
6. **Paraphrase the playbook into the issue body.** The Close gate section is lifted verbatim from `checks/phase-N-*.md`. Every paraphrase from playbook → report → issue → ticket AC dilutes the original rigor, and the gap is where closure-on-placeholders happens. The sink renders; it does not author.
7. **Close a finding without re-running its phase.** Closing an `[audit]` issue is the natural moment to verify the finding is actually gone. Either wire a repo-level hook (preferred — see sink docs) or run `/audit phase-N` by hand before merging the close-PR. "I shipped the fix" is not equivalent to "the next audit doesn't re-detect it".

### Common mistakes:

```
❌ Phase 1 reports "no findings" because grep didn't match anything.
✅ Phase 1 reports each candidate file checked + the patterns searched, so a
   PASS is auditable, not a silent omission.

❌ Phase 3 reports "Datenschutz is missing X". (vague)
✅ Phase 3 reports "Datenschutz §4 lists 7 sub-processors; sub-processors.ts
   declares 8; Stripe missing from the doc. Add per Art. 13(1)(e) DSGVO."

❌ Phase 5 flags every NULL-license row in the music library individually.
✅ Phase 5 aggregates: "12,043 rows with NULL license, sample 5 piece IDs:
   X, Y, Z. Block list: must resolve before public launch."
```

---

## References

- `checks/` — per-phase check files. Each is self-contained: a subagent can read one file and execute it.
- `sinks/` — per-sink output format references (github-issues, gitlab-issues, local-markdown). Read the one matching `compliance.yml -> audit_output.sink`.
- `../legal-research/` — sister skill for ad-hoc research, also keeps the findings catalog current.
- `../../findings/_current.md` — the live findings the audit applies.
- `../../findings/lifecycle.json` — per-finding status (active / superseded / withdrawn / pending).
- Project's own `compliance.yml` — drives which phases apply and where output goes.

---

## Example invocation

```
User: "Run a pre-launch audit on this repo."

Skill:
1. Detects we're in /path/to/your-project
2. Reads compliance.yml → all phases except phase 7 apply
3. Reads ../de-legal-toolkit/findings/_current.md
4. Spawns 7 parallel subagents (phases 1-6, 8)
5. Merges results
6. Outputs combined markdown report
7. Optionally: gh issue create --title "Audit run YYYY-MM-DD" --body-file report.md
```
