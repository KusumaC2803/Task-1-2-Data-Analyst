import sqlite3
from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DB_PATH = DATA_DIR / "placemux.db"
POSTINGS_PATH = DATA_DIR / "postings.csv"


# ---------------------------------------------------------
# Database schema
# ---------------------------------------------------------

def create_tables(connection):

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE companies (
            company_id TEXT PRIMARY KEY,
            company_name TEXT,
            location TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE jobs (
            job_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            title TEXT,
            location TEXT,
            work_type TEXT,
            experience_level TEXT,
            listed_time TEXT,
            expiry TEXT,
            closed_time TEXT,
            remote_allowed INTEGER,
            FOREIGN KEY (company_id)
                REFERENCES companies(company_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE job_metrics (
            job_id TEXT PRIMARY KEY,
            views INTEGER DEFAULT 0,
            applies INTEGER DEFAULT 0,
            FOREIGN KEY (job_id)
                REFERENCES jobs(job_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE marketplace_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            actor_type TEXT NOT NULL,
            actor_id TEXT,
            entity_type TEXT,
            entity_id TEXT,
            event_time TEXT NOT NULL,
            properties TEXT
        )
    """)

    connection.commit()


# ---------------------------------------------------------
# Build database
# ---------------------------------------------------------

def build_database():

    if not POSTINGS_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {POSTINGS_PATH}"
        )

    # -----------------------------------------------------
    # Always create a fresh database
    # -----------------------------------------------------

    if DB_PATH.exists():
        print("Removing existing database...")
        DB_PATH.unlink()

    print("Creating PlaceMux database...")

    connection = sqlite3.connect(DB_PATH)

    # Enable foreign-key validation
    connection.execute("PRAGMA foreign_keys = ON")

    create_tables(connection)

    # -----------------------------------------------------
    # Columns required from the raw dataset
    # -----------------------------------------------------

    columns = [
        "job_id",
        "company_id",
        "company_name",
        "title",
        "location",
        "views",
        "applies",
        "listed_time",
        "expiry",
        "closed_time",
        "formatted_experience_level",
        "remote_allowed",
        "work_type",
    ]

    total_rows = 0
    skipped_jobs = 0
    inserted_jobs = 0

    print("Reading postings.csv in chunks...")
    print()

    # -----------------------------------------------------
    # Read the 517 MB file in chunks
    # -----------------------------------------------------

    for chunk in pd.read_csv(
        POSTINGS_PATH,
        usecols=columns,
        chunksize=10000,
        low_memory=False
    ):

        total_rows += len(chunk)

        # -------------------------------------------------
        # Basic numeric cleaning
        # -------------------------------------------------

        chunk["views"] = pd.to_numeric(
            chunk["views"],
            errors="coerce"
        ).fillna(0).astype(int)

        chunk["applies"] = pd.to_numeric(
            chunk["applies"],
            errors="coerce"
        ).fillna(0).astype(int)

        chunk["remote_allowed"] = pd.to_numeric(
            chunk["remote_allowed"],
            errors="coerce"
        ).fillna(0).astype(int)

        # -------------------------------------------------
        # Remove duplicate job records inside chunk
        # -------------------------------------------------

        chunk = chunk.drop_duplicates(
            subset=["job_id"]
        )

        # -------------------------------------------------
        # Identify orphan jobs
        #
        # These have job_id but no company_id.
        # We keep the raw source unchanged but exclude
        # them from the relational marketplace model.
        # -------------------------------------------------

        orphan_jobs = chunk[
            chunk["job_id"].notna()
            & chunk["company_id"].isna()
        ]

        skipped_jobs += len(orphan_jobs)

        # -------------------------------------------------
        # Keep only jobs with both IDs
        # -------------------------------------------------

        valid_chunk = chunk.dropna(
            subset=["job_id", "company_id"]
        ).copy()

        # -------------------------------------------------
        # Companies
        # -------------------------------------------------

        companies = (
            valid_chunk[
                [
                    "company_id",
                    "company_name",
                    "location"
                ]
            ]
            .drop_duplicates(
                subset=["company_id"]
            )
        )

        company_records = []

        for row in companies.itertuples(index=False):

            company_records.append(
                (
                    row.company_id,
                    row.company_name,
                    row.location
                )
            )

        connection.executemany(
            """
            INSERT OR IGNORE INTO companies
            (
                company_id,
                company_name,
                location
            )
            VALUES (?, ?, ?)
            """,
            company_records
        )

        # -------------------------------------------------
        # Jobs
        # -------------------------------------------------

        jobs = valid_chunk[
            [
                "job_id",
                "company_id",
                "title",
                "location",
                "work_type",
                "formatted_experience_level",
                "listed_time",
                "expiry",
                "closed_time",
                "remote_allowed"
            ]
        ].copy()

        jobs = jobs.drop_duplicates(
            subset=["job_id"]
        )

        job_records = []

        for row in jobs.itertuples(index=False):

            job_records.append(
                (
                    row.job_id,
                    row.company_id,
                    row.title,
                    row.location,
                    row.work_type,
                    row.formatted_experience_level,
                    row.listed_time,
                    row.expiry,
                    row.closed_time,
                    row.remote_allowed
                )
            )

        connection.executemany(
            """
            INSERT OR IGNORE INTO jobs
            (
                job_id,
                company_id,
                title,
                location,
                work_type,
                experience_level,
                listed_time,
                expiry,
                closed_time,
                remote_allowed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            job_records
        )

        inserted_jobs += len(job_records)

        # -------------------------------------------------
        # Job metrics
        # -------------------------------------------------

        metrics = valid_chunk[
            [
                "job_id",
                "views",
                "applies"
            ]
        ].copy()

        metrics = metrics.drop_duplicates(
            subset=["job_id"]
        )

        metric_records = []

        for row in metrics.itertuples(index=False):

            metric_records.append(
                (
                    row.job_id,
                    int(row.views),
                    int(row.applies)
                )
            )

        connection.executemany(
            """
            INSERT OR IGNORE INTO job_metrics
            (
                job_id,
                views,
                applies
            )
            VALUES (?, ?, ?)
            """,
            metric_records
        )

        # -------------------------------------------------
        # Progress
        # -------------------------------------------------

        print(
            f"Processed: {total_rows:,} rows | "
            f"Valid jobs: {inserted_jobs:,} | "
            f"Skipped orphan jobs: {skipped_jobs:,}"
        )

    # -----------------------------------------------------
    # Commit
    # -----------------------------------------------------

    connection.commit()

    # -----------------------------------------------------
    # Final counts
    # -----------------------------------------------------

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM companies"
    )
    company_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM jobs"
    )
    job_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM job_metrics"
    )
    metric_count = cursor.fetchone()[0]

    connection.close()

    # -----------------------------------------------------
    # Final report
    # -----------------------------------------------------

    print()
    print("=" * 65)
    print("DATABASE CREATED SUCCESSFULLY")
    print("=" * 65)

    print(f"Raw rows processed:        {total_rows:,}")
    print(f"Companies created:         {company_count:,}")
    print(f"Jobs created:              {job_count:,}")
    print(f"Job metrics created:       {metric_count:,}")
    print(f"Orphan jobs excluded:      {skipped_jobs:,}")

    print()
    print(f"Database location:")
    print(DB_PATH)

    print("=" * 65)


if __name__ == "__main__":
    build_database()