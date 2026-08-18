"""Loaders for the package's core data layers.

All loaders accept an optional ``root`` (package root directory). When
omitted, the root is located by walking upward from the current working
directory looking for ``core/basis/basis_registry.json``.

Contracts (docs/DATA_DICTIONARY.md): every matrix is row-aligned to its
sibling ``*_compounds.parquet`` (positional alignment is the join key);
usage column j is program P{j+1} of the pinned basis; gene symbols come
only from the harmonized panel file.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

CONTEXTS = (
    "zel024_hek293",
    "zel024_h1650",
    "zel028_hek293",
    "zel028_a549",
    "zel028_h1650",
    "zel031_a549",
    "zel031_thp1",
    "zel039_aec7",
)

_ROOT_MARKERS = ("core/basis/basis_registry.json", "core/recipes.parquet")


def find_root(start: str | Path | None = None) -> Path:
    """Locate the package root by walking upward from ``start`` (default:
    the current working directory)."""
    here = Path(start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if all((candidate / marker).exists() for marker in _ROOT_MARKERS):
            return candidate
    raise FileNotFoundError(
        "could not locate the package root (no core/basis/basis_registry.json "
        "found upward from "
        f"{here}); pass root= explicitly")


def _resolve(root: str | Path | None) -> Path:
    return Path(root).resolve() if root is not None else find_root()


def _check_context(context: str) -> str:
    if context not in CONTEXTS:
        raise ValueError(
            f"unknown context {context!r}; expected one of {', '.join(CONTEXTS)}")
    return context


def load_usages(context: str, root: str | Path | None = None):
    """Return (usages, compounds) for a context: usages is float32
    (n_compounds, 32), compounds is the aligned single-column
    public_compound_id frame. Row i of the matrix is row i of the frame."""
    root = _resolve(root)
    _check_context(context)
    usages = np.load(root / "core" / "usages" / f"usages_{context}.npy")
    compounds = pd.read_parquet(
        root / "core" / "usages" / f"usages_{context}_compounds.parquet")
    if usages.shape[0] != len(compounds):
        raise ValueError(
            f"row-alignment broken for {context}: {usages.shape[0]} usage rows "
            f"vs {len(compounds)} compound rows")
    return usages, compounds


def load_surface(context: str, root: str | Path | None = None):
    """Return (surface, compounds) for a context: surface is float32
    (n_compounds, 6000) on the harmonized panel, compounds is the aligned
    single-column public_compound_id frame."""
    root = _resolve(root)
    _check_context(context)
    surface = np.load(root / "core" / "surfaces" / f"surfaces_{context}.npy")
    compounds = pd.read_parquet(
        root / "core" / "surfaces" / f"{context}_compounds.parquet")
    if surface.shape[0] != len(compounds):
        raise ValueError(
            f"row-alignment broken for {context}: {surface.shape[0]} surface rows "
            f"vs {len(compounds)} compound rows")
    return surface, compounds


def load_basis(k: int = 32, root: str | Path | None = None) -> np.ndarray:
    """Return the pinned shared basis as float32 (k, 6000). k is 32
    (shared_program_basis_v1) or 12 (shared_program_basis_k12_v1)."""
    root = _resolve(root)
    if k not in (12, 32):
        raise ValueError("k must be 32 or 12")
    return np.load(root / "core" / "basis" / f"shared_basis_k{k}.npy")


def load_recipes(root: str | Path | None = None) -> pd.DataFrame:
    """Return the building-block grammar table: one row per
    public_compound_id, columns bb0..bb4 (null = absent position) and
    n_positions_occupied."""
    root = _resolve(root)
    return pd.read_parquet(root / "core" / "recipes.parquet")


def load_folds(root: str | Path | None = None) -> pd.DataFrame:
    """Return fold assignments: context, public_compound_id, fold
    (fold = SHA256(public_compound_id) mod 5). Basis and reference model
    were fit with fold 0 held out."""
    root = _resolve(root)
    return pd.read_parquet(root / "core" / "splits" / "fold_assignments.parquet")


def panel_genes(root: str | Path | None = None) -> pd.DataFrame:
    """Return the harmonized 6,000-gene panel definition
    (panel_position, gene_index, gene). The only authoritative mapping of
    panel columns to gene symbols."""
    root = _resolve(root)
    return pd.read_parquet(root / "core" / "surfaces" / "harmonized_6000_genes.parquet")
