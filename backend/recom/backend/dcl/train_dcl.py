import os
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import torch.optim as optim

from ..dcl.features import build_feature_matrix
from ..dcl.model import ActivityEncoder, info_nce_loss

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = ARTIFACTS_DIR / "dcl_activity_encoder.pt"
EMBED_PATH = ARTIFACTS_DIR / "activity_embeddings.npy"
TITLES_PATH = ARTIFACTS_DIR / "activity_titles.txt"

# --- NumPy-only cosine similarity matrix ---
def cosine_similarity_matrix(X: np.ndarray) -> np.ndarray:
    X_norm = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return np.dot(X_norm, X_norm.T)

# Simple positive pairing by nearest neighbors in feature space
def build_positive_pairs(X: np.ndarray, titles: List[str]) -> List[Tuple[int, int]]:
    pairs = []
    S = cosine_similarity_matrix(X)
    for i in range(len(titles)):
        # pick top-3 nearest neighbors (excluding self)
        nn_indices = np.argsort(-S[i])  # descending
        count = 0
        for j in nn_indices:
            if j == i:
                continue
            pairs.append((i, j))
            count += 1
            if count >= 3:
                break
    return pairs

class ContrastiveDataset(Dataset):
    def __init__(self, X: np.ndarray, pairs: List[Tuple[int, int]]):
        self.X = X.astype(np.float32)
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        i, j = self.pairs[idx]
        xi = self.X[i]
        xj = self.X[j]
        # simple augmentation: gaussian noise
        noise_scale = 0.05
        xi_aug = xi + np.random.normal(0, noise_scale, size=xi.shape).astype(np.float32)
        xj_aug = xj + np.random.normal(0, noise_scale, size=xj.shape).astype(np.float32)
        return xi_aug, xj_aug

def train(num_epochs: int = 30, batch_size: int = 64, lr: float = 1e-3, embed_dim: int = 384):
    X, titles = build_feature_matrix()
    input_dim = X.shape[1]
    pairs = build_positive_pairs(X, titles)
    ds = ContrastiveDataset(X, pairs)
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True, drop_last=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ActivityEncoder(input_dim=input_dim, embed_dim=embed_dim).to(device)
    opt = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0
        for xi_aug, xj_aug in dl:
            xi_aug = torch.tensor(xi_aug, device=device)
            xj_aug = torch.tensor(xj_aug, device=device)

            zi = model(xi_aug)
            zj = model(xj_aug)
            loss = info_nce_loss(zi, zj, temperature=0.5)

            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total_loss += loss.item()

        avg = total_loss / max(1, len(dl))
        print(f"Epoch {epoch+1}/{num_epochs} - loss: {avg:.4f}")

    # Save model
    torch.save(model.state_dict(), MODEL_PATH)

    # Save embeddings for all activities
    model.eval()
    with torch.no_grad():
        X_t = torch.tensor(X, device=device)
        Z = model(X_t).cpu().numpy()  # [N, D]
    np.save(EMBED_PATH, Z)

    # Save titles alongside embeddings
    with open(TITLES_PATH, "w", encoding="utf-8") as f:
        for t in titles:
            f.write(t + "\n")

    print(f"Saved model -> {MODEL_PATH}")
    print(f"Saved embeddings -> {EMBED_PATH}")
    print(f"Saved titles -> {TITLES_PATH}")

if __name__ == "__main__":
    train()