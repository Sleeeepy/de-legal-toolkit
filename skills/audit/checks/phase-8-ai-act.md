---
phase: 8
name: AI Act Art. 50 transparency
tags: [ai-act, art-50, chatbot-disclosure, ai-content-labelling, editorial-responsibility]
applies_when_compliance_yaml: { ai_features: true }
---

# Phase 8 — AI Act Art. 50 transparency

**Goal:** Any AI feature on the site that interacts with users or generates user-facing content satisfies Art. 50 of EU Regulation 2024/1689 (AI Act), binding from **02.08.2026** with no grace period.

The four Art. 50 obligations:

| Paragraph | Obligation | Addressee | Relevant to deployer? |
|-----------|-----------|-----------|----------------------|
| 50(1) | AI-system interaction disclosure | Provider | Indirect (carve-out for "obvious from context") |
| 50(2) | Machine-readable watermarking | **Provider** | No — provider obligation |
| 50(3) | Emotion-recognition / biometric-categorisation disclosure | Deployer | Only if such systems used |
| 50(4) sentence 1 | Deep-fake disclosure | Deployer | Only if deep-fakes generated/used |
| 50(4) sentence 2 | AI-generated public-interest text labelling | Deployer | With "human review / editorial responsibility" carve-out |

## What to check

### 1. Catalog every AI surface in the codebase

Grep + read to find:
- AI text generation (OpenAI, Anthropic, Mistral SDKs — model.invoke / chat.completions.create / messages.create)
- AI image generation (DALL-E, Stable Diffusion, Midjourney API)
- Conversational chatbots (Vercel AI SDK `useChat`, Mendable, Crisp AI, etc.)
- AI-powered search (semantic search via embeddings)
- AI-driven personalisation that affects what's shown to the user

For each, determine:
- **User-facing role**: does the AI output reach a user, or is it internal (e.g. classification of admin records)?
- **Interactive (chatbot) vs one-shot (transform tool)?**
- **Who reviews before publication?** Operator? End-user (the teacher)? Nobody (auto-publish)?

### 2. Apply Art. 50 by surface

For each AI surface, walk through:

#### Chatbot / conversational AI
- Art. 50(1) applies (interaction disclosure)
- Required: "Du sprichst mit einem KI-System" or equivalent in the chat UI on first message
- The "obvious from the context" carve-out applies if the surface is explicitly branded as AI (e.g. a button labelled "Frag die KI" makes the AI nature obvious)

#### One-shot AI transform invoked by a button (e.g. "Mit KI verbessern")
- Art. 50(1) borderline — the button label makes it obvious, so carve-out likely applies
- Art. 50(2) is a provider obligation, not yours
- Art. 50(4) sentence 2 applies *only if* the output is "text published with the purpose of informing the public on matters of public interest"
  - Commercial profile text → typically NO
  - Blog posts on civic topics → potentially YES → need labelling OR editorial-responsibility carve-out
- **Editorial-responsibility carve-out**: if the user (not the operator) explicitly reviews + accepts + publishes the AI output, AND holds editorial responsibility for the published content, the labelling obligation does not apply

#### AI image generation
- Art. 50(2) watermarking is the provider's job (OpenAI, Stability, etc.)
- Art. 50(4) sentence 1 (deep-fakes) — only if the image depicts a real person and could be mistaken for genuine
- For decorative AI illustrations, no specific labelling obligation under Art. 50, but practitioner consensus is to label anyway

#### AI-powered features that don't produce user-facing content
- Backend classification, embeddings, ranking → typically out of Art. 50 scope (they're not "interaction" or "publication")
- But: if the ranking affects what content is shown in a way that influences opinion, may be DSA-relevant

### 3. Mitigation pattern evidence — per-surface

Maps to finding **FIND-POSTURE-2026-AI-TRAIL** in `findings/_current.md`. This is a *defensive posture* check — not a violation today, but the evidence trail that would deflect an aggressive Art. 50(4) reading once the regulation binds (02.08.2026).

For **each** AI surface that emits text into public user-facing content (NOT just the most prominent one — every surface re-triggers), verify all three pieces:

1. **Acceptance-log table** persisting `ai_suggestion`, `final_text`, `was_edited`, `accepted_at`, `user_id` per acceptance event. Locate the table by grepping migrations for `ai*_log`, `acceptance_log`, or by inspecting the server action invoked from the AI button.
2. **UI responsibility note** displayed on the surface itself — *not* on the consent modal, *not* only on the import flow. Pattern: "Du bist verantwortlich für den finalen Text — bitte prüfen, bevor du übernimmst." Must be visible in a screenshot of the surface.
3. **Datenschutz framing** in regulation language. The Datenschutz's AI-feature section explicitly cites Art. 50(4) sentence 2 and states the operator's position that the user holds editorial responsibility for AI-touched published content.

**Per-surface scoping is critical.** Every new AI feature re-triggers this check independently. A project may have acceptance-log + UI note on the profile editor, but adding an AI-powered blog assistant next month means the blog assistant needs its own logging + UI note + (possibly) Datenschutz extension.

**Severity:** Raise as **MEDIUM** for each surface missing any of the three pieces (one MEDIUM per missing piece per surface, OR one MEDIUM per surface noting which pieces are missing — pick whichever the project's audit-output sink handles more cleanly). Reasoning is in the finding entry: time-bounded (Aug 2026 phase-in) + no precedent yet → MEDIUM, not HIGH.

**If the project does not currently rely on the editorial-responsibility carve-out** (i.e. AI surfaces label all output as AI-generated): this check passes without raising findings. Document the labelling pattern in the report.

### 4. Phase-in date

Today's date vs 02.08.2026:
- **Before**: PASS-WITH-NOTES (recommend implementing before 02.08.2026)
- **On or after**: FAIL if any obligation unmet

## Output schema

```markdown
## Phase 8 — AI Act Art. 50

Status: PASS | PASS-WITH-NOTES | FAIL | NOT-APPLICABLE

### AI surfaces catalogue

| Surface | Type | User-facing? | Reviewer | Art. 50 obligation |
|---------|------|--------------|----------|---------------------|
| "Mit KI verbessern" text polish | one-shot transform | yes | end-user (teacher) | 50(4) sentence 2 — editorial-responsibility carve-out |
| Import-pipeline AI extraction | server-side | indirect (extracted text published) | operator on import | 50(4) sentence 2 — operator editorial responsibility |
| ... | ... | ... | ... | ... |

### Carve-out evidence (per surface relying on editorial-responsibility)

| Surface | Logging table | UI note | Datenschutz framing |
|---------|---------------|---------|---------------------|
| Mit KI verbessern | ai_text_acceptance_log ✓ | ✓ | ✓ |

### Phase-in status

Today vs 02.08.2026: ...

### Verdict
```

## Citation chain

- Art. 50 + Recital 134 + Art. 113 phase-in → Reg. (EU) 2024/1689
- Editorial-responsibility carve-out → Art. 50(4) second subparagraph, last sentence
- Penalty ceiling → Art. 99(4)(g) — €15M or 3% global turnover

## Notes for the executing subagent

- The full verbatim Art. 50 text is in the `legal-research` skill's references / findings file. Use it to verify any ambiguous case.
- The "matters of public interest" trigger is undefined in the regulation. Conservative reading: any text that could be argued to inform public opinion on social/political/health/economic topics. Liberal reading: only journalism. Audit defaults to the conservative reading for risk-management.
- "Editorial responsibility" is also undefined. The textual minimum is "human review or editorial control" with someone holding responsibility for the publication. The three evidence pieces above (logging + UI + Datenschutz) are the practical implementation that satisfies this minimum.
