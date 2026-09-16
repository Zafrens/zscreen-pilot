# Pilot results reference

Quantitative results below identify their input tables, evaluation splits and units. They describe the processed pilot resource and the analyses supported by its measurements.

## Recipe-to-response prediction

The shared-trunk evaluation reports **mean per-program Pearson r = 0.105–0.530**, with **z = 6.1–28.1** relative to its permutation null across eight measured contexts. Use [program_space_primary.csv](../core/benchmark/program_space_primary.csv) with `arm=context_token_trunk`, `split_type=compound_5fold`, `target_variant=device_centered_target`, `k=32`, and `eval_only=False` (15 runs per context). The mean is across the 32 predicted program coordinates; z expresses separation from the stated null, not potency or prediction error in physical units.

| Context | Mean program Pearson | Null z |
|---|---:|---:|
| `zel024_h1650` | 0.223 | 10.3 |
| `zel024_hek293` | 0.530 | 28.1 |
| `zel028_a549` | 0.105 | 9.5 |
| `zel028_h1650` | 0.105 | 7.6 |
| `zel028_hek293` | 0.149 | 16.6 |
| `zel031_a549` | 0.150 | 6.1 |
| `zel031_thp1` | 0.285 | 12.1 |
| `zel039_aec7` | 0.321 | 20.8 |

The separate **pinned fold-0 comparison** must be cited with its own split and model aggregation. Best simple recipe models reach r = 0.0986–0.5011; the three-seed transformer ensemble reaches 0.1063–0.5820. Each wins in four of eight contexts. The context-only train-mean control is numerically zero. Pearson measures response ranking/shape; raw transformer R² is negative in all eight contexts, and training-derived affine calibration improves it. See [fold-0 summary](../core/benchmark/fold0_reference_model_summary.csv) and [benchmark definitions](../core/benchmark/README.md).

## Held-out building blocks and imaging

- **Unseen building-block evaluation:** in `zel024_hek293`, the structure-input readout gives r = 0.339 ± 0.020 (mean ± SD across five folds × three seeds), compared with 0.333 for the architecture-matched identity model and 0.182 for the additive embedding baseline. The structure-versus-identity confidence interval includes zero. This is a retrospective evaluation on withheld building blocks; the structure inputs/model required to rerun it are outside the download. [Result table](../annex_chemistry/novel_bb_generalization.csv) · [Methods](../annex_chemistry/README.md).
- **Model component attribution:** the six recorded evaluations have median Spearman agreement of approximately 0.89–0.94 between model feature-removal effects and measurement-derived building-block effects. Feature removal is a model calculation. [Attribution certificate](../annex_chemistry/attribution_certificate.csv).
- **Image-to-program prediction:** averaging the saved fold/seed rows in [prediction_score_summary.csv](../annex_imaging/prediction_score_summary.csv), `clip_ridge` reaches 0.1360 in `zel024_hek293`, and `mean448_mlp` reaches 0.1342 in `zel039_aec7`. They refer to compound-level joins, distinct from directly paired wells. [Imaging methods and prediction arrays](../annex_imaging/README.md).
- **Direct pairing:** 11,435 wells, 35 controls and two batches link 448 image coordinates to 32 native RNA coordinates. Selected pairing-versus-shuffle and training-size results are available in the [same-well](../annex_same_well/README.md) and [measurement-design](../annex_measurement_design/README.md) annexes. Their `D00`–`D31` RNA coordinates differ from the shared `P01`–`P32` programs. Across the 35 control means, pairwise image/RNA correlation distances have Mantel r = 0.77289 (2,000 label permutations, two-sided p = 1/2,001). [Result and resampling definitions](../annex_same_well/MANTEL_METHODS.md).

## Combinatorial design arithmetic

The largest library, `zel028`, contains **117,950 observed recipes** across its three contexts. Its union of observed per-position building blocks defines a nominal **87 × 1 × 88 × 88 = 673,728** recipe grid; observed recipes cover 17.5% of that grid. This is a combinatorial count, not a claim that every combination can be synthesized or gives a usable response. Adding one component at the 87-block position would add 7,744 nominal combinations with the other variable positions.

| Library | Observed unique recipes | Nominal library grid | Measured contexts | Nominal grid × contexts |
|---|---:|---:|---:|---:|
| `zel024` | 13,925 | 13,944 | 2 | 27,888 |
| `zel028` | 117,950 | 673,728 | 3 | 2,021,184 |
| `zel031` | 10,226 | 11,352 | 2 | 22,704 |
| `zel039` | 20,813 | 23,373 | 1 | 23,373 |

Using each library's union vocabulary in every context gives **2,095,149 nominal compound-context states**, 11.0 times the 190,699 measured profiles. The [design-space figure](../figures/measured_and_nominal_design_space.png) instead uses the vocabulary observed *within each context*, totaling **2,079,661** states. The difference is 15,488: two `zel028` contexts contain 86 rather than 87 observed blocks at the first variable position. Both calculations are valid with their denominators stated. Inputs are [recipes](../core/recipes.parquet), [context membership](../core/splits/fold_assignments.parquet), and the [per-context figure table](../figures/measured_and_nominal_design_space.csv).

## Biological interpretation

The atlas supplies 1,007 chemistry-constrained response families, with 855 carrying a significant pathway annotation. Explicit members and centroids make these associations inspectable. The filtered HSPA5-associated example has 1,512 compounds and member-half r = 0.981; its 44.54% updating-model endpoint measures recovery of a fixed high-score set. Neither response-family coherence nor genetic resemblance establishes binding or inhibition. [Atlas](../atlas/original_clusters/README.md) · [Family and learning examples](../annex_case_studies/README.md).

## Relation to complementary public resources

These resources address different measurement questions. Counts, assay units, targets and evaluation splits differ, so this table is not a performance ranking.

| Resource | Measurement emphasis | How Z-Screen complements it |
|---|---|---|
| [LINCS / CMap L1000](https://clue.io/connectopedia/what_are_landmark_genes) | Landmark transcript measurements and inferred expression for perturbation connectivity | Public recurring-component recipes linked to processed RNA surfaces and shared program coordinates |
| [PRISM Repurposing](https://depmap.org/repurposing/) | Compound effects on viability across cancer cell lines | Rich cellular-response profiles for exploring how chemical components alter state |
| [Tahoe-100M](https://doi.org/10.1101/2025.02.20.639398) | The original report describes 100 million single-cell profiles, 1,100 small-molecule perturbations and 50 cancer cell lines | Broader combinatorial recipe coverage with processed compound-context profiles; these are different measurement units |
| [JUMP Cell Painting](https://github.com/jump-cellpainting/datasets) | Public Cell Painting images and morphological profiling | RNA-linked recipe measurements, an imaging annex and a directly paired control study |
