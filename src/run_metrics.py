import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def run_metrics():

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("=" * 65)
    print("PLACEMUX MARKETPLACE LIQUIDITY METRICS")
    print("=" * 65)

    # ---------------------------------------------------------
    # Basic marketplace metrics
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM jobs
    """)

    total_jobs = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(views)
        FROM job_metrics
    """)

    total_views = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(applies)
        FROM job_metrics
    """)

    total_applications = cursor.fetchone()[0] or 0

    # ---------------------------------------------------------
    # Jobs receiving applications
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM job_metrics
        WHERE applies > 0
    """)

    jobs_with_applications = cursor.fetchone()[0]

    jobs_without_applications = (
        total_jobs - jobs_with_applications
    )

    # ---------------------------------------------------------
    # Coverage
    # ---------------------------------------------------------

    job_application_coverage = (
        jobs_with_applications * 100.0 / total_jobs
        if total_jobs
        else 0
    )

    # ---------------------------------------------------------
    # Application conversion
    # ---------------------------------------------------------

    application_conversion = (
        total_applications * 100.0 / total_views
        if total_views
        else 0
    )

    # ---------------------------------------------------------
    # Averages
    # ---------------------------------------------------------

    cursor.execute("""
        SELECT
            AVG(views),
            AVG(applies)
        FROM job_metrics
    """)

    avg_views, avg_applications = cursor.fetchone()

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print(f"\nTotal Jobs:                    {total_jobs:,}")

    print(
        f"Total Job Views:              "
        f"{total_views:,}"
    )

    print(
        f"Total Applications:           "
        f"{total_applications:,}"
    )

    print(
        f"Jobs Receiving Applications:  "
        f"{jobs_with_applications:,}"
    )

    print(
        f"Jobs With Zero Applications:  "
        f"{jobs_without_applications:,}"
    )

    print(
        f"Application Coverage:         "
        f"{job_application_coverage:.2f}%"
    )

    print(
        f"View → Application Rate:      "
        f"{application_conversion:.2f}%"
    )

    print(
        f"Average Views / Job:           "
        f"{avg_views:.2f}"
    )

    print(
        f"Average Applications / Job:    "
        f"{avg_applications:.2f}"
    )

    print("\n" + "=" * 65)

    connection.close()


if __name__ == "__main__":
    run_metrics()