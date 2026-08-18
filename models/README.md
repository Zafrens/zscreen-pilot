# Reference model — context-token trunk (evaluation grade)

This directory ships a **reference model, evaluation grade**: three seeds of a
shared context-token transformer trunk that predicts the 32-dimensional
program-usage vector of a compound from its building-block recipe
(`bb0`–`bb4` public BB IDs) plus a context (library + cell line). It is the
same model family reported in `core/benchmark/` (`context_token_trunk` rows).

It is provided so collaborators can (a) reproduce the reference scores in the
benchmark tables, (b) generate program-usage predictions for new recipes in
the public BB grammar, and (c) verify their environment against fixed golden
predictions. It is a reference implementation of evaluation grade.

## Files

- `context_token_trunk_reference_eval_v1_seed0.pt` / `_seed1.pt` / `_seed2.pt`
  — the three checkpoints. Each is a plain dict: `state_dict`, `architecture`,
  `training`, `vocabulary` (per-slot BB-ID vocabularies, library/cell-line
  tables, context tokens), `usage_scales` (per-context standardization), and
  `provenance`. Loads with `torch.load(..., weights_only=True)`.
- `model_def.py` — self-contained architecture definition (PyTorch only; no
  imports from anywhere else in this package or elsewhere).
- `predict.py` — CPU inference and golden-prediction self-check.
- `bb_embedding_table.parquet` — the 128-dimensional pretrained chemistry
  embedding for each public BB ID (629 rows; public IDs only, no structures).
  This is the model's input featurization for building blocks.
- `golden_predictions.json` — 20 fixed public recipes (held-out fold-0
  compounds, 5 contexts) with seed-0 predictions, for environment
  verification.

## Fold-0 convention (read before benchmarking)

All three checkpoints were trained with **fold 0 held out**
(fold = SHA256(public_compound_id) mod 5; see
`core/splits/fold_assignments.parquet`). Fold-0 compounds were never seen in
training or in early stopping. The shared program basis the usages are
defined against (`core/basis/shared_basis_k32.npy`, pinned in
`core/basis/basis_registry.json`) was likewise fit on folds 1–4 only.
**Fold 0 is the intended test bed: train on folds 1–4, evaluate on fold 0.**

## Quick start

```bash
pip install torch pandas pyarrow numpy   # CPU torch is sufficient
python predict.py --check-golden          # reproduces golden_predictions.json
python predict.py --context zel028_a549 \
    --bb1 BB_0510191033 --bb2 BB_3460866978 --bb3 BB_1895570180 --bb4 BB_8135509566
```

`predict.py` prints both output spaces:

- `usage_z_scored` — the raw head output (per-context z-scored space the
  model was trained against);
- `usage` — the same vector mapped back to usage units with the per-context
  standardization stored in the checkpoint. This is the scale comparable to
  `core/usages/`.

**Program space is the model's output interface.** The per-context
gene-space decoders used in the original evaluation are not included; to map
usages to gene space, use the pinned shared basis
(`core/basis/shared_basis_k32.npy`) or train your own decoder against the
shipped surfaces.

## Provenance

The original evaluation campaign ran this exact registered configuration on
2026-08-13/14 but did not persist model checkpoints — only predictions and
metrics. **These weights are a 2026-08-15 retrain of the identical
registered configuration and code** (original code sha256
`89e4059f911cfb4c60450e3b790c55d091a4b265e8dfae3b464752fa1c1d797a`; same
data snapshot, same training image, torch 2.5.1, same seeds), with
checkpoint saving as the only change. Each seed was verified against the
original run's preserved held-out (fold-0 test) predictions:

- **Seeds 0 and 1** reproduce the original runs exactly: per-context
  program-space Pearson and decoded mcPearson deltas are 0.0, and
  per-compound prediction correlation is 1.000000 (bit-identical
  predictions on GPU).
- **Seed 2** diverged: the *original* seed-2 run took a one-off
  GPU-nondeterministic trajectory (early stop at epoch 33 vs. 39 in the
  retrain). Two independent retrains of seed 2 are bit-identical to each
  other, so the retrain is a faithful, reproducible execution of the
  registered configuration; the original run was the outlier. Population
  metrics still agree closely: program-space Pearson deltas per context are
  −0.0058 to +0.0016 (the never-trained transfer context zel031_h1650:
  +0.021, high-variance by construction), decoded mcPearson deltas −0.0016
  to +0.0028, and per-compound prediction correlation 0.84–0.93 vs. the
  original run. The retrained seed 2 scores marginally better on its
  validation criterion than the original did.

Training architecture summary: 8 tokens (classification + library +
cell-line + 5 building-block slots), d_model 128, 4 heads, 2 layers,
feed-forward 512, dropout 0.1, single shared 32-dim head, 473,120
parameters. Trained jointly across the 8 predictive contexts with
context-balanced batches; identity-channel dropout 0.30; AdamW lr 1e-3,
wd 0.01, 3-epoch warmup + cosine decay, early stop patience 8.

## Scope of the reference model

- **zel031_a549 exception.** On this context the trunk trails the
  per-context expert model by ~9% relative (decoded gene-space mcPearson
  0.0434 vs 0.0479, compound-disjoint split; see
  `core/benchmark/per_context_comparison_k32.csv`). In the other seven
  contexts the trunk improves in six and is flat in zel024_h1650 (~3%
  relative deficit, inside the evaluation tolerance). Treat zel031_a549
  trunk predictions accordingly.
- **Vocabulary coverage.** Only BB IDs seen in the training folds are
  representable as learned identity embeddings. Unseen public BB IDs are
  still featurized (chemistry embedding) but their identity channel maps to
  a shared "unknown" row; predictions for recipes heavy in unseen BBs are
  correspondingly less specific. Absent slots (fewer than 5 blocks) are
  masked and are fully supported.
- **Output space.** Predictions are program usages against the pinned
  shared basis v1; they are only meaningful against that basis (see
  `core/basis/basis_registry.json`).
- **Scale.** zel028 contexts support pooled/level-level reads only; do not
  make per-compound claims there (see `docs/INTERPRETATION_LIMITS.md`).
