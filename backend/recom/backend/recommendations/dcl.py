# DCL (Deep Contrastive Learning) stub: produces simple embeddings and a contrastive score.
# This abstracts the Item2Vec + contrastive fusion idea into a lightweight, testable component.

import numpy as np
from typing import Dict, List, Tuple

def seed_rng(seed: int = 42):
    np.random.seed(seed)

def random_vec(dim: int = 64) -> np.ndarray:
    return np.random.normal(0, 1, (dim,))

class DCLStub:
    def __init__(self, dim: int = 64):
        seed_rng(42)
        self.dim = dim
        self.activity_emb: Dict[str, np.ndarray] = {}
        self.state_emb: Dict[str, np.ndarray] = {}

    def get_activity_emb(self, name: str) -> np.ndarray:
        if name not in self.activity_emb:
            self.activity_emb[name] = random_vec(self.dim)
        return self.activity_emb[name]

    def get_state_emb(self, state: str) -> np.ndarray:
        if state not in self.state_emb:
            self.state_emb[state] = random_vec(self.dim)
        return self.state_emb[state]

    def user_preference_emb(self, likes: List[str], dislikes: List[str]) -> np.ndarray:
        # Aggregate liked activity embeddings; subtract disliked to create a contrastive anchor
        if not likes and not dislikes:
            return random_vec(self.dim)
        like_vecs = [self.get_activity_emb(a) for a in likes]
        dislike_vecs = [self.get_activity_emb(a) for a in dislikes]
        like_mean = np.mean(like_vecs, axis=0) if like_vecs else np.zeros(self.dim)
        dislike_mean = np.mean(dislike_vecs, axis=0) if dislike_vecs else np.zeros(self.dim)
        return like_mean - 0.5 * dislike_mean

    def contrastive_score(self, user_vec: np.ndarray, item_vec: np.ndarray) -> float:
        # Cosine similarity (normalized) as contrastive similarity
        uv = user_vec / (np.linalg.norm(user_vec) + 1e-8)
        iv = item_vec / (np.linalg.norm(item_vec) + 1e-8)
        return float(np.dot(uv, iv))