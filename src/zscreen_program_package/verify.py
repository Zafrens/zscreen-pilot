"""Package verification: required files, manifest hashes, schema checks.

Fast mode (default) checks that required files exist, validates sizes
against the manifest when it is present, and runs the schema checks
(row-alignment, shapes, row counts, ID formats). Full mode additionally
recalculates every manifested SHA-256 digest.

This package requires both the checksum inventory and its envelope.
Missing manifest metadata fails verification.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

import numpy as np
import pandas as pd

from .data import CONTEXTS

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

MANIFEST_PATH = Path("file_manifest.csv")

# Recognizable local tooling/OS artifacts are outside the distributed payload.
# Keep this list explicit: arbitrary hidden files and user-added data must still
# fail coverage. os.walk prunes these directories before visiting their contents.
GENERATED_DIRECTORIES = {
    "__pycache__", ".git", ".pytest_cache", ".ipynb_checkpoints", ".cache",
    "__MACOSX", ".mypy_cache", ".ruff_cache",
}
GENERATED_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
MANIFEST_METADATA = {"MANIFEST.json", "file_manifest.csv"}

CPD_RE = re.compile(r"^CPD_\d{12}$")
BB_RE = re.compile(r"^BB_\d{10}$")

ROOT_FILES = (
    "START_HERE.md",
    "README.md",
    "LICENSE.md",
    "LICENSE_OR_DATA_USE.md",
    "NOTICE",
    "LICENSES/Apache-2.0.txt",
    "LICENSES/CC-BY-NC-4.0.txt",
    "CITATION.cff",
    "pyproject.toml",
    "environment.lock",
    "verify.py",
    "component_licenses.json",
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
    "core/benchmark/fold0_baseline_comparison.csv",
    "core/benchmark/fold0_reference_model_summary.csv",
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
    "annex_imaging/reliability/embedding_reliability.json",
    "annex_imaging/reliability/marker_reliability.json",
    "annex_imaging/decomposition.csv",
    "annex_imaging/prediction_score_summary.csv",
    "annex_hypotheses/README.md",
    "annex_hypotheses/HOW_TO_READ.md",
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
    "annex_clusters/README.md",
    "annex_clusters/cluster_census.csv",
)

PHENOMIMICRY_FILES = (
    "annex_phenomimicry/README.md",
    "annex_phenomimicry/phenomimic_pairs.parquet",
    "annex_phenomimicry/antimimic_pairs.parquet",
    "annex_phenomimicry/showcase_hits.csv",
    "annex_phenomimicry/top100_phenomimics.csv",
    "annex_phenomimicry/top100_family_summary.csv",
    "annex_phenomimicry/validation_empirical_p.csv",
    "annex_phenomimicry/ensemble_rescoring_panel.csv",
    "annex_phenomimicry/target_hubness.csv",
)

DOC_FILES = (
    "docs/WHY_THIS_MATTERS.md",
    "docs/SCIENTIFIC_OVERVIEW.md",
    "docs/METHODS.md",
    "docs/DATA_DICTIONARY.md",
    "docs/REPRODUCTION.md",
    "docs/terminology.json",
    "docs/summary/README.md",
)

EXAMPLE_FILES = (
    "examples/01_quickstart_usages.ipynb",
    "examples/02_reproduce_benchmark.ipynb",
    "examples/03_browse_hypotheses.ipynb",
    "examples/04_join_imaging.ipynb",
)

PACKAGE_FILES = (
    "MANIFEST.json", "file_manifest.csv", "docs/REFERENCE_SOURCES.md",
    "docs/DOWNLOAD.md", "docs/RESULTS.md", "docs/PILOT_RESULTS_REFERENCE.md",
    "docs/ANALYSIS_ACCESS.md",
    "atlas/original_clusters/members.parquet", "atlas/original_clusters/centroid_keys.csv",
    "atlas/original_clusters/gene_centroids.npy", "atlas/original_clusters/program_centroids.npy",
    "annex_case_studies/README.md",
    "annex_case_studies/01_hspa5_building_block/README.md",
    "annex_measurement_design/README.md",
    "annex_measurement_design/evidence/pairing_summary.csv",
    "annex_controls/README.md", "annex_controls/control_compound_map.csv",
    "gallery/evidence/selected_examples.csv", "gallery/README.md",
    "annotations/control_target_annotations.csv",
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


def _payload_paths(root: Path) -> set[str]:
    """Inventory payloads without descending into local virtual environments.

    A Python environment is recognized by its pyvenv.cfg marker, including a
    .venv installed inside the package. Unrecognized .venv contents remain
    subject to coverage checks. build/dist are generated only at the package
    root; editable-install egg-info is allowed at the root or directly in src.
    """
    payloads = set()
    for current, directories, files in os.walk(root, followlinks=False):
        current = Path(current)
        directories[:] = [
            name for name in directories
            if name not in GENERATED_DIRECTORIES
            and not (current / name / "pyvenv.cfg").is_file()
            and not (current == root and name in {"build", "dist"})
            and not (current in {root, root / "src"} and name.endswith(".egg-info"))
        ]
        for name in files:
            path = current / name
            relative = path.relative_to(root).as_posix()
            if (name not in GENERATED_FILES and relative not in MANIFEST_METADATA
                    and path.is_file()):
                payloads.add(relative)
    return payloads


def _required_files(root: Path) -> list[CheckResult]:
    expected = list(ROOT_FILES) + list(CORE_STATIC_FILES) + list(MODEL_FILES)
    expected += list(ANNEX_FILES) + list(PHENOMIMICRY_FILES)
    expected += list(DOC_FILES) + list(EXAMPLE_FILES)
    expected += list(PACKAGE_FILES)
    for context in CONTEXTS:
        expected += [
            f"core/usages/usages_{context}.npy",
            f"core/usages/usages_{context}_compounds.parquet",
            f"core/surfaces/surfaces_{context}.npy",
            f"core/surfaces/{context}_compounds.parquet",
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
            "FAIL", "manifest", f"required {MANIFEST_PATH.as_posix()} not present")]
    frame = pd.read_csv(manifest)
    results = []
    failures = 0
    if not {"relative_path", "bytes", "sha256"}.issubset(frame.columns):
        return [CheckResult("FAIL", "manifest-schema", "missing required manifest fields")]
    if frame.relative_path.duplicated().any():
        return [CheckResult("FAIL", "manifest-unique", "duplicate file paths")]
    # A shortened checksum list must not silently leave payloads unchecked.
    actual = _payload_paths(root)
    listed = set(frame.relative_path.astype(str))
    if not listed or actual != listed:
        return [CheckResult("FAIL", "manifest-coverage",
                            f"unlisted payloads: {len(actual - listed)}; missing payloads: {len(listed - actual)}")]
    envelope = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    envelope_ok = (envelope["manifest_sha256"] == _sha256(manifest)
                   and envelope["manifested_file_count"] == len(frame)
                   and envelope["manifested_bytes"] == int(frame.bytes.sum()))
    results.append(CheckResult("PASS" if envelope_ok else "FAIL", "manifest-envelope",
                               "CSV digest, file count and total bytes checked against MANIFEST.json"))
    for row in frame.itertuples(index=False):
        path = root / str(row.relative_path)
        if path.is_absolute() and not path.resolve().is_relative_to(root.resolve()):
            failures += 1
            results.append(CheckResult("FAIL", "manifest-path", "path outside package root"))
            continue
        if ".." in Path(str(row.relative_path)).parts or Path(str(row.relative_path)).is_absolute():
            failures += 1
            results.append(CheckResult("FAIL", "manifest-path", "manifest paths must be relative and contain no parent traversal"))
            continue
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
        surface = np.load(root / "core" / "surfaces" / f"surfaces_{context}.npy", mmap_mode="r", allow_pickle=False)
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

    # Hypothesis ledger: exactly 1,027 rows; anchor leads carry kill/confirm.
    ledger = pd.read_csv(root / "annex_hypotheses" / "hypothesis_ledger_full.csv")
    record(len(ledger) == 1027, "schema:ledger", f"{len(ledger)} rows (expect 1,027)")
    leads = pd.read_csv(root / "annex_hypotheses" / "anchor_leads.csv")
    ok = ("kill_confirm_experiment" in leads.columns
          and leads["kill_confirm_experiment"].notna().all())
    record(ok, "schema:anchor-leads", f"{len(leads)} rows, kill/confirm on every row")

    # Cluster census: exactly 1,007 clusters, all at coherence q <= 0.01.
    census = pd.read_csv(root / "annex_clusters" / "cluster_census.csv")
    ok = len(census) == 1007 and bool((census["coherence_q"] <= 0.01).all())
    record(ok, "schema:cluster-census",
           f"{len(census)} clusters, max coherence_q {census['coherence_q'].max():.5f}")

    # Curated ensemble panel includes supported compound-target annotations.
    panel = pd.read_csv(root / "annex_phenomimicry" / "ensemble_rescoring_panel.csv")
    ok = len(panel) == 42 and int(panel["consistent_pair"].sum()) == 10
    record(ok, "schema:rescoring-panel",
           f"{len(panel)} pairs, {int(panel['consistent_pair'].sum())} consistent")

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

    return results


def _notebook_checks(root: Path) -> list[CheckResult]:
    """Inspect the distributed notebook code and saved outputs directly."""
    results = []
    for relative in EXAMPLE_FILES:
        notebook = json.loads((root / relative).read_text(encoding="utf-8"))
        code = [cell for cell in notebook.get("cells", [])
                if cell.get("cell_type") == "code" and "".join(cell.get("source", [])).strip()]
        outputs = [output for cell in code for output in cell.get("outputs", [])]
        ok = (notebook.get("nbformat") == 4 and bool(code) and bool(outputs)
              and all(isinstance(cell.get("execution_count"), int)
                      and cell["execution_count"] > 0 for cell in code)
              and all(output.get("output_type") != "error" for output in outputs))
        results.append(CheckResult("PASS" if ok else "FAIL", f"notebook:{Path(relative).stem}",
                                   f"{len(code)} code cells with execution counts, {len(outputs)} saved outputs; "
                                   "checks stored content without rerunning code"))
    return results


def _document_link_checks(root: Path) -> list[CheckResult]:
    """Check that local Markdown links resolve within this standalone package."""
    failures = []
    checked = 0
    for relative in sorted(_payload_paths(root)):
        if not relative.endswith(".md"):
            continue
        source = root / relative
        content = source.read_text(encoding="utf-8")
        # Fenced examples are prose/code, not rendered document links.
        content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", content)
        targets += re.findall(r"^\s*\[[^\]]+\]:\s*(.+)$", content, flags=re.MULTILINE)
        targets += re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", content)
        for raw_target in targets:
            target = raw_target.strip()
            if not target:
                continue
            target = target[1:target.index(">")] if target.startswith("<") and ">" in target else target.split()[0]
            if target.startswith(("https://", "http://", "mailto:", "data:", "#")):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            checked += 1
            destination = (source.parent / target).resolve()
            if not destination.is_relative_to(root) or not destination.exists():
                failures.append(f"{relative}: {target}")
    return [CheckResult("FAIL" if failures else "PASS", "document-links",
                        "; ".join(failures) if failures else
                        f"{checked} local Markdown links resolve inside the package")]


def _package_schema_checks(root: Path) -> list[CheckResult]:
    """Validate the distributed pilot objects."""
    results = []
    def record(ok: bool, name: str, detail: str) -> None:
        results.append(CheckResult("PASS" if ok else "FAIL", f"package:{name}", detail))

    members = pd.read_parquet(root / "atlas/original_clusters/members.parquet")
    keys = pd.read_csv(root / "atlas/original_clusters/centroid_keys.csv")
    sizes = members.groupby(["context", "cluster_id"]).size()
    expected = keys.set_index(["context", "cluster_id"]).n_members
    record(len(keys) == 1007 and len(members) == 5346
           and keys.centroid_row.tolist() == list(range(1007))
           and not keys.duplicated(["context", "cluster_id"]).any()
           and sizes.reindex(expected.index).equals(expected.rename(None)),
           "original-atlas", "1,007 keyed clusters and 5,346 memberships; member counts align")
    genes = np.load(root / "atlas/original_clusters/gene_centroids.npy", mmap_mode="r", allow_pickle=False)
    programs = np.load(root / "atlas/original_clusters/program_centroids.npy", mmap_mode="r", allow_pickle=False)
    record(genes.shape == (1007, 6000) and programs.shape == (1007, 32),
           "centroid-axes", "Original cluster centroids align with 6,000 genes and 32 programs")
    pairing = pd.read_csv(root / "annex_measurement_design/evidence/pairing_summary.csv")
    record(len(pairing) == 8 and set(pairing.train_size) == {350, 1000, 3000, 8000},
           "paired-result-table", "Stored result: four training sizes and two pairing conditions")
    gallery = pd.read_csv(root / "gallery/evidence/selected_examples.csv")
    record(len(gallery) == 2 and gallery.public_compound_id.is_unique,
           "gallery", "Two real crop examples with explicit public compound linkage")
    annotation = pd.read_csv(root / "annex_phenomimicry/validation_empirical_p.csv")
    record(len(annotation) == 2074, "curated-calibration", "2,074 curated query rows")
    controls = pd.read_csv(root / "annex_controls/control_compound_map.csv")
    record(len(controls) == 35 and controls.public_compound_id.is_unique,
           "control-map", "35 named controls have unique public keys")
    return results


def verify_package(root: str | Path, full: bool = False) -> list[CheckResult]:
    """Run all verification checks against the package rooted at ``root``."""
    root = Path(root).resolve()
    results = _required_files(root)
    if any(r.status == "FAIL" for r in results):
        return results
    results += _manifest_checks(root, full=full)
    results += _schema_checks(root)
    results += _package_schema_checks(root)
    results += _notebook_checks(root)
    results += _document_link_checks(root)
    return results


def verification_passed(results: list[CheckResult]) -> bool:
    """PASS means no FAIL; SKIP is acceptable (documented absence)."""
    return all(r.status != "FAIL" for r in results)


if __name__ == "__main__":
    from .cli import main

    raise SystemExit(main())
