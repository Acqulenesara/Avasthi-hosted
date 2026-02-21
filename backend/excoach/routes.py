from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd

router = APIRouter(prefix="/exercise", tags=["Exercise ML"])

# -----------------------------
#   ML MODEL LOADING (ONCE)
# -----------------------------
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "backend")

model = joblib.load(os.path.join(MODEL_DIR, "exercise_model.pkl"))
label_encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

# try:
#     model = joblib.load("backend/exercise_model.pkl")
#     label_encoder = joblib.load("backend/label_encoder.pkl")
# except Exception as e:
#     model = None
#     label_encoder = None
#     print("❌ Failed to load exercise ML models:", e)

FEATURE_COLS = [
    "Shoulder_Angle", "Elbow_Angle", "Hip_Angle", "Knee_Angle", "Ankle_Angle",
    "Shoulder_Ground_Angle", "Elbow_Ground_Angle", "Hip_Ground_Angle",
    "Knee_Ground_Angle", "Ankle_Ground_Angle"
]

# -----------------------------
#   SCHEMAS
# -----------------------------
class AngleData(BaseModel):
    angles: List[float]  # must be length = 10

class PostureData(BaseModel):
    user_id: str
    exercise: str
    posture_score: float
    reps: int

# Temporary in-memory store (⚠️ non-persistent)
data_store: List[PostureData] = []

# -----------------------------
#   ENDPOINTS
# -----------------------------
@router.post("/predict")
def predict_exercise(data: AngleData):
    print("✅ /predict HIT")
    print("Angles length:", len(data.angles))
    print("Angles:", data.angles)
    print("Model loaded:", model is not None)
    print("Encoder loaded:", label_encoder is not None)

    if model is None or label_encoder is None:
        return {"error": "ML model not loaded"}

    if len(data.angles) != 10:
        return {"error": "Expected exactly 10 angle values"}

    df = pd.DataFrame([data.angles], columns=FEATURE_COLS)
    pred = model.predict(df)[0]
    label = label_encoder.inverse_transform([pred])[0]

    return {"predicted_exercise": label}



@router.post("/posture")
def save_posture(data: PostureData):
    data_store.append(data)
    return {"message": "Data saved", "count": len(data_store)}


@router.get("/posture")
def get_posture():
    return data_store
