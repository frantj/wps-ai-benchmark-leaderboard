# Reliability and validity — WPS AI Benchmark v6

How much weight a score from this instrument can bear, stated plainly.

We publish this because the alternative is worse: a benchmark that reports scores without
reporting their resolution invites readers to over-interpret small differences. Two things below
are unflattering — inter-judge agreement is low, and two of five tiers did not fully reproduce on
re-scoring. Both are stated with the evidence that bounds them.

---

## 1. Inter-judge agreement is low, for a measurable reason

Agreement between the three judges is measured with **Krippendorff's α** (ordinal distance).
Conventional interpretation on the platform:

| α | Classification |
|---|---|
| ≥ 0.800 | Reliable |
| 0.667–0.799 | Tentative |
| < 0.667 | Unreliable |

**Observed α fell below 0.5 on all 30 prompts** for the top-scoring system, with a mean of
**+0.188**. By the table above that is "unreliable," and it needs explaining rather than burying.

### Why: restricted range, not judge chaos

α measures observed disagreement against *how much the judges could have disagreed given the
spread of scores*. When a system's scores barely spread, that denominator collapses, and even
near-identical judgments yield a low coefficient. The evidence that this is what is happening:

| System | Score spread | SD | Mean α |
|---|---|---|---|
| Highest-scoring agent build | 0.12 (0.75–0.87) | 0.026 | +0.188 |
| Second agent build | 0.15 | 0.040 | +0.167 |
| Bare commercial model | 0.48 | 0.108 | — |

α is *lowest* exactly where the score distribution is *tightest*. The pattern also predates the
best-performing run — an earlier build was below threshold on 28 of 30 prompts with a slightly
worse mean α (+0.167) — so this is a property of scoring compressed distributions, not a
regression in a particular batch.

### What follows

**Differences of a few hundredths are not real.** Effects that are safe to report are those well
clear of the noise floor: the large structure effects (+0.238 and +0.378 coverage), the ~+30
percentage-point tier-level uplifts, and consistent gradients across five tiers. A +0.040
difference on a single criterion is **not** interpretable.

Operationally we treat **differences under 0.10 as directional only**.

---

## 2. Test–retest: the instrument reproduces overall, not uniformly by tier

Because systems were scored in separate batches, every cross-system comparison assumes the
instrument did not drift between batches. That assumption was **tested, not asserted**: one bare
commercial model was re-scored through the identical route six days after its original scoring.

| Tier | Original | Re-score | Δ | |
|---|---|---|---|---|
| **Overall** | 0.601 | 0.614 | **+0.013** | reproduces |
| T1 (context-rich) | 0.706 | 0.709 | +0.003 | reproduces |
| T2 (gender-neutral) | 0.628 | 0.627 | −0.001 | reproduces |
| T3 (sparse) | 0.531 | 0.575 | **+0.044** | moved |
| T4 (adversarial) | 0.500 | 0.545 | **+0.045** | moved |
| T1-neutral | 0.630 | 0.605 | −0.024 | |

The **overall figure reproduces** comfortably inside the ±0.10 directional band, so cross-batch
comparisons hold. But **T3 and T4 each moved ~0.045**, and T3 is where the headline same-model
uplift is measured: against the original baseline that uplift is +30.9pp, against the fresh
baseline +26.5pp. Both clear the pre-registered 15pp bar, so the finding survives — but the
precise figure depends on which baseline vintage is quoted, and we say so rather than picking the
larger one.

**What this does and does not isolate.** The re-score was run without response caching, so
responses were *regenerated* as well as re-judged. The movement therefore bounds **generation
variability and judge drift together**. That is the conservative reading — it bounds the whole
pipeline's reproducibility — but it means a moved tier cannot be blamed on the judges alone.
Re-judging cached responses would separate the two and remains an open follow-up.

T4 rests on 3 scenarios and T1-neutral on 4, so those two tiers are the noisiest by construction
and their deltas deserve the least weight.

---

## 3. Known threats to validity

**Response length.** The criteria reward covering ground, so verbosity is a plausible confound.
Two facts bound it: within a single run, response length and score correlated at **r = +0.012**
across 30 prompts — no detectable within-run length advantage — and most of the verbosity of the
top system was a property of its base model rather than the scaffolding around it. Where a
comparison was *not* length-matched (a 3.1× gap), we report the result as an upper bound rather
than a point estimate.

**Possible under-enforcement of a rubric clause.** The Clarity/Actionability criterion explicitly
penalizes padding and unranked enumeration, yet scored **0.935** for a system whose responses were
three times longer than its comparator. Either those responses genuinely stayed well-prioritized,
or the judges under-enforced that clause. This is unresolved and is a live caution on that
criterion specifically.

**No external anchor.** No human expert baseline and no gold reference answers exist, so absolute
scores mean nothing on their own. Only comparisons between systems scored on the same instrument
are meaningful.

**Judges are not practitioners.** The rubric encodes WPS expert judgment; the *application* of it
is by general-purpose language models. Agreement between those judges and human WPS experts has
not been measured. This is the single largest open validity question for the benchmark.

**Construct coverage.** The instrument measures WPS quality in *written advisory text* on
constructed scenarios. It does not measure multi-turn advisory behavior, behavior under real
operational pressure, or anything about deployed use.

**Contamination — accepted deliberately, and it does bound what this set can measure.** The
blueprint is public and carries no canary or no-train request, because getting this rubric in front
of model developers and into training corpora is a goal of publishing it (README §6). The cost is
real: for any model released after publication, a good score may reflect having learned this rubric
rather than reasoning well about WPS, and there is no way to tell the two apart from the score
alone. Two consequences follow.

- **Cross-sectional comparisons among models of the same vintage remain usable**, since any
  contamination is roughly shared.
- **Longitudinal claims — "models are getting better at WPS" — cannot rest on this set.** Improvement
  and absorption are indistinguishable here. Such claims need held-out scenarios written to the same
  rubric and never published.

Treat a high score from a recently released model on this public set as an upper bound on genuine
WPS competence.

---

## 4. Summary: what a score supports

| Claim type | Supported? |
|---|---|
| "System A scores materially higher than System B" (gap > 0.10) | Yes |
| "Structure/scaffolding produces large gains over a bare model" | Yes |
| "Performance degrades from cued to uncued to sparse prompts" | Yes, consistent across tiers and runs |
| "System A beats System B" (gap < 0.10) | **No** — directional at best |
| "Criterion X improved by 0.04" | **No** |
| "System A is safe for WPS operational use" | **No** — out of scope by design |
| "System A scores near human expert level" | **No** — no human baseline exists |
| "Models improved at WPS between year X and year Y" | **No** — not on this public set; contamination and improvement are indistinguishable |
