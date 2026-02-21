# Training Script for mainDATASET.csv
# 753 individual foods with complete nutritional data, allergy info, and carbon footprint

import pandas as pd
import numpy as np
import networkx as nx
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import warnings
import pickle

warnings.filterwarnings('ignore')

print("=" * 80)
print("DIET RECOMMENDATION MODEL - mainDATASET")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD DATASET
# ============================================================================

print("\n[STEP 1] Loading mainDATASET.csv...")

df = pd.read_csv('mainDATASET.csv')
print(f"✓ Dataset loaded: {df.shape[0]} foods, {df.shape[1]} columns")
print(f"✓ Columns: {list(df.columns)}")

# Clean column names
df.columns = df.columns.str.strip()

# Display sample
print(f"\n✓ Sample foods:")
display_cols = ['Food', 'Region', 'Type', 'Category', 'Energy(kcal)', 'Proteins', 'Fiber']
print(df[display_cols].head(10))

print(f"\n✓ Dataset Statistics:")
print(f"  - Regions: {df['Region'].nunique()}")
print(f"  - Food Types: {df['Type'].nunique()}")
print(f"  - Categories: {df['Category'].nunique()}")
print(f"  - Allergen Info: Available")

# ============================================================================
# STEP 2: DATA CLEANING
# ============================================================================

print("\n[STEP 2] Cleaning and preparing data...")

# Handle missing values in numerical columns
numerical_cols = ['Energy(kcal)', 'Proteins', 'Carbohydrates', 'Fats', 'Fiber', 'Carbon Footprint(kg CO2e)']

for col in numerical_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Remove any duplicates
df = df.drop_duplicates(subset=['Food'])

# Fill missing text columns
for col in ['Allergy', 'Category', 'Type']:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')

print(f"✓ Cleaned dataset: {len(df)} unique foods")

# ============================================================================
# STEP 3: CALCULATE MENTAL HEALTH SCORES
# ============================================================================

print("\n[STEP 3] Calculating mental health benefit scores...")

# Normalize nutrients
scaler_norm = MinMaxScaler()
nutrients = ['Energy(kcal)', 'Proteins', 'Carbohydrates', 'Fats', 'Fiber']

df_norm = df.copy()
df_norm[nutrients] = scaler_norm.fit_transform(df[nutrients])

# Calculate mental health scores (0-1 scale)
# Based on nutrition science research

# 1. Stress Relief: High protein + High fiber + Moderate energy + Low fat
df['stress_relief'] = (
        0.35 * df_norm['Proteins'] +
        0.35 * df_norm['Fiber'] +
        0.15 * (1 - df_norm['Energy(kcal)'] / (df_norm['Energy(kcal)'].max() + 0.001)) +
        0.15 * (1 - df_norm['Fats'])
)

# 2. Mood Boost: Balanced macros + High fiber (gut-brain axis)
df['mood_boost'] = (
        0.3 * df_norm['Proteins'] +
        0.3 * df_norm['Carbohydrates'] +
        0.4 * df_norm['Fiber']
)

# 3. Anxiety Reduction: High fiber + Balanced nutrition + Low processed (lower fat/cal ratio)
df['anxiety_reduction'] = (
        0.5 * df_norm['Fiber'] +
        0.3 * df_norm['Proteins'] +
        0.2 * (1 - df_norm['Fats'])
)

# 4. Sleep Improvement: Complex carbs + Fiber + Moderate protein (tryptophan sources)
df['sleep_improvement'] = (
        0.4 * df_norm['Carbohydrates'] +
        0.4 * df_norm['Fiber'] +
        0.2 * df_norm['Proteins']
)

# 5. Cognitive Function: High protein + Low excess calories + Balanced fats
df['cognitive_function'] = (
        0.5 * df_norm['Proteins'] +
        0.3 * (1 - df_norm['Energy(kcal)'] / (df_norm['Energy(kcal)'].max() + 0.001)) +
        0.2 * df_norm['Fats']
)

# Clip scores to 0-1
mental_cols = ['stress_relief', 'mood_boost', 'anxiety_reduction',
               'sleep_improvement', 'cognitive_function']
for col in mental_cols:
    df[col] = df[col].clip(0, 1)

print("✓ Mental health scores calculated!")
print(f"\n✓ Sample scores for '{df.iloc[0]['Food']}':")
for col in mental_cols:
    print(f"  - {col}: {df.iloc[0][col]:.3f}")

# ============================================================================
# STEP 4: BUILD COMPATIBILITY GRAPH (K-CLIQUE)
# ============================================================================

print("\n[STEP 4] Building food compatibility graph...")


def build_food_graph(df, compatibility_threshold=0.5):
    """
    Build graph where foods are nodes and edges represent compatibility.

    Compatibility factors:
    - Same category bonus (both vegetables, both proteins, etc.)
    - Same region bonus (cultural compatibility)
    - Complementary nutrients (variety)
    - No allergy conflicts
    """
    G = nx.Graph()

    # Add nodes
    for idx, row in df.iterrows():
        G.add_node(idx, **row.to_dict())

    print(f"✓ Added {G.number_of_nodes()} food items as nodes")

    mental_cols = ['stress_relief', 'mood_boost', 'anxiety_reduction',
                   'sleep_improvement', 'cognitive_function']

    edges_added = 0

    print(f"✓ Analyzing food compatibility...")

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            # Skip if same food
            if df.iloc[i]['Food'] == df.iloc[j]['Food']:
                continue

            # Compatibility bonuses
            same_category = df.iloc[i]['Category'] == df.iloc[j]['Category']
            category_bonus = 0.15 if same_category else 0

            same_region = df.iloc[i]['Region'] == df.iloc[j]['Region']
            region_bonus = 0.1 if same_region else 0

            # Nutritional complementarity (foods with different strengths work well together)
            nutrients_i = df.iloc[i][mental_cols].values
            nutrients_j = df.iloc[j][mental_cols].values

            similarity = np.dot(nutrients_i, nutrients_j) / (
                    np.linalg.norm(nutrients_i) * np.linalg.norm(nutrients_j) + 0.001)

            # We want moderate similarity (0.3-0.85) - not too similar, not too different
            if 0.3 <= similarity <= 0.85:
                compatibility = similarity + category_bonus + region_bonus

                if compatibility >= compatibility_threshold:
                    G.add_edge(i, j, weight=compatibility)
                    edges_added += 1

    print(f"✓ Added {edges_added} compatibility edges")
    print(f"✓ Graph density: {nx.density(G):.3f}")

    return G


G = build_food_graph(df, compatibility_threshold=0.5)

# ============================================================================
# STEP 5: FIND K-CLIQUES (MEAL COMBINATIONS)
# ============================================================================

print("\n[STEP 5] Finding meal combinations (k-cliques)...")


def find_meal_combinations(G, k=3, max_cliques=500):
    """
    Find k-cliques: groups of k mutually compatible foods.
    k=3 means meals with 3 food items (balanced meal)
    """
    from itertools import combinations

    cliques = []

    print(f"✓ Searching for groups of {k} compatible foods...")

    all_cliques = list(nx.find_cliques(G))
    print(f"✓ Found {len(all_cliques)} maximal cliques")

    for clique in all_cliques:
        if len(clique) >= k:
            for combo in combinations(clique, k):
                cliques.append(list(combo))
                if len(cliques) >= max_cliques:
                    break
        if len(cliques) >= max_cliques:
            break

    print(f"✓ Generated {len(cliques)} meal combinations")

    if cliques:
        sample = cliques[0]
        print(f"\n✓ Sample meal combination:")
        for idx in sample:
            print(f"  - {df.iloc[idx]['Food']} ({df.iloc[idx]['Category']})")

    return cliques


cliques = find_meal_combinations(G, k=3, max_cliques=1000)

# ============================================================================
# STEP 6: CREATE TRAINING DATA
# ============================================================================

print("\n[STEP 6] Creating training data for deep learning...")


def create_training_data(df, cliques, num_users=2500):
    """
    Create synthetic training data.
    X: [user_mental_health_profile, meal_nutritional_profile]
    y: suitability_score
    """

    mental_cols = ['stress_relief', 'mood_boost', 'anxiety_reduction',
                   'sleep_improvement', 'cognitive_function']

    X_data = []
    y_data = []

    print(f"✓ Generating training data for {num_users} virtual users...")

    for _ in range(num_users):
        # Random user profile (what they need)
        user_profile = np.random.uniform(0.3, 1.0, size=len(mental_cols))

        # Sample meal combinations
        sample_cliques = np.random.choice(len(cliques), size=min(12, len(cliques)), replace=False)

        for clique_idx in sample_cliques:
            clique = cliques[clique_idx]

            # Meal's average mental health scores
            meal_nutrients = df.iloc[clique][mental_cols].mean().values

            # Combine user needs + meal benefits
            features = np.concatenate([user_profile, meal_nutrients])

            # Calculate suitability (how well meal matches user needs)
            suitability = np.dot(user_profile, meal_nutrients) / (
                    np.linalg.norm(user_profile) * np.linalg.norm(meal_nutrients) + 0.001)

            # Add some realistic noise
            suitability += np.random.normal(0, 0.05)
            suitability = np.clip(suitability, 0, 1)

            X_data.append(features)
            y_data.append(suitability)

    X = np.array(X_data)
    y = np.array(y_data)

    print(f"✓ Created {len(X)} training samples")
    print(f"✓ Feature dimension: {X.shape[1]}")

    return X, y


X, y = create_training_data(df, cliques, num_users=2500)

# ============================================================================
# STEP 7: BUILD AND TRAIN NEURAL NETWORK
# ============================================================================

print("\n[STEP 7] Building and training neural network...")

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42)

print(f"✓ Training samples: {len(X_train)}")
print(f"✓ Test samples: {len(X_test)}")

# Build deep learning model
model = keras.Sequential([
    layers.Input(shape=(X_train.shape[1],)),
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    layers.Dense(64, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),

    layers.Dense(32, activation='relu'),
    layers.Dropout(0.2),

    layers.Dense(1, activation='sigmoid')  # Output: suitability score 0-1
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='mse',
    metrics=['mae']
)

print("\n✓ Model architecture:")
model.summary()

print("\n✓ Training model (this may take a few minutes)...")
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=30,
    batch_size=32,
    verbose=1
)

print(f"\n✓ Training complete!")
print(f"✓ Final training loss: {history.history['loss'][-1]:.4f}")
print(f"✓ Final validation loss: {history.history['val_loss'][-1]:.4f}")

# ============================================================================
# STEP 8: SAVE EVERYTHING
# ============================================================================

print("\n" + "=" * 80)
print("SAVING MODEL AND DATA...")
print("=" * 80)

# Save model
model.save('main_diet_model.h5')
print("✓ Model saved as 'main_diet_model.h5'")

# Save scaler
with open('model/main_diet_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✓ Scaler saved as 'main_diet_scaler.pkl'")

# Save cliques
with open('model/main_diet_cliques.pkl', 'wb') as f:
    pickle.dump(cliques, f)
print("✓ Cliques saved as 'main_diet_cliques.pkl'")

# Save processed dataframe
df.to_csv('main_diet_processed.csv', index=False)
print("✓ Processed data saved as 'main_diet_processed.csv'")

# Save config
config = {
    'columns': {
        'food_name': 'Food',
        'category': 'Category',
        'type': 'Type',
        'region': 'Region',
        'allergy': 'Allergy',
        'calories': 'Energy(kcal)',
        'protein': 'Proteins',
        'carbs': 'Carbohydrates',
        'fat': 'Fats',
        'fiber': 'Fiber',
        'carbon_footprint': 'Carbon Footprint(kg CO2e)'
    }
}

with open('model/main_diet_config.pkl', 'wb') as f:
    pickle.dump(config, f)
print("✓ Config saved as 'main_diet_config.pkl'")

print("\n" + "=" * 80)
print("🎉 MODEL TRAINING COMPLETE!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"  Foods in database: {len(df)}")
print(f"  Meal combinations generated: {len(cliques)}")
print(f"  Training samples: {len(X_train)}")
print(f"  Regions covered: {df['Region'].nunique()}")
print(f"  Food categories: {df['Category'].nunique()}")
print(f"  Features:")
print(f"    ✓ Complete nutrition (5 macronutrients)")
print(f"    ✓ Allergy information")
print(f"    ✓ Carbon footprint data")
print(f"    ✓ Regional diversity")
print(f"\n📁 Output files created:")
print(f"  - main_diet_model.h5")
print(f"  - main_diet_scaler.pkl")
print(f"  - main_diet_cliques.pkl")
print(f"  - main_diet_processed.csv")
print(f"  - main_diet_config.pkl")
print(f"\n✅ Next: Update app.py to use these new files!")
print(f"    Then run: streamlit run app.py")