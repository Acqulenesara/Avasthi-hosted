import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class ActivityEncoder(nn.Module):
    def __init__(self, input_dim: int, embed_dim: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, embed_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.net(x)
        return F.normalize(z, dim=-1)

def info_nce_loss(z_i: torch.Tensor, z_j: torch.Tensor, temperature: float = 0.5) -> torch.Tensor:
    """
    z_i, z_j: shape [B, D] positive pairs (augmented or paired samples)
    Implements symmetric InfoNCE across the concatenated batch.
    """
    batch_size = z_i.shape[0]
    z = torch.cat([z_i, z_j], dim=0)             # [2B, D]
    sim = torch.mm(z, z.t()) / temperature       # [2B, 2B]
    # mask out self-similarity
    mask = torch.eye(2 * batch_size, dtype=torch.bool, device=z.device)
    sim = sim.masked_fill(mask, -1e9)

    # positives are diagonal across halves; build targets
    targets = torch.arange(batch_size, device=z.device)
    targets = torch.cat([targets + batch_size, targets], dim=0)  # [2B]

    return F.cross_entropy(sim, targets)