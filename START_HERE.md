# Z-Screen Program Package — Start Here

This folder contains the shared program layer of the Z-Screen pilot:
190,699 compound–cell-line transcriptomes from 162,914 combinatorial
recipes, expressed as coordinates on 32 transcriptional programs that
are defined once and used in every screen. The chemistry is assembled
from reusable building blocks (public identifiers `BB_##########`); a
compound's recipe states which block occupies which position
(`bb0`–`bb4`). A context is one library × cell-line combination. The
eight contexts are `zel024_hek293`, `zel024_h1650`, `zel028_hek293`,
`zel028_a549`, `zel028_h1650`, `zel031_a549`, `zel031_thp1`, and
`zel039_aec7` (evidence: `core/splits/fold_assignments.parquet`,
`core/recipes.parquet`).

Relative to the chemical space the same libraries can generate, these
screens are a pilot. Their value is the factorization — building-block
chemistry and a shared 32-program readout — because both make the next
measurement more informative than the last. The design argument, the
comparison to LINCS, JUMP-CP, Tahoe-100M, Recursion, and DNA-encoded
libraries, and the recoverable biology are in
`docs/WHY_THIS_MATTERS.md`.

A *program* is one of the 32 coordinated gene-expression patterns in
the shared **basis** (`core/basis/`). A compound's *usage* of a program
is the corresponding coordinate of its measured RNA response, so every
compound in every context is a point in a 32-dimensional
**program-usage space**. Compounds are partitioned into five fixed
folds (fold = SHA256(`public_compound_id`) mod 5) so that models can
be trained on four folds and scored on the held-out fifth.

---

## For model-builders

### What the universal surface is

For each of the 8 contexts, the package includes two aligned measured
layers:

- **Program usages** — `core/usages/usages_{context}.npy`: a
  (compounds × 32) matrix of per-compound usage vectors against the
  pinned shared basis `shared_program_basis_v1`
  (`core/basis/shared_basis_k32.npy`, hashes in
  `core/basis/basis_registry.json`). Column *j* is program P*j*+1 in
  every context.
- **Harmonized 6,000-gene surfaces** —
  `core/surfaces/surfaces_{context}.npy`: the same compounds as
  (compounds × 6,000) device-centered expression matrices on one
  shared gene panel (`core/surfaces/harmonized_6000_genes.parquet`).

Row *i* of every matrix is the compound named in row *i* of its
sibling `*_compounds.parquet` (the row-alignment contract; see
`docs/DATA_DICTIONARY.md`). Each compound's building-block recipe is
in `core/recipes.parquet`, keyed on `public_compound_id`.

### The fold convention: fold 0 is the test bed

Both the shared basis and the reference model were fit with **fold 0
held out** (`core/splits/fold_assignments.parquet`). Fold-0 compounds
were not seen in basis fitting, model training, or early stopping.
The intended protocol is: train on folds 1–4, evaluate on fold 0.
Usage coordinates are valid only against the pinned basis; a future
refit would rotate program identities.

### Benchmark reference scores

`core/benchmark/` reports the shared **context-token trunk** (one
model across all contexts; the checkpoints in `models/`) and
per-context expert models. On held-out compounds:

- Program-space prediction (predicted vs measured usages, mean
  per-program Pearson) is 0.105–0.530 across the eight training
  contexts, z = 6.1–28.1 against permutation nulls, and 0.530
  (z = 28.1) in `zel024_hek293` (evidence:
  `core/benchmark/program_space_primary.csv`).
- Decoded to gene space, the shared trunk improves on per-context
  experts in six of eight contexts, is within about 3% in
  `zel024_h1650`, and is lower by about 9% relative in `zel031_a549`
  (0.0434 vs 0.0479; evidence:
  `core/benchmark/per_context_comparison_k32.csv`).
- k = 32 is the released resolution; a k = 12 basis is included for
  coarser work (evidence: `core/benchmark/k_resolution.csv`).
- Cross-context transfer, including a probe into a cell line never
  used in training, is in `core/benchmark/cross_context_probe.csv`.

### The reference model

`models/` contains three seeds of the context-token trunk (a small
transformer over the recipe tokens plus library and cell-line tokens,
473,120 parameters), labeled as a reference model of evaluation
grade. It maps a public recipe plus a context to a predicted
32-dimensional usage vector. `models/golden_predictions.json` lets
an environment be checked with one command
(`python models/predict.py --check-golden`; optional `model` extra;
PyTorch CPU is sufficient). See `models/README.md`.

**First three objects:** (1) `core/usages/` with
`core/basis/basis_registry.json`, (2) `core/benchmark/` with
`core/splits/fold_assignments.parquet`, (3) `models/README.md`.
`examples/01_quickstart_usages.ipynb` and
`examples/02_reproduce_benchmark.ipynb` walk through both.

---

## For guided readers

### What the 32 programs are

The 32 programs are coordinated gene-expression patterns, learned
without labels from the measured screens, that recur across all 8
contexts. They compress each compound's 6,000-gene response into 32
coordinates, and they concentrate signal: cross-context structure is
10–20× stronger in program space than gene by gene (see
`docs/WHY_THIS_MATTERS.md` and `docs/SCIENTIFIC_OVERVIEW.md`).
`annex_hypotheses/program_atlas.csv` organizes them into 26 named
program groups (for example Myc/E2F proliferation,
translation/ribosome, heat shock) with their top genes, driving
building blocks, and anchor controls.

### Imaging

Two libraries were also imaged, and a third carries per-detection
image latents. Image embeddings predict the same 32 program usages at
a mean per-program Pearson r of 0.135 in `zel024_hek293` and 0.1345
in `zel039_aec7` — every fold × seed cell above its pairing null —
while predicting the gene surface directly reaches only 0.014–0.032
in the two deep contexts (6–14% of the ~0.24 oracle ceiling).
Decoding through the 32-program bottleneck improves on direct gene
prediction by about 50–65%: the program layer is the representation
in which the images become usable. Imaging is largely redundant with
chemistry in program space, with a small image-only component on
stress/proteostasis programs and marker-level biology the RNA layer
does not express. Evidence: `annex_imaging/README.md` and the
decision-grade tables in that annex.

### Same-well pairing

`annex_same_well/` is a control study: 35 named compounds across
11,435 wells, each well carrying both 448-dimensional image latents
and 32-dimensional RNA latents measured from that well. Image→RNA
ridge regression reaches mcPearson 0.277 (permutation p = 0.005);
within-control well-to-well coupling remains 0.217 after control
means are removed; all 35 controls show significant coupling
(median 0.557). The learning curve crosses the null near 300 wells.
A design paired only at compound grain (35 points) sits below the
null band. See `annex_same_well/README.md`.

### Control mRNA profiles

`annex_controls/` holds the measured mRNA response profiles of the 35
control compounds — the most replicated measurements in the pilot
(256,052 wells across five cell-line contexts: `zic008_a549`,
`zic008_aec7`, `zic008_h1650`, `zic008_hek293`, `zic008_hek293clone`).
Each control ships as a 6,000-gene harmonized surface, a 32-program
usage vector against the pinned basis, and a per-batch pseudobulk
replicate layer. Use it for positive-control anchoring and
reliability estimation. See `annex_controls/README.md`.

### Therapeutic hypotheses

`annex_hypotheses/` is the hypothesis layer: prioritized, tiered
leads mined from the program and grammar layers, each with its null
model and a concrete kill/confirm experiment. `anchor_leads.csv`
(16 rows) is the guided entry point, led by a heat-shock chemotype
that reproduces the measured phenotype of the control HTH-01-015 at
rank 1. Confidence tiers run A (anchor-validated, multiple
independent evidence lines) through B (strong pooled signal) to C
(triage). The complete 3,754-row mining ledger is
`hypothesis_ledger_full.csv`, labeled triage-grade on its face.
Read `annex_hypotheses/README.md` and `LIMITS.md` with the tables.

### Chemistry annex and the NDA path

`annex_chemistry/` holds the chemistry-facing results:
structure-based models generalize to never-before-synthesized
building blocks at parity with identity-based models in the deepest
context (r = 0.339 ± 0.020 in `zel024_hek293`, within 0.018 of the
identity models elsewhere; evidence:
`novel_bb_generalization.csv`), and structure-based attribution is
validated against measurement at median Spearman 0.89–0.94
(evidence: `attribution_certificate.csv`), plus three
public-identifier structure-activity tables. Actual chemical
structures are not in this package; the building-block→structure
mapping and the structure-level models are available under NDA.
See `annex_chemistry/README.md`.

**First four objects:** (1) `docs/WHY_THIS_MATTERS.md`,
(2) `annex_hypotheses/README.md`, (3) `annex_imaging/README.md`,
(4) `annex_same_well/README.md`.
`examples/03_browse_hypotheses.ipynb` and
`examples/04_join_imaging.ipynb` walk through the tables.

---

## Orientation

- `docs/WHY_THIS_MATTERS.md` — design argument, field comparison,
  recoverable biology.
- `README.md` — package layout, install, quickstart, verification.
- `docs/SCIENTIFIC_OVERVIEW.md` — the science and the design choices.
- `docs/METHODS.md` — the pipeline, step by step.
- `docs/DATA_DICTIONARY.md` — every file, column, array key, and contract.
- `docs/INTERPRETATION_LIMITS.md` — how to read each layer.
- `docs/REPRODUCTION.md` — worked reproduction recipes.
- `verify.py` — one-command integrity and schema check
  (`python verify.py`).

License: software Apache-2.0; data and weights CC BY 4.0. See
`LICENSE.md`. Cite DOI 10.5281/zenodo.22003566 (concept DOI, latest
version). Contact: hello@zafrens.com.
