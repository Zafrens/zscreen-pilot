# Methods: raw counts to the shared program layer

Numbered procedures, in pipeline order. Method names cited as
`registered_name_v1` strings are the names of record for those
procedures; each is defined in the step that uses it.

## 1. Pseudobulk construction

Wells are pooled into **pseudobulks**: for each compound × device
combination, raw UMI counts (unique molecular identifier counts, the
per-gene molecule counts) are summed over that combination's wells. The
pseudobulk space spans 46,944 genes.

## 2. Exposure normalization

Each pseudobulk profile is normalized to log1p-CP10k: counts are scaled to
a common exposure of 10,000 per profile (counts per 10k, CP10k) and
log-transformed as log(1 + x). This puts profiles of different sequencing
depth on a comparable scale.

## 3. Per-device mean centering

A **device** is a physical measurement batch of nanowells. For each
device, the across-compound mean profile (over all profiles on that
device) is subtracted from every profile on it. This removes the shared
abundance shape and additive device shift; it is provably the optimal
additive device correction for this design. Device centering is step 3 of
the pipeline, not the final correction.

## 4. Compound means

Device-centered profiles are averaged across devices to one mean profile
per compound per context, with support metadata (well counts, depth-tier
composition) retained for the per-context analyses.

## 5. Per-context depth layer (registered lineage)

Sequencing depth couples into expression, and the correct handling differs
by what each context can identify. The registered per-context lineage:

| contexts | registered method | why |
|---|---|---|
| zel024_hek293, zel039_aec7 | `within_compound_depth_standardization_v1` | These contexts contain repeated measurements of the same compound over a meaningful depth range. Within one compound, treatment identity is fixed, so the depth slope is estimated without using between-compound biology. |
| zel031_a549, zel028_hek293, zel028_a549 | `context_covariate_depth_adjustment_v1` | No adequate within-compound depth ladder; an across-compound per-gene regression on support covariates (intercept, log1p well count, log1p UMI exposure) is the qualified adjustment there. |
| zel024_h1650, zel028_h1650, zel031_thp1 | none; device-centered only | For the three newer contexts, across-compound RNA yield may itself be treatment-associated biology and no within-compound identification exists, so no depth layer is applied. |

The depth layer belongs to the per-context analysis surfaces. The
shared program layer in this package (harmonized surfaces, basis,
usages) is built on the **device-centered** surfaces: the
depth-corrected and device-centered targets reconstruct through the
shared 32-program bottleneck equally well, and a fold-nested
depth-regressed target variant was flat-to-worse in every
context × architecture cell, so the device-centered target is
canonical here (evidence: `core/benchmark/correction_arm.csv`). Depth
handling lives in the per-context target and decoder side of
downstream models; the shared program space is correction-free.

## 6. Harmonized 6,000-gene panel

All contexts are placed on one shared gene panel of 6,000 genes, selected
by mean rank across the 8 predictive contexts from per-gene log1p-CP10k
variance rankings recomputed at full 46,944-gene width with the pipeline
estimator. The panel definition is
`core/surfaces/harmonized_6000_genes.parquet`
(`harmonized_panel_6000_v1`): `panel_position` 0–5999, `gene_index` (raw
position in the 46,944-gene space), `gene` (symbol). **Gene symbols come
only from this file**; never map panel positions through any context's
released 3,000-gene panel, which is a different index space (see
`docs/DATA_DICTIONARY.md`). Per-context harmonized surfaces
(`device_centered_harmonized_surface_v1`) are materialized from the
full-width compound-by-device pseudobulks using the pipeline-faithful
centering of step 3 (per-device means taken over all profiles on each
device).

## 7. Shared semi-NMF basis

The shared program basis (`shared_program_basis_v1`) is a semi-NMF
factorization: gene loadings W ≥ 0, shape (32, 6000), fit on the stacked,
context-scaled harmonized surfaces. Fitting was restricted to **training
folds 1–4** (fold = SHA256(`public_compound_id`) mod 5; fold 0 untouched
by any fitting), with at most 10,000 compounds sampled per context. A k =
12 companion basis (`shared_program_basis_k12_v1`) ships for
lower-resolution work; k = 32 is the shipped resolution (evidence:
`core/benchmark/k_resolution.csv`). Both bases are hash-pinned in
`core/basis/basis_registry.json`; usage coordinates are valid only against
the pinned basis.

## 8. Usage projection

Per-compound **usages** (`program_usage_projection_v1`) are the free-sign
least-squares projection of each context-scaled harmonized surface onto
the shared k = 32 basis: one 32-dimensional coordinate vector per compound
per context, shipped as `core/usages/usages_{context}.npy`. Column *j* is
program P*j*+1 of the pinned basis in every context and every derived
table in the package.

## 9. Reference model

The shipped reference model (`context_token_trunk_reference_eval_v1`,
three seeds) is a shared context-token transformer that predicts a
compound's 32-dimensional usage vector from its recipe plus context. An
8-token sequence (one classification readout token, one library token, one
cell-line token, and one token per building-block slot) is encoded by a
2-layer, 4-head transformer (d_model 128, feed-forward 512, dropout 0.1);
each building-block token combines a 128-dimensional pretrained chemistry
embedding of the block with a 64-dimensional learned identity embedding of
its public BB ID; a single shared linear head maps the classification
token to the 32 programs (473,120 parameters, deliberately no per-context
heads). Training was joint across the 8 predictive contexts with
context-balanced batches, identity-channel dropout 0.30, AdamW (lr 1e-3,
weight decay 0.01, 3-epoch warmup + cosine decay), early stopping patience
8, and **fold 0 held out** from training and early stopping. Provenance,
stated factually: the original evaluation campaign ran this exact
registered configuration but persisted only predictions and metrics; the
shipped weights are a 2026-08-15 retrain of the identical registered
configuration and code (original code sha256
`89e4059f911cfb4c60450e3b790c55d091a4b265e8dfae3b464752fa1c1d797a`; same
data snapshot, same training image, torch 2.5.1, same seeds), with
checkpoint saving as the only change. Seeds 0 and 1 reproduce the original
runs' held-out predictions bit-identically; seed 2 diverged from a one-off
nondeterministic original trajectory while two independent retrains agree
bit-identically with each other, with population metrics agreeing to
~5×10⁻³ on trained contexts. Full deltas: `models/README.md`.

## 10. Summary

Each well holds a few cells and one recipe; we count gene activity in
those cells and pool the counts per compound and measurement batch. We
then put every measurement on the same scale, subtract each batch's
average behavior so batches stop looking different, and average each
compound's repeats. Where the design allows it, we additionally correct
for how deeply each sample was sequenced, using the strongest method each
context supports. All eight screens are then placed on one shared list of
6,000 genes, and a factorization learns 32 recurring gene patterns, the
programs, that mean the same thing in every screen. Every compound's
measurement is re-expressed as 32 numbers saying how strongly it uses each
program. Finally, a small neural network learns to predict those 32
numbers from the recipe alone, so the effect of recipes never measured can
be estimated. One fixed group of compounds, fold 0, was kept untouched by
all of this fitting, so anyone can test their own models on data the
package's fitting never saw.
