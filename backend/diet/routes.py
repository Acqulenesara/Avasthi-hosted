from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
import pandas as pd
import pickle
import tensorflow as tf

router = APIRouter(prefix="/diet", tags=["Diet Recommendation"])

from pathlib import Path

# Absolute path to backend/diet/
BASE_DIR = Path(__file__).resolve().parent

# Absolute path to backend/diet/model/
MODEL_PATH = BASE_DIR / "model"



mental_cols = [
    "stress_relief",
    "mood_boost",
    "anxiety_reduction",
    "sleep_improvement",
    "cognitive_function"
]


# ---- Load model ONCE ----
model = tf.keras.models.load_model(
    MODEL_PATH / "main_diet_model.h5",
    compile=False
)

with open(MODEL_PATH / "main_diet_scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open(MODEL_PATH / "main_diet_cliques.pkl", "rb") as f:
    cliques = pickle.load(f)

with open(MODEL_PATH / "main_diet_config.pkl", "rb") as f:
    config = pickle.load(f)

df = pd.read_csv(MODEL_PATH / "main_diet_processed.csv")


class UserProfile(BaseModel):
    stress_relief: float
    mood_boost: float
    anxiety_reduction: float
    sleep_improvement: float
    cognitive_function: float
    top_n: int = 5


def meal_similarity(meal_a, meal_b):
    """
    Strong similarity penalty:
    - Food name overlap (dominant)
    - Category overlap
    - Calorie closeness
    """

    foods_a = set(f["name"] for f in meal_a["foods"])
    foods_b = set(f["name"] for f in meal_b["foods"])

    # 🔴 FOOD OVERLAP (most important)
    food_overlap = len(foods_a & foods_b) / max(len(foods_a), 1)

    # Category overlap
    cat_overlap = len(
        set(meal_a["categories"]) & set(meal_b["categories"])
    ) / max(len(meal_a["categories"]), 1)

    # Calorie similarity
    cal_diff = abs(meal_a["total_calories"] - meal_b["total_calories"])
    cal_sim = max(0, 1 - cal_diff / 700)

    return (
            0.85 * food_overlap +  # 🔥 dominant
            0.10 * cat_overlap +
            0.05 * cal_sim
    )


# ----------------------------------------------------------------------------
# CORE RECOMMENDATION FUNCTION
# ----------------------------------------------------------------------------
def recommend_meals(user_profile: dict, top_n: int):
    user_array = np.array([user_profile[c] for c in mental_cols])

    food_name_col = config["columns"]["food_name"]
    category_col = config["columns"]["category"]
    calories_col = config["columns"]["calories"]
    protein_col = config["columns"]["protein"]

    predictions = []
    seen = set()

    for clique in cliques:
        meal_id = tuple(sorted(clique))
        if meal_id in seen:
            continue
        seen.add(meal_id)

        foods = []
        total_calories = 0
        categories = set()

        for idx in clique:
            food = df.iloc[idx]
            foods.append({
                "name": food[food_name_col],
                "category": food[category_col],
                "calories": float(food[calories_col]),
                "protein": float(food[protein_col])
            })
            total_calories += food[calories_col]
            categories.add(food[category_col])

        meal_vector = df.iloc[clique][mental_cols].mean().values
        features = np.concatenate([user_array, meal_vector]).reshape(1, -1)
        features_scaled = scaler.transform(features)

        score = float(model.predict(features_scaled, verbose=0)[0][0])

        # 🔧 Calibrate score to human range (IMPORTANT)
        match_score = int(70 + (score * 30))  # → 70–100 range
        match_score = min(match_score, 99)  # never show 100%

        predictions.append({
            "foods": foods,
            "score": score,  # raw model score (keep)
            "match_score": match_score,  # ✅ UI score
            "total_calories": float(total_calories),
            "categories": list(categories)
        })

        if len(predictions) >= top_n * 5:
            break

    # Sort by relevance first
    predictions.sort(key=lambda x: x["score"], reverse=True)

    selected = []
    lambda_diversity = 0.55  # ← diversity strength (0.2–0.5 sweet spot)

    while predictions and len(selected) < top_n:
        if not selected:
            selected.append(predictions.pop(0))
            continue

        best_idx = 0
        best_value = -1

        for i, candidate in enumerate(predictions):
            # HARD penalty: repeated core foods
            used_foods = set(
                f["name"] for s in selected for f in s["foods"]
            )

            candidate_foods = set(
                f["name"] for f in candidate["foods"]
            )

            hard_penalty = 0.0
            if used_foods & candidate_foods:
                hard_penalty = 0.15  # strong discouragement

            relevance = candidate["score"]
            diversity_penalty = max(
                meal_similarity(candidate, s) for s in selected
            )

            value = relevance - lambda_diversity * diversity_penalty - hard_penalty


            if value > best_value:
                best_value = value
                best_idx = i

        selected.append(predictions.pop(best_idx))

    return selected

@router.post("/recommend")
def recommend(profile: UserProfile):
    user_profile = {
        "stress_relief": profile.stress_relief,
        "mood_boost": profile.mood_boost,
        "anxiety_reduction": profile.anxiety_reduction,
        "sleep_improvement": profile.sleep_improvement,
        "cognitive_function": profile.cognitive_function
    }

    results = recommend_meals(user_profile, profile.top_n)

    return {
        "status": "success",
        "recommendations": results
    }
