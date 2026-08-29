# Reproduction

Worked recipes for the common tasks. Everything below runs with
`numpy` + `pandas` + `pyarrow` except §3, which needs the optional `model`
extra (PyTorch, CPU is sufficient). All paths are relative to the package
root. The four notebooks in `examples/` execute these same flows end to
end.

## 1. Load usages for a context

```python
import numpy as np, pandas as pd

CTX = "zel039_aec7"
usages = np.load(f"core/usages/usages_{CTX}.npy")              # (20813, 32) float32
compounds = pd.read_parquet(f"core/usages/usages_{CTX}_compounds.parquet")
assert len(compounds) == usages.shape[0]                       # row-aligned, positional
basis = np.load("core/basis/shared_basis_k32.npy")             # (32, 6000), pinned v1
panel = pd.read_parquet("core/surfaces/harmonized_6000_genes.parquet")
# top genes of program j (0-based -> program P{j+1}):
j = 0
top = panel.iloc[np.argsort(-basis[j])[:10]]["gene"].tolist()
```

With the helper package installed (`pip install -e .`):

```python
from zscreen_program_package import data
usages, compounds = data.load_usages("zel039_aec7")
basis = data.load_basis(k=32)
```

## 2. Reproduce a benchmark number

`core/benchmark/program_space_primary.csv` reports, per context, the mean
per-program Pearson of predicted vs measured usages with a permutation
null (`null_mean`, `null_sd`) and the resulting z. The null scale is
recomputable from the shipped usages alone: shuffle the compound pairing,
compute per-program Pearson across compounds, average over the 32
programs.

```python
import numpy as np, pandas as pd

CTX = "zel039_aec7"
u = np.load(f"core/usages/usages_{CTX}.npy").astype(np.float64)
rng = np.random.default_rng(0)
stats = []
for _ in range(200):
    perm = rng.permutation(len(u))
    r = [np.corrcoef(u[:, j], u[perm, j])[0, 1] for j in range(u.shape[1])]
    stats.append(np.mean(r))
print(np.mean(stats), np.std(stats))   # compare with null_mean / null_sd
ref = pd.read_csv("core/benchmark/program_space_primary.csv")
row = ref.query("arm=='context_token_trunk' and k==32 and "
                "split_type=='compound_5fold' and context==@CTX").iloc[0]
print(row[["prog_pearson_mean", "null_mean", "null_sd", "z"]])
```

The recomputed null mean/sd will land near the published `null_mean` /
`null_sd` (same quantity, estimated independently); the published nulls
were computed per evaluation cell, so treat this as a cross-check of
scale, not a bit-exact reproduction. `examples/02_reproduce_benchmark.ipynb`
runs this and also verifies the fold rule
(SHA256(`public_compound_id`) mod 5) against
`core/splits/fold_assignments.parquet`.

## 3. Run the reference model and check golden predictions

```bash
pip install -e ".[model]"          # adds torch (CPU is sufficient)
cd models
python predict.py --check-golden   # reproduces golden_predictions.json (tolerance 2e-6)
python predict.py --context zel028_a549 \
    --bb1 BB_0510191033 --bb2 BB_3460866978 --bb3 BB_1895570180 --bb4 BB_8135509566
```

`predict.py` prints two spaces: `usage_z_scored` (the raw head output, the
per-context z-scored training space) and `usage` (mapped back to usage
units with the checkpoint's `usage_scales`; this is the scale comparable
to `core/usages/`). Program space is the model's output interface; the
per-context gene-space decoders are not shipped.

## 4. Join imaging to usages

Every per-compound imaging table keys on `public_compound_id`, the same
key as `core/usages/*_compounds.parquet`:

```python
import numpy as np, pandas as pd

CTX = "zel024_hek293"
emb = pd.read_parquet("annex_imaging/zel024_compound_embeddings.parquet")
compounds = pd.read_parquet(f"core/usages/usages_{CTX}_compounds.parquet")
usages = np.load(f"core/usages/usages_{CTX}.npy")
u = pd.DataFrame(usages, columns=[f"P{j+1:02d}" for j in range(32)])
u.insert(0, "public_compound_id", compounds["public_compound_id"])
joined = emb[["public_compound_id", "n_fovs"]].merge(u, on="public_compound_id")
```

The fold-clean dumps (`annex_imaging/image_to_program_predictions/`)
already carry `y_true_z` / `y_pred_z` in program coordinates, and
`prediction_score_summary.csv` is derived from them: recompute any row as
the mean over the 32 programs of the per-program Pearson between
`y_pred_z` and `y_true_z` in that row's NPZ. Worked example:
`examples/04_join_imaging.ipynb`.

## 5. Filter the hypothesis ledger

```python
import pandas as pd

ledger = pd.read_csv("annex_hypotheses/hypothesis_ledger_full.csv")
anchors = ledger[ledger["status"] == "hypothesis_anchor_validated"]
strong_b = ledger[(ledger["confidence_tier"] == "B")]
hsf1 = ledger[ledger["hypothesis_id"] == "ZSH-0001"]      # flagship heat-shock lead
leads = pd.read_csv("annex_hypotheses/anchor_leads.csv")  # distilled entry point,
                                                          # kill_confirm_experiment per row
```

Filter by `status` / `confidence_tier` first; the `hypothesis_triage`
rows (98.7% of the table) are raw material for re-ranking with your own
priors. Read `annex_hypotheses/README.md` and `LIMITS.md` alongside for
the weak-null rule and tier-matched null conventions.


