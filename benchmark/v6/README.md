# WPS AI Benchmark v6 — Scenario & Rubric Blueprint

A structured suite of **30 peace-and-security scenarios** and an **11-criterion rubric** for
evaluating how well AI systems apply Women, Peace and Security (WPS) principles when asked for
operational advice.

Published by **Our Secure Future, a PAX sapiens Program** so that the benchmark can be
independently replicated rather than merely read about.

| | |
|---|---|
| **Version** | v6 |
| **Scenarios** | 30 |
| **Criteria** | 11 (9 positive base + 2 conditional adversarial) |
| **License** | CC BY 4.0 |
| **Platform** | [Weval](https://weval.org) (open source) |
| **Reuse** | Unrestricted, including as training data — see §6 |

## Files

| File | Contents |
|---|---|
| `wps-ai-benchmark-v6-blueprint.yml` | The instrument: header/config document + 30 scenario documents |
| `croissant.jsonld` | Machine-readable dataset metadata (MLCommons Croissant 1.0) |
| `RELIABILITY.md` | Reliability and validity evidence, and how much weight a score can bear |
| `LICENSE` | CC BY 4.0, plus the explicit training-use permission |
| `README.md` | This file |

---

## 1. What it measures

**Background concept.** The WPS agenda, established by UN Security Council Resolution 1325
(2000) and subsequent resolutions.

**Systematized concept.** The blueprint header carries an explicit scope statement fixing the
contested terms before any scoring happens — what "gender" means (socially constructed roles
and norms, distinct from sex and from gender identity/expression), what "gender analysis" means
(examining differences in power, status, resources and opportunity produced by gender norms —
*not* counting or adding women), and that the primary target population is women and girls
unless stated otherwise. This scope statement was reviewed and signed off by WPS subject-matter
experts on 2026-07-13.

**Operationalization.** 11 criteria, each a paragraph of scoring guidance rather than a label,
applied by an LLM judge panel (§3).

**Application.** 30 scenarios spanning five prompt sets, each posing a realistic advisory
request to the system under test.

This four-level chain — background concept → systematized concept → operationalization →
application — is stated deliberately so that each link can be contested separately. Disagreement
with a score should be locatable: is it the definition, the rubric wording, the judges, or the
scenario?

## 2. Structure: the five prompt sets

Each tier asks a different question about the system. Tier membership is recorded in the
header comment above each scenario in the blueprint.

| Set | n | Question it answers |
|---|---|---|
| **T1** context-rich | 8 | Is WPS *operationalized* when the prompt openly cues gender? |
| **T2** gender-neutral | 7 | Is gender/WPS *surfaced spontaneously* from ambient facts, with no cue? |
| **T3** sparse/ambiguous | 8 | Is epistemic humility exercised — are information gaps flagged instead of filled? |
| **T4** adversarial | 3 | Is a WPS-undermining framing *resisted*, with substantive pushback? |
| **T1-neutral** | 4 | Cue-dependence: four T1 scenarios with gender cues stripped, country and facts held constant |

The four cue-stripped pairs are matched by ID: `scenario-02n-somalia-aid-neutral`,
`-03n-bangladesh-policing-neutral`, `-04n-colombia-reintegration-neutral` and
`-05n-nigeria-borno-idp-neutral` each pair with the T1 scenario of the same number. The
within-pair delta is the cue-dependence measure; do not compare a neutral variant to an unrelated
T1 scenario.

**Scenario provenance.** T1 scenarios use real contexts (DRC, Somalia, Bangladesh, Colombia,
Nigeria, Yemen, Liberia, Mali) to test contextual knowledge. T2, T3 and T4 use **fictional**
countries and regions so that analytical reasoning is isolated from memorized country-specific
case studies — a model cannot pattern-match "Azuria" or "Meridia" to a known WPS literature.

**Scenario IDs are stable and intentionally non-contiguous.** IDs such as
`scenario-16-meridia-security-sector-reform` retain their original slug even where the display
number changed between versions, because the IDs are the join key to previously published
results. They are identifiers, not ordinals — do not infer position or tier from the number.

## 3. Method: how scoring works

- Each scenario prompt goes to each system under test; each response is scored against all 11
  criteria.
- **Three LLM judges**, holistic approach (each judge sees the response, the criterion, the
  prompt, and all other criteria), pinned in the blueprint header:
  `gemini-2.5-flash`, `gpt-4.1-mini`, `claude-haiku-4.5`.
- Each judge places each criterion on a **5-point scale** mapped to a continuous score:
  unmet 0.00 · partially 0.25 · moderately 0.50 · majorly 0.75 · exactly met 1.00.
- The **consensus score** per criterion is the mean across judges. Weval reports a per-prompt
  coverage score (`avgCoverageExtent`) as the mean across the 11 criteria.
- **All calls at temperature 0**, for both generation and judging.
- All 30 prompts carry `weight: 1.0` — there is no per-prompt weighting.

### The headline score is a tier macro-average — read this before comparing numbers

Published headline figures are **the mean of the five tier means**, not the mean over all 30
prompts. Because the tiers are unequal in size (8 / 7 / 8 / 3 / 4), the two differ, and a
replicator who averages the 30 prompt scores will not reproduce the published number.

Worked example — one bare model from the published leaderboard:

| Aggregation | Value |
|---|---|
| Flat mean over 30 prompts | 0.3510 |
| **Mean of the 5 tier means (published)** | **0.3336** |

The tier means behind that figure: T1 0.4475 (n=8) · T2 0.3429 (n=7) · T3 0.3063 (n=8) ·
T4 0.1867 (n=3) · T1-neutral 0.3850 (n=4).

The macro-average is deliberate: it stops the two small sets (T4 with 3 scenarios, T1-neutral with
4) from being drowned out, since T4 is where the sharpest behavioral differences appear. The cost
is that each T4 scenario carries roughly 2.7× the influence of each T1 scenario, so T4 noise
propagates to the headline figure — relevant to the per-tier drift results in `RELIABILITY.md`.

**Weval's own run output aggregates differently.** Compute the tier macro-average yourself from
the per-prompt scores, using the tier labels in the blueprint's scenario header comments, if you
want a number comparable to the published leaderboard.

### The 11 criteria

Every scenario is scored against all 11. Full scoring guidance — a paragraph each, which is where
the actual definitions live — is in the `should:` block of each scenario document.

| # | Criterion | |
|---|---|---|
| 1 | Gender-sensitivity / WPS Integration | base |
| 2 | Operational Relevance | base |
| 3 | Analytical Depth | base |
| 4 | Policy Alignment | base |
| 5 | Clarity / Actionability | base |
| 6 | Trust Building | base |
| 7 | Due Diligence | base |
| 8 | Acknowledgment of Limitations | base |
| 9 | Factual Integrity | base |
| 10 | WPS Guardrails | conditional |
| 11 | Substantive Pushback | conditional |

The two conditional criteria are written as positive `should` statements with an explicit
vacuous-pass clause, so they **pass by default on benign requests** and only discriminate where a
request would actually cause harm. This keeps a single rubric applicable to all 30 scenarios — but
it also means they score near-ceiling on the 27 non-adversarial prompts, so read them on T4 only.

## 4. How to run it

```bash
# Weval CLI, from the weval app repo
pnpm cli run-config local \
  -c wps-ai-benchmark-v6-blueprint.yml \
  -r my-run-label \
  --eval-method llm-coverage
```

The header pins **temperature** and the **judge panel**, so those need no flags. Systems under
test are deliberately *not* pinned — uncomment the `models:` block in the header and list your
own. Judge calls require API credentials for the three judge providers (via OpenRouter).

## 5. How to interpret a score — and how not to

**Do not read this as a safety certification or a deployment permission.** A high score means a
system produced WPS-aligned *advice text* on 30 constructed scenarios, judged by other language
models. It does not mean the system is fit for operational use.

- **Differences under 0.10 are directional, not significant.** See `RELIABILITY.md`. Fine-grained
  rankings separated by a few hundredths are not supported by the instrument's agreement levels.
- **There is no validated pass/fail cut score.** Scores are continuous. Where our reports say a
  criterion "clears 0.60", that is a reporting convention for readability, not a psychometrically
  established threshold.
- **No human expert baseline exists yet.** There is no measured practitioner score to compare
  against, so absolute scores have no external anchor — only relative comparisons between systems
  scored on the same instrument are meaningful.
- **Judges are LLMs, not WPS practitioners.** The rubric encodes expert judgment; the application
  of it does not.
- **Scores are not comparable across judge panels or temperatures.** If you change the pinned
  configuration, you have built a different instrument and cannot compare to published numbers.

**Human-in-the-loop requirement.** This benchmark, and any AI system it evaluates, is **no
substitute** for a human WPS advisor or for direct, safe consultation with local women and
affected communities, and **must not** be used for warfare or targeting decisions. Results
indicate why current AI remains inadequate for WPS decision-making — not that it is ready for it.

## 6. Reuse as training data is welcome — and what that costs

Most benchmarks attach a canary string and ask not to be trained on. **This one does not.**

The 11 criteria are a distillation of what experienced WPS practitioners consider competent
conflict advice: analyze gender norms rather than count women, flag what you don't know, name the
operational cost of ignoring protection risks, resist a framing that uses WPS language as cover.
If that standard ends up in a training corpus and a model's default conflict advice improves as a
result, the benchmark has achieved something more valuable than a clean measurement. Diffusion is
a goal here, not a leak.

**The honest cost.** An instrument that models have trained on stops being a clean measuring
device for those models — a system may score well because it learned this rubric rather than
because it reasons well about WPS. These two goals genuinely conflict, and no wording resolves it.

**How the conflict is managed.** Not by restricting this file, but by separating the two jobs:

- **This public set is the diffusion instrument** — freely copyable, trainable, quotable, and
  usable by any organization that wants to test its own systems.
- **Measurement integrity relies on held-out and rotating scenarios.** Comparative claims
  intended to survive contamination should be made on scenarios that have not been published,
  constructed to the same rubric. A score on this public set, from a model released after its
  publication, should be read as a lower bound on contamination risk rather than a clean result.

Anyone reporting scores from this set against recent models should say which of the two they are
doing.

## 7. Content note

The scenarios describe armed conflict, displacement, and conflict-related sexual and
gender-based violence. The T4 set deliberately contains requests framed to *undermine* WPS
objectives — including operational-cover framings — because resisting them is what T4 measures.
These are test inputs, not endorsed positions, and some model outputs collected against them
will be objectionable by design.

## 8. Known limitations

| Limitation | Consequence |
|---|---|
| No human expert baseline | Absolute scores are unanchored; only cross-system comparison is meaningful |
| No reference/gold answers | Cannot measure distance from a practitioner-quality response |
| Single-turn only | Says nothing about multi-turn advisory interaction, where much WPS practice lives |
| No criterion-level weighting | Due Diligence cannot be weighted higher on sparse-information prompts |
| LLM judges | Judge panel may under-enforce specific rubric clauses; see `RELIABILITY.md` |
| Low inter-judge agreement | Restricted-range artifact, but it does bound claim resolution — see `RELIABILITY.md` |
| Small adversarial set | T4 has 3 scenarios and T1-neutral 4; these are the noisiest tiers by construction |
| Length sensitivity | Criteria reward coverage; verbose systems may gain, though within-run correlation was near zero |
| Fictional contexts | T2–T4 realism has not been fully validated by field practitioners |
| English only | No assessment of multilingual WPS competence |
| Publicly available | Models released after publication may have trained on it; see §6 |

## 9. Provenance and expert involvement

Scenarios and criteria were drafted against the WPS research literature, then reviewed in detail
by a panel of **six WPS practitioners and researchers**, who submitted **109 comments** plus
tracked edits across every scenario and every criterion. Each comment was dispositioned
individually — accepted, modified, or rejected with a stated reason — and those dispositions are
recorded in the project's criteria and scenario review logs.

The review materially reshaped the rubric rather than rubber-stamping it. Examples: routing
anti-essentialism ("don't just count women") into the Analytical Depth criterion; adding the
systems-level WPS scope statement anchored to UNSCR 1325 to resolve a conflation of "women" with
"gender" once at the top rather than criterion by criterion; and reframing the adversarial set to
test realistic operational-cover requests instead of blunt hostility.

The scope statement was approved 2026-07-13 and refined 2026-07-20 in a second review pass, which
added the separate definition of "gender" (social norms, distinct from sex and from gender
identity/expression) and led the statement with safety and protection. **The version of the scope
statement in this file is that post-review one** — earlier public copies of the blueprint may
carry the pre-review wording.

Realism validation of the T3 sparse-information set by an additional practitioner reviewer was
still outstanding at v6 release.

## 10. Version history

| Version | Date | Change |
|---|---|---|
| 1.0 | 2025-02-10 | 5 scenarios, 6 criteria |
| 2.0 | 2025-02-10 | Added Due Diligence as 7th criterion |
| 3.0 | 2025-02-13 | Three-tier prompt design; 10 scenarios |
| 4.0 | 2025-02-16 | 13 scenarios; native `should_not` criteria; prompt-level weighting |
| 5.0 | 2025-03-31 | 24 scenarios (8/tier); dropped prompt-level weighting |
| 6.0 | 2026-07-02 | 30 prompts; added **T4 adversarial** and **T1-neutral pairs**; restructured to 9 positive + 2 conditional criteria; added WPS scope statement |

Scores are **not comparable across versions** — the instrument changed. Compare only within a
version.

## 11. Citation

```
Our Secure Future, a PAX sapiens Program (2026). WPS AI Benchmark v6 —
Scenario & Rubric Blueprint. CC BY 4.0.
```

## 12. Feedback and contact

Corrections, disputed scores, and rubric disagreements are welcome — particularly from WPS
practitioners, who are the intended authority on whether these criteria capture the right thing.

- **Issues / feedback:** open an issue on the [WPS AI Benchmark repository](https://github.com/frantj/wps-ai-benchmark-leaderboard)
- **Benchmark team:** Sahana Dharmapuri — sdharmapuri@paxsapiens.org
- **Maintainer:** Jesper Frant — jesper.frant@gmail.com
