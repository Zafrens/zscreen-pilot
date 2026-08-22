# Controls Annex

Measured mRNA response profiles of the 35 well-known control compounds —
the most deeply replicated measurements in the Z-Screen pilot: 256,052
wells in total, across five cell-line contexts, with every control
measured in hundreds to thousands of wells per context. Use this layer
for positive-control anchoring (the controls are named drugs with known
mechanisms), for replication-based reliability estimates, and as
reference points for the 32-program space.

A *control* is a well-known reference compound dosed into the screen.
A *pseudobulk* is the pooled profile of one control on one measurement
batch (wells summed before normalization). A *context* is one
library × cell-line combination. *Program usages* are 32-dimensional
coordinates against the pinned shared basis (`core/basis/`).

## Where these data come from

The controls were run in a dedicated controls-only library screen (every
well in that run carries one of the 35 controls), in five cell lines:
`zic008_a549`, `zic008_aec7`, `zic008_h1650`, `zic008_hek293`, and
`zic008_hek293clone`. The eight core contexts of the package
(`zel024_*` … `zel039_*`) are different library screens and contain no
control wells, which is why the controls are not rows of the `core/`
matrices and ship here as their own layer. Everything in this annex is
**measured** (derived from measurement by the same pipeline steps as
`core/`; see `docs/METHODS.md`), not predicted.

## What is in this annex

| File | Grain | Contents |
|---|---|---|
| `control_compound_map.csv` | 35 rows | `control_name` ↔ `public_compound_id` ↔ `public_compound_name`. The same mapping ships in `annex_same_well/`; copied here so the annex is self-contained. |
| `control_surfaces_{context}.npy` | 35 × 6,000 float32 | Per-control harmonized surfaces on the 6,000-gene panel: device-centered log1p-CP10k expression, one row per control, columns aligned to `core/surfaces/harmonized_6000_genes.parquet`. Same pipeline recipe and gene space as `core/surfaces/`. |
| `control_surfaces_{context}_compounds.parquet` | 35 rows | Row key for the surface matrix: `public_compound_id`, `control_name`, `n_wells`, `n_devices` (batches), `total_umis`. Row *i* of the parquet names row *i* of the `.npy` (the row-alignment contract of `core/`, applied here). |
| `control_usages_k32.parquet` | 175 rows | Per-control 32-program usages for all five contexts: `control_context`, `public_compound_id`, `control_name`, `n_wells`, `u_P01`–`u_P32`. Each control surface projected onto the pinned k = 32 basis with the same free-sign least-squares operator as `core/usages/`. |
| `control_pseudobulk_counts_{context}.npy` | (n_pseudobulks) × 6,000 float32 | The replicate layer: summed UMI counts per control × batch pseudobulk, restricted to the 6,000-gene panel. Raw summed counts, **not** normalized — normalize before use (see below). |
| `control_pseudobulks_{context}.parquet` | n_pseudobulks rows | Row key for the pseudobulk matrix: `public_compound_id`, `control_name`, `batch_id` (anonymized per context), `n_wells`, `total_umis` (summed over all 46,944 genes, so CP10k normalization is exactly reproducible from the panel counts). |

Replication per context (wells / pseudobulks / batches):

| context | wells | pseudobulks | batches |
|---|---|---|---|
| `zic008_a549` | 84,952 | 350 | 10 |
| `zic008_aec7` | 91,448 | 560 | 16 |
| `zic008_h1650` | 26,382 | 140 | 4 |
| `zic008_hek293` | 19,010 | 139 | 4 |
| `zic008_hek293clone` | 34,260 | 70 | 2 |

## How to start using it

```python
import numpy as np
import pandas as pd

surf = np.load("annex_controls/control_surfaces_zic008_aec7.npy")   # (35, 6000)
keys = pd.read_parquet("annex_controls/control_surfaces_zic008_aec7_compounds.parquet")
usages = pd.read_parquet("annex_controls/control_usages_k32.parquet")  # 175 x 32
panel = pd.read_parquet("core/surfaces/harmonized_6000_genes.parquet")

# pseudobulk replicates, normalized the package way (log1p-CP10k):
counts = np.load("annex_controls/control_pseudobulk_counts_zic008_aec7.npy")
pb = pd.read_parquet("annex_controls/control_pseudobulks_zic008_aec7.parquet")
L = np.log1p(counts / pb["total_umis"].to_numpy()[:, None] * 1e4)
```

With the helper package installed (`pip install -e .`),
`data.load_control_surface(context)`, `data.load_control_pseudobulks(context)`,
and `data.load_control_usages()` wrap exactly these reads.

## Three things to know before analyzing

- **Controls were never used in any fitting.** The shared basis was fit
  on training folds 1–4 of the library compounds only, and the reference
  model was fit the same way. The controls are an untouched, independent
  measurement set; the fold-0 test-bed convention
  (`docs/DATA_DICTIONARY.md`) is unaffected.
- **The replicate unit is the pseudobulk, not the well.** Pseudobulk
  counts are summed over each control × batch's wells and carry
  full-width `total_umis`, so log1p-CP10k and any batch-centering
  variant are exactly reproducible. `batch_id` is anonymized within each
  context (`batch_01`, `batch_02`, …) and is not comparable across
  contexts. `zic008_hek293clone` has only 2 batches; batch-level
  statistics there are thin even though well counts are deep.
- **Centering is within the controls-only run.** Per-batch centering
  subtracts each batch's mean over that run's profiles — because the run
  contained only the 35 controls, that mean is a control-population
  mean. This is the same recipe as `core/` surfaces applied to the
  controls-only run, but the centering population differs from the
  library screens; keep that in mind when putting control and library
  profiles in one scatter. Control usages are likewise the direct
  basis projection of the control surfaces; the per-context scale
  factors of the eight core contexts have no counterpart for the
  control run, so compare usages across layers by correlation, not by
  absolute coordinate.

## Relationship to `annex_same_well/`

The same-well annex profiles the same 35 controls in HEK293 with paired
microscopy: 448-dimensional image latents and 32-dimensional RNA latents
per well. Its RNA latents (`D00`–`D31`) are the same-well assay's own
encoder space, **not** the 32-program usages in this annex; the two
32-dimensional spaces must not be concatenated or compared coordinate by
coordinate. This annex adds the gene-level view (6,000-gene surfaces and
their program projections) and the four other cell lines.

## Validation anchors

- The usage projection operator reproduces a shipped core usage matrix
  from its shipped surface exactly (per-program Pearson 1.0), and the
  control surfaces reproduce the internal control-surface build at
  per-control Pearson 1.000000 in all five contexts.
- The control usages carry the expected biology: HTH-01-015, the
  heat-shock anchor used in `annex_hypotheses/`, loads the heat-shock
  program (P16) at z ≈ +2 among the 35 controls in `zic008_aec7`.
- Basis coverage is complete: the control surfaces are observed on all
  6,000 panel genes, so the projection uses the full basis loading mass
  in every control context.

## Interpretation guidance

- Thirty-five controls × five contexts is a positive-control layer, not
  a library-scale screen: use it for anchoring, reliability estimation,
  and method calibration, and draw compound-discovery conclusions from
  the `core/` contexts.
- Program-space structure is the strongest analysis level here too;
  single-program single-control calls in one context are triage-grade.
- As everywhere in the package, usage column *j* is program P*j*+1 of
  the pinned basis (`core/basis/basis_registry.json`).

## Provenance notes

- Well-level UMI counts were pooled per control × batch, normalized to
  log1p-CP10k, batch-centered, and averaged per control with capped
  square-root well-count weights (cap 20 wells) — steps 1–4 of
  `docs/METHODS.md` applied to the controls-only run, then restricted to
  the harmonized 6,000-gene panel. No depth-correction layer is applied
  (the shared program layer is correction-free; METHODS step 5).
- All 256,052 control wells in the run are included; no wells were
  excluded beyond the package-wide public-identifier mapping.
- Chemical structures are not included (identifier policy:
  `LICENSE.md` and `docs/DATA_DICTIONARY.md`).
