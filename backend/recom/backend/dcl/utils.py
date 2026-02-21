from pathlib import Path
from typing import Dict, List
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
EMBED_PATH = ARTIFACTS_DIR / "activity_embeddings.npy"
TITLES_PATH = ARTIFACTS_DIR / "activity_titles.txt"

def load_activity_embeddings() -> Dict[str, np.ndarray]:
    Z = np.load(EMBED_PATH)  # [N, D]
    with open(TITLES_PATH, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f.readlines()]
    return {t: Z[i] for i, t in enumerate(titles)}

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-8
    return float(np.dot(a, b) / denom)