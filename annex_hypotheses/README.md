# Therapeutic-hypothesis annex

This annex is the hypothesis layer of the package: prioritized leads
with explicit null models and stated kill/confirm experiments, mined
from the program and grammar layers of the screens. Read `LIMITS.md`
alongside any table.

## The flagship stories

**1. A heat-shock chemotype that phenocopies HTH-01-015 at rank 1**
(ZSH-0001). In the AEC7 context, compounds carrying bb0 level
`BB_2085420374` (2,294 carriers) induce a canonical HSF1/heat-shock
program, and that program reproduces the measured phenotype of the
control HTH-01-015 — the most extreme heat-shock response in the
35-control panel (mean z = +3.94 across 9 HSP genes) and the level's
rank-1 control match (cos 0.631). Three independent lines converge:
the control's own measurement (r = 0.53 against the library-derived
effect vector), neighborhood enrichment (49/50 top neighbors carry
the level, p = 3.3e-46), and unsupervised recovery (the shared
program basis recovers the whole triangle with no control
supervision). The kill/confirm: raw-pseudobulk confirmation of
HSPA1A/DNAJB1 induction in carriers, an HSF1 reporter on carrier
compounds, and a test of whether the control's own heat-shock
phenotype is on-target (NUAK1/ROCK) or a chemotype off-target — the
other ROCK-family controls show no heat-shock outlier behavior,
which already weakens the on-target reading.

**2. METTL3 inhibitors phenocopy the METTL3 knockout** (ZSH-3760).
The two METTL3-inhibitor controls (STM2457, STC-15) reproduce the
METTL3-knockout signature at signed z = +8.8 to +16.1 in all three
cell lines — the strongest control result in the dataset, against
1,000 random-gene-set nulls, and one of only two exact-mechanism
recoveries against the external knockout atlas. The m6A-writer
inhibition phenotype transfers from adherent-line drug treatment to
a K562 knockout. Library-scale, METTL3-KO-mimicking compounds
cluster in specific bb1 scaffolds (grammar-level) — a testable m6A
program with a chemistry handle.

**3. A sharp ER-stress SAR family with a chemistry cliff**
(ZSH-3757). The bb0 `BB_2371372935` sub-series (53 and 47 compounds)
are the screen's sharpest chemistry-coupled SAR object:
within-phenotype coherence 0.79, chemical coherence 0.97, and the
50 chemically nearest non-members **anti-correlate** with the series
phenotype (ring1 = −0.33; falloff null percentile 1.00 — 1 of only
11/376 candidates that extreme). Two independent metrics converge
on the same family, and imaging gives an orthogonal vote (IF
coherence p = 0.020, tier-matched). Drivers are UPR/ER-stress genes
(IGFBP1, HSPA5, MANF, PDIA6, PTX3, DDIT3). The kill/confirm is
spelled out: raw pseudobulks of series members vs their ring1
chemical neighbors for HSPA5/DDIT3 induction, plus an ATF6/XBP1s
UPR reporter on members and non-members.

## The tables

| file | rows | what it is |
|---|---:|---|
| `anchor_leads.csv` | 16 | The distilled, hand-curated leads — the guided entry point. Each row states the building-block level(s), context, biological program, matched control (if any), external triangulation, the evidence with its null named, a confidence tier, caveats, and a concrete **kill/confirm experiment**. |
| `program_atlas.csv` | 26 | The 26 program groups that organize the screens: theme and named gene-set family per group, top genes, driving BB levels, anchor controls, CRISPR-knockout links, depth-tier diagnostics, confidence tier, and a focus experiment. Program identities are tied to the pinned shared basis (see `core/basis/basis_registry.json`). |
| `sharp_sar_candidates.csv` | 133 | Biology-ranked shortlist of sharp structure-activity objects: two-position BB sub-series, resolution-stable micro-clusters, and single-level R-groups, ranked by within-phenotype coherence against tier-matched nulls plus chemistry-ring falloff (do the chemically nearest non-members lose the phenotype?). zel024 rows are marked `grammar_level` (bb-backbone discovery only). The full SAR tables, organized for chemists, are in the chemistry annex — this file is the cross-reference shortlist, not a duplicate. |
| `hypothesis_ledger_full.csv` | 3,754 | The complete, unfiltered mining ledger. **Triage-grade, hypothesis-generating** — the filename, the `status` column (`hypothesis_anchor_validated` / `hypothesis_strong` / `hypothesis_triage`), and `confidence_tier` make that unambiguous. It is included for completeness and for collaborators who want to re-rank with their own priors. |

## How the tiers work

- **A — anchor-validated pattern class.** Multiple independent data
  lines converge (measured control signature + bb-effect alignment +
  unsupervised recovery), all stated nulls addressed. Two patterns
  reach this tier: the HSF1 heat-shock chemotype and the
  palbociclib/translation match. The METTL3 phenocopy lead is
  tier A on external-validation strength.
- **B — strong pooled signal, nulls addressed, but limited
  independence or single-context support.** Level→control rank-1
  matches and the recurring grammar programs live here.
- **C — triage.** Everything else, including all 2,727
  external-atlas resemblance rows (see LIMITS) and recorded nulls,
  which are kept because a well-characterized null is as useful as
  a positive.

Caveat flags use a controlled vocabulary: `weak_null` (match
p-value is permissive — specificity is in the rank/identity),
`singleton` (pooled, level-level reads only), `triage_grade`
(grammar-level or non-discriminatory null), `low_coverage`
(external panel cannot test this mechanism).

## How to read the full ledger

`hypothesis_ledger_full.csv` keeps one row per mined claim: a claim
sentence, the evidence numbers with the null type named, caveats,
the matched control and MOA class where applicable, and a rank
score. Filter by `status`/`confidence_tier` first; the
`hypothesis_triage` rows (98.7% of the table) are raw material.
Hypothesis IDs (ZSH-####) are stable across package versions:
anchor leads that distill a ledger row carry that row's ID, and
the six narrative-only leads (ZSH-3755–ZSH-3760) continue the same
sequence. A complete ledger will contain false positives even with
correct nulls; that is why the distilled tables exist.
