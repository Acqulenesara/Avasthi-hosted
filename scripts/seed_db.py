# in scripts/seed_db.py

from backend.recom.backend.database import Base, engine, SessionLocal
# 1. Import the new models from your central models file
from backend.recom.backend.models import User, ChatInteraction, UserPreference, Feedback
# 2. Import the password hashing utility from your auth file
from backend.recom.backend.auth import get_password_hash


def seed_database():
    # Create tables based on the new schema in models.py
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Clear existing test data to prevent duplicates
        test_usernames = ['test_user_1', 'test_user_2']
        db.query(User).filter(User.username.in_(test_usernames)).delete(synchronize_session=False)
        db.query(ChatInteraction).filter(ChatInteraction.username.in_(test_usernames)).delete(synchronize_session=False)
        db.query(UserPreference).filter(UserPreference.username.in_(test_usernames)).delete(synchronize_session=False)
        db.query(Feedback).filter(Feedback.username.in_(test_usernames)).delete(synchronize_session=False)
        db.commit()

        # --- Create Test User 1 ---
        user1 = User(
            username="test_user_1",
            email="user1@example.com",
            password=get_password_hash("password123"),  # Add hashed password
            preferences_collected=1
        )
        db.add(user1)

        # Add long-term preference to the new UserPreference table
        db.add(UserPreference(
            username="test_user_1",
            preference_type="modality",
            content="outdoor"
        ))

        # Add feedback (this model is mostly unchanged)
        db.add(Feedback(
            username="test_user_1",
            activity_title="Go for a bike ride",
            liked=True
        ))

        # --- Create Test User 2 ---
        user2 = User(
            username="test_user_2",
            email="user2@example.com",
            password=get_password_hash("password123"),
            preferences_collected=1
        )
        db.add(user2)

        # Add long-term preference
        db.add(UserPreference(
            username="test_user_2",
            preference_type="modality",
            content="indoor"
        ))

        # Add chat interaction using the new table structure
        db.add(ChatInteraction(
            username="test_user_2",
            query="I had a stressful day at work and feel tired.",
            response="I'm sorry to hear that. How about a relaxing activity?",
            scenario="stress_relief"
        ))

        db.commit()
        print("✅ Database seeded with test users based on the new schema.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()