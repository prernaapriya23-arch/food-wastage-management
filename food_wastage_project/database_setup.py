"""
database_setup.py
Creates SQLite database and loads all CSV data into tables.
Run this once before launching the Streamlit app.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "food_wastage.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Create Tables ──────────────────────────────────────────────────────────
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT,
        Address       TEXT,
        City          TEXT,
        Contact       TEXT
    );

    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT,
        City          TEXT,
        Contact       TEXT
    );

    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID       INTEGER PRIMARY KEY,
        Food_Name     TEXT NOT NULL,
        Quantity      INTEGER,
        Expiry_Date   TEXT,
        Provider_ID   INTEGER,
        Provider_Type TEXT,
        Location      TEXT,
        Food_Type     TEXT,
        Meal_Type     TEXT,
        FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
    );

    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID      INTEGER PRIMARY KEY,
        Food_ID       INTEGER,
        Receiver_ID   INTEGER,
        Status        TEXT,
        Timestamp     TEXT,
        FOREIGN KEY (Food_ID)    REFERENCES food_listings(Food_ID),
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
    );
    """)

    conn.commit()

    # ── Load CSVs ──────────────────────────────────────────────────────────────
    tables = {
        "providers":     "providers_data.csv",
        "receivers":     "receivers_data.csv",
        "food_listings": "food_listings_data.csv",
        "claims":        "claims_data.csv",
    }

    for table, csv_file in tables.items():
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df.to_sql(table, conn, if_exists="replace", index=False)
            print(f"✅ Loaded {len(df)} rows into '{table}'")
        else:
            print(f"⚠️  {csv_file} not found — skipping '{table}'")

    conn.close()
    print(f"\n🎉 Database created: {DB_PATH}")

if __name__ == "__main__":
    create_database()
