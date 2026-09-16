# Data dictionary

Core schemas and principal annex objects, plus the contracts that make the layers join. Detailed module schemas are linked beside their data. Contexts (8): `zel024_hek293`,
`zel024_h1650`, `zel028_hek293`, `zel028_a549`, `zel028_h1650`,
`zel031_a549`, `zel031_thp1`, `zel039_aec7`. Compound counts per context:
13,914 / 10,686 / 61,396 / 40,622 / 25,906 / 8,321 / 9,041 / 20,813
(190,699 compound-context pairs; 162,914 distinct compounds).

## Contracts (read first)

**Row-alignment contract.** Every `{context}.npy` matrix (in
[core/surfaces/](../core/surfaces) and [core/usages/](../core/usages)) is row-aligned to its sibling
`{context}_compounds.parquet`: row *i* of the matrix is the compound named
in row *i* of the parquet, and the parquet has exactly one column,
`public_compound_id`. Surface, usage, and compounds tables for the same
context have the same row count and the same row order. There is no other
join key and no index column; positional alignment is the contract.

**Panel index-space contract.** The harmonized panel is defined by
[core/surfaces/harmonized_6000_genes.parquet](../core/surfaces/harmonized_6000_genes.parquet). Its `gene_index` column
holds raw positional indices into the 46,944-gene pseudobulk
space. Gene symbols for panel positions come ONLY from this file's `gene`
column; never map panel positions through any context's released
3,000-gene panel, which is a different index space.

**Usages/basis contract.** Usage column *j* (0-based) is program P*j*+1 of
the pinned basis in [core/basis/](../core/basis) for the core usages and aligned prediction dumps. Usages are valid only against that basis ([core/basis/basis_registry.json](../core/basis/basis_registry.json)); a refit changes program identities. The annotated program atlas uses a separate label namespace; follow its documented mapping and scope. Same-well `D00`–`D31` coordinates are a separate representation.

**Fold convention.** fold = SHA256(`public_compound_id`) mod 5, computed
on the full 64-hex-character digest as an integer. The shared basis and
the reference model were both fit with fold 0 held out. Train on folds
1-4, evaluate on fold 0. Note: promoted usages can be slightly more
predictable on fold 0 in some exercises, so clean cross-exercise
comparisons use folds 1-4.

**Measured vs predicted.** Core surfaces are processed measurements; usages are their projection onto a learned basis. Recipes and splits are metadata; the basis is a fitted representation, and benchmark tables contain model-evaluation results. [models/](../models) outputs, the `y_pred_z` arrays in the imaging annex dumps, and
any table marked `grammar_level` or model-predicted are predictions, and
are labeled as such where they ship.

**Empirical-p floors.** Empirical p-values are floored at the resolution
of their null: 1/1001 in the phenomimicry validation tables (1,000-draw
nulls) and 1/201 wherever a 200-draw null is used. Permutation p-values
in the chemistry tables ship as separate `*_p_permutation` columns
alongside the empirical ones. A printed `p=0.000` in the hypothesis
ledger means the value fell below the 200-draw floor, not that it is
exactly zero.

## core/

### core/usages/

- `usages_{context}.npy`: float32, (n_compounds, 32), free sign.
  Per-compound program usages (`program_usage_projection_v1`): the
  free-sign least-squares projection of the context-scaled harmonized
  surface onto the pinned k = 32 basis.
- `usages_{context}_compounds.parquet`: one column:
  `public_compound_id` (string). One row per usage-matrix row, aligned
  positionally.

### core/surfaces/

- `surfaces_{context}.npy`: float32, (n_compounds, 6000). Device-centered
  log1p-CP10k expression on the harmonized panel
  (`device_centered_harmonized_surface_v1`). Column *j* is panel position
  *j* of [harmonized_6000_genes.parquet](../core/surfaces/harmonized_6000_genes.parquet).
- `{context}_compounds.parquet`: one column: `public_compound_id`.
- [harmonized_6000_genes.parquet](../core/surfaces/harmonized_6000_genes.parquet): 6,000 rows, the panel definition
  (`harmonized_panel_6000_v1`):
  - `panel_position` (int64, 0-5999): column index in every
    `surfaces_{context}.npy`.
  - `gene_index` (int64): raw position in the 46,944-gene pseudobulk
    space (full-width index space; see the contract above).
  - `gene` (string): gene symbol. The only authoritative symbol mapping.

### core/basis/

- [shared_basis_k32.npy](../core/basis/shared_basis_k32.npy): float32, (32, 6000), nonnegative
  (`shared_program_basis_v1`). Row *j* is the gene-loading vector of
  program P*j*+1, columns aligned to the panel.
- [shared_basis_k12.npy](../core/basis/shared_basis_k12.npy): float32, (12, 6000), nonnegative
  (`shared_program_basis_k12_v1`), lower-resolution companion.
- [basis_registry.json](../core/basis/basis_registry.json): the version pin:
  - `registry_name`, `basis_version`
    (`shared_program_basis_v1`).
  - `basis_fit_scope`: training folds 1-4 only; fold 0 untouched by any
    fitting.
  - `pinned_files`: list of `{package_name, file, k, sha256}` for the two
    basis arrays.
  - `validity_statement`: usages are valid only against the pinned basis
    files.

### core/recipes.parquet

162,914 rows, one per distinct `public_compound_id`:

- `public_compound_id` (string, `CPD_############`).
- `bb0`-`bb4` (string, `BB_##########`, or null when the position is
  absent in that recipe). Position sets differ between libraries.
- `n_positions_occupied` (int64): how many of the five positions carry a
  block.

### core/splits/fold_assignments.parquet

190,699 rows (= total compound count across the 8 contexts):

- `context` (string), `public_compound_id` (string), `fold` (int64, 0-4).

### core/benchmark/

[README.md](../core/benchmark/README.md) explains the two configurations (`per_context_expert`,
`context_token_trunk`), the two splits (`compound_5fold`, `bb_disjoint`),
and the two output spaces (program space vs decoded gene space). Tables:

- [per_context_comparison_k32.csv](../core/benchmark/per_context_comparison_k32.csv) (16 rows): `context`, `split_type`,
  `per_context_expert_mean`, `per_context_expert_sd_cells`,
  `per_context_expert_n_compounds`, `context_token_trunk_mean`,
  `context_token_trunk_sd_cells`, `context_token_trunk_n_compounds`,
  `diff_mean`, `diff_ci_lo`, `diff_ci_hi`. Decoded gene-space mean
  per-compound Pearson (mcPearson) per model with the paired difference
  and its 95% confidence interval.
- [program_space_primary.csv](../core/benchmark/program_space_primary.csv) (90 rows): `arm`, `split_type`,
  `target_variant`, `k`, `context`, `eval_only`, `n_runs`,
  `prog_pearson_mean`, `prog_pearson_sd_programs`, `null_mean`,
  `null_sd`, `z`. Mean per-program Pearson of predicted vs measured usage
  coordinates against a permutation null, with the resulting z-score.
  Includes the probe context `zel031_h1650` (never trained).
- [k_resolution.csv](../core/benchmark/k_resolution.csv) (64 rows): `context`, `split_type`, `arm`, `k`,
  `decoded_mcpearson_mean`, `decoded_mcpearson_sd_cells`,
  `prog_pearson_mean`, `prog_pearson_sd`. k = 12 vs k = 32.
- [correction_arm.csv](../core/benchmark/correction_arm.csv) (12 rows): `context`, `arm`, `target_variant`
  (`device_centered_target` / `depth_regressed_target`), `k`, `n_cells`,
  `prog_pearson_mean`, `prog_pearson_sd`,
  `decoded_vs_device_centered_target_mean`,
  `decoded_vs_device_centered_target_sd_cells`,
  `decoded_vs_depth_regressed_target_mean`,
  `decoded_vs_depth_regressed_target_sd_cells`. The depth-regressed
  variant did not improve; the device-centered target is canonical.
- [program_signal_concentration.csv](../core/benchmark/program_signal_concentration.csv) (4 rows): `analysis_layer`, `metric`,
  `range_min`, `range_max`, `note`. Gene-space versus program-space
  repeat-measurement ceilings and cross-cell-line agreement; the evidence
  table for the "10-20× stronger in program space" claim.
- [cross_context_probe.csv](../core/benchmark/cross_context_probe.csv) (9 rows): `ctx_a`, `ctx_b`, `n_compounds`,
  `n_cells`, `measured_transfer_mean`,
  `per_context_expert_transfer_mean`, `per_context_expert_transfer_sd_cells`,
  `per_context_expert_measured_pred_corr`,
  `per_context_expert_measured_pred_corr_sd`,
  `context_token_trunk_transfer_mean`,
  `context_token_trunk_transfer_sd_cells`,
  `context_token_trunk_measured_pred_corr`,
  `context_token_trunk_measured_pred_corr_sd`, `target_variant`, `k`,
  `prog_pearson_mean`, `prog_pearson_sd`, `null_mean`, `null_sd`, `z`.
  `ctx_b = probe_only_never_trained` rows are the never-trained cell-line
  probe.
- [fold0_baseline_comparison.csv](../core/benchmark/fold0_baseline_comparison.csv) (72 rows): `context`, `model`, `split`,
  `n_train`, `n_test`, `tuning_parameter`, `tuning_value`,
  `mean_program_pearson`, `median_program_pearson`, `min_program_pearson`,
  `max_program_pearson`, `n_programs_with_defined_pearson`,
  `mean_compound_pearson`, `global_r2_vs_train_mean`, `rmse`,
  `source_or_fit`. Per-context fold-0 test scores for a context-only
  train-mean control, three transparent recipe/building-block models, and
  the three reference-transformer seeds with their ensemble.
- [fold0_reference_model_summary.csv](../core/benchmark/fold0_reference_model_summary.csv) (8 rows): one row per context with
  the control score, the simple-model scores, the three-seed transformer
  ensemble score, and the winner.

## models/

See [models/README.md](../models/README.md) for usage and the fold-0 convention.

- `context_token_trunk_reference_eval_v1_seed{0,1,2}.pt`: PyTorch
  checkpoints (`torch.load(..., weights_only=True)`), each a plain dict:
  - `format`: `context_token_trunk_reference_eval_v1`.
  - `state_dict`: model weights (keys match [model_def.py](../models/model_def.py) exactly).
  - `architecture`: `d_model` 128, `n_heads` 4, `n_layers` 2,
    `feedforward` 512, `dropout` 0.1, `n_programs` 32, `n_tokens` 8,
    `d_chemistry` 128, `d_identity` 64, `n_libraries`, `n_cell_lines`,
    `vocabulary_sizes` (per bb slot), `n_parameters` 473,120.
  - `training`: `held_out_fold` 0, `seed`, `split_convention`
    `compound_5fold`, `target` `device_centered_program_usage`,
    `basis_version` `shared_program_basis_v1`, `max_epochs`,
    `batch_size`, `learning_rate`, `weight_decay`, `warmup_epochs`,
    `patience`, `best_epoch`, `epochs_run`, `best_val_score`,
    `training_contexts`.
  - `vocabulary`: `bb_slots` (`bb0`-`bb4`); `level_to_index` (per-slot
    maps public BB ID → identity-embedding row; row 0 = absent slot,
    row 1 = unseen ID); `libraries`; `cell_lines`; `context_tokens`
    (per context `{library, cell_line, trained}`; the probe context is
    marked `trained: false`).
  - `usage_scales`: per context `{mu, sd}` (32 values each): the
    per-context standardization mapping the raw head output
    (`usage_z_scored`) back to usage units comparable to [core/usages/](../core/usages)
    (`usage = usage_z_scored * sd + mu`).
  - `provenance`: `role` ("reference model, evaluation grade").
- [bb_embedding_table.parquet](../models/bb_embedding_table.parquet): 629 rows: `public_bb_id` (string) +
  `embedding_000`…`embedding_127` (float32), the 128-dimensional
  pretrained chemistry embedding per public BB ID. Public IDs only.
- [golden_predictions.json](../models/golden_predictions.json): environment verification fixture:
  `format`, `seed` 0, `model_file`, `tolerance` 2e-6, `note`, `entries`
  (20 fixed fold-0 recipes across 5 contexts, each `{context,
  public_compound_id, recipe: {bb0..bb4}, prediction_usage_z_scored:
  [32 floats]}`).
- [model_def.py](../models/model_def.py): self-contained architecture (PyTorch only).
- [predict.py](../models/predict.py): CPU inference CLI and `--check-golden` self-check.

## annex_imaging/

Full narrative: [annex_imaging/README.md](../annex_imaging/README.md). All per-compound tables key on
`public_compound_id`.

- [zel024_compound_embeddings.parquet](../annex_imaging/zel024_compound_embeddings.parquet) (10,129 × 3,075) /
  [zel031_compound_embeddings.parquet](../annex_imaging/zel031_compound_embeddings.parquet) (8,443 × 3,075):
  `public_compound_id`, `n_fovs` (fields of view averaged), `n_panels`,
  `rn50_0000`…`rn50_2047` (ResNet-50 embedding means),
  `clip_0000`…`clip_1023` (CLIP embedding means).
- [zel024_compound_intensity.parquet](../annex_imaging/zel024_compound_intensity.parquet) (10,129 × 8):
  `public_compound_id`, `n_fovs`, `n_panels`, `brightfield_cell_mean`,
  `dapi_cell_mean`, `p21_cell_mean`, `p62_cell_mean`,
  `phalloidin_cell_mean`.
- [zel031_compound_intensity.parquet](../annex_imaging/zel031_compound_intensity.parquet) (8,443 × 8): same key and support
  columns; marker set `brd4_cell_mean`, `brightfield_cell_mean`,
  `cona_cell_mean`, `dapi_cell_mean`, `phalloidin_cell_mean`. The two
  libraries are different panels (p62 only in zel024; BRD4/ConA only in
  zel031): pool only with panel-aware normalization.
- [zel039_imaging_latents.parquet](../annex_imaging/zel039_imaging_latents.parquet) (78,896 detections × 457):
  `public_compound_id` (empty for unmapped detections; see
  `mapped_to_compound_master`), `public_bb0_id`…`public_bb2_id`,
  `mapped_to_compound_master` (bool), `zlibrary`, `cell_line_context`,
  `scantype` (cell painting or immunofluorescent staining), `if_target`
  (immunofluorescence target where applicable), `D0`…`D447` (per-detection
  448-dimensional image latents).
- [reliability/embedding_reliability.json](../annex_imaging/reliability/embedding_reliability.json): `min_fovs`, `n_splits`, `libraries` (per library: `n_fovs`,
  `n_compounds`, and per backbone `rn50`/`clip`:
  `split_half_sb_median_raw`, `null_median_raw`,
  `split_half_sb_median_centered`, `null_median_centered`,
  `n_compounds_evaluated`). Split-half = two half-averages of a
  compound's FOVs correlated across compounds, Spearman-Brown corrected.
- [reliability/marker_reliability.json](../annex_imaging/reliability/marker_reliability.json): `libraries` (per library: `n_fovs`, `n_compounds`, `markers` with
  per-marker `split_half_sb`; plus the marker-marker
  correlation matrix).
- `image_to_program_predictions/{context}/` and
  `chemistry_to_program_predictions/{context}/`: fold-clean test
  predictions, one `.npz` per fold × seed × model. NPZ keys:
  - `public_compound_id`: (n,) unicode strings, held-out test compounds
    only.
  - `y_true_z`: float32 (n, 32), measured usages, z-scored per program.
  - `y_pred_z`: float32 (n, 32), predicted usages, same z-scored space.

  Filename grammar: `{features}_{model}__fold{f}_seed{s}.npz` for
  image→program (features `clip`, `rn50` for zel024/zel031; `cp448`,
  `if448`, `mean448`, `scantype896` for zel039; models `ridge`, `mlp`),
  and `fold{f}_seed{s}.npz` for chemistry→program (a cross-attention
  model over the building blocks). Contexts covered: zel024_hek293,
  zel031_a549, zel031_thp1, zel039_aec7. Column *j* of either matrix is
  program P*j*+1 of the pinned basis.
- [prediction_score_summary.csv](../annex_imaging/prediction_score_summary.csv) (175 rows): `family`
  (`image_to_program` / `chemistry_to_program`), `context`, `model`,
  `fold`, `seed`, `n_test_compounds`, `mean_program_pearson`. Derived
  from the dumps; recomputing a row is shown in
  [examples/04_join_imaging.ipynb](../examples/04_join_imaging.ipynb).
- [decomposition.csv](../annex_imaging/decomposition.csv) (128 rows: 4 contexts × 32 programs): `context`,
  `program` (P01-P32), `image_features`, `chemistry_model`, `folds`,
  `n_test_compounds`, `r2_chem`, `r2_img`, `r2_joint`, `chem_only`,
  `img_only`, `shared`, `unexplained`, `img_only_fold_sd`,
  `chem_only_fold_sd`, `img_only_null_mean`, `img_only_null_sd`,
  `img_only_z`, `img_only_tail`, `chem_only_null_mean`,
  `chem_only_null_sd`, `chem_only_z`, `chem_only_tail`, `rel_img`,
  `img_only_rel_ceiling`, `r2_img_rel_ceiling`, `r_ceiling_img`.
  Per-program variance ownership (chemistry alone / imaging alone /
  shared / neither) with permutation nulls and reliability ceilings.
- [decision_grade_image_to_program_panels.csv](../annex_imaging/decision_grade_image_to_program_panels.csv) (35 rows): `context`,
  `image_backbone` (clip / rn50), `model` (ridge / mlp), `fold`, `seed`,
  `n_train_compounds`, `n_test_compounds`, `prog_pearson_mean`,
  `prog_pearson_median`, `pairing_null_mean`, `pairing_null_sd`,
  `pairing_null_z`, `pairing_null_tail_frac`. Cell-level decision-grade
  image→program evaluation for zel024_hek293, zel031_thp1, zel031_a549.
- [decision_grade_image_to_program_zel039_aec7.csv](../annex_imaging/decision_grade_image_to_program_zel039_aec7.csv) (60 rows): `context`,
  `model_variant` (mean448/scantype896 × ridge/mlp), `fold`, `seed`,
  train/val/test counts, `prog_pearson_mean/median/min/max`,
  `null_mean/sd/q95/tail_frac_ge`, `above_floor_q95`,
  `margin_over_q95`, `model_hyperparameter`. The 5-fold × 3-seed ×
  4-variant decision-grade zel039 evaluation.
- [decode_through_comparison.csv](../annex_imaging/decode_through_comparison.csv) (30 rows): `context`, `fold`, `seed`,
  train/test counts, `bottleneck_mcpearson_*` (decode through the
  32-program bottleneck), `direct_mcpearson_*` (direct image→gene
  prediction), `oracle_mcpearson_*` (usage-space ceiling), null q95s,
  paired `diff_mean` with CI, `fraction_of_oracle_filled`.
- [marker_program_association.csv](../annex_imaging/marker_program_association.csv) (768 rows): `context`, `library`,
  `marker`, `program`, `n_test`, `r_raw`, `z_raw`, `tail_raw`,
  `r_partial`, `z_partial`, `tail_partial`, `marker_rel_sb`, `r_ceiling`,
  `r_chem_pred`, `z_chem_pred`, `r_img_pred`, `z_img_pred`, `fw_flag`.
  Marker intensity vs measured usages (`r_raw`; `r_partial` removes the
  shared cell-density axis) and vs image-predicted / chemistry-predicted
  usages, with nulls and reliability ceilings.
- [marker_program_depth_stratified.csv](../annex_imaging/marker_program_depth_stratified.csv) (3 rows): `context`, `marker`,
  `program`, `depth_stratum`, `n_test`, `r_partial`, `r_raw`.

## annex_hypotheses/

Read [annex_hypotheses/README.md](../annex_hypotheses/README.md) and [HOW_TO_READ.md](../annex_hypotheses/HOW_TO_READ.md) first. All tables are
hypothesis-generating.

- [anchor_leads.csv](../annex_hypotheses/anchor_leads.csv) (16 rows): `hypothesis_id` (ZSH-####, stable),
  `bb_level_ids`, `contexts`, `biological_program`, `matched_control`,
  `moa_class`, `external_triangulation`, `evidence_summary`,
  `confidence_tier` (A/B/C), `caveats` (controlled vocabulary:
  `weak_null`, `singleton`, `triage_grade`, `low_coverage`),
  `kill_confirm_experiment`.
- [program_atlas.csv](../annex_hypotheses/program_atlas.csv) (26 rows): `program_group_id`, `context`,
  `primary_program`, `n_programs_merged`, `member_programs`,
  `theme_family`, `named_theme`, `top_genes`, `top_gene_sets`,
  `driving_bb_levels`, `n_bb_levels_q05`, `anchor_control`,
  `anchor_top3_controls`, `crispr_ko_links`,
  `member_compounds_usageZ_ge1`, `mean_abs_usage`, `frac_deep_top500`,
  `library_frac_deep`, `depth_tier_skew_flag`, `ica_median_abs_cos`,
  `confidence_tier`, `focus_experiment`. Program-atlas labels use the namespace documented in the [interpretation notes](../annex_hypotheses/INTERPRETATION_NOTES.md); they must not be used directly as current basis indices.
- [sharp_sar_candidates.csv](../annex_hypotheses/sharp_sar_candidates.csv) (133 rows): `candidate_id`, `context`,
  `candidate_kind`, `n_members`, `within_phenotype_coherence`,
  `coherence_null_z`, `coherence_permutation_p`,
  `falloff_null_percentile`, `chemistry_within`, `ring1_similarity`,
  `driver_genes`, `evidence_tier` (zel024 rows marked `grammar_level`),
  `selection_note`.
- [hypothesis_ledger_full.csv](../annex_hypotheses/hypothesis_ledger_full.csv) (1,027 rows, triage-grade,
  hypothesis-generating): `hypothesis_id`, `hypothesis_type`, `status`
  (`hypothesis_anchor_validated` / `hypothesis_strong` /
  `hypothesis_triage`), `confidence_tier`, `context`, `bb_level_ids`,
  `claim`, `evidence`, `matched_control`, `moa_class`, `caveats`,
  `evidence_rank_score`.

Current named-control target annotations and their primary citation are documented in [annotations](../annotations/README.md).

## annex_phenomimicry/

Read [annex_phenomimicry/README.md](../annex_phenomimicry/README.md) first. These are
hypothesis-grade compound × CRISPR-knockout correspondence tables. Named-control
validation queries include random-target and hub-matched empirical comparisons;
consensus scores and family rankings have separate definitions.

- [phenomimic_pairs.parquet](../annex_phenomimicry/phenomimic_pairs.parquet) (426,461 rows): `public_compound_id`,
  `target_gene`, `n_contexts`, `contexts`, `best_z`, `mean_z`,
  `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`,
  `kd_flag_weak`, `tier` (`B_consensus_strong` / `B_single_context` /
  `C_moderate`), `bb0`-`bb4`, `hub_flag`.
- [antimimic_pairs.parquet](../annex_phenomimicry/antimimic_pairs.parquet) (561,355 rows): direction-adjusted opposition track,
  selected by stored `best_z >= 5`. Context scores are the negative of the signed
  consensus before maximum/mean aggregation; negative standardized consensus does
  not prove negative unstandardized cosine or biological rescue. Columns:
  `public_compound_id`, `target_gene`, `n_contexts`, `contexts`, `best_z`, `mean_z`,
  `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`, `kd_flag_weak`,
  `hub_flag`. There is **no `tier` and no `bb0`–`bb4`**. [Score convention,
  worked example and method](../annex_phenomimicry/SCORE_SEMANTICS.md).
- [showcase_hits.csv](../annex_phenomimicry/showcase_hits.csv) (2,000 rows): per-dataset evidence columns
  (`n_datasets_scored`, `n_datasets_top5pct`, `n_datasets_top1pct`,
  `best_percentile`, `max_cosine`, `median_percentile`,
  `best_dataset_exact`) plus consensus columns and control annotations
  (`name`, `moa_class`, `primary_target`).
- [top100_phenomimics.csv](../annex_phenomimicry/top100_phenomimics.csv) (101 rows): `rank`, `family_id`,
  `target_gene`, `family_size`, `family_max_z`, `family_evidence`,
  `public_compound_id`, `best_z`, `tier`, `contexts`, `kd_flag_weak`,
  `is_family_representative`, `n_contexts`, `family_contexts`,
  `total_family_size`, `hub_flag`, `kd_delta_median`, `mean_top3_z`,
  `replication_factor`, `composite_score`.
- [top100_family_summary.csv](../annex_phenomimicry/top100_family_summary.csv) (31 rows): `family_id`, `target_gene`,
  `family_size`, `family_max_z`, `family_evidence`, `n_in_top100`,
  `total_family_size`, `n_contexts`, `family_contexts`, `hub_flag`,
  `kd_delta_median`, `mean_top3_z`, `replication_factor`,
  `composite_score`.
- [validation_empirical_p.csv](../annex_phenomimicry/validation_empirical_p.csv) (2,074 rows): `context`, `dataset`,
  `public_compound_id`, `target_gene`, `cosine`, `rank_mimic`,
  `n_targets`, `n_shared_genes`, `percentile`, `control_name`, `p_emp`,
  `p_emp_hub`, `p_emp_20draw`.
- [ensemble_rescoring_panel.csv](../annex_phenomimicry/ensemble_rescoring_panel.csv) (42 rows): `public_compound_id`,
  `compound_name`, `target_gene`, `ens_min_best_percentile`,
  `cosine_best_percentile`, `frac_cells_top20`, `n_cells`,
  `consistent_pair`. The per-pair table behind the ensemble-rescoring
  section of the annex README.
- [target_hubness.csv](../annex_phenomimicry/target_hubness.csv) (18,789 rows): `target_gene`,
  `n_compounds_hit`, `hub_frac`, `hub_flag`.

Additional records:

- [family_null_check.csv](../annex_phenomimicry/family_null_check.csv): 100 degree-weighted draws plus six summary rows (`draw`, `count_all_filtered`, `count_replicated_subset`). There are 166 observed filtered families versus a null mean of 108.79 and SD of 9.44277. The replicated-subset count is zero in both the observed set and every draw (empirical p = 1). [Null method and scope](../annex_phenomimicry/FAMILY_NULL_METHOD.md).
- [curation_summary.json](../annex_phenomimicry/curation_summary.json): current descriptive counts and known-control calibration summaries.

## annex_chemistry/

Column-by-column definitions with interpretation are in
[annex_chemistry/README.md](../annex_chemistry/README.md); headers for reference:

- [novel_bb_generalization.csv](../annex_chemistry/novel_bb_generalization.csv) (8 rows): `context`,
  `structure_readout_model_r_mean`, `structure_readout_model_r_sd`,
  `identity_readout_model_r_mean`, `structure_minus_identity_r_mean`,
  `structure_minus_identity_r_ci95`,
  `structure_minus_identity_frac_folds_positive`,
  `reference_trunk_model_r_mean`, `structure_minus_trunk_r_mean`,
  `structure_ridge_r_mean`, `additive_embedding_floor_r_mean`,
  `structure_ridge_minus_floor_r_mean`,
  `structure_ridge_minus_floor_r_ci95`,
  `structure_ridge_minus_floor_frac_folds_positive`.
- [attribution_certificate.csv](../annex_chemistry/attribution_certificate.csv) (6 rows): `context`, `fold`,
  `usage_target`, `structure_model_r`, `model_null_z`,
  `n_building_blocks`, `bb_knockout_vs_measurement_median_spearman`,
  `bb_knockout_null_mean`, `bb_knockout_null_sd`, `bb_knockout_z`,
  `parts_sum_vs_direct_median_spearman`, `n_structure_parts`,
  `negative_control_median_spearman` (empty where not applicable).
- [activity_cliffs.csv](../annex_chemistry/activity_cliffs.csv) (450 rows): `context`, `bb_pair_id`,
  `n_members`, `within_phenotype_coherence`,
  `within_candidate_chemical_coherence`, `ring1_phenotype_correlation`,
  `ring2_phenotype_correlation`, `ring3_phenotype_correlation`,
  `falloff`, `null_falloff_mean`, `null_falloff_sd`,
  `falloff_null_percentile`.
- [chemotype_series.csv](../annex_chemistry/chemotype_series.csv) (2,727 rows): `context`, `evidence_level`
  (`measured` / `grammar_level`), `bb_pair_id`, `position_a`, `bb_id_a`,
  `position_b`, `bb_id_b`, `n_members`, `effect_strength_l2`,
  `top20_gene_energy_fraction`, `participation_ratio`, `coherence`,
  `sibling_max_cos`, `sibling_mean_cos`, `n_siblings`,
  `null_coherence_mean`, `null_coherence_sd`, `coherence_z_vs_null`,
  `coherence_p_empirical`, `coherence_q_fdr_bh`,
  `effect_strength_z_vs_null`, `effect_strength_p_empirical`,
  `coherence_p_permutation`, `mean_shrinkage_weight`, `mean_n_wells`,
  `composite_score`, `composite_rank`, `is_positive_control`,
  `driver_genes_up`, `driver_genes_down`, and per-depth-tier fractions
  (`frac_*_depth_tier`, `library_base_frac_*_depth_tier`,
  `delta_frac_*_depth_tier`).
- [bb_effect_rankings.csv](../annex_chemistry/bb_effect_rankings.csv) (431 rows): `context`, `position`, `bb_id`,
  `n_carriers`, `in_sar_window`, `coherence`, `coherence_z`,
  `coherence_p`, `sparse_coherence`, `sparse_coherence_z`,
  `sibling_max_cos`, `sibling_max_sparse_j`, `sparse_falloff`,
  `effect_strength_l2`, `top20_gene_energy_fraction`,
  `delta_frac_deep_depth_tier`, `driver_genes_up`, `driver_genes_down`,
  `is_positive_control`, `sparse_composite_score`,
  `coherence_p_permutation`, `sparse_rank`,
  `within_candidate_chemical_coherence`, `ring1_phenotype_correlation`,
  `ring3_phenotype_correlation`, `falloff`, `falloff_null_percentile`.

## annex_same_well/

Full narrative: [annex_same_well/README.md](../annex_same_well/README.md). The well key is
(`batch_id`, `well_id`); `well_id` is unique only within a batch. Context
label: `same_well_hek293`.

- [same_well_wells.parquet](../annex_same_well/same_well_wells.parquet) (11,435 × 486): `batch_id` (`batch_1` /
  `batch_2`), `well_id`, `public_compound_id`, `control_name`,
  `cell_line`, `n_detections`, `img_lat_0_0`…`img_lat_3_63` (448 image
  latents, mean over the well's detections; blocks 0-2 × 128 plus block 3
  × 64), `D00`…`D31` (32 RNA latents, constant within a well).
- [same_well_detections.parquet](../annex_same_well/same_well_detections.parquet) (14,757 × 486): the detection-level
  table behind the wells table: same columns plus `detection_index`
  (0-based within each well); image latents are per-detection, RNA latents
  repeat per well.
- [control_compound_map.csv](../annex_same_well/control_compound_map.csv) (35 rows): `control_name`,
  `public_compound_id`, `public_compound_name`.
- [evidence/cross_modal_regimes.csv](../annex_same_well/evidence/cross_modal_regimes.csv) (3 rows): `regime`, `n_wells`,
  `alpha`, `mcPearson`, `R2_mean_perdim`, `R2_pooled`, `null_mean`,
  `null_std`, `null_p95`, `p_value`. Image→RNA ridge predictability in
  three regimes (raw / within-control / across-control LOGO).
- [evidence/per_control_coupling.csv](../annex_same_well/evidence/per_control_coupling.csv) (36 rows: 35 controls plus a
  `GLOBAL_WITHIN_CONTROL` summary row): `control`, `n_wells`,
  `pls1_corr`, `null_mean`, `null_std`, `null_p95`, `p_value`.
- [evidence/learning_curve.csv](../annex_same_well/evidence/learning_curve.csv) (6 rows): `n_wells`, `mcPearson_mean`,
  `mcPearson_std`, `null_mean`, `null_std`, `null_p025`, `null_p975`.
- [evidence/learning_curve.png](../annex_same_well/evidence/learning_curve.png): the learning curve, plotted.

- [evidence/mantel_bootstrap.csv](../annex_same_well/evidence/mantel_bootstrap.csv): two resampling summaries with `estimate`, `mantel_r`, `perm_p`, `boot_ci_lo`, `boot_ci_hi`, `boot_mean`, `boot_std`. The Mantel r correlates pairwise correlation distances between 35 control means in image and RNA space (r = 0.77289; two-sided permutation p = 1/2,001). Controls and wells are different bootstrap units; the well bootstrap samples image and RNA wells independently within fixed controls. [Methods and runnable check](../annex_same_well/MANTEL_METHODS.md).



## annex_clusters/

Read [annex_clusters/README.md](../annex_clusters/README.md) first.

- [cluster_census.csv](../annex_clusters/cluster_census.csv) (1,007 rows): `context`, `cluster_id`,
  `n_members`, `coherence`, `coherence_z`, `coherence_q`, `anchor_bb`,
  `anchor_pos`, `anchor_frac`, `top_up_set`, `top_up_q`, `top_dn_set`,
  `top_dn_q`, `prior_series_n` (count of matching chemistry-series records by context and anchor building block). One row per chemistry-constrained response-family
  cluster recovered from the 32-program usage vectors; every row at
  coherence q <= 0.01 against 200 size-matched random compound sets.

- [pathway_family_counts.csv](../annex_clusters/pathway_family_counts.csv): current pathway-family totals across the 1,007 census rows; 855 have a significant annotation and 152 do not. [Selection and grouping rule](../annex_clusters/pathway_family_method.json).

## annotations/

[Control target annotations](../annotations/control_target_annotations.csv) records current targets, mechanisms and primary citations. [Annotation guide](../annotations/README.md) explains the MSC1094308 VCP/p97 and VPS4B annotation and the distinction between chemical response similarity and direct target evidence.

## figures/

[Figure guide](../figures/README.md) indexes all six overview assets. [platform_counts.json](../figures/platform_counts.json) stores the five overview counts. [measured_and_nominal_design_space.csv](../figures/measured_and_nominal_design_space.csv) has one row per context: `observed_compounds`, `bb0`–`bb4` vocabulary sizes, `nominal_independent_combinations`, `observed_to_nominal_fraction`, and `scope`. PNG/SVG pairs visualize those inputs. [The results reference](PILOT_RESULTS_REFERENCE.md) explains the distinct library-union calculation.


## Additional pilot objects

| Module | Principal key and unit | Schema/method entry |
|---|---|---|
| Response-family members/centroids | `context, cluster_id` and explicit `atlas_id`; member order and centroid row are separate | [Response-family atlas](../atlas/original_clusters/README.md) |
| Selected case-study evidence | Chemical family/group; objective, policy, start and round; processed summaries | [Case-study data guide](../annex_case_studies/DATA_GUIDE.md) |
| Measurement-design evidence | Exact well key or context/control/batch; sample/partition IDs and training size | [Measurement design](../annex_measurement_design/README.md) |
| Microscopy examples | Image crop index, channel and public compound ID; RNA linked by compound | [Gallery](../gallery/DATA_GUIDE.md) |

The [annex index](ANNEX_INDEX.md) distinguishes measured profiles, predictions, correspondence analyses and hypotheses. [Data access](ANALYSIS_ACCESS.md) describes the processed-data scope and how to obtain raw measurements or external genetic references.
