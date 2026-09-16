# Same-Well Annex

A same-well control study: 35 well-known control compounds across 11,435
wells (2 batches), where each well was measured twice, once by microscopy
and once by RNA sequencing, so imaging and RNA are paired at the
individual-well grain, not just at the compound grain. This is the
package’s direct observation-level link between the two modalities.

**Terms used throughout.** A *well* is one nanowell holding cells during
measurement; a *detection* is one imaged object (cell) found in a well, so
a well can have several detections. A *latent* is a fixed-length numeric
summary produced by a learned encoder: 448 numbers per image detection,
32 numbers per well's RNA profile. A *control* is a well-known reference
compound dosed into the screen. *mcPearson* is the mean per-dimension
Pearson correlation between predicted and measured vectors (0 = none,
1 = perfect). *LOGO* is leave-one-control-out cross-validation: train on
34 controls, score on the held-out 35th. The context label for this study
is `same_well_hek293` (one cell line, HEK293).

## What is in this annex

| File | Grain | Contents |
|---|---|---|
| `same_well_wells.parquet` | 11,435 wells × 486 cols | The well-level analysis table. One row per well: `batch_id` (`batch_1`, `batch_2`), `well_id`, `public_compound_id`, `control_name`, `cell_line`, `n_detections`, the 448 image latents `img_lat_*` (mean over the well's detections), and the 32 RNA latents `D00`-`D31` (constant within a well). |
| `same_well_detections.parquet` | 14,757 detections × 486 cols | The detection-level table behind the wells table: same metadata columns plus `detection_index` (0-based within each well), with per-detection image latents. The 32 RNA latents are carried on every row (constant within a well) so the table is self-contained for detection-level work; for any well-level statistic use `same_well_wells.parquet` instead of re-aggregating. |
| `control_compound_map.csv` | 35 rows | `control_name` ↔ `public_compound_id` ↔ `public_compound_name` for the 35 controls. |
| `evidence/cross_modal_regimes.csv` | 3 rows | Image→RNA ridge predictability in three evaluation regimes (raw, within-control, across-control LOGO) with permutation-null statistics. |
| `evidence/per_control_coupling.csv` | 36 rows | Within-control image↔RNA coupling per control (PLS1 score correlation with nulls): 35 control rows plus a `GLOBAL_WITHIN_CONTROL` summary row (pooled across controls, 0.420 vs null 0.052). |
| `evidence/learning_curve.csv` | 6 rows | Cross-modal predictability vs total sampled CV-dataset wells, with null bands. |
| [evidence/mantel_bootstrap.csv](evidence/mantel_bootstrap.csv) | 2 rows | Control-mean Mantel statistic, permutation p value and two bootstrap summaries, keyed by `estimate`. |
| [MANTEL_METHODS.md](MANTEL_METHODS.md) | n/a | Statistic definition, runnable reconstruction, result-table schema and interpretation of the two resampling units. |
| [evidence/learning_curve.png](evidence/learning_curve.png) | n/a | Plot of prediction agreement versus total wells in the sampled cross-validation dataset. |
| `../annex_measurement_design/figures/same_well_learning_curve.png` | n/a | The same sample-size comparison in the measurement-design annex. |

## How to start using it

```python
import pandas as pd

wells = pd.read_parquet("annex_same_well/same_well_wells.parquet")
img_cols = [c for c in wells.columns if c.startswith("img_lat_")]   # 448
rna_cols = [f"D{i:02d}" for i in range(32)]                          # 32
X = wells[img_cols].to_numpy()
Y = wells[rna_cols].to_numpy()
```

Three things to know before analyzing:

- **The well key is (`batch_id`, `well_id`).** `well_id` is a well-position
  identifier reused across the two batches: it is unique only within a
  batch (10,872 unique `well_id` values vs 11,435 unique
  `batch_id` × `well_id` pairs). Keying on `well_id` alone silently merges
  wells from different batches.
- **Detections are not wells.** A well has 1-4 detections (mean 1.29). In
  `same_well_wells.parquet` the image latents are already the mean over
  each well's detections; treating detection rows as wells yields 14,757
  "wells" and double-counts multi-detection wells.
- **The 448 image latents are laid out as 3 × 128 + 64.** Columns
  `img_lat_0_*`, `img_lat_1_*`, `img_lat_2_*` hold 128 dimensions each and
  `img_lat_3_*` holds 64, so a scan for `img_lat_` returns exactly 448
  columns but the fourth block is truncated. The RNA latents are `D00`-`D31`.

## Headline findings

**1. Same-well measurements support image-to-RNA prediction.**
Ridge regression from the 448 image latents to the 32 RNA latents reaches
mcPearson 0.277 at the well level (5-fold, label-shuffle null
0.000 ± 0.007, p = 0.005). The signal is not just control identity: after
removing each control's mean from both modalities, within-control
well-to-well coupling remains at 0.217 (null 0.000 ± 0.006, p = 0.005),
and a fully across-control evaluation (LOGO over the 35 controls) reaches
0.238 (null -0.000 ± 0.007, p = 0.005). Evidence:
`evidence/cross_modal_regimes.csv`.

**2. Every one of the 35 controls shows significant within-control
coupling.** Per-control PLS1 score correlations between image and RNA are
significant for 35/35 controls (each at the p = 0.005 permutation floor),
median 0.557, range 0.465-0.752. Cross-modal coupling is a generic
property of perturbed wells, not a few strong controls carrying the
average. Evidence: `evidence/per_control_coupling.csv`.

**3. Control-mean image and RNA distances agree.** Across the 35 controls,
the correlation-distance Mantel statistic is **r = 0.772892** (two-sided
permutation p = 0.00049975). The compound-bootstrap interval is
[0.688, 0.895]; the within-control well-resampling interval is
[0.711, 0.778]. The latter
resamples image and RNA wells independently and keeps the controls fixed;
these intervals answer different uncertainty questions and their width or
SD ratio does not isolate a benefit caused by exact pairing.
[Results](evidence/mantel_bootstrap.csv) ·
[Method, schema and reconstruction](MANTEL_METHODS.md).

**4. The learning curve varies dataset size.** The learning curve
(ridge image→RNA, 10 resampled replicates per well count, null bands
from 50 shuffles each) shows mcPearson emerging above the null 95%
band at ~300 total sampled CV-dataset wells and reaching 0.279 in
the full 11,435-well learning-curve table. At 35 total sampled wells,
one paired point per compound, the score is -0.219, below the null
band [-0.106, 0.096]. These are sizes of the entire sampled
cross-validation dataset, not the number of training wells in each
fold. The comparison changes sample size and cannot by itself establish
that compound-level joins across plates lack signal or isolate a
causal advantage of exact pairing. The 0.277 regime estimate
and the 0.279 learning-curve mean use separate evaluation configurations.
Evidence: `evidence/learning_curve.csv` and the
[sample-size plot](../annex_measurement_design/figures/same_well_learning_curve.png).

**5. The matched comparison tests pairing at equal size.** With training-only
control/batch residualization, exact pairs reach mean held-out RNA-coordinate
r = 0.1248 at 8,000 training wells, versus 0.0007 after within-control/batch
RNA shuffling. Mean R² is 0.0029 versus -0.0309. Both arms use the same
training subsets and 2,287 correctly paired test wells. See the
[completed comparison and smaller sizes](../annex_measurement_design/README.md).

## Interpretation guidance

- **Native RNA coordinates differ from core programs.** This study's
  `D00`–`D31` are its own RNA encoder space, not the shared gene programs
  `P01`–`P32`. Never compare them coordinate by coordinate or describe
  their prediction scores as shared-program prediction.
- **Resampling units determine the question.** The Mantel comparison varies
  control identities or wells within fixed controls. The learning curve
  varies total dataset size. The matched pairing comparison holds the
  training and test wells fixed. These estimates cannot be substituted for
  one another when interpreting uncertainty or the value of exact pairing.
- **Image-latent spaces are not documented as shared across annexes.** The
  channel-level correspondence between the 448-dimensional latents in this
  annex and the 448-dimensional zel039 latents in `annex_imaging/` is not
  documented; do not concatenate, average, or transfer models between the
  two latent spaces assuming per-channel alignment. All analyses reported
  here live entirely within this annex and are unaffected.
- **This is pilot scale by design.** Thirty-five controls in one cell line
  supports a same-well measurement example: prediction, within-control
  coupling and sample-size sensitivity in this study. Conclusions about specific
  biology should be drawn from the package's deep contexts; conclusions
  about what same-well pairing buys methodologically are what this annex
  is for.

## Data representation

- Batches use the public identifiers `batch_1` and `batch_2`.
- The RNA latents are the 32-dimensional latents of the same-well assay's
  RNA measurement (`D00`-`D31`), carried inline per well.
- All matched detections are included, with no filtering on barcode match
  type or iteration counts.
