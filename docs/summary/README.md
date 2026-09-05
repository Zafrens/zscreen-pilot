# Z-Screen pilot: platform summary. Package v1.5.1, 2026-09-04.

**A breadth-first combinatorial-chemistry pilot: 190,699 compound-context
transcriptional profiles from 162,914 unique recipes across 8 library x
cell-line contexts, released as per-compound 32-program usage vectors and
harmonized 6,000-gene response surfaces, with five annexes (imaging,
hypotheses, chemistry, same-well, phenomimicry) and an evaluation-grade
reference model.**

## The question

Z-Screen was assembled from active drug-discovery programs, and the
release is a screening-data resource for drug discovery, not a
machine-learning benchmark. The question it answers:

> Does the information surrounding those programs contain reusable
> structure, at a level that changes which compound a discovery team
> makes or tests next?

## What the pilot demonstrates

Across the full release, the answer is yes at the level most relevant to
prioritization and experimental design.

- **Chemical breadth.** 190,699 compound-context profiles, 162,914 unique
  recipes, 8 contexts (`docs/WHY_THIS_MATTERS.md`). The design grids of
  the four libraries, multiplied by the cell lines already screened,
  comprise 2,095,149 compound-context states, so the measured set can grow
  eleven-fold within the same chemistry (`core/recipes.parquet`).
- **Held-out recipes carry recoverable program signal.** The reference
  model predicts the 32 program usages of held-out compounds at mean
  per-program Pearson 0.105-0.530 across the eight training contexts,
  z = 6.1-28.1 against a permutation null
  (`core/benchmark/program_space_primary.csv`). Cross-context structure is
  ten- to twenty-fold stronger in this program space than gene by gene
  (`core/benchmark/program_signal_concentration.csv`).
- **The building-block grammar is reusable.** Building-block effects,
  pooled over the compounds that carry a given block, have split-half
  reliability 0.50-0.58 (`docs/WHY_THIS_MATTERS.md`). A structure-input
  model evaluated on building blocks withheld before synthesis is at
  parity with the identity model (r = 0.339 +/- 0.020 vs 0.333 in
  `zel024_hek293`; additive embedding floor 0.182)
  (`annex_chemistry/novel_bb_generalization.csv`), and removing one block
  through the structure model recovers that block's measured effect at
  median Spearman 0.89-0.94 (`annex_chemistry/attribution_certificate.csv`).
- **Contexts share learnable organization.** A shared model trunk improves
  decoded gene-space prediction over per-context experts in 6 of 8
  contexts (`core/benchmark/per_context_comparison_k32.csv`).
- **No heavy machinery required.** On the pinned fold-0 split, a
  context-only control scores exactly zero in all 8 contexts, and
  transparent models built on recipe and building-block features land in
  the same range as the three-seed reference transformer (mean program
  Pearson 0.0986-0.5011 vs 0.1063-0.5820; each side leads in 4 of 8
  contexts) (`core/benchmark/fold0_baseline_comparison.csv`,
  `core/benchmark/fold0_reference_model_summary.csv`).
- **Biological structure recovers without labels.** An unsupervised census
  of the 32-program usage space finds 1,007 analog-family clusters across
  the eight contexts, each coherent at q <= 0.01 against 200 size-matched
  random compound sets (median coherence z = 4.8); 855 of the 1,007 carry
  at least one significant Hallmark/KEGG/Reactome pathway on their gene
  centroids at q < 0.05. A bonsai tree on the 32-dimensional cluster
  centroids preserves pairwise distances at median Pearson R 0.87, against
  0.66 for UMAP (`annex_clusters/cluster_census.csv`).
- **Known pharmacology is recovered by independent CRISPR references.**
  The METTL3 inhibitors STM2457 and STC-15 reproduce the METTL3-knockout
  signature at signed z = +8.8 to +16.1 in all three tested cell lines
  (`annex_hypotheses/anchor_leads.csv`, ZSH-3760). Under the 1,000-draw
  empirical null, STM2457 to METTL3 reaches p <= 0.05 in 16 of 88 scored
  cells, STC-15 in 19 of 88, and the DOT1L inhibitor MSC1094308 in 8 of 35
  (`annex_phenomimicry/validation_empirical_p.csv`); correlation-aware
  pair-level calibration of the same cells gives p = 0.0036, 0.0080, and
  0.015 for the three pairs. A rescoring that takes, per cell, the better
  of top-100 gene overlap and pathway-program cosine (ens_min) lifts
  control recovery further: median best percentile 0.018 vs 0.049 for
  full-gene cosine, 30 of 43 control pairs in the rank-scoring panel
  recovered at the 5% level, and 11 pairs with at least half their cells
  in the top 20%, vs 0 for cosine
  (`annex_phenomimicry/ensemble_rescoring_panel.csv`).
- **Hits form structure-activity families, not singletons.** The
  guardrail-filtered mimicry hits organize into 166 SAR families against
  108.8 +/- 9.4 expected under a degree-matched null, above all 100 null
  draws (`annex_phenomimicry/README.md`,
  `annex_phenomimicry/top100_phenomimics.csv`).
- **Ancillary imaging is informative in the same coordinates.** Image
  embeddings predict the 32 program usages at r = 0.135 in
  `zel024_hek293` and 0.1345 in `zel039_aec7`, every evaluated fold above
  its pairing null (`annex_imaging/README.md`,
  `annex_imaging/prediction_score_summary.csv`). A same-well study pairs
  448-dimensional image latents with 32-dimensional RNA latents in 11,435
  wells of 35 named controls; image-to-RNA regression reaches mcPearson
  0.277 at the full 11,435 wells (z = 34.3 against the null) and first
  clears the null band near 300 wells (`annex_same_well/README.md`,
  `annex_same_well/evidence/learning_curve.csv`).
- **The output is a ranked experimental queue.** The mining ledger holds
  1,027 rows: 2 anchor-validated patterns, 47 strong hypotheses, 978
  triage rows (`annex_hypotheses/hypothesis_ledger_full.csv`). Sixteen
  distilled leads each carry a specified kill/confirm experiment
  (`annex_hypotheses/anchor_leads.csv`).

## Why this matters

The pilot's value is a coherent decision layer built from
discovery-generated chemical space: recurring building-block effects guide
library design, program-level responses support held-out recipe ranking,
shared context structure supports transfer rather than isolated models,
orthogonal CRISPR references turn hits into SAR families, same-well
imaging adds a second modality at adequate sample size, and the hypothesis
annexes convert all of this into a ranked, testable queue.

## Where to start

`START_HERE.md` gives two reading paths (guided readers and
model-builders). `docs/WHY_THIS_MATTERS.md` expands the design argument;
`docs/SCIENTIFIC_OVERVIEW.md` and `docs/METHODS.md` carry the technical
detail. Each annex has its own README, and `verify.py` checks the
integrity and schema of the full release in one command.
