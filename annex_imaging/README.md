# Imaging Annex

Microscopy-derived features for the compound libraries in this package, plus
held-out-compound predictions that connect imaging to the shared 32-program
coordinates in `core/`.

For measured five-channel image crops linked to public recipes
and core RNA profiles, start with the [real microscopy gallery](../gallery/README.md).
It includes selected channel arrays and a deterministic
selection rule with surrounding family and crop distributions. The gallery
image metadata has no cell-line field: its link to `zel024_hek293`
is by compound and library, not evidence that the image cells are HEK293
or that those images and RNA were measured in the same well.

**Terms used throughout.** A *field of view* (FOV) is one microscope image of
one well region. A *program* is one of 32 coordinated gene-expression patterns
shared across all contexts in this package (the shared basis in
`core/basis/`); a compound's *usage* of a program is how strongly that program
is expressed in its RNA response, so each compound is a point in a 32-number
*program-usage space*. An *embedding* is a fixed-length numeric vector
summarizing an image, produced by a pretrained image model. *Pearson
correlation* (r) measures linear agreement between two measurements (0 = none,
1 = perfect). A *fold* is one of five fixed groups of compounds used for
cross-validation: every model is trained on four folds and scored on the held
out fifth, so every prediction here is for a compound the model never saw
during training.

## What is in this annex

### Per-compound tables (one row per compound)

| File | Grain | Contents |
|---|---|---|
| `zel024_compound_embeddings.parquet` | 10,129 compounds × 3,075 cols | Image embeddings for the zel024 library: 2,048 ResNet-50 dimensions (`rn50_0000`-`rn50_2047`) + 1,024 CLIP dimensions (`clip_0000`-`clip_1023`), averaged over FOVs, plus `n_fovs` / `n_panels` support counts. Key: `public_compound_id`. |
| `zel031_compound_embeddings.parquet` | 8,443 compounds × 3,075 cols | Same schema, zel031 library. |
| `zel024_compound_intensity.parquet` | 10,129 compounds × 8 cols | Marker-channel intensity means per compound (replicate-averaged): brightfield, DAPI (DNA/nuclei), p21, p62, phalloidin (actin cytoskeleton), plus support counts. Key: `public_compound_id`. |
| `zel031_compound_intensity.parquet` | 8,443 compounds × 8 cols | Same schema, zel031 marker set: BRD4, brightfield, ConA (concanavalin A, membrane/nucleolar stain), DAPI, phalloidin. |

### Per-detection table (one row per detected object)

| File | Grain | Contents |
|---|---|---|
| `zel039_imaging_latents.parquet` | 78,896 detections × 457 cols | Per-detection 448-dimensional image latents (`D0`-`D447`) for the zel039 library, with `public_compound_id` (empty for the 6,081 detections not mapped to a compound; see `mapped_to_compound_master`), the three public building-block IDs (`public_bb0_id`-`public_bb2_id`), library/cell-line context, and scan type (`scantype`: cell painting or immunofluorescent staining; `if_target` names the immunofluorescence target where applicable). 15,003 distinct compounds are covered. |

### Reliability estimates (`reliability/`)

| File | Contents |
|---|---|
| [embedding_reliability.json](reliability/embedding_reliability.json) | Split-half reliability of the per-compound embeddings: FOVs of each compound are split in two, the two half-averages are correlated across compounds, and the correlation is Spearman-Brown corrected to full-data reliability. Median centered split-half reliability is 0.40-0.43 across both libraries and both embedding backbones (50 random splits, ~1,900-2,460 deeply sampled compounds evaluated per library). |
| [marker_reliability.json](reliability/marker_reliability.json) | Split-half estimates for marker intensities: 0.43-0.59 for true marker channels (p62 0.59, phalloidin 0.53, BRD4 0.52, ConA 0.48, DAPI 0.44-0.47, p21 0.43), plus the marker-marker correlation matrix. Brightfield is near zero in zel031, as expected for a non-marker channel in those panels. |

### Fold-clean prediction dumps

`image_to_program_predictions/{context}/` and
`chemistry_to_program_predictions/{context}/` hold one `.npz` file per
fold × seed × model. Each file contains `public_compound_id`, `y_true_z`, and
`y_pred_z`: measured and predicted program usages (z-scored per program, 32
columns) for held-out test compounds only. Filenames encode feature set,
model, fold, and seed, e.g. `clip_mlp__fold2_seed1.npz`:

- Image feature sets: `clip` (CLIP embeddings), `rn50` (ResNet-50 embeddings)
  for zel024/zel031; for zel039, `cp448` (cell-painting scan latents),
  `if448` (immunofluorescence scan latents), `mean448` (their mean),
  `scantype896` (their concatenation).
- Models: `ridge` (linear ridge regression) and `mlp` (a small multi-layer
  perceptron, i.e. a two-hidden-layer neural network). The chemistry
  predictions come from a cross-attention model over the compound's building
  blocks.
- Contexts covered: zel024_hek293, zel031_a549, zel031_thp1, zel039_aec7.

`prediction_score_summary.csv` (generated from these dumps) gives the mean
per-program Pearson r of every file, the local evidence table for headline
finding 1 below, together with three decision-grade evaluation tables:
`decision_grade_image_to_program_panels.csv` (cell-level scores with
pairing-null statistics for zel024_hek293, zel031_thp1, zel031_a549),
`decision_grade_image_to_program_zel039_aec7.csv` (the 5-fold × 3-seed ×
4-variant zel039 evaluation with null floors), and
`decode_through_comparison.csv` (direct image→gene prediction vs decoding
through the 32-program bottleneck vs the oracle ceiling).

`decomposition.csv` is the per-program ownership map (128 rows: 4 contexts ×
32 programs): for each program, how much predictable variance belongs to
chemistry alone, imaging alone, both (shared), or neither, with permutation
nulls and reliability ceilings attached. It is the local evidence table for
headline finding 2.

## How this joins to `core/`

Every per-compound table keys on `public_compound_id`, the same identifier
used by `core/usages/usages_{context}_compounds.parquet` and
`core/recipes.parquet`. The prediction dumps use the same key, and their
`y_true_z` / `y_pred_z` columns are expressed in the shared 32-program
coordinates defined by `core/basis/shared_basis_k32.npy`: column *j* of a
prediction matrix is program P*j*+1 of the pinned basis. So a typical join
is: compound embeddings (this annex) → `public_compound_id` → usages (`core/`).

## Headline findings

**1. Image features predict part of the program response.** In
[prediction_score_summary.csv](prediction_score_summary.csv), the mean of
all five saved `clip_ridge` folds in `zel024_hek293` is **0.1360** per-program
Pearson r. In `zel039_aec7`, `mean448_mlp` averages **0.1342** across five
folds × three seeds. These are compound-level image-to-program evaluations.

The separate panel and variant evaluations report their own matched-pairing
nulls and test-compound sets in
[decision_grade_image_to_program_panels.csv](decision_grade_image_to_program_panels.csv)
and [decision_grade_image_to_program_zel039_aec7.csv](decision_grade_image_to_program_zel039_aec7.csv).
Use their stated units and model selections when comparing absolute scores.

The [decode-through comparison](decode_through_comparison.csv) compares
direct image-to-gene prediction, prediction through the 32-program layer,
and the usage-space oracle ceiling. Gene-level prediction is substantially
harder than predicting shared program coordinates. Related cross-modality
evaluations are described by [Haghighi et al., Nature Methods, 2022](https://doi.org/10.1038/s41592-022-01667-0);
their assays and prediction targets differ from this pilot.

Performance depends on context: the saved `clip_ridge` means are 0.0187
in `zel031_thp1` and 0.0079 in `zel031_a549`. Retain these weaker results
when assessing the transferability of image-to-RNA prediction.

**2. Chemistry and imaging share much of their program-level predictive signal.** The
per-program variance decomposition shows chemistry alone explains most
predictable usage variance (mean chemistry-only R² 0.30 in zel024_hek293,
0.09 in zel039_aec7), with smaller image-only increments
in the proteostasis/stress programs (top
image-only increments in zel024_hek293: P21 +0.0038, P16 +0.0032, P15
+0.0025, all z > 4 against permutation nulls). In zel039_aec7, imaging is
almost fully shared with chemistry. Evidence: `decomposition.csv`.

**3. Imaging tracks some marker variation not visible in RNA programs.**
Marker intensities correlate with *image-predicted* usages well beyond their
correlation with *measured* usages (e.g. p62 × P18 r = 0.139), while
chemistry-predicted usages show no such marker correlations. Imaging
carries morphology/marker-level biology that the RNA program layer does not
express. After removing the shared cell-density axis, p62 (SQSTM1, an
autophagy adaptor) keeps a specific anticorrelation with the P16
proteostasis program (-0.065 pooled, -0.091 on deeply sampled compounds).
This is the orthogonal information imaging adds, and it lives at the
morphology/marker level rather than the program-usage level.
Evidence: `marker_program_association.csv`,
`marker_program_depth_stratified.csv`.

## Marker channels and independent prediction targets

Image embeddings include marker-channel pixels. Predicting a marker
intensity from those images can recover the marker signal already present
in the input; it does not demonstrate an independent biological link.
The RNA measurements provide a separate target for image-to-program
prediction. Keep marker-recovery results distinct from prediction of RNA,
and use the stated compound or well linkage for each comparison.

## Panel note: zel024 and zel031 are different panels

The two libraries were imaged with different channel sets: p62 exists only
in the zel024 panel; BRD4 and ConA exist only in the zel031 panel.
Cross-library pooling of marker intensities or embeddings needs panel-aware
normalization (e.g. z-scoring within panel before pooling); do not treat the
two marker tables as one homogeneous matrix.

## Measurement and split definitions

- Per-FOV embeddings are averaged to the compound level. The
  [gallery](../gallery/README.md) supplies image metadata, per-crop marker
  means and two selected channel arrays. Other raw image panels and
  per-FOV embeddings require [additional input access](../docs/ANALYSIS_ACCESS.md).
- The zel039 latents table has one row per detection. Use
  `mapped_to_compound_master` to distinguish detections with public
  compound assignments.
- Prediction folds use SHA256(`public_compound_id`) mod 5, matching
  [core/splits](../core/splits/fold_assignments.parquet).
- The embedding reliability table uses at least four FOVs per evaluated
  compound and 50 random splits. `n_compounds_evaluated` records the
  subset used for each backbone’s estimates, distinct from the total
  `n_compounds` in that library.

[Completed measurement-design comparisons](../annex_measurement_design/README.md) · [Methods and input access](../docs/ANALYSIS_ACCESS.md).
