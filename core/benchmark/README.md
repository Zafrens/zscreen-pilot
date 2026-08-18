# Benchmark reference tables

These six tables are the reference scores for the shared-program layer and for
the two model configurations compared against each other throughout the
package (`program_signal_concentration.csv`, listed last, is the evidence
table for the program-versus-gene signal-concentration claim):

- **per_context_expert** — a separate prediction model fit independently for
  each context (no sharing across contexts).
- **context_token_trunk** — a single shared model across all contexts, with a
  per-context token identifying which context each profile comes from. This is
  the configuration shipped as the package's reference model.

Two evaluation splits appear throughout: `compound_5fold` (held-out compounds,
fold = SHA256(public_compound_id) mod 5) and `bb_disjoint` (held-out building
blocks, so test compounds contain a building block never seen in training).
"Program space" means the 32-dimensional usage coordinates against the pinned
shared basis; "decoded" means predictions projected back to the 6,000-gene
surface, scored by Pearson correlation against the measured profile.

## Tables

- **per_context_comparison_k32.csv** — headline per-context comparison at
  k = 32 programs: decoded gene-space Pearson for each model, both splits,
  with the paired difference and its 95% confidence interval. The shared
  context-token trunk improves over the per-context expert in 6 of 8
  contexts, is flat in zel024_h1650 (~3% relative deficit), and trails in
  **zel031_a549**, where the shared trunk trails
  the per-context expert by ~9% relative (0.0434 vs 0.0479 decoded Pearson on
  compound_5fold; the confidence interval excludes zero). This deficit ships
  openly here and in the reference-model scores. zel024_h1650 shows a much
  smaller deficit (~3% relative).
- **program_space_primary.csv** — the primary program-space result: Pearson
  correlation of predicted vs measured usage coordinates (mean and spread
  across the 32 programs), against a permutation null, with the resulting
  z-score, for each model, program count (k), target variant, and split.
- **k_resolution.csv** — how the number of shared programs (k = 12 vs k = 32)
  affects both program-space and decoded accuracy. k = 32 is the shipped
  resolution; k = 12 ships as a lower-resolution companion basis.
- **correction_arm.csv** — comparison of two target constructions:
  `device_centered_target` (device-centered harmonized surface, the shipped
  default) and `depth_regressed_target` (an alternative that additionally
  regresses out sequencing-depth covariates). The depth-regressed variant did
  not improve on the device-centered target, so the device-centered target is
  the canonical surface throughout this package.
- **cross_context_probe.csv** — cross-context transfer: train in one context,
  predict in another sharing the same cell line or compound set, plus a probe
  into a cell line the model was never trained on
  (`probe_only_never_trained`). Reported as measured transfer, model transfer,
  and prediction–measurement correlation per model.

All scores are evaluation-grade reference values; they describe the shipped
data and reference configurations as measured, and are not tuning targets.
