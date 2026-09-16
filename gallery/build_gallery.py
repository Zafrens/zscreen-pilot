"""Select and render the gallery from public metadata and preserved raw crops.

Selection is deterministic and uses the frozen JSON rules. The full source
microscopy archive is unnecessary once the selected raw crop arrays are
exported. This script renders measurements; it does not synthesize images.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def select_examples(root: Path, output: Path) -> pd.DataFrame:
    gallery = root / "gallery"
    settings = json.loads((gallery / "config.json").read_text(encoding="utf-8"))
    context = settings["linked_rna_context"]
    ids = pd.read_parquet(root / f"core/usages/usages_{context}_compounds.parquet")
    raw_usages = np.load(root / f"core/usages/usages_{context}.npy", allow_pickle=False).astype(np.float64)
    recipes = pd.read_parquet(root / "core/recipes.parquet")
    meta = pd.read_parquet(gallery / "data/fov_metadata.parquet")
    markers = pd.read_parquet(gallery / "data/crop_marker_intensities.parquet")
    if len(meta) != 10661 or meta.hdf5_dim_0_index.duplicated().any():
        raise ValueError("Unexpected ZS13 metadata")
    merged = meta.merge(markers, on=["panel", "hdf5_dim_0_index"], validate="one_to_one")
    valid = merged.loc[(merged.panel == settings["source_panel"]) & ~merged.is_control
                       & ~merged.is_censored & merged.mapped_to_compound_master
                       & (merged.n_cells > 0)].copy()
    marker_columns = settings["marker_columns"]
    valid = valid.loc[np.isfinite(valid[marker_columns]).all(axis=1)
                      & (valid[marker_columns] >= 0).all(axis=1)].copy()
    # Link to the selected RNA context without assigning its cell line to the images.
    joined = ids.merge(recipes, on="public_compound_id", how="left", validate="one_to_one")
    if joined.bb0.isna().any() or len(joined) != len(raw_usages):
        raise ValueError("Missing recipe or broken RNA row alignment")
    valid = valid.merge(joined, on="public_compound_id", how="inner", validate="many_to_one")
    for position in range(4):
        source_col, recipe_col = f"public_bb{position}_id", f"bb{position}"
        mismatch = valid[source_col].fillna("").astype(str) != valid[recipe_col].fillna("").astype(str)
        if mismatch.any():
            raise ValueError(f"Public FOV/core recipe mismatch at {recipe_col}")
    support = valid.groupby("public_compound_id").size()
    joined["valid_zs13_crops"] = joined.public_compound_id.map(support).fillna(0).astype(int)
    center, scale = np.median(raw_usages, axis=0), raw_usages.std(axis=0)
    if (scale <= 0).any():
        raise ValueError("Constant program column")
    standardized = (raw_usages - center) / scale
    candidates = joined.valid_zs13_crops >= settings["minimum_valid_crops_per_representative"]
    summaries, members = [], {}
    for position in (f"bb{i}" for i in range(5)):
        for block, group in joined.groupby(position, dropna=True, sort=True):
            idx = group.index.to_numpy()
            n_candidates = int(candidates.loc[idx].sum())
            median = np.median(standardized[idx], axis=0)
            eligible = (len(idx) >= settings["minimum_core_family_compounds"]
                        and n_candidates >= settings["minimum_representative_candidates_per_family"])
            summaries.append({"position": position, "public_building_block_id": block,
                              "core_compounds": len(idx), "imaged_representative_candidates": n_candidates,
                              "standardized_median_response_norm": float(np.linalg.norm(median)), "eligible": eligible})
            members[(position, block)] = (idx, median)
    ranking = pd.DataFrame(summaries)
    eligible = ranking[ranking.eligible].sort_values(
        ["standardized_median_response_norm", "position", "public_building_block_id"],
        ascending=[False, True, True], kind="stable")
    if eligible.empty:
        raise ValueError("No family passes the frozen gallery support thresholds")
    high = eligible.iloc[0]
    comparator_rows = eligible[(eligible.position == high.position)
                               & (eligible.public_building_block_id != high.public_building_block_id)]
    if comparator_rows.empty:
        raise ValueError("No eligible comparator at the selected position")
    low = comparator_rows.sort_values(["standardized_median_response_norm", "public_building_block_id"],
                                     kind="stable").iloc[0]
    panel_markers = np.log1p(valid[marker_columns].to_numpy(dtype=np.float64))
    marker_scale = np.percentile(panel_markers, 75, axis=0) - np.percentile(panel_markers, 25, axis=0)
    marker_scale[marker_scale < 1e-12] = 1.0
    selected_rows, member_rows, response_rows, crop_rows = [], [], [], []
    for role, family in (("response_family", high), ("comparator_family", low)):
        idx, median = members[(family.position, family.public_building_block_id)]
        available = idx[candidates.loc[idx].to_numpy()]
        distances = np.linalg.norm(standardized[available] - median, axis=1)
        possible = pd.DataFrame({"row": available, "distance": distances,
                                 "public_compound_id": joined.loc[available, "public_compound_id"].to_numpy()})
        winner = possible.sort_values(["distance", "public_compound_id"], kind="stable").iloc[0]
        row = int(winner.row)
        compound = str(joined.loc[row, "public_compound_id"])
        own = valid[valid.public_compound_id == compound].copy()
        marker_vectors = np.log1p(own[marker_columns].to_numpy(dtype=np.float64)) / marker_scale
        crop_distances = np.linalg.norm(marker_vectors - np.median(marker_vectors, axis=0), axis=1)
        own["distance_to_own_marker_median"] = crop_distances
        crop = own.sort_values(["distance_to_own_marker_median", "hdf5_dim_0_index"], kind="stable").iloc[0]
        selected_rows.append({"role": role, "position": family.position,
                              "family_building_block_id": family.public_building_block_id,
                              "public_compound_id": compound, "rna_context": context,
                              "source_panel": settings["source_panel"],
                              "hdf5_dim_0_index": int(crop.hdf5_dim_0_index),
                              "valid_crops_for_compound": len(own), "segmented_cells_in_crop": int(crop.n_cells),
                              "rna_distance_to_family_median": float(winner.distance),
                              "crop_distance_to_marker_median": float(crop.distance_to_own_marker_median),
                              "family_core_compounds": int(family.core_compounds),
                              "family_representative_candidates": int(family.imaged_representative_candidates),
                              "family_response_norm": float(family.standardized_median_response_norm)})
        for i in idx:
            member_rows.append({"role": role, "public_compound_id": joined.loc[i, "public_compound_id"],
                                "valid_zs13_crops": int(joined.loc[i, "valid_zs13_crops"]),
                                "distance_to_family_median": float(np.linalg.norm(standardized[i] - median)),
                                "standardized_response_norm": float(np.linalg.norm(standardized[i])),
                                "eligible_as_representative": bool(candidates.loc[i]),
                                "chosen": i == row})
        for i, col in enumerate(f"P{j:02d}" for j in range(1, 33)):
            response_rows.append({"role": role, "public_compound_id": compound, "program": col,
                                  "raw_core_usage": float(raw_usages[row, i]),
                                  "standardized_core_usage": float(standardized[row, i]),
                                  "standardized_family_median": float(median[i]),
                                  "context_program_median": float(center[i]),
                                  "context_program_standard_deviation": float(scale[i])})
        crop_rows.extend(own[["public_compound_id", "hdf5_dim_0_index", "n_cells",
                             "distance_to_own_marker_median"] + marker_columns].to_dict("records"))
    output.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(output / "family_selection_scores.csv", index=False)
    pd.DataFrame(member_rows).to_csv(output / "selected_family_distribution.csv", index=False)
    pd.DataFrame(response_rows).to_csv(output / "linked_programs.csv", index=False)
    pd.DataFrame(crop_rows).to_csv(output / "representative_crop_candidates.csv", index=False)
    selected = pd.DataFrame(selected_rows)
    selected.to_csv(output / "selected_examples.csv", index=False)
    return selected


def render(root: Path, output: Path, selected: pd.DataFrame) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    gallery = root / "gallery"
    settings = json.loads((gallery / "config.json").read_text(encoding="utf-8"))
    registry = json.loads((gallery / "data/raw_crop_registry.json").read_text(encoding="utf-8"))
    raw = []
    for row in selected.itertuples(index=False):
        entry = next(x for x in registry["crops"] if x["public_compound_id"] == row.public_compound_id
                     and x["hdf5_dim_0_index"] == row.hdf5_dim_0_index)
        path = gallery / entry["array_path"]
        if sha256(path) != entry["file_sha256"]:
            raise ValueError("A preserved raw crop has changed")
        array = np.load(path, allow_pickle=False)
        if array.dtype != np.dtype("float32") or array.shape != (5, 340, 340):
            raise ValueError("Unexpected raw crop array")
        if hashlib.sha256(array.tobytes(order="C")).hexdigest() != entry["raw_values_sha256"]:
            raise ValueError("Raw pixel values do not match the registered array")
        raw.append(array)
    values = np.stack(raw)
    channel_names = ["Brightfield", "p21 / CDKN1A", "Phalloidin", "DAPI", "p62 / SQSTM1"]
    limits = np.percentile(values.transpose(1, 0, 2, 3).reshape(5, -1),
                           settings["display_percentiles"], axis=1)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "svg.fonttype": "none"})
    figures = output / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 5, figsize=(13.4, 6.5))
    for i, row in enumerate(selected.itertuples(index=False)):
        for j, channel in enumerate(channel_names):
            axes[i, j].imshow(values[i, j], cmap="gray", vmin=limits[0, j], vmax=limits[1, j], interpolation="nearest")
            axes[i, j].set_xticks([])
            axes[i, j].set_yticks([])
            for spine in axes[i, j].spines.values():
                spine.set_visible(False)
            if i == 0:
                axes[i, j].set_title(channel, fontsize=12, pad=9)
            if j == 0:
                label = "Response family" if row.role == "response_family" else "Comparator family"
                axes[i, j].set_ylabel(f"{label}\n{row.public_compound_id}\nZS13 crop {row.hdf5_dim_0_index}",
                                      fontsize=10, labelpad=13)
    fig.suptitle("Real microscopy linked to chemical recipes", fontsize=18, fontweight="bold", y=0.987)
    fig.text(0.51, 0.918, "ZEL024 / ZS13 · five measured channels · shared grayscale limits within each channel",
             ha="center", fontsize=11, color="#5a6476")
    fig.text(0.52, 0.013, "Images selected by fixed RNA-family and marker-median rules; source image cell line is unspecified.\n"
             "RNA linkage is by compound and library, from separate measurements.",
             ha="center", fontsize=9, color="#5a6476")
    fig.subplots_adjust(left=0.155, right=0.992, top=0.83, bottom=0.09, wspace=0.055, hspace=0.12)
    for extension in ("png", "svg"):
        fig.savefig(figures / f"microscopy_channels.{extension}", dpi=220, facecolor="white")
    plt.close(fig)
    linked = pd.read_csv(output / "linked_programs.csv")
    fig, axes = plt.subplots(2, 1, figsize=(12, 5.9), sharex=True, sharey=True)
    x = np.arange(32)
    for axis, row in zip(axes, selected.itertuples(index=False)):
        view = linked[linked.role == row.role]
        axis.axhline(0, color="#d4d9e2", linewidth=0.8)
        axis.bar(x - 0.18, view.standardized_family_median, width=0.36, color="#8892a2", label="Family median")
        axis.bar(x + 0.18, view.standardized_core_usage, width=0.36, color="#262f7b", label="Selected compound")
        axis.set_title(f"{row.family_building_block_id} · {row.public_compound_id}", loc="left", fontsize=11)
        axis.set_ylabel("Program usage\n(context SD)")
        axis.grid(axis="y", alpha=0.2)
        axis.set_axisbelow(True)
    axes[-1].set_xticks(x, [f"P{i:02d}" for i in range(1, 33)], rotation=90, fontsize=8)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.52, 0.94), frameon=False, ncol=2)
    fig.suptitle("The linked RNA view: selected compounds and their families", fontsize=16, fontweight="bold")
    fig.text(0.5, 0.025, "Core zel024_hek293 responses · compound-level link to ZS13 images · median-centered per program and divided by context SD",
             ha="center", fontsize=9, color="#5a6476")
    fig.tight_layout(rect=[0, 0.065, 1, 0.86])
    for extension in ("png", "svg"):
        fig.savefig(figures / f"linked_programs.{extension}", dpi=220, facecolor="white")
    plt.close(fig)
    pd.DataFrame({"channel": channel_names, "lower_display_value": limits[0],
                  "upper_display_value": limits[1]}).to_csv(output / "display_scaling.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "evidence")
    args = parser.parse_args()
    selected = select_examples(args.package_root.resolve(), args.output_dir.resolve())
    render(args.package_root.resolve(), args.output_dir.resolve(), selected)
    print(selected.to_string(index=False))


if __name__ == "__main__":
    main()
