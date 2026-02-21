import json
import psycopg2
import os

# Your PG config from your bot
PG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", 5432)),
    "dbname": os.getenv("PGDB", "mental_health_bot"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "1234")
}

OUTPUT_FILE = "ragas_data.jsonl"

def fetch_interactions():
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()

    cur.execute("""
        SELECT query, response, retrieved_context
        FROM interactions_for_ragas
        ORDER BY timestamp DESC
        LIMIT 200;
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return rows


def main():
    interactions = fetch_interactions()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for query, response, context in interactions:

            # context must be a list
            if isinstance(context, str):
                contexts = [c.strip() for c in context.split("\n") if c.strip()]
            else:
                contexts = context or []

            entry = {
                "question": query,
                "answer": response,
                "contexts": contexts,
                "ground_truth": ""
            }

            f.write(json.dumps(entry) + "\n")

    print(f"Export complete → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
