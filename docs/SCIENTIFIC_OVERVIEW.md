# Scientific overview

What the data are, what the program layer is, and why the package is
built the way it is. Package-specific terms are defined at first use;
the full registry is `docs/terminology.json`. The design argument and
the comparison to existing atlases are in `docs/WHY_THIS_MATTERS.md`.

## The screens

Z-Screen profiles combinatorial chemistry libraries by few-cell RNA
sequencing in **nanowells**. Compounds are assembled from a fixed
vocabulary of chemical **building blocks** (BBs), so a compound is
fully described by its **recipe**: which block sits at which position
(`bb0`-`bb4`). Building blocks carry public, opaque identifiers
(`BB_##########`) throughout this package; structures are not included
(see `annex_chemistry/README.md` for the NDA path).

A **context** is one library × cell-line combination. The package
covers eight contexts:

| context | cell line | compounds |
|---|---|---:|
| zel024_hek293 | HEK293 | 13,914 |
| zel024_h1650 | H1650 | 10,686 |
| zel028_hek293 | HEK293 | 61,396 |
| zel028_a549 | A549 | 40,622 |
| zel028_h1650 | H1650 | 25,906 |
| zel031_a549 | A549 | 8,321 |
| zel031_thp1 | THP1 | 9,041 |
| zel039_aec7 | AEC7 endothelial | 20,813 |

(Row counts: `core/splits/fold_assignments.parquet`.) Because
libraries recur across cell lines, many compounds are measured in
several contexts, which is what makes cross-context analysis possible.
A named-control panel of 35 known compounds was measured alongside the
screens and is used as a validation layer in the hypothesis annex; the
same 35 compounds, with paired image and RNA latents, are in
`annex_same_well/`.

Relative to the grids the same libraries define, these screens are a
pilot. The `zel028` library is an 87 × 88 × 88 grid (673,728 recipes),
of which 117,950 are measured. Across all four libraries the design
grids × the cell lines already screened comprise about 2.1 million
compound-context states, eleven times the number of measurements
released here. That expansion, and why a new building block is the
incremental object, is developed in `docs/WHY_THIS_MATTERS.md`.

## The program layer

Each context's measured data is a compound × gene matrix. The package
summarizes every such matrix on a shared set of 32 **programs**:
coordinated gene-expression patterns, learned unsupervised (by
semi-NMF, a variant of non-negative matrix factorization in which gene
loadings are non-negative but usage coordinates are free-sign) from
the stacked screens. The 32 programs are the **shared basis**; a
compound's **usage** of a program is how strongly that program is
expressed in its response, so each compound in each context becomes a
point in a 32-number **program-usage space**.

The program layer is a design choice, not a compression convenience,
and it concentrates signal:

- Cross-context structure is 10-20× stronger in program space than
  gene by gene (the same chemistry moved to a second cell line is far
  more visible in its 32 program coordinates than in any individual
  gene).
- Building-block-level effects, the effect of one block averaged over
  all compounds carrying it, transfer across contexts at 2-3× the
  per-compound level: pooling over the recurring substructure is
  exactly what the combinatorial design is for.
- Image models and chemistry models both predict the 32 usages far
  better than they predict genes (image→programs reaches r = 0.135
  while direct image→gene prediction reaches 0.014-0.032 decoded
  mcPearson, 6-14% of the ~0.24 oracle ceiling; evidence:
  `annex_imaging/prediction_score_summary.csv`,
  `annex_imaging/decode_through_comparison.csv`).

The program layer sits on top of two measured core layers, both
included:

- **Harmonized 6,000-gene surfaces** (`core/surfaces/`): every context
  on one shared 6,000-gene panel, so cross-context modeling never
  touches per-context gene panels.
- **Program usages** (`core/usages/`): per-compound coordinates
  against the pinned shared basis (`core/basis/`,
  `shared_program_basis_v1`).

## Design choices

**Device centering.** Wells are measured in physical batches called
devices. Each profile is normalized (log1p-CP10k; see
`docs/METHODS.md`) and each device's across-compound mean profile is
subtracted. This removes the shared abundance shape and additive
device shift, and it is the optimal additive device correction for
this design.

**Per-context depth layer.** Sequencing depth couples into expression
and is handled per context. The methods used are
`within_compound_depth_standardization_v1` for `zel024_hek293` and
`zel039_aec7` (within-compound depth ladders);
`context_covariate_depth_adjustment_v1` for `zel031_a549`,
`zel028_hek293`, and `zel028_a549`; device-centered only for the
three newer contexts (`zel024_h1650`, `zel028_h1650`, `zel031_thp1`),
where across-compound RNA yield may itself be treatment biology and
no within-compound identification exists. `docs/METHODS.md` step 5
gives the mapping and rationale.

**Correction-free shared program space.** The shared basis and usages
in this package are built on the device-centered harmonized surfaces.
Depth-corrected targets reconstruct through the shared 32-program
bottleneck as well as device-centered ones, and a fold-nested
depth-regressed target variant was flat-to-worse across all
context × architecture cells (evidence:
`core/benchmark/correction_arm.csv`). Depth handling therefore lives
in the per-context target and decoder side of any downstream model;
the shared program space itself is correction-free.

**Pinned basis, held-out fold 0.** The basis is pinned by hash
(`core/basis/basis_registry.json`) and was fit on training folds 1-4
only, with fold 0 untouched by any fitting, so collaborators inherit
a clean test bed. Usage coordinates are valid only against the pinned
basis; a refit would rotate program identities.

## The imaging modality

Two libraries (`zel024`, `zel031`) were imaged by high-content
microscopy and a third (`zel039`) carries per-detection image latents
(`annex_imaging/`). Image embeddings predict the 32 program usages at
levels that survive pairing-null tests where the cell line matches
the RNA context, and the per-program variance decomposition shows
imaging is largely shared with chemistry, with a small image-only
component on stress/proteostasis programs and marker-level biology
the RNA layer does not express. All prediction dumps are fold-clean.
Details, the circularity rule (markers are targets, never features),
and the panel-difference note are in `annex_imaging/README.md`.

## The hypothesis and chemistry layers

`annex_hypotheses/` turns the program and grammar layers into tiered
leads: 16 distilled anchor leads with kill/confirm experiments, the
26-group program atlas, a sharp-SAR shortlist, and the complete
1,027-row mining ledger labeled triage-grade on its face.
`annex_chemistry/` holds the chemistry-facing results:
structure-based models generalize to never-before-synthesized
building blocks at parity with identity-based models in the deepest
context (within 0.018 in the other contexts), structure-based
attribution is validated against measurement, and three
public-identifier SAR tables enumerate candidate series and
single-block effects. Both annexes generate hypotheses;
`annex_hypotheses/HOW_TO_READ.md` is the reading guide.

## Signal strength by analysis level

Signal strength differs by analysis level; this is why the package
routes interpretation to the program and building-block levels.
Values are from the reliability audits in
`annex_imaging/reliability/` and from
`core/benchmark/program_signal_concentration.csv`:

| analysis level | typical scale | reading |
|---|---|---|
| program level (32 usages) | cross-context structure 10-20× gene space | strongest layer; headline claims live here |
| building-block level (pooled over carriers) | split-half ~0.5-0.58 | pooled, level-level claims supported |

Unsupervised structure sits at the same aggregate level: an
analog-family census finds 1,007 clusters across the eight contexts
(3-137 members, median 4), every cluster coherent at q <= 0.01
against 200 size-matched random compound sets (median coherence
z = 4.8).

Per-compound profiles are inputs to these aggregates, not standalone
calls. Additional wells on compounds that are
presently singletons move claims from brick-level toward
molecule-level; that is one of the three scaling directions in
`docs/WHY_THIS_MATTERS.md`.
