import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def main():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    print()
    print("=" * 65)
    print("PLACEMUX MARKETPLACE EVENT CHECK")
    print("=" * 65)

    cursor.execute("""
        SELECT
            event_name,
            COUNT(*) AS event_count
        FROM marketplace_events
        GROUP BY event_name
        ORDER BY event_count DESC
    """)

    rows = cursor.fetchall()

    if not rows:

        print(
            "No marketplace events found."
        )

    else:

        for event_name, count in rows:

            print(
                f"{event_name:35} "
                f"{count:,}"
            )

    cursor.execute("""
        SELECT COUNT(*)
        FROM marketplace_events
    """)

    total_events = cursor.fetchone()[0]

    print()
    print(
        f"Total events: {total_events:,}"
    )

    print("=" * 65)

    connection.close()


if __name__ == "__main__":
    main()