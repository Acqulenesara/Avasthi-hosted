import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def load_kg_edges():
    kg = {}
    with open(DATA_DIR / "kg_edgelist.csv", newline='') as f:
        for row in csv.DictReader(f):
            source = row["source"]
            relation = row["relation"]
            target = row["target"]

            if not source.startswith("ACTIVITY::"):
                continue

            title = source.replace("ACTIVITY::", "")
            if "NaN" in target:
                continue

            kg.setdefault(title, {}).setdefault(relation, []).append(target)
    return kg