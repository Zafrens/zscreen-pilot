"""Recompute control-mean image/RNA correspondence from the packaged wells.

Run from any directory. Use --check to compare with the included result or
--output PATH to save a CSV. No fitted prediction model is used.
"""
from pathlib import Path
import argparse
import json
import sys

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist


def correlation_of_distances(image_means, rna_means):
    return float(np.corrcoef(pdist(image_means, metric="correlation"),
                            pdist(rna_means, metric="correlation"))[0, 1])


def calculate(wells, seed=0, permutations=2000, bootstrap_replicates=500):
    required = {"batch_id", "well_id", "control_name", "public_compound_id"}
    if not required.issubset(wells):
        raise ValueError(f"Missing metadata columns: {sorted(required - set(wells))}")
    if wells.duplicated(["batch_id", "well_id"]).any():
        raise ValueError("Each batch_id/well_id key must identify one well.")
    wells = wells.sort_values(["batch_id", "well_id", "public_compound_id"], kind="stable").reset_index(drop=True)
    image_columns = [c for c in wells if c.startswith("img_lat_")]
    rna_columns = [f"D{i:02d}" for i in range(32)]
    if len(image_columns) != 448 or not set(rna_columns).issubset(wells):
        raise ValueError("Expected 448 image coordinates and RNA D00-D31.")
    X = wells[image_columns].to_numpy(dtype=np.float64)
    Y = wells[rna_columns].to_numpy(dtype=np.float64)
    for label, array in [("image", X), ("RNA", Y)]:
        if not np.isfinite(array).all() or np.any(array.std(axis=0) == 0):
            raise ValueError(f"{label} values must be finite with nonzero coordinate variance.")
    X = (X - X.mean(axis=0)) / X.std(axis=0)
    Y = (Y - Y.mean(axis=0)) / Y.std(axis=0)
    control_names = sorted(wells.control_name.unique())
    groups = [np.flatnonzero(wells.control_name.to_numpy() == name) for name in control_names]
    if len(groups) < 3:
        raise ValueError("At least three controls are required.")
    image_means = np.stack([X[rows].mean(axis=0) for rows in groups])
    rna_means = np.stack([Y[rows].mean(axis=0) for rows in groups])
    observed = correlation_of_distances(image_means, rna_means)
    rng = np.random.default_rng(seed)
    null = np.array([correlation_of_distances(image_means[rng.permutation(len(groups))], rna_means)
                     for _ in range(permutations)])
    p = float((1 + np.count_nonzero(np.abs(null) >= abs(observed))) / (permutations + 1))
    control_boot = np.empty(bootstrap_replicates)
    for repeat in range(bootstrap_replicates):
        selected = rng.integers(0, len(groups), len(groups))
        control_boot[repeat] = correlation_of_distances(image_means[selected], rna_means[selected])
    well_boot = np.empty(bootstrap_replicates)
    for repeat in range(bootstrap_replicates):
        image_sample = np.stack([X[rows[rng.integers(0, len(rows), len(rows))]].mean(axis=0) for rows in groups])
        rna_sample = np.stack([Y[rows[rng.integers(0, len(rows), len(rows))]].mean(axis=0) for rows in groups])
        well_boot[repeat] = correlation_of_distances(image_sample, rna_sample)
    result = []
    for label, sample in [("compound_grain_35pairs", control_boot),
                          ("well_powered_mean_of_resampled_wells", well_boot)]:
        result.append({"estimate": label, "mantel_r": observed, "perm_p": p,
                       "boot_ci_lo": float(np.percentile(sample, 2.5)),
                       "boot_ci_hi": float(np.percentile(sample, 97.5)),
                       "boot_mean": float(sample.mean()), "boot_std": float(sample.std())})
    return pd.DataFrame(result), {"wells": len(wells), "controls": len(groups), "seed": seed,
                                  "permutations": permutations, "bootstrap_replicates": bootstrap_replicates}


def main():
    annex = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=annex / "same_well_wells.parquet")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--permutations", type=int, default=2000)
    parser.add_argument("--bootstrap-replicates", type=int, default=500)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if min(args.permutations, args.bootstrap_replicates) < 1:
        parser.error("Permutation and bootstrap counts must be positive.")
    result, settings = calculate(pd.read_parquet(args.input), args.seed, args.permutations, args.bootstrap_replicates)
    if args.check:
        expected = pd.read_csv(annex / "evidence/mantel_bootstrap.csv")
        if result.estimate.tolist() != expected.estimate.tolist():
            raise ValueError("Result rows differ from the included estimates.")
        if not np.allclose(result.iloc[:, 1:], expected.iloc[:, 1:], rtol=0, atol=1e-10):
            raise ValueError("Result differs from the included table; check input and randomization settings.")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(args.output, index=False, lineterminator="\n")
    print(json.dumps({"settings": settings, "verified": bool(args.check), "results": result.to_dict(orient="records")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print(f"Mantel reconstruction failed: {error}", file=sys.stderr)
        raise SystemExit(1)
