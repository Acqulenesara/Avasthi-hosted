import csv
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
ACTIVITIES_CSV = DATA_DIR / "activities.csv"

# Controlled vocab for categorical features; extend as needed
MODALITIES = ["creative", "physical", "mindful", "social", "outdoors", "learning"]
DURATION_BUCKETS = ["5min", "10min", "15min", "30min", "45min", "60min+"]
ENVIRONMENTS = ["quiet space", "home", "studio", "kitchen", "outdoors", "gym"]

def one_hot(value: str, vocab: List[str]) -> np.ndarray:
    vec = np.zeros(len(vocab), dtype=np.float32)
    if value in vocab:
        vec[vocab.index(value)] = 1.0
    return vec

def bucketize_duration(raw: str) -> str:
    s = (raw or "").lower().strip()
    if "5" in s: return "5min"
    if "10" in s: return "10min"
    if "15" in s: return "15min"
    if "30" in s: return "30min"
    if "45" in s: return "45min"
    return "60min+"

def parse_environment(raw: str) -> str:
    s = (raw or "").lower().strip()
    for env in ENVIRONMENTS:
        if env in s:
            return env
    # fallback
    if "outdoor" in s: return "outdoors"
    if "gym" in s: return "gym"
    if "kitchen" in s: return "kitchen"
    if "studio" in s: return "studio"
    if "quiet" in s: return "quiet space"
    return "home"

# 🔹 New: Safe mapping for difficulty and energy
def map_difficulty(raw: str) -> float:
    mapping = {
        "easy": 1.0,
        "medium": 3.0,
        "hard": 5.0
    }
    if not raw:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return mapping.get(raw.lower().strip(), 0.0)

def map_energy(raw: str) -> float:
    mapping = {
        "low": 1.0,
        "moderate": 3.0,
        "high": 5.0
    }
    if not raw:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return mapping.get(raw.lower().strip(), 0.0)

def load_activities() -> List[Dict[str, str]]:
    with open(ACTIVITIES_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build_feature_matrix() -> Tuple[np.ndarray, List[str]]:
    """
    Returns:
      X: shape [N, D] feature matrix
      titles: list of activity titles aligned with rows in X
    """
    rows = load_activities()
    feats = []
    titles = []
    for r in rows:
        title = r.get("title", "")
        modality = r.get("modality", "").lower().strip()
        duration_bucket = bucketize_duration(r.get("duration", ""))
        environment = parse_environment(r.get("environment", ""))

        v_mod = one_hot(modality, MODALITIES)
        v_dur = one_hot(duration_bucket, DURATION_BUCKETS)
        v_env = one_hot(environment, ENVIRONMENTS)

        # 🔹 Use safe mapping functions
        diff = map_difficulty(r.get("difficulty", "")) / 5.0
        energy = map_energy(r.get("energy", "")) / 5.0
        v_num = np.array([diff, energy], dtype=np.float32)

        feat = np.concatenate([v_mod, v_dur, v_env, v_num], axis=0)
        feats.append(feat)
        titles.append(title)

    X = np.stack(feats, axis=0)
    return X, titles