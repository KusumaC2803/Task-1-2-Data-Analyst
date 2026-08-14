import sqlite3
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


def track_event(
    event_name,
    actor_type,
    actor_id,
    entity_type,
    entity_id,
    properties=None,
    event_time=None
):
    """
    Insert one marketplace event into the database.
    """

    if event_time is None:

        event_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
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
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_name,
            actor_type,
            actor_id,
            entity_type,
            entity_id,
            event_time,
            json.dumps(
                properties or {},
                separators=(",", ":")
            )
        )
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":

    track_event(
        event_name="company_signed_up",
        actor_type="company",
        actor_id="DEMO_COMPANY_001",
        entity_type="company",
        entity_id="DEMO_COMPANY_001",
        properties={
            "source": "demo"
        }
    )

    print(
        "Test marketplace event inserted successfully."
    )