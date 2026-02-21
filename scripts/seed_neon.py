"""
Run this once to populate Neon with all required data.
Usage: python scripts/seed_neon.py
"""
import os
import csv
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from psycopg2.extras import execute_values

# ── Connection ────────────────────────────────────────────────
NEON_URL = "postgresql://neondb_owner:npg_wZsvfid1tK9N@ep-sparkling-cake-aiqx75vr-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_conn():
    return psycopg2.connect(NEON_URL)

# ── Paths ─────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "recom" / "data"
ACTIVITIES_CSV = DATA_DIR / "activities.csv"
KG_CSV         = DATA_DIR / "kg_edgelist.csv"

# ─────────────────────────────────────────────────────────────
# 1. Create tables if they don't exist yet
# ─────────────────────────────────────────────────────────────
CREATE_TABLES_SQL = """
DROP TABLE IF EXISTS kg_edges CASCADE;
DROP TABLE IF EXISTS entities CASCADE;
DROP TABLE IF EXISTS activities CASCADE;

CREATE TABLE activities (
    id               SERIAL PRIMARY KEY,
    title            TEXT NOT NULL UNIQUE,
    short_description TEXT,
    modality         TEXT,
    duration         INTEGER,
    difficulty       TEXT,
    expected_environment TEXT,
    contraindications TEXT,
    evidence         TEXT,
    visual_asset_id  TEXT
);

CREATE TABLE entities (
    id     SERIAL PRIMARY KEY,
    name   TEXT NOT NULL UNIQUE,
    type   TEXT
);

CREATE TABLE kg_edges (
    id       SERIAL PRIMARY KEY,
    source   TEXT NOT NULL,
    relation TEXT NOT NULL,
    target   TEXT NOT NULL,
    UNIQUE(source, relation, target)
);

CREATE TABLE IF NOT EXISTS feedback (
    id             SERIAL PRIMARY KEY,
    username       TEXT NOT NULL,
    activity_title TEXT NOT NULL,
    liked          BOOLEAN NOT NULL,
    timestamp      TIMESTAMP DEFAULT NOW(),
    UNIQUE(username, activity_title)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id              SERIAL PRIMARY KEY,
    username        TEXT NOT NULL,
    preference_type TEXT NOT NULL,
    content         TEXT NOT NULL,
    UNIQUE(username, preference_type, content)
);
"""

# ─────────────────────────────────────────────────────────────
# 2. Seed activities
# ─────────────────────────────────────────────────────────────
def seed_activities(cur):
    print("📋 Seeding activities...")
    with open(ACTIVITIES_CSV, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    data = []
    for r in rows:
        try:
            duration = int(r.get("duration", 0))
        except ValueError:
            duration = 0
        data.append((
            r["title"].strip(),
            r.get("short_description", "").strip(),
            r.get("modality", "").strip(),
            duration,
            r.get("difficulty", "").strip(),
            r.get("expected_environment", "").strip(),
            r.get("contraindications", "").strip(),
            r.get("evidence", "").strip(),
            r.get("visual_asset_id", "").strip(),
        ))

    execute_values(cur, """
        INSERT INTO activities
            (title, short_description, modality, duration, difficulty,
             expected_environment, contraindications, evidence, visual_asset_id)
        VALUES %s
        ON CONFLICT (title) DO NOTHING
    """, data)
    print(f"   ✅ {len(data)} activities inserted (duplicates skipped)")

# ─────────────────────────────────────────────────────────────
# 3. Seed KG edges + derive entities
# ─────────────────────────────────────────────────────────────
def seed_kg(cur):
    print("🔗 Seeding KG edges & entities...")
    with open(KG_CSV, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    edges = [(r["source"].strip(), r["relation"].strip(), r["target"].strip()) for r in rows]

    # Collect unique entity names + types
    entity_map = {}
    for source, relation, target in edges:
        src_type = source.split("::")[0] if "::" in source else "UNKNOWN"
        tgt_type = target.split("::")[0] if "::" in target else "UNKNOWN"
        entity_map[source] = src_type
        entity_map[target] = tgt_type

    # Insert entities
    execute_values(cur, """
        INSERT INTO entities (name, type) VALUES %s
        ON CONFLICT (name) DO NOTHING
    """, list(entity_map.items()))
    print(f"   ✅ {len(entity_map)} entities inserted")

    # Insert edges
    execute_values(cur, """
        INSERT INTO kg_edges (source, relation, target) VALUES %s
        ON CONFLICT (source, relation, target) DO NOTHING
    """, edges)
    print(f"   ✅ {len(edges)} KG edges inserted")

# ─────────────────────────────────────────────────────────────
# 4. Seed professionals (for consultation module)
# ─────────────────────────────────────────────────────────────
PROFESSIONALS = [
    ("Dr. Ayesha Khan",    "Anxiety & Stress",      "Specializes in CBT for anxiety and workplace stress."),
    ("Dr. Rohan Mehta",    "Depression & Grief",    "Expert in grief counseling and mood disorders."),
    ("Dr. Priya Sharma",   "Relationships",         "Focuses on relationship issues and communication."),
    ("Dr. Arjun Nair",     "Academic Stress",       "Helps students manage academic pressure and burnout."),
    ("Dr. Fatima Siddiqui","Trauma & PTSD",         "Trauma-informed therapist with EMDR certification."),
]

def seed_professionals(cur):
    print("👩‍⚕️ Seeding professionals...")
    cur.execute("SELECT COUNT(*) FROM professionals")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"   ⏭️  Already has {count} professionals, skipping.")
        return

    execute_values(cur, """
        INSERT INTO professionals (full_name, specialty, bio) VALUES %s
    """, PROFESSIONALS)
    print(f"   ✅ {len(PROFESSIONALS)} professionals inserted")

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    print("\n🚀 Connecting to Neon...")
    try:
        conn = get_conn()
        conn.autocommit = False
        cur = conn.cursor()
        print("   ✅ Connected\n")

        # Neon requires explicit schema selection
        cur.execute("SET search_path TO public;")

        print("🏗️  Creating tables...")
        cur.execute(CREATE_TABLES_SQL)
        print("   ✅ Tables ready\n")

        seed_activities(cur)
        seed_kg(cur)
        seed_professionals(cur)

        conn.commit()
        print("\n🎉 All done! Neon is fully seeded.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback; traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
