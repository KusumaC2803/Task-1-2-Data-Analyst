import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def run_check(
    cursor,
    name,
    query
):
    """
    Run a data-quality query.
    A zero result means the check passed.
    """

    cursor.execute(query)

    result = cursor.fetchone()[0]

    status = "PASS" if result == 0 else "FAIL"

    print(
        f"{name:45} "
        f"{result:10}  "
        f"{status}"
    )

    return result


def main():

    if not DB_PATH.exists():

        print(
            f"Database not found: {DB_PATH}"
        )

        return

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    print()
    print("=" * 80)
    print("PLACEMUX DATA QUALITY CHECK")
    print("=" * 80)

    failures = 0

    # -----------------------------------------------------
    # 1. NULL job IDs
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs with NULL job_id",
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE job_id IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 2. NULL company IDs
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs with NULL company_id",
        """
        SELECT COUNT(*)
        FROM jobs
        WHERE company_id IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 3. Duplicate job IDs
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Duplicate job IDs",
        """
        SELECT COUNT(*)
        FROM (
            SELECT job_id
            FROM jobs
            GROUP BY job_id
            HAVING COUNT(*) > 1
        )
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 4. Orphan jobs
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs with missing company reference",
        """
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN companies c
            ON j.company_id = c.company_id
        WHERE c.company_id IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 5. Negative views
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs with negative views",
        """
        SELECT COUNT(*)
        FROM job_metrics
        WHERE views < 0
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 6. Negative applications
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs with negative applications",
        """
        SELECT COUNT(*)
        FROM job_metrics
        WHERE applies < 0
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 7. Applications greater than views
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Applications greater than views",
        """
        SELECT COUNT(*)
        FROM job_metrics
        WHERE applies > views
        AND views > 0
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 8. Missing job metrics
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Jobs without job metrics",
        """
        SELECT COUNT(*)
        FROM jobs j
        LEFT JOIN job_metrics jm
            ON j.job_id = jm.job_id
        WHERE jm.job_id IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 9. Duplicate marketplace events
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Duplicate event records",
        """
        SELECT COUNT(*)
        FROM (
            SELECT
                event_name,
                actor_id,
                entity_id,
                event_time,
                COUNT(*) AS duplicate_count
            FROM marketplace_events
            GROUP BY
                event_name,
                actor_id,
                entity_id,
                event_time
            HAVING COUNT(*) > 1
        )
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 10. Missing event name
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Events with missing event_name",
        """
        SELECT COUNT(*)
        FROM marketplace_events
        WHERE event_name IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # 11. Missing event timestamp
    # -----------------------------------------------------

    result = run_check(
        cursor,
        "Events with missing timestamp",
        """
        SELECT COUNT(*)
        FROM marketplace_events
        WHERE event_time IS NULL
        """
    )

    failures += result > 0

    # -----------------------------------------------------
    # Event count
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM marketplace_events
    """)

    total_events = cursor.fetchone()[0]

    # -----------------------------------------------------
    # Latest event
    # -----------------------------------------------------

    cursor.execute("""
        SELECT MAX(event_time)
        FROM marketplace_events
    """)

    latest_event = cursor.fetchone()[0]

    print()
    print(
        f"Total marketplace events: "
        f"{total_events:,}"
    )

    print(
        f"Latest event:             "
        f"{latest_event}"
    )

    # -----------------------------------------------------
    # Final status
    # -----------------------------------------------------

    print()
    print("=" * 80)

    if failures == 0:

        print(
            "DATA QUALITY STATUS: PASS"
        )

    else:

        print(
            f"DATA QUALITY STATUS: "
            f"FAIL ({failures} checks failed)"
        )

    print("=" * 80)

    connection.close()


if __name__ == "__main__":
    main()