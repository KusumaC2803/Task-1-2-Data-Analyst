import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def main():

    if not DB_PATH.exists():
        print("Database not found.")
        print(f"Expected location: {DB_PATH}")
        return

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    tables = [
        "companies",
        "jobs",
        "job_metrics",
        "marketplace_events"
    ]

    print()
    print("=" * 60)
    print("PLACEMUX DATABASE CHECK")
    print("=" * 60)

    for table in tables:

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(
            f"{table:25} {count:,} rows"
        )

    # -----------------------------------------------------
    # Check orphan jobs
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN companies c
            ON j.company_id = c.company_id
        WHERE c.company_id IS NULL
    """)

    orphan_jobs = cursor.fetchone()[0]

    print()
    print(
        f"Orphan jobs in processed DB: "
        f"{orphan_jobs:,}"
    )

    # -----------------------------------------------------
    # Check duplicate jobs
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT job_id
            FROM jobs
            GROUP BY job_id
            HAVING COUNT(*) > 1
        )
    """)

    duplicate_jobs = cursor.fetchone()[0]

    print(
        f"Duplicate job IDs:           "
        f"{duplicate_jobs:,}"
    )

    print("=" * 60)

    connection.close()


if __name__ == "__main__":
    main()