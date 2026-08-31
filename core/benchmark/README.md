# Benchmark reference tables

These eight tables are the reference scores for the shared-program layer and for
the two model configurations compared against each other throughout the
package (`program_signal_concentration.csv`, listed last, is the evidence
table for the program-versus-gene signal-concentration claim):

- **per_context_expert**: a separate prediction model fit independently for
  each context (no sharing across contexts).
- **context_token_trunk**: a single shared model across all contexts, with a
  per-context token identifying which context each profile comes from. This is
  the configuration shipped as the package's reference model.

Two evaluation splits appear throughout: `compound_5fold` (held-out compounds,
fold = SHA256(public_compound_id) mod 5) and `bb_disjoint` (held-out building
blocks, so test compounds contain a building block never seen in training).
"Program space" means the 32-dimensional usage coordinates against the pinned
shared basis; "decoded" means predictions projected back to the 6,000-gene
surface, scored by Pearson correlation against the measured profile.

## Tables

- **per_context_comparison_k32.csv**: headline per-context comparison at
  k = 32 programs: decoded gene-space Pearson for each model, both splits,
  with the paired difference and its 95% confidence interval. The shared
  context-token trunk improves over the per-context expert in 6 of 8
  contexts, is flat in zel024_h1650 (~3% relative deficit), and trails in
  **zel031_a549** by ~9% relative (0.0434 vs 0.0479 decoded Pearson on
  compound_5fold; the confidence interval excludes zero).
- **program_space_primary.csv**: the primary program-space result: Pearson
  correlation of predicted vs measured usage coordinates (mean and spread
  across the 32 programs), against a permutation null, with the resulting
  z-score, for each model, program count (k), target variant, and split.
- **k_resolution.csv**: how the number of shared programs (k = 12 vs k = 32)
  affects both program-space and decoded accuracy. k = 32 is the shipped
  resolution; k = 12 ships as a lower-resolution companion basis.
- **correction_arm.csv**: comparison of two target constructions:
  `device_centered_target` (device-centered harmonized surface, the shipped
  default) and `depth_regressed_target` (an alternative that additionally
  regresses out sequencing-depth covariates). The depth-regressed variant did
  not improve on the device-centered target, so the device-centered target is
  the canonical surface throughout this package.
- **cross_context_probe.csv**: cross-context transfer: train in one context,
  predict in another sharing the same cell line or compound set, plus a probe
  into a cell line the model was never trained on
  (`probe_only_never_trained`). Reported as measured transfer, model transfer,
  and prediction-measurement correlation per model.
- **program_signal_concentration.csv**: the evidence table for the
  program-versus-gene signal-concentration claim: cross-context agreement of
  per-compound measurements in gene space versus program space, with the
  interpretation note per row.

## Fold-0 baseline comparison

Two added tables score simple recipe-feature models against the shipped
reference transformer on one pinned split: fold 0 is the held-out test fold,
folds 1-4 are used for training, and fold 4 serves as the inner validation
fold for tuning the simple models.

- **fold0_baseline_comparison.csv**: per-context scores (72 rows: 8 contexts
  x 9 models) for a context-only train-mean control, transparent models built
  on recipe and building-block features (shrunk additive building-block
  marginals; ridge on building-block embeddings, mean-pooled or
  slot-concatenated), and the three seeds of the shipped reference
  transformer plus their ensemble, raw and affine-calibrated. Columns include
  mean_program_pearson, mean_compound_pearson, global_r2_vs_train_mean, and
  rmse.
- **fold0_reference_model_summary.csv**: the per-context summary (8 rows):
  control score, the two main simple models, best simple model, three-seed
  transformer ensemble, and the winner per context.

The context-only train-mean control scores zero in all 8 contexts
(|r| <= 2.01e-16, floating-point zero), so context identity alone predicts
nothing. The transparent models and the three-seed reference transformer land
in the same range: mean program Pearson runs 0.0986-0.5011 across contexts
for the best simple model and 0.1063-0.5820 for the transformer ensemble,
and each side leads in 4 of 8 contexts. The point of the table is that the
data are usable without heavy machinery. All scores remain reference values,
not tuning targets.

All scores are evaluation-grade reference values; they describe the shipped
data and reference configurations as measured, and are not tuning targets.
