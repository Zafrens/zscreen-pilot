---
license: cc-by-4.0
pretty_name: Z-Screen Pilot
tags:
  - biology
  - chemistry
  - transcriptomics
  - drug-discovery
---

# Z-Screen Program Package

Version 1.4.2, 2026-08-29. A standalone data and reference-model
package centered on the shared program layer of the Z-Screen
combinatorial chemistry screens: per-compound 32-dimensional
program-usage vectors and harmonized 6,000-gene response surfaces
across 8 library × cell-line contexts, the pinned shared program
basis they are defined against, an evaluation-grade reference model,
and five annexes (imaging, therapeutic hypotheses, chemistry,
same-well, phenomimicry).

> **New in v1.4.2 (2026-08-29).** The phenomimicry calibration now runs
> on a 1,000-draw random-target empirical null with a hub-matched
> companion null (`validation_empirical_p.csv`: `p_emp`, `p_emp_hub`),
> target-symbol normalization widens control coverage to all 35 named
> controls (55 scored control → target pairs, adding cobimetinib →
> MAP2K1 to the recovered set), and the ranked top-100 SAR-family table
> is rebuilt on families passing every annex guardrail (non-hub target,
> validated knockdown, non-promiscuous compounds, 3–200 recipe-mates),
> ranked by CRISPR-match strength, family size, and cross-context
> replication. **If you downloaded an earlier version, re-fetch
> `annex_phenomimicry/`, `annex_hypotheses/`, and `docs/`.**
>
> **New in v1.4.1 (2026-08-29).** The CRISPR-knockout comparison has
> been expanded into a full annex, **`annex_phenomimicry/`**: every
> compound signature is now scored against 43 knockout signature sets
> from 10 public perturb-seq datasets (~18.8k target genes, ~8M
> perturbed cells), calibrated against a random-target empirical null
> (named-control pharmacology recovered across independent contexts and
> datasets, METTL3 and DOT1L inhibitor classes the strongest), with a
> per-target hub guardrail and a ranked top-100 SAR-family table. This
> replaces the previous single-atlas triage track, and the hypothesis
> ledger is correspondingly slimmer (1,027 rows).

The screens are a pilot relative to the chemical space the same
libraries can generate. The objects that scale are the building-block
grammar and the 32-program readout; that argument, and where this
release sits next to LINCS, JUMP-CP, Tahoe-100M, Recursion, and
DNA-encoded libraries, is in `docs/WHY_THIS_MATTERS.md`. Start there
or with `START_HERE.md`.

Code and documentation: https://github.com/Zafrens/zscreen-pilot  
Full package (arrays and checkpoints): https://huggingface.co/datasets/Zafrens/zscreen-pilot  
DOI: https://doi.org/10.5281/zenodo.22003566

## Layout

```
START_HERE.md               tiered entry point: model-builders top, guided readers bottom
docs/WHY_THIS_MATTERS.md    design argument, field comparison, recoverable biology
README.md                   this file
LICENSE.md                  software Apache-2.0; data and weights CC-BY-4.0
LICENSES/                   full Apache-2.0 and CC-BY-4.0 texts
NOTICE                      copyright notice (Zafrens, Inc.)
LICENSE_OR_DATA_USE.md      pointer to LICENSE.md (old name retained)
CITATION.cff                citation metadata
pyproject.toml              installable helper package (numpy/pandas/pyarrow; torch optional)
environment.lock            reference environment pins
verify.py                   one-command integrity + schema check -> src/zscreen_program_package
core/
  usages/                   per-context (compounds x 32) usage matrices + compound keys
  surfaces/                 per-context (compounds x 6,000) harmonized surfaces + panel
  basis/                    shared k=32 and k=12 bases + basis_registry.json (version pin)
  recipes.parquet           building-block grammar per public compound
  splits/                   fold_assignments.parquet (fold = SHA256(public_compound_id) mod 5)
  benchmark/                reference scores: per-context comparison, program-space primary,
                            k-resolution, correction arm, cross-context probe (+ README)
models/                     reference model (evaluation grade): 3 checkpoints, model_def.py,
                            predict.py, bb_embedding_table.parquet, golden_predictions.json
annex_imaging/              per-compound image embeddings, marker intensities, zel039 latents,
                            reliability audits, fold-clean prediction dumps, decomposition
annex_hypotheses/           anchor_leads.csv, program_atlas.csv, sharp_sar_candidates.csv,
                            hypothesis_ledger_full.csv (1,027 rows, triage-grade), LIMITS.md
annex_phenomimicry/         calibrated compound x CRISPR-KO concordance: phenomimic pair
                            tables, top-100 SAR-family list, empirical-p validation, hub flags
annex_chemistry/            novel_bb_generalization.csv, attribution_certificate.csv,
                            activity_cliffs.csv, chemotype_series.csv, bb_effect_rankings.csv
annex_same_well/            same-well control study: 11,435 wells x 35 controls with paired
                            448-d image + 32-d RNA latents per well, evidence tables, README
docs/                       WHY_THIS_MATTERS, SCIENTIFIC_OVERVIEW, METHODS, DATA_DICTIONARY,
                            REPRODUCTION, terminology.json
src/zscreen_program_package/  thin loader + verification library (no model training code)
examples/                   4 notebooks: quickstart usages, reproduce benchmark,
                            browse hypotheses, join imaging
provenance/                 file manifest (frozen at release)
```

## Two reading paths

- **Model-builders:** `START_HERE.md` top half → `core/usages/` +
  `core/basis/basis_registry.json` → `core/benchmark/` → `models/README.md`
  → `examples/01` and `examples/02`. Depth: `docs/METHODS.md`,
  `docs/DATA_DICTIONARY.md`.
- **Guided readers / discovery:** `docs/WHY_THIS_MATTERS.md` →
  `START_HERE.md` bottom half → `annex_hypotheses/README.md` →
  `annex_imaging/README.md` → `annex_same_well/README.md` →
  `annex_chemistry/README.md` → `examples/03` and `examples/04`.
  Depth: `docs/SCIENTIFIC_OVERVIEW.md`.

## Install and quickstart

The data layers need only `numpy`, `pandas`, and `pyarrow`. The
reference model additionally needs PyTorch (CPU is sufficient),
available as the `model` extra.

```bash
pip install -e .          # helper loaders + verify CLI
pip install -e ".[model]" # adds torch for models/predict.py
```

or just use pandas/pyarrow directly. With the helpers installed:

```python
from zscreen_program_package import data
usages, compounds = data.load_usages("zel039_aec7")   # (20813, 32), aligned keys
basis = data.load_basis(k=32)                         # (32, 6000), pinned v1
folds = data.load_folds()                             # context, public_compound_id, fold
```

Without installing, `src/` can be put on `sys.path` (the root
`verify.py` shim does exactly that). `docs/REPRODUCTION.md` has
worked examples.

## Verify

```bash
python verify.py           # fast: required files, schemas, shapes, ID formats
python verify.py --full    # additionally rechecks sha256 against provenance/file_manifest.csv
```

The fast check validates the row-alignment contract (every matrix
against its compounds parquet), basis shapes, usage dimension 32, the
6,000-row panel, the 1,027-row hypothesis ledger, the same-well
tables, and public-ID formats. `--full` rehashes every file once
`provenance/file_manifest.csv` is present.

## Citation and license

Cite per `CITATION.cff` (DOI [10.5281/zenodo.22003567](https://doi.org/10.5281/zenodo.22003567);
data at https://huggingface.co/datasets/Zafrens/zscreen-pilot).
Software is Apache License 2.0. Data and model weights are CC BY 4.0.
Chemical structures are not included. See `LICENSE.md`.
Contact: hello@zafrens.com.
