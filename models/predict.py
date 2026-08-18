"""CPU inference for the context-token trunk reference model.

Takes a recipe (bb0..bb4 public building-block IDs, null/absent allowed)
plus a context name, and outputs the 32-dimensional program-usage
prediction. Program space is the model's output interface: the per-context
gene-space decoders used in the original evaluation are not included.

Output spaces
-------------
``usage_z_scored`` is the raw head output (the per-context z-scored space
the model was trained against). ``usage`` maps it back to usage units with
the per-context standardization stored in the checkpoint
(``usage = usage_z_scored * sd + mu``), which is the scale comparable to
``core/usages/``.

Usage (CLI):
    python predict.py --context zel028_a549 \
        --bb1 BB_0510191033 --bb2 BB_3460866978 --bb3 BB_1895570180 \
        --bb4 BB_8135509566
    python predict.py --check-golden

Usage (library):
    from predict import load_reference_model, predict_program_usage
    model, ckpt, bb_vec = load_reference_model("path/to/models", seed=0)
    out = predict_program_usage(model, ckpt, bb_vec, "zel028_a549",
                                {"bb1": "BB_0510191033", ...})
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

from model_def import BB_SLOTS, N_BB_SLOTS, build_from_checkpoint

MODEL_FILE_TEMPLATE = "context_token_trunk_reference_eval_v1_seed{seed}.pt"
BB_TABLE_FILE = "bb_embedding_table.parquet"
GOLDEN_FILE = "golden_predictions.json"

PAD_INDEX = 0  # absent slot
UNK_INDEX = 1  # building-block ID not seen in the training folds


def load_reference_model(models_dir: str | Path, seed: int = 0):
    """Load checkpoint + BB embedding table. Returns (model, checkpoint,
    bb_vec) where bb_vec maps public BB ID -> float32 (128,) vector."""
    models_dir = Path(models_dir)
    ckpt_path = models_dir / MODEL_FILE_TEMPLATE.format(seed=seed)
    # Shipped checkpoints contain only tensors and plain Python scalars, so
    # weights_only=True must always succeed; fail loudly rather than falling
    # back to unrestricted pickle loading.
    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    model = build_from_checkpoint(checkpoint)
    import pandas as pd
    table = pd.read_parquet(models_dir / BB_TABLE_FILE)
    ecols = [c for c in table.columns if c.startswith("embedding_")]
    bb_vec = dict(zip(table["public_bb_id"].astype(str),
                      table[ecols].to_numpy(np.float32)))
    return model, checkpoint, bb_vec


def _recipe_arrays(checkpoint, bb_vec, recipes: list[dict]):
    """Build (chemistry, identity_index, present) for a batch of recipes."""
    level_to_index = checkpoint["vocabulary"]["level_to_index"]
    n = len(recipes)
    chemistry = np.zeros((n, N_BB_SLOTS, 128), dtype=np.float32)
    identity_index = np.zeros((n, N_BB_SLOTS), dtype=np.int64)
    present = np.zeros((n, N_BB_SLOTS), dtype=bool)
    for ri, recipe in enumerate(recipes):
        for si, slot in enumerate(BB_SLOTS):
            bb_id = recipe.get(slot)
            if bb_id is None or (isinstance(bb_id, float) and np.isnan(bb_id)):
                continue  # absent slot: PAD token, masked out
            bb_id = str(bb_id)
            vec = bb_vec.get(bb_id)
            if vec is None:
                raise KeyError(
                    f"{slot}: {bb_id} has no chemistry embedding in "
                    f"{BB_TABLE_FILE}")
            chemistry[ri, si] = vec
            # IDs not seen in the training folds map to UNK (still usable).
            identity_index[ri, si] = level_to_index[si].get(bb_id, UNK_INDEX)
            present[ri, si] = True
    return chemistry, identity_index, present


@torch.no_grad()
def predict_program_usage(model, checkpoint, bb_vec, context: str,
                          recipes: list[dict] | dict) -> dict:
    """Predict 32-dim program usage for one recipe or a list of recipes.

    Returns {"context": ..., "usage_z_scored": (n, 32), "usage": (n, 32)}
    with numpy arrays.
    """
    single = isinstance(recipes, dict)
    if single:
        recipes = [recipes]
    context_tokens = checkpoint["vocabulary"]["context_tokens"]
    if context not in context_tokens:
        raise KeyError(f"unknown context {context!r}; available: "
                       f"{sorted(context_tokens)}")
    meta = context_tokens[context]
    vocab = checkpoint["vocabulary"]
    library_index = vocab["libraries"].index(meta["library"])
    cell_line_index = vocab["cell_lines"].index(meta["cell_line"])
    chemistry, identity_index, present = _recipe_arrays(
        checkpoint, bb_vec, recipes)
    z = model.forward_context(
        torch.from_numpy(chemistry), torch.from_numpy(identity_index),
        torch.from_numpy(present), library_index, cell_line_index,
        identity_dropout=0.0).numpy().astype(np.float64)
    scales = checkpoint["usage_scales"][context]
    mu = np.asarray(scales["mu"], dtype=np.float64)
    sd = np.asarray(scales["sd"], dtype=np.float64)
    usage = z * sd + mu
    if single:
        return {"context": context, "usage_z_scored": z[0], "usage": usage[0]}
    return {"context": context, "usage_z_scored": z, "usage": usage}


def check_golden(models_dir: str | Path) -> bool:
    """Reproduce golden_predictions.json with the shipped seed-0 checkpoint."""
    models_dir = Path(models_dir)
    golden = json.loads((models_dir / GOLDEN_FILE).read_text())
    tolerance = float(golden.get("tolerance", 2e-6))
    model, checkpoint, bb_vec = load_reference_model(
        models_dir, seed=int(golden["seed"]))
    ok = True
    for entry in golden["entries"]:
        out = predict_program_usage(model, checkpoint, bb_vec,
                                    entry["context"], entry["recipe"])
        for key in ("usage_z_scored", "usage"):
            expected = np.asarray(entry["prediction_" + key],
                                  dtype=np.float64)
            diff = float(np.abs(out[key] - expected).max())
            if diff > tolerance:
                ok = False
                print(f"MISMATCH {entry['context']} {entry['recipe']} {key}: "
                      f"max abs diff {diff:.3e}")
    print(f"golden predictions: {'OK' if ok else 'FAILED'} "
          f"({len(golden['entries'])} entries, tolerance {tolerance})")
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models-dir", default=str(Path(__file__).parent))
    parser.add_argument("--seed", type=int, default=0, choices=(0, 1, 2))
    parser.add_argument("--context")
    for slot in BB_SLOTS:
        parser.add_argument(f"--{slot}", default=None)
    parser.add_argument("--check-golden", action="store_true")
    args = parser.parse_args()
    if args.check_golden:
        sys.exit(0 if check_golden(args.models_dir) else 1)
    if not args.context:
        parser.error("--context is required (or use --check-golden)")
    model, checkpoint, bb_vec = load_reference_model(args.models_dir,
                                                     seed=args.seed)
    recipe = {slot: getattr(args, slot) for slot in BB_SLOTS}
    out = predict_program_usage(model, checkpoint, bb_vec, args.context,
                                recipe)
    print(json.dumps({
        "context": out["context"],
        "seed": args.seed,
        "usage_z_scored": [round(float(v), 6) for v in out["usage_z_scored"]],
        "usage": [round(float(v), 6) for v in out["usage"]],
    }, indent=2))


if __name__ == "__main__":
    main()
