"""Package verification: required files, manifest hashes, schema checks.

Fast mode (default) checks that required files exist, validates sizes
against the manifest when it is present, and runs the schema checks
(row-alignment, shapes, row counts, ID formats). Full mode additionally
recalculates every manifested SHA-256 digest.

When ``provenance/file_manifest.csv`` is not present yet (it is frozen at
release), the manifest checks report SKIP with a clear message and the
schema checks still run.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .data import CONTEXTS, CONTROL_CONTEXTS

COMPOUND_COUNTS = {
    "zel024_hek293": 13914,
    "zel024_h1650": 10686,
    "zel028_hek293": 61396,
    "zel028_a549": 40622,
    "zel028_h1650": 25906,
    "zel031_a549": 8321,
    "zel031_thp1": 9041,
    "zel039_aec7": 20813,
}

CONTROL_PSEUDOBULK_COUNTS = {
    "zic008_a549": 350,
    "zic008_aec7": 560,
    "zic008_h1650": 140,
    "zic008_hek293": 139,
    "zic008_hek293clone": 70,
}

N_CONTROLS = 35

MANIFEST_PATH = Path("provenance") / "file_manifest.csv"

CPD_RE = re.compile(r"^CPD_\d{12}$")
BB_RE = re.compile(r"^BB_\d{10}$")

ROOT_FILES = (
    "START_HERE.md",
    "README.md",
    "LICENSE.md",
    "LICENSE_OR_DATA_USE.md",
    "NOTICE",
    "LICENSES/Apache-2.0.txt",
    "LICENSES/CC-BY-4.0.txt",
    "CITATION.cff",
    "pyproject.toml",
    "environment.lock",
    "verify.py",
)

CORE_STATIC_FILES = (
    "core/recipes.parquet",
    "core/splits/fold_assignments.parquet",
    "core/surfaces/harmonized_6000_genes.parquet",
    "core/basis/shared_basis_k32.npy",
    "core/basis/shared_basis_k12.npy",
    "core/basis/basis_registry.json",
    "core/benchmark/README.md",
    "core/benchmark/per_context_comparison_k32.csv",
    "core/benchmark/program_space_primary.csv",
    "core/benchmark/k_resolution.csv",
    "core/benchmark/correction_arm.csv",
    "core/benchmark/cross_context_probe.csv",
    "core/benchmark/program_signal_concentration.csv",
)

MODEL_FILES = (
    "models/README.md",
    "models/model_def.py",
    "models/predict.py",
    "models/bb_embedding_table.parquet",
    "models/golden_predictions.json",
    "models/context_token_trunk_reference_eval_v1_seed0.pt",
    "models/context_token_trunk_reference_eval_v1_seed1.pt",
    "models/context_token_trunk_reference_eval_v1_seed2.pt",
)

ANNEX_FILES = (
    "annex_imaging/README.md",
    "annex_imaging/zel024_compound_embeddings.parquet",
    "annex_imaging/zel031_compound_embeddings.parquet",
    "annex_imaging/zel024_compound_intensity.parquet",
    "annex_imaging/zel031_compound_intensity.parquet",
    "annex_imaging/zel039_imaging_latents.parquet",
    "annex_imaging/reliability/embedding_reliability_audit.json",
    "annex_imaging/reliability/marker_reliability_audit.json",
    "annex_imaging/decomposition.csv",
    "annex_imaging/prediction_score_summary.csv",
    "annex_hypotheses/README.md",
    "annex_hypotheses/LIMITS.md",
    "annex_hypotheses/anchor_leads.csv",
    "annex_hypotheses/program_atlas.csv",
    "annex_hypotheses/sharp_sar_candidates.csv",
    "annex_hypotheses/hypothesis_ledger_full.csv",
    "annex_chemistry/README.md",
    "annex_chemistry/novel_bb_generalization.csv",
    "annex_chemistry/attribution_certificate.csv",
    "annex_chemistry/activity_cliffs.csv",
    "annex_chemistry/chemotype_series.csv",
    "annex_chemistry/bb_effect_rankings.csv",
    "annex_same_well/README.md",
    "annex_same_well/same_well_wells.parquet",
    "annex_same_well/same_well_detections.parquet",
    "annex_same_well/control_compound_map.csv",
    "annex_same_well/evidence/cross_modal_regimes.csv",
    "annex_same_well/evidence/per_control_coupling.csv",
    "annex_same_well/evidence/learning_curve.csv",
    "annex_same_well/evidence/learning_curve.png",
    "annex_controls/README.md",
    "annex_controls/control_compound_map.csv",
    "annex_controls/control_usages_k32.parquet",
)

DOC_FILES = (
    "docs/WHY_THIS_MATTERS.md",
    "docs/SCIENTIFIC_OVERVIEW.md",
    "docs/METHODS.md",
    "docs/DATA_DICTIONARY.md",
    "docs/INTERPRETATION_LIMITS.md",
    "docs/REPRODUCTION.md",
    "docs/terminology.json",
)

EXAMPLE_FILES = (
    "examples/01_quickstart_usages.ipynb",
    "examples/02_reproduce_benchmark.ipynb",
    "examples/03_browse_hypotheses.ipynb",
    "examples/04_join_imaging.ipynb",
)


@dataclass
class CheckResult:
    status: str  # PASS / FAIL / SKIP
    check: str
    detail: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(16 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _required_files(root: Path) -> list[CheckResult]:
    expected = list(ROOT_FILES) + list(CORE_STATIC_FILES) + list(MODEL_FILES)
    expected += list(ANNEX_FILES) + list(DOC_FILES) + list(EXAMPLE_FILES)
    for context in CONTEXTS:
        expected += [
            f"core/usages/usages_{context}.npy",
            f"core/usages/usages_{context}_compounds.parquet",
            f"core/surfaces/surfaces_{context}.npy",
            f"core/surfaces/{context}_compounds.parquet",
        ]
    for context in CONTROL_CONTEXTS:
        expected += [
            f"annex_controls/control_surfaces_{context}.npy",
            f"annex_controls/control_surfaces_{context}_compounds.parquet",
            f"annex_controls/control_pseudobulk_counts_{context}.npy",
            f"annex_controls/control_pseudobulks_{context}.parquet",
        ]
    results, missing = [], [p for p in expected if not (root / p).is_file()]
    if missing:
        for path in missing:
            results.append(CheckResult("FAIL", "required-file", f"missing: {path}"))
    results.append(CheckResult(
        "PASS" if not missing else "FAIL", "required-files",
        f"{len(expected) - len(missing)}/{len(expected)} expected files present"))
    return results


def _manifest_checks(root: Path, full: bool) -> list[CheckResult]:
    manifest = root / MANIFEST_PATH
    if not manifest.is_file():
        return [CheckResult(
            "SKIP", "manifest",
            f"{MANIFEST_PATH.as_posix()} not present (frozen at release); "
            "skipping byte/hash checks, schema checks still run")]
    frame = pd.read_csv(manifest)
    results = []
    failures = 0
    for row in frame.itertuples(index=False):
        path = root / str(row.relative_path)
        if not path.is_file():
            failures += 1
            results.append(CheckResult(
                "FAIL", "manifest-exists", f"missing: {row.relative_path}"))
            continue
        size = path.stat().st_size
        if int(row.bytes) != size:
            failures += 1
            results.append(CheckResult(
                "FAIL", "manifest-bytes",
                f"{row.relative_path}: manifest {row.bytes} != on-disk {size}"))
        if full and _sha256(path) != str(row.sha256):
            failures += 1
            results.append(CheckResult(
                "FAIL", "manifest-sha256", f"digest mismatch: {row.relative_path}"))
    mode = "bytes+sha256" if full else "bytes only (use --full for sha256)"
    results.append(CheckResult(
        "PASS" if failures == 0 else "FAIL", "manifest",
        f"{len(frame) - failures}/{len(frame)} manifested files verified ({mode})"))
    return results


def _schema_checks(root: Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    def record(ok: bool, check: str, detail: str) -> None:
        results.append(CheckResult("PASS" if ok else "FAIL", check, detail))

    # Per-context row alignment and shapes.
    for context in CONTEXTS:
        expected = COMPOUND_COUNTS[context]
        usage = np.load(root / "core" / "usages" / f"usages_{context}.npy")
        surface = np.load(root / "core" / "surfaces" / f"surfaces_{context}.npy")
        u_comp = pd.read_parquet(
            root / "core" / "usages" / f"usages_{context}_compounds.parquet")
        s_comp = pd.read_parquet(
            root / "core" / "surfaces" / f"{context}_compounds.parquet")
        ok = (usage.shape == (expected, 32) and surface.shape == (expected, 6000)
              and list(u_comp.columns) == ["public_compound_id"]
              and list(s_comp.columns) == ["public_compound_id"]
              and len(u_comp) == expected and len(s_comp) == expected
              and u_comp["public_compound_id"].equals(s_comp["public_compound_id"]))
        record(ok, f"schema:{context}",
               f"usages {usage.shape}, surfaces {surface.shape}, "
               f"{expected} aligned compounds")

    # Fold assignments: per-context counts + fold rule on a sample.
    folds = pd.read_parquet(root / "core" / "splits" / "fold_assignments.parquet")
    counts = folds.groupby("context").size().to_dict()
    ok = counts == COMPOUND_COUNTS and folds["fold"].between(0, 4).all()
    record(ok, "schema:folds", f"{len(folds)} rows across {len(counts)} contexts")

    # Basis shapes, nonnegativity, and registry pins.
    import json
    registry = json.loads((root / "core" / "basis" / "basis_registry.json").read_text())
    for entry in registry["pinned_files"]:
        basis = np.load(root / "core" / "basis" / entry["file"])
        shape_ok = basis.shape == (entry["k"], 6000) and (basis >= 0).all()
        hash_ok = _sha256(root / "core" / "basis" / entry["file"]) == entry["sha256"]
        record(shape_ok and hash_ok, f"schema:basis-k{entry['k']}",
               f"shape {basis.shape}, nonnegative, registry sha256 {'ok' if hash_ok else 'MISMATCH'}")

    # Panel: 6,000 rows, contiguous positions.
    panel = pd.read_parquet(root / "core" / "surfaces" / "harmonized_6000_genes.parquet")
    ok = (len(panel) == 6000
          and panel["panel_position"].tolist() == list(range(6000)))
    record(ok, "schema:panel", f"{len(panel)} rows, positions 0..5999")

    # Hypothesis ledger: exactly 3,754 rows; anchor leads carry kill/confirm.
    ledger = pd.read_csv(root / "annex_hypotheses" / "hypothesis_ledger_full.csv")
    record(len(ledger) == 3754, "schema:ledger", f"{len(ledger)} rows (expect 3,754)")
    leads = pd.read_csv(root / "annex_hypotheses" / "anchor_leads.csv")
    ok = ("kill_confirm_experiment" in leads.columns
          and leads["kill_confirm_experiment"].notna().all())
    record(ok, "schema:anchor-leads", f"{len(leads)} rows, kill/confirm on every row")

    # ID format spot checks.
    compounds = pd.concat([
        pd.read_parquet(root / "core" / "usages" / f"usages_{c}_compounds.parquet")
        for c in CONTEXTS])
    sample = compounds["public_compound_id"].sample(
        n=2000, random_state=0).astype(str)
    ok = sample.str.match(CPD_RE).all()
    record(ok, "schema:compound-ids", "2,000 sampled IDs match CPD_############")
    recipes = pd.read_parquet(root / "core" / "recipes.parquet")
    bb_values = pd.unique(
        recipes[[c for c in recipes.columns if c.startswith("bb")]].values.ravel())
    bb_values = [str(v) for v in bb_values if pd.notna(v)]
    bb_sample = pd.Series(bb_values).sample(n=min(2000, len(bb_values)), random_state=0)
    ok = bb_sample.str.match(BB_RE).all()
    record(ok, "schema:bb-ids", f"{len(bb_sample)} sampled IDs match BB_##########")

    # Controls annex: per-context row alignment, shapes, and support counts.
    control_map = pd.read_csv(root / "annex_controls" / "control_compound_map.csv")
    map_ok = (len(control_map) == N_CONTROLS
              and control_map["public_compound_id"].astype(str).str.match(CPD_RE).all())
    record(map_ok, "schema:control-map", f"{len(control_map)} controls, CPD ID format")
    control_ids = set(control_map["public_compound_id"])
    for context in CONTROL_CONTEXTS:
        surface = np.load(root / "annex_controls" / f"control_surfaces_{context}.npy")
        s_keys = pd.read_parquet(
            root / "annex_controls" / f"control_surfaces_{context}_compounds.parquet")
        counts = np.load(
            root / "annex_controls" / f"control_pseudobulk_counts_{context}.npy")
        pb = pd.read_parquet(
            root / "annex_controls" / f"control_pseudobulks_{context}.parquet")
        expected_pb = CONTROL_PSEUDOBULK_COUNTS[context]
        ok = (surface.shape == (N_CONTROLS, 6000)
              and counts.shape == (expected_pb, 6000)
              and len(s_keys) == N_CONTROLS and len(pb) == expected_pb
              and set(s_keys["public_compound_id"]) == control_ids
              and set(pb["public_compound_id"]) <= control_ids
              and int(pb["n_wells"].sum()) == int(s_keys["n_wells"].sum()))
        record(ok, f"schema:controls:{context}",
               f"surfaces {surface.shape}, pseudobulks {counts.shape}, "
               f"{int(pb['n_wells'].sum())} wells")
    usages = pd.read_parquet(root / "annex_controls" / "control_usages_k32.parquet")
    u_cols = [f"u_P{j + 1:02d}" for j in range(32)]
    ok = (len(usages) == N_CONTROLS * len(CONTROL_CONTEXTS)
          and all(c in usages.columns for c in u_cols)
          and set(usages["control_context"]) == set(CONTROL_CONTEXTS)
          and usages["public_compound_id"].astype(str).str.match(CPD_RE).all()
          and np.isfinite(usages[u_cols].to_numpy(dtype=np.float64)).all())
    record(ok, "schema:control-usages",
           f"{len(usages)} rows x 32 usage columns, finite")

    return results


def verify_package(root: str | Path, full: bool = False) -> list[CheckResult]:
    """Run all verification checks against the package rooted at ``root``."""
    root = Path(root).resolve()
    results = _required_files(root)
    if any(r.status == "FAIL" for r in results):
        return results
    results += _manifest_checks(root, full=full)
    results += _schema_checks(root)
    return results


def verification_passed(results: list[CheckResult]) -> bool:
    """PASS means no FAIL; SKIP is acceptable (documented absence)."""
    return all(r.status != "FAIL" for r in results)


if __name__ == "__main__":
    from .cli import main

    raise SystemExit(main())
