import sqlite3
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def seed_events():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("Creating marketplace events...")

    # ---------------------------------------------------------
    # 1. Company signup events
    # ---------------------------------------------------------

    cursor.execute("""
        INSERT INTO marketplace_events
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            properties
        )
        SELECT
            'company_signed_up',
            'company',
            company_id,
            'company',
            company_id,
            datetime('now'),
            '{"source":"marketplace"}'
        FROM companies
    """)

    print(
        "Company signup events created:",
        cursor.rowcount
    )

    # ---------------------------------------------------------
    # 2. Job created events
    # ---------------------------------------------------------

    cursor.execute("""
        INSERT INTO marketplace_events
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            properties
        )
        SELECT
            'job_created',
            'company',
            company_id,
            'job',
            job_id,
            listed_time,
            json_object(
                'title', title,
                'location', location,
                'work_type', work_type
            )
        FROM jobs
        WHERE company_id IS NOT NULL
    """)

    print(
        "Job created events created:",
        cursor.rowcount
    )

    # ---------------------------------------------------------
    # 3. Job published events
    # ---------------------------------------------------------

    cursor.execute("""
        INSERT INTO marketplace_events
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            properties
        )
        SELECT
            'job_published',
            'company',
            company_id,
            'job',
            job_id,
            listed_time,
            '{}'
        FROM jobs
        WHERE listed_time IS NOT NULL
    """)

    print(
        "Job published events created:",
        cursor.rowcount
    )

    # ---------------------------------------------------------
    # 4. Job viewed events
    #
    # We store representative tracking events rather than
    # inserting millions of individual view records.
    # ---------------------------------------------------------

    cursor.execute("""
        INSERT INTO marketplace_events
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            properties
        )
        SELECT
            'job_viewed',
            'candidate',
            'anonymous_candidate',
            'job',
            jm.job_id,
            datetime('now'),
            json_object(
                'view_count', jm.views
            )
        FROM job_metrics jm
        WHERE jm.views > 0
        LIMIT 10000
    """)

    print(
        "Job view events created:",
        cursor.rowcount
    )

    # ---------------------------------------------------------
    # 5. Candidate application events
    #
    # The public dataset contains application counts rather
    # than individual candidate identities.
    # ---------------------------------------------------------

    cursor.execute("""
        INSERT INTO marketplace_events
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            properties
        )
        SELECT
            'candidate_applied',
            'candidate',
            'anonymous_candidate',
            'job',
            jm.job_id,
            datetime('now'),
            json_object(
                'application_count', jm.applies
            )
        FROM job_metrics jm
        WHERE jm.applies > 0
        LIMIT 10000
    """)

    print(
        "Application events created:",
        cursor.rowcount
    )

    connection.commit()

    # ---------------------------------------------------------
    # Final event count
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM marketplace_events
    """)

    total = cursor.fetchone()[0]

    connection.close()

    print()
    print("=" * 50)
    print("EVENT SEEDING COMPLETE")
    print("=" * 50)
    print(f"Total events: {total:,}")


if __name__ == "__main__":
    seed_events()