# Reference model: context-token trunk

The reference model predicts a compound's 32-dimensional program-usage vector
from its building-block recipe (`bb0`–`bb4` public BB IDs) and cellular context
(library and cell line). Three seed checkpoints support program-space inference
and comparison with the `context_token_trunk` rows in `core/benchmark/`.

## Quick start

Run from the package root with Python 3.11.14 for the pinned CPU environment:

```bash
python -m pip install numpy==2.4.6 pandas==2.3.3 pyarrow==24.0.0
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python models/predict.py --check-golden
python models/predict.py --context zel028_a549 \
    --bb1 BB_0510191033 --bb2 BB_3460866978 --bb3 BB_1895570180 --bb4 BB_8135509566
```

The package-root `environment.lock` also specifies the notebook and analysis
dependencies. CPU inference is sufficient.

The golden check evaluates 20 fixed recipes with seed 0 and an absolute tolerance
of `2e-6`. It temporarily sets PyTorch's CPU computation thread count to 12,
matching the numerical reference configuration, and restores the caller's
setting even on errors. **Twelve physical cores are not required**: the operating
system can schedule these threads across fewer cores. Ordinary predictions
retain the caller's thread setting. Since the thread count is process-wide,
run the diagnostic without concurrent inference in the same Python process.

The pinned environment passes the check when started with 1, 4 or 12 OMP/MKL
threads, with maximum absolute error below `5e-7`. Floating-point reduction order
can otherwise cause small thread-dependent differences. The strict tolerance
has not been certified for other PyTorch builds or CPU architectures.

## Supported contexts

The public inference interface supports these eight trained contexts:

`zel024_h1650`, `zel024_hek293`, `zel028_a549`, `zel028_h1650`,
`zel028_hek293`, `zel031_a549`, `zel031_thp1`, and `zel039_aec7`.

`available_contexts(checkpoint)` derives the supported list from the checkpoint's
training metadata, context-token vocabulary and valid usage normalization.
The transfer-only entry `zel031_h1650` is not a supported inference context.
Unsupported contexts produce a CLI error with available choices (exit code 2),
or a `ValueError` from `predict_program_usage(...)` before inference.

## Inputs and outputs

Each building block is represented by a 128-dimensional chemistry embedding and
a learned identity embedding. The embedding table covers 629 public BB IDs.
IDs absent from training folds use a shared unknown identity embedding while
retaining their chemistry features. Missing recipe slots are masked. An ID
without a chemistry embedding cannot be used by this interface.

`predict.py` returns two program-space vectors:

- `usage_z_scored`: the head output in per-context standardized units.
- `usage`: `usage_z_scored * sd + mu`, using the checkpoint's context-specific
  normalization; this scale is comparable to the corresponding `core/usages/`
  matrices.

The output interface is **program space**. The evaluation's per-context
gene-space decoders are not included. The shared basis
`core/basis/shared_basis_k32.npy` can map usages into its 6,000-gene representation;
this mapping is distinct from reproducing the separately decoded benchmark.

## Training and evaluation

All checkpoints hold out **fold 0** using
`SHA256(public_compound_id) mod 5`; see `core/splits/fold_assignments.parquet`.
Fold-0 compounds participate in neither training nor early stopping. The shared
program basis is also fit on folds 1–4 only. Evaluate on fold 0 when comparing
against the supplied reference.

The transformer contains eight tokens (classification, library, cell line and
five building-block slots), model width 128, four attention heads, two layers,
feed-forward width 512, dropout 0.1 and one 32-dimensional output head: 473,120
parameters. Training uses context-balanced batches across the eight supported
contexts, identity dropout 0.30, AdamW with learning rate `1e-3` and weight decay
0.01, three warmup epochs followed by cosine decay, and early-stopping patience 8.

### Relation to the benchmark tables

The supplied seed-0 and seed-1 checkpoints reproduce their corresponding
benchmark evaluation predictions. Seed 2 is a repeated training execution of
the same configuration whose GPU training trajectory differs from the seed-2
evaluation underlying the aggregate benchmark tables. Across supported contexts,
its program-space Pearson differences are −0.0058 to +0.0016 and decoded
mcPearson differences are −0.0016 to +0.0028; per-compound prediction correlations
are 0.84–0.93. Treat the three supplied checkpoints as a reference implementation,
with this seed-2 discrepancy when comparing exact aggregate benchmark numbers.

## Interpretation

- In `zel031_a549`, the trunk trails the per-context expert by about 9% relative
  in decoded mcPearson (0.0434 versus 0.0479); see
  `core/benchmark/per_context_comparison_k32.csv`.
- Predictions are meaningful against the pinned shared basis and the specified
  context. Check `core/basis/basis_registry.json` for basis identity.
- `zel028` supports pooled and building-block-level interpretation. Per-compound
  claims are not supported there; see `docs/SCIENTIFIC_OVERVIEW.md`.

## Files

- `context_token_trunk_reference_eval_v1_seed0.pt`, `_seed1.pt`, `_seed2.pt`:
  checkpoint dictionaries with parameters, architecture, training metadata,
  vocabularies and usage normalization; loaded with `weights_only=True`.
- `model_def.py`: self-contained PyTorch architecture.
- `predict.py`: CPU inference and golden check.
- `bb_embedding_table.parquet`: public BB IDs and chemistry embeddings.
- `golden_predictions.json`: fixed held-out recipes and numerical reference outputs.
