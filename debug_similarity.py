# in debug_similarity.py

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import numpy as np

# 1. Define the two texts you want to compare
text_context = "I had a stressful day at work and feel tired."
activity_title = "Write in a journal"

# 2. Load the exact same model your recommender uses
model = SentenceTransformer('all-mpnet-base-v2')

# 3. Encode both texts into vectors
print("Encoding texts...")
embedding_context = model.encode(text_context)
embedding_activity = model.encode(activity_title)

# 4. Calculate and print the cosine similarity
similarity_score = cos_sim(embedding_context, embedding_activity)

print("\n--- Similarity Debug ---")
print(f"User Context: '{text_context}'")
print(f"Activity Title: '{activity_title}'")
print(f"Cosine Similarity Score: {similarity_score.item():.4f}")
print("------------------------")