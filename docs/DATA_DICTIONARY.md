# Data dictionary

Every file, column, array key, and JSON field in the package, plus the
contracts that make the layers join. Contexts (8): `zel024_hek293`,
`zel024_h1650`, `zel028_hek293`, `zel028_a549`, `zel028_h1650`,
`zel031_a549`, `zel031_thp1`, `zel039_aec7`. Compound counts per context:
13,914 / 10,686 / 61,396 / 40,622 / 25,906 / 8,321 / 9,041 / 20,813
(190,699 compound-context pairs; 162,914 distinct compounds).

## Contracts (read first)

**Row-alignment contract.** Every `{context}.npy` matrix (in
`core/surfaces/` and `core/usages/`) is row-aligned to its sibling
`{context}_compounds.parquet`: row *i* of the matrix is the compound named
in row *i* of the parquet, and the parquet has exactly one column,
`public_compound_id`. Surface, usage, and compounds tables for the same
context have the same row count and the same row order. There is no other
join key and no index column; positional alignment is the contract.

**Panel index-space contract.** The harmonized panel is defined by
`core/surfaces/harmonized_6000_genes.parquet`. Its `gene_index` column
holds raw positional indices into the 46,944-gene pseudobulk
space. Gene symbols for panel positions come ONLY from this file's `gene`
column; never map panel positions through any context's released
3,000-gene panel, which is a different index space.

**Usages/basis contract.** Usage column *j* (0-based) is program P*j*+1 of
the pinned basis in `core/basis/`, in every context, every prediction
dump, and every annex table. Usages are valid only against the pinned
basis (`core/basis/basis_registry.json`); any refit changes program
identities (P32 is currently unnamed; program-atlas naming is tied to this
basis version).

**Fold convention.** fold = SHA256(`public_compound_id`) mod 5, computed
on the full 64-hex-character digest as an integer. The shared basis and
the reference model were both fit with fold 0 held out. Train on folds
1–4, evaluate on fold 0. Note: promoted usages can be slightly more
predictable on fold 0 in some exercises, so clean cross-exercise
comparisons use folds 1–4 (see `docs/INTERPRETATION_LIMITS.md`).

**Measured vs predicted.** Everything under `core/` is measured
(derived from measurement by the pipeline in `docs/METHODS.md`).
`models/` outputs, the `y_pred_z` arrays in the imaging annex dumps, and
any table marked `grammar_level` or model-predicted are predictions, and
are labeled as such where they ship.

## core/

### core/usages/

- `usages_{context}.npy` — float32, (n_compounds, 32), free sign.
  Per-compound program usages (`program_usage_projection_v1`): the
  free-sign least-squares projection of the context-scaled harmonized
  surface onto the pinned k = 32 basis.
- `usages_{context}_compounds.parquet` — one column:
  `public_compound_id` (string). One row per usage-matrix row, aligned
  positionally.

### core/surfaces/

- `surfaces_{context}.npy` — float32, (n_compounds, 6000). Device-centered
  log1p-CP10k expression on the harmonized panel
  (`device_centered_harmonized_surface_v1`). Column *j* is panel position
  *j* of `harmonized_6000_genes.parquet`.
- `{context}_compounds.parquet` — one column: `public_compound_id`.
- `harmonized_6000_genes.parquet` — 6,000 rows, the panel definition
  (`harmonized_panel_6000_v1`):
  - `panel_position` (int64, 0–5999): column index in every
    `surfaces_{context}.npy`.
  - `gene_index` (int64): raw position in the 46,944-gene pseudobulk
    space (full-width index space; see the contract above).
  - `gene` (string): gene symbol. The only authoritative symbol mapping.

### core/basis/

- `shared_basis_k32.npy` — float32, (32, 6000), nonnegative
  (`shared_program_basis_v1`). Row *j* is the gene-loading vector of
  program P*j*+1, columns aligned to the panel.
- `shared_basis_k12.npy` — float32, (12, 6000), nonnegative
  (`shared_program_basis_k12_v1`), lower-resolution companion.
- `basis_registry.json` — the version pin:
  - `registry_name`, `created`, `basis_version`
    (`shared_program_basis_v1`).
  - `basis_fit_scope`: training folds 1–4 only; fold 0 untouched by any
    fitting.
  - `source_product`, `source_manifest_sha256`: semantic provenance of
    the pinned basis (this package's `shared_program_basis_v1`).
  - `pinned_files`: list of `{package_name, file, k, sha256}` for the two
    basis arrays.
  - `validity_statement`: usages are valid only against the pinned basis
    files.

### core/recipes.parquet

162,914 rows, one per distinct `public_compound_id`:

- `public_compound_id` (string, `CPD_############`).
- `bb0`–`bb4` (string, `BB_##########`, or null when the position is
  absent in that recipe). Position sets differ between libraries.
- `n_positions_occupied` (int64): how many of the five positions carry a
  block.

### core/splits/fold_assignments.parquet

190,699 rows (= total compound count across the 8 contexts):

- `context` (string), `public_compound_id` (string), `fold` (int64, 0–4).

### core/benchmark/

`README.md` explains the two configurations (`per_context_expert`,
`context_token_trunk`), the two splits (`compound_5fold`, `bb_disjoint`),
and the two output spaces (program space vs decoded gene space). Tables:

- `per_context_comparison_k32.csv` (16 rows) — `context`, `split_type`,
  `per_context_expert_mean`, `per_context_expert_sd_cells`,
  `per_context_expert_n_compounds`, `context_token_trunk_mean`,
  `context_token_trunk_sd_cells`, `context_token_trunk_n_compounds`,
  `diff_mean`, `diff_ci_lo`, `diff_ci_hi`. Decoded gene-space mean
  per-compound Pearson (mcPearson) per model with the paired difference
  and its 95% confidence interval.
- `program_space_primary.csv` (90 rows) — `arm`, `split_type`,
  `target_variant`, `k`, `context`, `eval_only`, `n_runs`,
  `prog_pearson_mean`, `prog_pearson_sd_programs`, `null_mean`,
  `null_sd`, `z`. Mean per-program Pearson of predicted vs measured usage
  coordinates against a permutation null, with the resulting z-score.
  Includes the probe context `zel031_h1650` (never trained).
- `k_resolution.csv` (64 rows) — `context`, `split_type`, `arm`, `k`,
  `decoded_mcpearson_mean`, `decoded_mcpearson_sd_cells`,
  `prog_pearson_mean`, `prog_pearson_sd`. k = 12 vs k = 32.
- `correction_arm.csv` (12 rows) — `context`, `arm`, `target_variant`
  (`device_centered_target` / `depth_regressed_target`), `k`, `n_cells`,
  `prog_pearson_mean`, `prog_pearson_sd`,
  `decoded_vs_device_centered_target_mean`,
  `decoded_vs_device_centered_target_sd_cells`,
  `decoded_vs_depth_regressed_target_mean`,
  `decoded_vs_depth_regressed_target_sd_cells`. The depth-regressed
  variant did not improve; the device-centered target is canonical.
- `program_signal_concentration.csv` (4 rows) — `analysis_layer`, `metric`,
  `range_min`, `range_max`, `note`. Gene-space versus program-space
  repeat-measurement ceilings and cross-cell-line agreement; the evidence
  table for the "10–20× stronger in program space" claim.
- `cross_context_probe.csv` (9 rows) — `ctx_a`, `ctx_b`, `n_compounds`,
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

## models/

See `models/README.md` for usage, the fold-0 convention, and provenance.

- `context_token_trunk_reference_eval_v1_seed{0,1,2}.pt` — PyTorch
  checkpoints (`torch.load(..., weights_only=True)`), each a plain dict:
  - `format` — `context_token_trunk_reference_eval_v1`.
  - `state_dict` — model weights (keys match `model_def.py` exactly).
  - `architecture` — `d_model` 128, `n_heads` 4, `n_layers` 2,
    `feedforward` 512, `dropout` 0.1, `n_programs` 32, `n_tokens` 8,
    `d_chemistry` 128, `d_identity` 64, `n_libraries`, `n_cell_lines`,
    `vocabulary_sizes` (per bb slot), `n_parameters` 473,120.
  - `training` — `held_out_fold` 0, `seed`, `split_convention`
    `compound_5fold`, `target` `device_centered_program_usage`,
    `basis_version` `shared_program_basis_v1`, `max_epochs`,
    `batch_size`, `learning_rate`, `weight_decay`, `warmup_epochs`,
    `patience`, `best_epoch`, `epochs_run`, `best_val_score`,
    `training_contexts`.
  - `vocabulary` — `bb_slots` (`bb0`–`bb4`); `level_to_index` (per-slot
    maps public BB ID → identity-embedding row; row 0 = absent slot,
    row 1 = unseen ID); `libraries`; `cell_lines`; `context_tokens`
    (per context `{library, cell_line, trained}`; the probe context is
    marked `trained: false`).
  - `usage_scales` — per context `{mu, sd}` (32 values each): the
    per-context standardization mapping the raw head output
    (`usage_z_scored`) back to usage units comparable to `core/usages/`
    (`usage = usage_z_scored * sd + mu`).
  - `provenance` — `role` ("reference model, evaluation grade"),
    `retrained_utc`, `original_code_sha256`, `note`.
- `bb_embedding_table.parquet` — 629 rows: `public_bb_id` (string) +
  `embedding_000`…`embedding_127` (float32), the 128-dimensional
  pretrained chemistry embedding per public BB ID. Public IDs only.
- `golden_predictions.json` — environment verification fixture:
  `format`, `seed` 0, `model_file`, `tolerance` 2e-6, `note`, `entries`
  (20 fixed fold-0 recipes across 5 contexts, each `{context,
  public_compound_id, recipe: {bb0..bb4}, prediction_usage_z_scored:
  [32 floats]}`).
- `model_def.py` — self-contained architecture (PyTorch only).
- `predict.py` — CPU inference CLI and `--check-golden` self-check.

## annex_imaging/

Full narrative: `annex_imaging/README.md`. All per-compound tables key on
`public_compound_id`.

- `zel024_compound_embeddings.parquet` (10,129 × 3,075) /
  `zel031_compound_embeddings.parquet` (8,443 × 3,075) —
  `public_compound_id`, `n_fovs` (fields of view averaged), `n_panels`,
  `rn50_0000`…`rn50_2047` (ResNet-50 embedding means),
  `clip_0000`…`clip_1023` (CLIP embedding means).
- `zel024_compound_intensity.parquet` (10,129 × 8) —
  `public_compound_id`, `n_fovs`, `n_panels`, `brightfield_cell_mean`,
  `dapi_cell_mean`, `p21_cell_mean`, `p62_cell_mean`,
  `phalloidin_cell_mean`.
- `zel031_compound_intensity.parquet` (8,443 × 8) — same key and support
  columns; marker set `brd4_cell_mean`, `brightfield_cell_mean`,
  `cona_cell_mean`, `dapi_cell_mean`, `phalloidin_cell_mean`. The two
  libraries are different panels (p62 only in zel024; BRD4/ConA only in
  zel031): pool only with panel-aware normalization.
- `zel039_imaging_latents.parquet` (78,896 detections × 457) —
  `public_compound_id` (empty for unmapped detections; see
  `mapped_to_compound_master`), `public_bb0_id`…`public_bb2_id`,
  `mapped_to_compound_master` (bool), `zlibrary`, `cell_line_context`,
  `scantype` (cell painting or immunofluorescent staining), `if_target`
  (immunofluorescence target where applicable), `D0`…`D447` (per-detection
  448-dimensional image latents).
- `reliability/embedding_reliability_audit.json` — `created_utc`,
  `min_fovs`, `n_splits`, `libraries` (per library: `n_fovs`,
  `n_compounds`, and per backbone `rn50`/`clip`:
  `split_half_sb_median_raw`, `null_median_raw`,
  `split_half_sb_median_centered`, `null_median_centered`,
  `n_compounds_audited`), `runtime_s`. Split-half = two half-averages of a
  compound's FOVs correlated across compounds, Spearman-Brown corrected.
- `reliability/marker_reliability_audit.json` — `created_utc`,
  `libraries` (per library: `n_fovs`, `n_compounds`, `markers` with
  per-marker `split_half_sb` and legacy cross-check fields
  `legacy_column`, `legacy_corr`, `legacy_n`; plus the marker–marker
  correlation matrix).
- `image_to_program_predictions/{context}/` and
  `chemistry_to_program_predictions/{context}/` — fold-clean test
  predictions, one `.npz` per fold × seed × model. NPZ keys:
  - `public_compound_id` — (n,) unicode strings, held-out test compounds
    only.
  - `y_true_z` — float32 (n, 32), measured usages, z-scored per program.
  - `y_pred_z` — float32 (n, 32), predicted usages, same z-scored space.

  Filename grammar: `{features}_{model}__fold{f}_seed{s}.npz` for
  image→program (features `clip`, `rn50` for zel024/zel031; `cp448`,
  `if448`, `mean448`, `scantype896` for zel039; models `ridge`, `mlp`),
  and `fold{f}_seed{s}.npz` for chemistry→program (a cross-attention
  model over the building blocks). Contexts covered: zel024_hek293,
  zel031_a549, zel031_thp1, zel039_aec7. Column *j* of either matrix is
  program P*j*+1 of the pinned basis.
- `prediction_score_summary.csv` (175 rows) — `family`
  (`image_to_program` / `chemistry_to_program`), `context`, `model`,
  `fold`, `seed`, `n_test_compounds`, `mean_program_pearson`. Derived
  from the dumps; recomputing a row is shown in
  `examples/04_join_imaging.ipynb`.
- `decomposition.csv` (128 rows: 4 contexts × 32 programs) — `context`,
  `program` (P01–P32), `image_features`, `chemistry_model`, `folds`,
  `n_test_compounds`, `r2_chem`, `r2_img`, `r2_joint`, `chem_only`,
  `img_only`, `shared`, `unexplained`, `img_only_fold_sd`,
  `chem_only_fold_sd`, `img_only_null_mean`, `img_only_null_sd`,
  `img_only_z`, `img_only_tail`, `chem_only_null_mean`,
  `chem_only_null_sd`, `chem_only_z`, `chem_only_tail`, `rel_img`,
  `img_only_rel_ceiling`, `r2_img_rel_ceiling`, `r_ceiling_img`.
  Per-program variance ownership (chemistry alone / imaging alone /
  shared / neither) with permutation nulls and reliability ceilings.
- `decision_grade_image_to_program_panels.csv` (35 rows) — `context`,
  `image_backbone` (clip / rn50), `model` (ridge / mlp), `fold`, `seed`,
  `n_train_compounds`, `n_test_compounds`, `prog_pearson_mean`,
  `prog_pearson_median`, `pairing_null_mean`, `pairing_null_sd`,
  `pairing_null_z`, `pairing_null_tail_frac`. Cell-level decision-grade
  image→program evaluation for zel024_hek293, zel031_thp1, zel031_a549.
- `decision_grade_image_to_program_zel039_aec7.csv` (60 rows) — `context`,
  `model_variant` (mean448/scantype896 × ridge/mlp), `fold`, `seed`,
  train/val/test counts, `prog_pearson_mean/median/min/max`,
  `null_mean/sd/q95/tail_frac_ge`, `above_floor_q95`,
  `margin_over_q95`, `model_hyperparameter`. The 5-fold × 3-seed ×
  4-variant decision-grade zel039 evaluation.
- `decode_through_comparison.csv` (30 rows) — `context`, `fold`, `seed`,
  train/test counts, `bottleneck_mcpearson_*` (decode through the
  32-program bottleneck), `direct_mcpearson_*` (direct image→gene
  prediction), `oracle_mcpearson_*` (usage-space ceiling), null q95s,
  paired `diff_mean` with CI, `fraction_of_oracle_filled`.
- `marker_program_association.csv` (768 rows) — `context`, `library`,
  `marker`, `program`, `n_test`, `r_raw`, `z_raw`, `tail_raw`,
  `r_partial`, `z_partial`, `tail_partial`, `marker_rel_sb`, `r_ceiling`,
  `r_chem_pred`, `z_chem_pred`, `r_img_pred`, `z_img_pred`, `fw_flag`.
  Marker intensity vs measured usages (`r_raw`; `r_partial` removes the
  shared cell-density axis) and vs image-predicted / chemistry-predicted
  usages, with nulls and reliability ceilings.
- `marker_program_depth_stratified.csv` (3 rows) — `context`, `marker`,
  `program`, `depth_stratum`, `n_test`, `r_partial`, `r_raw`.

## annex_hypotheses/

Read `annex_hypotheses/README.md` and `LIMITS.md` first. All tables are
hypothesis-generating.

- `anchor_leads.csv` (16 rows) — `hypothesis_id` (ZSH-####, stable),
  `bb_level_ids`, `contexts`, `biological_program`, `matched_control`,
  `moa_class`, `external_triangulation`, `evidence_summary`,
  `confidence_tier` (A/B/C), `caveats` (controlled vocabulary:
  `weak_null`, `singleton`, `triage_grade`, `low_coverage`),
  `kill_confirm_experiment`.
- `program_atlas.csv` (26 rows) — `program_group_id`, `context`,
  `primary_program`, `n_programs_merged`, `member_programs`,
  `theme_family`, `named_theme`, `top_genes`, `top_gene_sets`,
  `driving_bb_levels`, `n_bb_levels_q05`, `anchor_control`,
  `anchor_top3_controls`, `crispr_ko_links`,
  `member_compounds_usageZ_ge1`, `mean_abs_usage`, `frac_deep_top500`,
  `library_frac_deep`, `depth_tier_skew_flag`, `ica_median_abs_cos`,
  `confidence_tier`, `focus_experiment`. Program identities are tied to
  the pinned basis.
- `sharp_sar_candidates.csv` (133 rows) — `candidate_id`, `context`,
  `candidate_kind`, `n_members`, `within_phenotype_coherence`,
  `coherence_null_z`, `coherence_permutation_p`,
  `falloff_null_percentile`, `chemistry_within`, `ring1_similarity`,
  `driver_genes`, `evidence_tier` (zel024 rows marked `grammar_level`),
  `selection_note`.
- `hypothesis_ledger_full.csv` (3,754 rows, triage-grade,
  hypothesis-generating) — `hypothesis_id`, `hypothesis_type`, `status`
  (`hypothesis_anchor_validated` / `hypothesis_strong` /
  `hypothesis_triage`), `confidence_tier`, `context`, `bb_level_ids`,
  `claim`, `evidence`, `matched_control`, `moa_class`, `caveats`,
  `evidence_rank_score`.

## annex_chemistry/

Column-by-column definitions with interpretation are in
`annex_chemistry/README.md`; headers for reference:

- `novel_bb_generalization.csv` (8 rows) — `context`,
  `structure_readout_model_r_mean`, `structure_readout_model_r_sd`,
  `identity_readout_model_r_mean`, `structure_minus_identity_r_mean`,
  `structure_minus_identity_r_ci95`,
  `structure_minus_identity_frac_folds_positive`,
  `reference_trunk_model_r_mean`, `structure_minus_trunk_r_mean`,
  `structure_ridge_r_mean`, `additive_embedding_floor_r_mean`,
  `structure_ridge_minus_floor_r_mean`,
  `structure_ridge_minus_floor_r_ci95`,
  `structure_ridge_minus_floor_frac_folds_positive`.
- `attribution_certificate.csv` (6 rows) — `context`, `fold`,
  `usage_target`, `structure_model_r`, `model_null_z`,
  `n_building_blocks`, `bb_knockout_vs_measurement_median_spearman`,
  `bb_knockout_null_mean`, `bb_knockout_null_sd`, `bb_knockout_z`,
  `parts_sum_vs_direct_median_spearman`, `n_structure_parts`,
  `negative_control_median_spearman` (empty where not applicable),
  `runtime_seconds`.
- `activity_cliffs.csv` (450 rows) — `context`, `bb_pair_id`,
  `n_members`, `within_phenotype_coherence`,
  `within_candidate_chemical_coherence`, `ring1_phenotype_correlation`,
  `ring2_phenotype_correlation`, `ring3_phenotype_correlation`,
  `falloff`, `null_falloff_mean`, `null_falloff_sd`,
  `falloff_null_percentile`.
- `chemotype_series.csv` (2,727 rows) — `context`, `evidence_level`
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
- `bb_effect_rankings.csv` (431 rows) — `context`, `position`, `bb_id`,
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

Full narrative: `annex_same_well/README.md`. The well key is
(`batch_id`, `well_id`); `well_id` is unique only within a batch. Context
label: `same_well_hek293`.

- `same_well_wells.parquet` (11,435 × 486) — `batch_id` (`batch_1` /
  `batch_2`), `well_id`, `public_compound_id`, `control_name`,
  `cell_line`, `n_detections`, `img_lat_0_0`…`img_lat_3_63` (448 image
  latents, mean over the well's detections; blocks 0–2 × 128 plus block 3
  × 64), `D00`…`D31` (32 RNA latents, constant within a well).
- `same_well_detections.parquet` (14,757 × 486) — the detection-level
  table behind the wells table: same columns plus `detection_index`
  (0-based within each well); image latents are per-detection, RNA latents
  repeat per well.
- `control_compound_map.csv` (35 rows) — `control_name`,
  `public_compound_id`, `public_compound_name`.
- `evidence/cross_modal_regimes.csv` (3 rows) — `regime`, `n_wells`,
  `alpha`, `mcPearson`, `R2_mean_perdim`, `R2_pooled`, `null_mean`,
  `null_std`, `null_p95`, `p_value`. Image→RNA ridge predictability in
  three regimes (raw / within-control / across-control LOGO).
- `evidence/per_control_coupling.csv` (36 rows: 35 controls plus a
  `GLOBAL_WITHIN_CONTROL` summary row) — `control`, `n_wells`,
  `pls1_corr`, `null_mean`, `null_std`, `null_p95`, `p_value`.
- `evidence/learning_curve.csv` (6 rows) — `n_wells`, `mcPearson_mean`,
  `mcPearson_std`, `null_mean`, `null_std`, `null_p025`, `null_p975`.
- `evidence/learning_curve.png` — the learning curve, plotted.


