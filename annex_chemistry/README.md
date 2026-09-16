# Chemistry Annex

Use this annex to inspect recurring chemical components, related recipe
series and local changes in cellular response. It contains two completed
structure-model evaluations and three tables of response-associated chemical
families, all using public identifiers.

Chemical structures are not included. Building blocks are identified
only by public, opaque identifiers of the form `BB_##########`. The
underlying structure maps and structure-model inputs are outside this
public download. For access enquiries, contact hello@zafrens.com.

## Background vocabulary

- **Building block (BB).** Z-Screen compounds are assembled combinatorially
  from a fixed vocabulary of chemical building blocks. A *recipe* specifies
  which block sits at which *position* (`bb0`, `bb1`, …). Positions are
  numbered per library, so position sets differ between contexts.
- **Context.** One library × cell-type combination, e.g. `zel024_hek293`.
  Context names are public and used throughout the package.
- **Programs and usages.** Measured gene-expression responses are summarized
  as usages of 32 shared transcriptional programs (see the core package).
  Most numbers below are correlations or similarities computed in that
  32-dimensional program space. These coordinates derive from processed
  response surfaces; some contexts include substantial recipe-model pooling.
- **Coherence.** Mean pairwise cosine similarity of the measured program
  profiles of a set of compounds. High coherence = the set moves biology in
  a consistent direction.
- **Null percentile / z / p / q.** Each SAR statistic is compared against
  random compound sets matched in size and read-depth tier (shallow / mid /
  deep sequencing depth). `z` is the standard-score distance from that null,
  `p` the empirical fraction of null draws at least as extreme, and `q` the
  Benjamini-Hochberg false-discovery-rate adjustment across candidates.

## The two distilled findings

1. **Structure features represent building blocks withheld from model fitting.**
   In the saved held-out-building-block evaluation, the structure model predicts the 32
   measured programs at r = 0.339 ± 0.020 in `zel024_hek293` (at parity
   with the architecture-matched identity model there, and within 0.018 of
   it in the other contexts), while the additive learned-embedding
   baseline reaches 0.182. Structure features give the model a representation
   for components absent from training; this is a retrospective model
   evaluation, not a prospective synthesis result. Evidence: `novel_bb_generalization.csv`.

2. **Model component effects agree with the measurement-derived reference.**
   Knocking out one building block at a time through the structure model
   recovers the measurement-side effect of that block at median Spearman
   0.89-0.94 (z = 13.8-19.2 against matched nulls; negative controls near
   zero where measured; see the table note), and
   knocking out the block's constituent parts sums to the whole-block
   knockout at 0.97-0.99. These comparisons support building-block attribution in this
   model and response representation. Removing a feature from the model is
   an in-silico operation, not a laboratory component-deletion experiment. Evidence:
   `attribution_certificate.csv`.

## The tables

### `novel_bb_generalization.csv`: 8 rows, one per context

Completed generalization results for building blocks withheld from model
training. Columns:

- `structure_readout_model_r_mean` / `_sd`: mean ± sd Pearson r (predicted
  vs measured program usages) of the structure-input readout model across 5
  folds × 3 seeds. The headline number above is this column in
  `zel024_hek293`.
- `identity_readout_model_r_mean`: the same architecture fed building-block
  identity instead of structure. The comparison against
  `structure_readout_model_r_mean` is the parity claim:
  `structure_minus_identity_r_mean` with its 95% confidence interval
  (`_ci95`) and the fraction of folds where structure is ahead
  (`_frac_folds_positive`).
- `reference_trunk_model_r_mean`: the package's reference context-token
  trunk model for orientation, and `structure_minus_trunk_r_mean` the gap
  to it.
- `structure_ridge_r_mean`: a simple linear (ridge) model on structure
  features, compared against `additive_embedding_floor_r_mean`, the
  additive learned-embedding baseline. The structure ridge beats that floor
  in 7 of 8 contexts with confidence intervals excluding zero
  (`structure_ridge_minus_floor_r_mean`, `_ci95`, `_frac_folds_positive`).

### `attribution_certificate.csv`: 6 rows (2 contexts × 3 folds)

The validation certificate for structure-based attribution. For each
building block, the block is removed from the structure model's input and
the predicted change is compared against the block's measured effect across
programs. Columns:

- `usage_target`: which usage layer the certificate was computed against
  (`primary`, or the cross-validation variants `cross_fold_1`/`cross_fold_2`
  as robustness checks).
- `structure_model_r`, `model_null_z`: overall model quality and its
  null-calibrated significance.
- `n_building_blocks`: number of blocks certified in that row.
- `bb_knockout_vs_measurement_median_spearman`, the headline certificate:
  median Spearman correlation between predicted knockout effects and
  measured block effects (0.89-0.94).
- `bb_knockout_null_mean` / `_sd` / `_z`: the same statistic under label
  nulls and the resulting z-score (13.8-19.2).
- `parts_sum_vs_direct_median_spearman`, `n_structure_parts`:
  consistency: knocking out a block's constituent structure parts one by one
  and summing reproduces the whole-block knockout (0.97-0.99).
- `negative_control_median_spearman`: a shuffled-control certificate; near
  zero as required. Empty (NaN) in rows where the shuffled control was not
  applicable to that context's certificate design; the two measured values
  are -0.026 and 0.083.

### `activity_cliffs.csv`: 450 rows (`zel024_hek293`, `zel039_aec7`)

One row per building-block pair candidate: all compounds that share two
fixed blocks at two positions while the rest of the recipe varies
(`bb_pair_id` gives both position-block pairs). This table tests how quickly
phenotype decays as chemistry moves away from the candidate set: the
"activity cliff" read. Compounds are binned into chemical-similarity rings
around the candidate set (ring 1 = most similar). Columns:

- `n_members`, `within_phenotype_coherence` (coherence of the candidate
  set's measured profiles), `within_candidate_chemical_coherence`.
- `ring1`/`ring2`/`ring3_phenotype_correlation`: mean similarity of ring
  compounds' measured profiles to the candidate set's average profile.
- `falloff` = within-set coherence minus ring-1 correlation. Positive
  falloff means the candidate set's phenotype is sharper than that of its
  nearest chemical neighbors. The SAR is steep exactly at the candidate.
- `null_falloff_mean` / `_sd` and `falloff_null_percentile`: the same
  statistic for matched random sets and where the candidate sits against
  them (1.0 = sharper than every null draw).

Note: `zel031_a549` contributes no building-block-pair candidates at this
analysis level (its library vocabulary supports single-position reads), so
it appears in `bb_effect_rankings.csv` but not here.

### `chemotype_series.csv`: 2,727 rows (`zel024_hek293`, `zel039_aec7`)

The ranked chemotype-series table: building-block pairs whose member
compounds form a statistically coherent series. This is the primary table
for series-level SAR. Columns:

- `bb_pair_id`, `position_a`/`bb_id_a`, `position_b`/`bb_id_b`: the pair.
- `evidence_level`: `measured` for `zel039_aec7` rows; `grammar_level` for
  `zel024_hek293` rows. Grammar-level means the series is defined at the
  recipe level in a library where per-compound measurements are pooled;
  read those rows as recipe-level expectations, not per-compound claims.
- `n_members`, `effect_strength_l2` (magnitude of the series' average
  program-space signature), `top20_gene_energy_fraction` and
  `participation_ratio` (how concentrated vs spread the underlying gene
  signal is).
- `coherence` with `null_coherence_mean`/`_sd`, `coherence_z_vs_null`,
  `coherence_p_empirical`, `coherence_q_fdr_bh`, and
  `coherence_p_permutation` (a second, permutation-based p-value).
- `sibling_max_cos` / `sibling_mean_cos` / `n_siblings`: how similar the
  series' signature is to other series sharing one block (specificity:
  high-coherence series with low sibling similarity are the sharpest).
- `effect_strength_z_vs_null`, `effect_strength_p_empirical`: size of the
  effect against the same matched nulls.
- `mean_shrinkage_weight`, `mean_n_wells`: average measurement support per
  member.
- `composite_score` and `composite_rank`: the overall ranking within each
  context; `is_positive_control` flags series carrying known-mechanism
  blocks.
- `driver_genes_up` / `driver_genes_down`: the genes contributing most to
  the series signature, with signed weights.
- `frac_*_depth_tier`, `library_base_frac_*_depth_tier`,
  `delta_frac_*_depth_tier`: read-depth-tier composition of the series'
  members versus the library base rate, so depth confounds are visible
  alongside every effect.

**Phenotype example:** the heat-shock-associated series anchored by
`BB_2085420374` (`bb0=BB_2085420374 & bb1=BB_5422857344`) lands at
`composite_rank` 1 in `zel039_aec7`, with heat-shock genes (HSP90AA1,
HSPA1A, HSPD1, DNAJB1, HSPB1, …) as its top up-drivers. The ranking
recovers a recognizable response pattern. The
`is_positive_control` field is a classification flag; it does not disclose
the building block’s structure or establish a molecular mechanism.

### `bb_effect_rankings.csv`: 431 rows (all three SAR contexts)

Single-building-block effects: for one block at one position, everything
measured across all compounds carrying it. Columns:

- `position`, `bb_id`, `n_carriers` (compounds carrying the block),
  `in_sar_window` (whether the block passes the minimum-support rule for
  SAR reads).
- `coherence`, `coherence_z`, `coherence_p`, `coherence_p_permutation`:
  consistency of carriers' measured profiles, against matched nulls.
- `sparse_coherence`, `sparse_coherence_z`, `sibling_max_cos`,
  `sibling_max_sparse_j`, `sparse_falloff`, `sparse_composite_score`,
  `sparse_rank`: a sparsified variant of the same analysis (robustness to
  diffuse signatures), ranked within each context.
- `effect_strength_l2`, `top20_gene_energy_fraction`,
  `delta_frac_deep_depth_tier`.
- `within_candidate_chemical_coherence`,
  `ring1`/`ring3_phenotype_correlation`, `falloff`,
  `falloff_null_percentile`: the same cliff statistics as in
  `activity_cliffs.csv`, computed at single-block level.
- `driver_genes_up` / `driver_genes_down`, `is_positive_control`.

## Reading guidance and limits

- All SAR tables are building-block-level, not compound-level: they say
  which *blocks and block pairs* carry coherent biology, which is the level
  at which this dataset is most reliable.
- `zel024_hek293` SAR rows are grammar-level (see `evidence_level` in
  `chemotype_series.csv`); treat them as recipe-level expectations.
- Specificity lives in the rank and identity of a candidate, not in small
  p-values alone; use `composite_rank`, sibling-similarity columns, and the
  null percentiles together.
- These tables enumerate candidates for medicinal-chemistry follow-up. They
  are hypothesis-generating, not confirmatory.
- The two UPR-associated series in ZSH-3757 have different neighbor
  correlations and depth composition. See the [interpretation notes](../annex_hypotheses/INTERPRETATION_NOTES.md)
  when interpreting their different responses.
- Structures and structure-model inputs are outside this download.
  [Methods and input access](../docs/ANALYSIS_ACCESS.md).
