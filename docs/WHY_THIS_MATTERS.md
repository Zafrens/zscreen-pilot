# Why the design is worth scaling

This package is the shared program layer of a Z-Screen pilot: 190,699
compound–cell-line transcriptomes, from 162,914 combinatorial recipes, in
eight library × cell-line contexts. Relative to the chemical space the
same libraries can generate, the screens are a pilot. Their value is the
factorization they establish — reusable building-block chemistry, and a
32-program transcriptional readout defined once and used in every context —
because both make the next measurement more informative than the last.

The four libraries carry the public names `zel024`, `zel028`, `zel031`,
and `zel039`. A context is one library paired with one cell line
(HEK293, H1650, A549, THP1, or AEC7). Building blocks and compounds are
identified only by public opaque IDs (`BB_##########`, `CPD_############`);
structures are not in this folder.

## Combinatorial chemistry as a measurement grammar

A Z-Screen compound is a recipe: which building block occupies which
assembly position. Because a block recurs across thousands of recipes, its
effect can be estimated by pooling, and a model trained on measured recipes
can assign coordinates to recipes that have not been synthesized.

The largest library, `zel028`, is a grid of 87 × 88 × 88 recipes
(673,728 members; the fourth occupied slot is a singleton and does not
expand the product). This package contains 117,950 of those recipes
(17.5% of the grid) in up to three cell lines. Completing the same grid
in those three lines is 2,021,184 transcriptomes. Across all four
libraries, the design grids multiplied by the cell lines already screened
comprise 2,095,149 compound–context states, of which 190,699 are
measured — an eleven-fold expansion relative to the physical data
(`core/recipes.parquet`, `core/splits/fold_assignments.parquet`).

Adding one unused building block at the 87-member position of the
`zel028` grid produces 7,744 new recipes (the 88 × 88 partners at the
other two variable positions), or 23,232 predicted transcriptomes in the
three cell lines the reference model already treats. Where a well in a
conventional screen purchases one answer, and a DNA-encoded library
purchases binders to an isolated protein, the incremental object here
is a building block whose partners have already been observed.

## A shared 32-program coordinate system

Each measured profile is a 6,000-gene vector. The same profiles,
projected onto a shared semi-NMF basis, become 32 program-usage
coordinates (`core/usages/`, `core/basis/`). Cross-context structure is
ten- to twenty-fold stronger in that space than gene by gene
(`core/benchmark/program_signal_concentration.csv`). Building-block
effects, pooled over the compounds that carry a given block, have
split-half reliability of about 0.50–0.58; a single compound at the
present sequencing depth does not. The combinatorial design is built for
the former reading.

A 473,120-parameter transformer predicts the 32 usages from a public
recipe and a context token. On compounds held out of both basis fitting
and training, mean per-program Pearson correlation ranges from 0.105 to
0.530 across the eight training contexts (z = 6.1–28.1 against a
permutation null), and is 0.530 (z = 28.1) in the deepest context,
`zel024_hek293` (`core/benchmark/program_space_primary.csv`). The same
architecture, given chemical structure rather than building-block
identity, generalizes to blocks withheld before synthesis, at
r = 0.339 ± 0.020 in that context, against an additive embedding floor of
0.182 (`annex_chemistry/novel_bb_generalization.csv`). Removing a block
from the structure model recovers that block's measured effect at median
Spearman 0.89–0.94 (`annex_chemistry/attribution_certificate.csv`).

Published L1000 models often report Pearson correlations of 0.6–0.8 on
978 landmark genes. On a unified split, Bai, Prince and Nitschke
(bioRxiv, 2026) found that removing the drug encoder changes those
scores by at most 0.012: the models are reconstructing basal cell state.
Gene-space correlations in this package are lower (about 0.02–0.13)
because the prediction target is a treatment effect, not a cell-line
identity. The 0.53 lives in the 32-program layer the package is
organized around, and it is reported against a permutation null.

## Recovered mechanisms, and leads that can be tested

The same 32-program layer recovers mechanisms that were not supplied as
labels. The METTL3 inhibitors STM2457 and STC-15 reproduce the METTL3
knockout signature in every line tested (signed z = +8.8 to +16.1;
`annex_hypotheses/anchor_leads.csv`, ZSH-3760). Building block
`BB_2085420374`, carried by 2,294 compounds, matches the measured
heat-shock control HTH-01-015 at rank 1 (r = 0.53 against the control's
own profile; 49 of the 50 nearest neighbors carry the block). An
ER-stress sub-series is coherent at 0.79 while its 50 nearest chemical
neighbors anti-correlate (−0.33). The hypothesis annex includes sixteen
distilled leads, each with a specified kill/confirm experiment; the
mining ledger behind them has 1,027 rows and is labeled as triage
material.

## Imaging in the same coordinates

Image embeddings predict the 32 program usages at mean per-program
r = 0.135 in `zel024_hek293` and 0.1345 in `zel039_aec7`, with every
evaluated fold above a pairing null. Direct image-to-gene prediction in
the same contexts reaches 0.014–0.032, six to fourteen percent of a
~0.24 oracle ceiling; routing through the 32 programs improves that
gene-level prediction by about 50–65% (`annex_imaging/`). Haghighi et al.
(*Nat. Methods*, 2022) found 58 of 978 L1000 landmarks highly
predictable from Cell Painting across datasets. The gene-level image map
here sits in that difficult regime. The program layer is the
representation in which the images become usable.

A separate same-well study pairs 448-dimensional image latents with
32-dimensional RNA latents in 11,435 wells of 35 named controls
(`annex_same_well/`). Image-to-RNA ridge regression reaches mean
per-dimension Pearson 0.277. The same statistic at 35 wells — one paired
point per control, the grain at which image and RNA are usually joined by
compound identity across plates (Way et al., *Cell Syst.*, 2022) — falls
below the null band. The learning curve crosses the null near 300 wells
(`annex_same_well/evidence/learning_curve.png`). JUMP-CP photographed on
the order of 117,000 compounds without a transcriptome; Recursion's
public RxRx3 release contains 1,674 compounds and keeps imaging and RNA
in separate maps. Combinatorial chemistry with both modalities taken
from the same well is not, as of this writing, a public product.

## Relation to existing atlases

The relevant comparison is the measurement job, not the cell count.

| Job | Representative public resource | This pilot |
|---|---|---|
| Lookup of known drugs across many lines | LINCS L1000 (~20,000 compounds, 978 landmarks; Subramanian et al., *Cell*, 2017); PRISM (Corsello et al., 2020) | 35 named controls in eight contexts |
| Single-cell depth for virtual-cell training | Tahoe-100M (~100 million cells, a few hundred unique compounds after quality control; Zhang et al., 2025) | 190,699 profiles; not a single-cell atlas |
| Morphology at compound scale | JUMP-CP (~117,000 compounds, images only; Chandrasekaran / Weisbart et al., 2023–24); Recursion RxRx3 (1,674 compounds; Fay et al., 2023) | Imaging is an annex, informative when paired in the same well |
| Binding at very large chemical scale | DNA-encoded libraries | A different quantity: no live cell |
| Recipe → transcriptional program | — | 162,914 recipes, 6,000 genes, 32 shared programs |

Tahoe is the depth champion. This package contains two orders of
magnitude more distinct chemical entities than the Tahoe compound set
after quality control. JUMP is comparable in compound count and reports
no genes. DNA-encoded libraries are larger in molecules and silent in
cells. Almost all published chemistry-to-transcriptome models take a
finished molecule or a gene identifier as input; a public system that
tokenizes a multi-block synthetic recipe, trains across several
library × cell contexts, and emits a program-scale RNA profile is not
in the 2024–2026 literature we surveyed.

## Intended use

Fold 0 of the SHA256-mod-5 compound split was held out of basis fitting
and of reference-model training; it is the intended test set. The
32-program usages, the recipes, and the checkpoints are the objects a
model-builder needs. The hypothesis and chemistry annexes are the
objects a discovery group needs. Chemical structures are omitted; the
building-block-to-structure map is available under NDA.

The measurements that most increase the value of what is already here
are additional building blocks, additional wells on compounds that are
presently singletons, and same-well imaging on the 673,728-recipe grid.

## References

- Bai, D., Prince, E. W. & Nitschke, R. Unified evaluation of
  L1000 perturbation-response models. *bioRxiv* (15 May 2026).
- Chandrasekaran, S. N. et al. JUMP Cell Painting dataset.
  Preprint / *Nat. Methods* companion (2023–24); Weisbart, E. et al.,
  *Nat. Methods* (2024).
- Corsello, S. M. et al. Discovering the anticancer potential of
  non-oncology drugs by systematic viability profiling. *Nat. Cancer*
  (2020).
- Fay, M. M. et al. RxRx3: phenomics resource of images for 17,063
  gene knockouts and 1,674 compounds. Recursion (2023).
- Haghighi, M., Caicedo, J. C., Cimini, B. A., Carpenter, A. E. &
  Singh, S. High-dimensional gene expression and morphology profiles
  of cells across 28,000 genetic and chemical perturbations.
  *Nat. Methods* **19**, 1550–1557 (2022).
- Subramanian, A. et al. A next generation connectivity map: L1000
  platform and the first 1,000,000 profiles. *Cell* **171**,
  1437–1452 (2017).
- Way, G. P. et al. Morphology and gene expression profiling provide
  complementary information for mapping cell state. *Cell Syst.*
  **13**, 911–923 (2022).
- Zhang, J. et al. Tahoe-100M: a giga-scale single-cell perturbation
  atlas. Parse Biosciences / associated preprint (2025).
