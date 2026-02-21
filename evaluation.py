# in evaluation.py

import time
import numpy as np
from sqlalchemy.orm import Session

# Adjust these import paths to match your project structure
from backend.recom.backend.database import SessionLocal
from backend.recom.backend.recommendations.recommender import recommend_activities


def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_test_user_profiles():
    """
    Loads the defined user profiles for the evaluation.

    Each profile should exist in the database (created by seed_db.py),
    and the 'held_out_item' is the "correct" answer we expect to see
    in the recommendations.
    """
    test_profiles = [
        {
            "username": "test_user_1",
            "held_out_item": "Hike on a nature trail"
        },
        {
            "username": "test_user_2",
            "held_out_item": "Write in a journal"
        },
        # You can add more simulated user profiles here for a more robust evaluation
    ]
    return test_profiles


def run_evaluation(model_variation: str, db: Session):
    """
    Runs the evaluation for a single model variation and prints the results.
    """
    test_profiles = load_test_user_profiles()
    num_users = len(test_profiles)
    if num_users == 0:
        print("No test profiles found.")
        return

    recall_hits = 0
    total_time = 0.0

    # Set ablation flags based on the model variation name
    flags = {
        "use_short_term": "No-Short-Term" not in model_variation,
        "use_long_term": "No-Long-Term" not in model_variation,
        "use_feedback": "No-Feedback" not in model_variation,
    }

    for profile in test_profiles:
        username = profile["username"]
        held_out_item = profile["held_out_item"]

        start_time = time.time()

        recs = recommend_activities(
            db=db,
            username=username,
            top_k=8,
            **flags  # Pass the configured flags to the recommender
        )

        end_time = time.time()
        total_time += (end_time - start_time)

        # Check for a recall hit
        recommended_titles = [r['title'] for r in recs]
        if held_out_item in recommended_titles:
            recall_hits += 1

    # Calculate final metrics
    recall_at_8 = recall_hits / num_users if num_users > 0 else 0
    avg_response_time = (total_time / num_users) * 1000 if num_users > 0 else 0

    print(f"| {model_variation:<25} | {recall_at_8:<10.3f} | {avg_response_time:<22.0f} |")


if __name__ == "__main__":
    db_session = next(get_db())

    model_variations = [
        "Full Model",
        "No-Short-Term",
        "No-Long-Term",
        "No-Feedback",
    ]

    print("Running evaluation...")
    print("| Model Variation           | Recall@8   | Avg Response Time (ms)   |")
    print("|---------------------------|------------|--------------------------|")

    for variation in model_variations:
        run_evaluation(variation, db_session)

    print("\nEvaluation complete.")