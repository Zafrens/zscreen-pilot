# Imaging Annex

Microscopy-derived features for the compound libraries in this package, plus
fold-clean test predictions that connect imaging to the shared 32-program
coordinates in `core/`.

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
| `zel024_compound_embeddings.parquet` | 10,129 compounds × 3,075 cols | Image embeddings for the zel024 library: 2,048 ResNet-50 dimensions (`rn50_0000`–`rn50_2047`) + 1,024 CLIP dimensions (`clip_0000`–`clip_1023`), averaged over FOVs, plus `n_fovs` / `n_panels` support counts. Key: `public_compound_id`. |
| `zel031_compound_embeddings.parquet` | 8,443 compounds × 3,075 cols | Same schema, zel031 library. |
| `zel024_compound_intensity.parquet` | 10,129 compounds × 8 cols | Marker-channel intensity means per compound (replicate-averaged): brightfield, DAPI (DNA/nuclei), p21, p62, phalloidin (actin cytoskeleton), plus support counts. Key: `public_compound_id`. |
| `zel031_compound_intensity.parquet` | 8,443 compounds × 8 cols | Same schema, zel031 marker set: BRD4, brightfield, ConA (concanavalin A, membrane/nucleolar stain), DAPI, phalloidin. |

### Per-detection table (one row per detected object)

| File | Grain | Contents |
|---|---|---|
| `zel039_imaging_latents.parquet` | 78,896 detections × 457 cols | Per-detection 448-dimensional image latents (`D0`–`D447`) for the zel039 library, with `public_compound_id` (empty for the 6,081 detections not mapped to a compound; see `mapped_to_compound_master`), the three public building-block IDs (`public_bb0_id`–`public_bb2_id`), library/cell-line context, and scan type (`scantype`: cell painting or immunofluorescent staining; `if_target` names the immunofluorescence target where applicable). 15,003 distinct compounds are covered. |

### Reliability audits (`reliability/`)

| File | Contents |
|---|---|
| `embedding_reliability_audit.json` | Split-half reliability of the per-compound embeddings: FOVs of each compound are split in two, the two half-averages are correlated across compounds, and the correlation is Spearman-Brown corrected to full-data reliability. Median centered split-half reliability is 0.40–0.43 across both libraries and both embedding backbones (50 random splits, ~1,900–2,460 deeply sampled compounds audited per library). |
| `marker_reliability_audit.json` | Same audit for marker intensities: 0.43–0.59 for true marker channels (p62 0.59, phalloidin 0.53, BRD4 0.52, ConA 0.48, DAPI 0.44–0.47, p21 0.43), plus the marker–marker correlation matrix. Brightfield is near zero in zel031, as expected for a non-marker channel in those panels. |

### Fold-clean prediction dumps

`image_to_program_predictions/{context}/` and
`chemistry_to_program_predictions/{context}/` hold one `.npz` file per
fold × seed × model. Each file contains `public_compound_id`, `y_true_z`, and
`y_pred_z` — measured and predicted program usages (z-scored per program, 32
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
per-program Pearson r of every file — the local evidence table for headline
finding 1 below, together with three decision-grade evaluation tables:
`decision_grade_image_to_program_panels.csv` (cell-level scores with
pairing-null statistics for zel024_hek293, zel031_thp1, zel031_a549),
`decision_grade_image_to_program_zel039_aec7.csv` (the 5-fold × 3-seed ×
4-variant zel039 evaluation with null floors), and
`decode_through_comparison.csv` (direct image→gene prediction vs decoding
through the 32-program bottleneck vs the oracle ceiling).

`decomposition.csv` is the per-program ownership map (128 rows: 4 contexts ×
32 programs): for each program, how much predictable variance belongs to
chemistry alone, imaging alone, both (shared), or neither — with permutation
nulls and reliability ceilings attached. It is the local evidence table for
headline finding 2.

## How this joins to `core/`

Every per-compound table keys on `public_compound_id`, the same identifier
used by `core/usages/usages_{context}_compounds.parquet` and
`core/recipes.parquet`. The prediction dumps use the same key, and their
`y_true_z` / `y_pred_z` columns are expressed in the shared 32-program
coordinates defined by `core/basis/shared_basis_k32.npy` — column *j* of a
prediction matrix is program P*j*+1 of the pinned basis. So a typical join
is: compound embeddings (this annex) → `public_compound_id` → usages (`core/`).

## Headline findings

**1. Image embeddings predict the 32 program usages; the program layer
is the representation in which the images become usable.** Predicting
program usages from image embeddings reaches a mean per-program Pearson
r of 0.135 in zel024_hek293 (CLIP + ridge, clean folds 1–4 of the
per-compound dumps; every fold × seed cell of the panel evaluation sits
above its pairing null, i.e. the correlation obtained after shuffling
the compound↔image pairing) and 0.1345 in zel039_aec7 (best model
variant, mean over 5 folds × 3 seeds; all 60 fold × seed × variant
cells above their nulls; the dumps reproduce 0.103–0.127 clean-fold
means on the scantype-matched compound universe). Predicting the gene
surface directly from images, without the program layer, reaches only
0.014–0.032 decoded mcPearson in the two deep contexts — 6–14% of the
~0.24 oracle ceiling — while decoding through the 32-program bottleneck
improves on direct prediction by ~50–65%. Haghighi et al. (*Nat.
Methods*, 2022) found 58 of 978 L1000 landmarks highly predictable from
Cell Painting across datasets; the gene-level image map here sits in
that difficult regime. Signal requires the matched cell line:
zel031_thp1 is weakly real (~0.019) and zel031_a549 is a documented
null (≤ 0.012). Evidence: `prediction_score_summary.csv`,
`decision_grade_image_to_program_panels.csv`,
`decision_grade_image_to_program_zel039_aec7.csv`,
`decode_through_comparison.csv`.

**2. Imaging is ~96% redundant with chemistry in program space — with a
small, real image-only component on stress/proteostasis programs.** The
per-program variance decomposition shows chemistry alone explains most
predictable usage variance (mean chemistry-only R² 0.30 in zel024_hek293,
0.09 in zel039_aec7), while the image-only sliver is small but significant
exactly where biology would put it: the proteostasis/stress programs (top
image-only increments in zel024_hek293: P21 +0.0038, P16 +0.0032, P15
+0.0025, all z > 4 against permutation nulls). In zel039_aec7, imaging is
almost fully shared with chemistry. Evidence: `decomposition.csv`.

**3. Imaging tracks some marker variation not visible in RNA programs.**
Marker intensities correlate with *image-predicted* usages well beyond their
correlation with *measured* usages (e.g. p62 × P18 r = 0.139), while
chemistry-predicted usages show no such marker correlations — imaging
carries morphology/marker-level biology that the RNA program layer does not
express. After removing the shared cell-density axis, p62 (SQSTM1, an
autophagy adaptor) keeps a specific anticorrelation with the P16
proteostasis program (−0.065 pooled, −0.091 on deeply sampled compounds).
This is the orthogonal information imaging adds, and it lives at the
morphology/marker level rather than the program-usage level.
Evidence: `marker_program_association.csv`,
`marker_program_depth_stratified.csv`.

## Usage guidance: markers are targets, never features (circularity note)

The pixels used to compute the embeddings and latents **include the marker
channels**. Any model that takes embeddings as input features and predicts
marker intensities can therefore succeed by reading the marker pixels
directly — a circular measurement, not biology. The safe direction is the
one used throughout this package: **marker values may only ever be
prediction targets, never input features.** Predicting RNA program usages
from embeddings is not circular (the RNA measurement shares no pixels with
the images).

## Panel note: zel024 and zel031 are different panels

The two libraries were imaged with different channel sets: p62 exists only
in the zel024 panel; BRD4 and ConA exist only in the zel031 panel.
Cross-library pooling of marker intensities or embeddings needs panel-aware
normalization (e.g. z-scoring within panel before pooling); do not treat the
two marker tables as one homogeneous matrix.

## Provenance notes

- Per-FOV embeddings were aggregated to compound level before shipping;
  per-FOV and per-crop raw tables are **available on request**, not in this
  package.
- The zel039 latents table is at detection grain; raw image filename,
  detection ID, and device name were removed before release.
- All prediction dumps are fold-clean: fold assignment is
  SHA256(`public_compound_id`) mod 5, identical to `core/splits/`.
- Two smoke-test prediction files (tiny sanity-check runs) were excluded.
