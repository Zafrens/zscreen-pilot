"""Self-contained architecture for the context-token trunk reference model.

This file has no imports outside the Python standard library and PyTorch.
It fully defines the network used by the shipped reference checkpoints
(``context_token_trunk_reference_eval_v1_seed*.pt``); nothing here imports
from any other project or workspace.

Architecture
------------
A shared transformer trunk over an 8-token sequence:

  position 0: classification token (readout)
  position 1: library embedding token
  position 2: cell-line embedding token
  positions 3-7: one token per building-block slot (bb0..bb4)

Each building-block token is a linear projection of the concatenation of a
128-dimensional pretrained chemistry embedding of the building block and a
64-dimensional learned identity embedding of the public building-block ID
(row 0 = absent slot, row 1 = ID not seen in training, rows 2+ = IDs seen
in the training folds). Context enters only through the library and
cell-line tokens; a single shared linear head maps the classification-token
representation to the k=32 program-usage output. There are deliberately no
per-context heads.

The head output is in the per-context z-scored usage space used during
training; each checkpoint carries the per-context standardization
(``usage_scales``) needed to map back to usage units.
"""

from __future__ import annotations

import torch
import torch.nn as nn

D_CHEMISTRY = 128   # pretrained chemistry embedding width per building block
D_IDENTITY = 64     # learned identity embedding width per building-block ID
N_TOKENS = 8        # CLS + LIBRARY + CELL_LINE + 5 building-block slots
N_BB_SLOTS = 5
BB_SLOTS = ["bb0", "bb1", "bb2", "bb3", "bb4"]


class SlotIdentityEmbedding(nn.Module):
    """Per-slot trainable ID embeddings. Row 0 = absent slot (zeros),
    row 1 = ID not seen in training, rows 2+ = IDs seen in training folds."""

    def __init__(self, vocabulary_sizes: list[int]):
        super().__init__()
        if len(vocabulary_sizes) != N_BB_SLOTS:
            raise ValueError("Expected one vocabulary size per building-block slot")
        self.embeddings = nn.ModuleList(
            [nn.Embedding(size + 2, D_IDENTITY, padding_idx=0)
             for size in vocabulary_sizes])
        for embedding in self.embeddings:
            nn.init.trunc_normal_(embedding.weight, std=0.1)
            with torch.no_grad():
                embedding.weight[0].zero_()

    def forward(self, identity_index):
        return torch.stack(
            [emb(identity_index[:, slot])
             for slot, emb in enumerate(self.embeddings)],
            dim=1)


class ContextTokenTrunk(nn.Module):
    """Shared context-token transformer with one Linear(d_model -> k) head.

    Context enters only through the library / cell-line tokens (positions 1
    and 2); there are deliberately no per-context heads.
    """

    def __init__(self, vocabulary_sizes, n_libraries, n_cell_lines, n_out,
                 d_model=128, n_heads=4, n_layers=2, feedforward=512,
                 dropout=0.1):
        super().__init__()
        self.identity = SlotIdentityEmbedding(vocabulary_sizes)
        self.bb_projection = nn.Linear(D_CHEMISTRY + D_IDENTITY, d_model)
        self.classification_token = nn.Parameter(torch.zeros(1, d_model))
        self.library_embedding = nn.Embedding(n_libraries, d_model)
        self.cell_line_embedding = nn.Embedding(n_cell_lines, d_model)
        self.position_embedding = nn.Embedding(N_TOKENS, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=feedforward,
            dropout=dropout, activation="gelu", batch_first=True,
            norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.normalization = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, n_out)
        nn.init.trunc_normal_(self.classification_token, std=0.02)
        nn.init.trunc_normal_(self.library_embedding.weight, std=0.02)
        nn.init.trunc_normal_(self.cell_line_embedding.weight, std=0.02)
        nn.init.trunc_normal_(self.position_embedding.weight, std=0.02)

    def forward_context(self, chemistry, identity_index, present,
                        library_index: int, cell_line_index: int,
                        identity_dropout: float = 0.0):
        """chemistry (b, 5, 128) float, identity_index (b, 5) long,
        present (b, 5) bool; returns (b, k) program-usage prediction in the
        per-context z-scored training space."""
        if identity_dropout > 0:
            drop_sample = (torch.rand(identity_index.shape[0], device=identity_index.device)
                           < identity_dropout)
            if drop_sample.any():
                identity_index = identity_index.clone()
                replacement = torch.where(
                    present[drop_sample],
                    torch.ones_like(identity_index[drop_sample]),
                    torch.zeros_like(identity_index[drop_sample]))
                identity_index[drop_sample] = replacement
        identity = self.identity(identity_index)
        building_blocks = self.bb_projection(torch.cat([chemistry, identity], dim=-1))

        batch_size = chemistry.shape[0]
        sequence = torch.zeros(
            batch_size, N_TOKENS, building_blocks.shape[-1],
            dtype=building_blocks.dtype, device=building_blocks.device)
        sequence[:, 0] = self.classification_token
        library_ids = torch.full((batch_size,), library_index,
                                 dtype=torch.long, device=building_blocks.device)
        cell_line_ids = torch.full((batch_size,), cell_line_index,
                                   dtype=torch.long, device=building_blocks.device)
        sequence[:, 1] = self.library_embedding(library_ids)
        sequence[:, 2] = self.cell_line_embedding(cell_line_ids)
        sequence[:, 3:] = building_blocks
        positions = torch.arange(N_TOKENS, device=building_blocks.device)
        sequence = sequence + self.position_embedding(positions).unsqueeze(0)

        token_mask = torch.ones(batch_size, N_TOKENS,
                                dtype=torch.bool, device=building_blocks.device)
        token_mask[:, 3:] = present
        encoded = self.encoder(sequence, src_key_padding_mask=~token_mask)
        representation = self.normalization(encoded[:, 0])
        return self.head(representation)


def build_from_checkpoint(checkpoint: dict) -> "ContextTokenTrunk":
    """Instantiate the trunk from a shipped checkpoint dict and load its
    weights (strict)."""
    arch = checkpoint["architecture"]
    model = ContextTokenTrunk(
        vocabulary_sizes=list(arch["vocabulary_sizes"]),
        n_libraries=int(arch["n_libraries"]),
        n_cell_lines=int(arch["n_cell_lines"]),
        n_out=int(arch["n_programs"]),
        d_model=int(arch["d_model"]),
        n_heads=int(arch["n_heads"]),
        n_layers=int(arch["n_layers"]),
        feedforward=int(arch["feedforward"]),
        dropout=float(arch["dropout"]))
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.eval()
    return model
