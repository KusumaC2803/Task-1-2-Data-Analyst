import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/postings.csv")

IMPORTANT_COLUMNS = [
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


def inspect_postings():

    print("=" * 70)
    print("PLACEMUX MARKETPLACE DATA INSPECTION")
    print("=" * 70)

    # ---------------------------------------------------------
    # Step 1: Read only the header
    # ---------------------------------------------------------

    header = pd.read_csv(DATA_PATH, nrows=0)

    print("\nTOTAL COLUMNS:", len(header.columns))

    print("\nALL COLUMNS:")
    for column in header.columns:
        print(f"  {column}")

    # ---------------------------------------------------------
    # Step 2: Check requested columns
    # ---------------------------------------------------------

    available = [
        column for column in IMPORTANT_COLUMNS
        if column in header.columns
    ]

    missing = [
        column for column in IMPORTANT_COLUMNS
        if column not in header.columns
    ]

    print("\nIMPORTANT COLUMNS FOUND:")
    for column in available:
        print(f"  ✓ {column}")

    if missing:
        print("\nIMPORTANT COLUMNS NOT FOUND:")
        for column in missing:
            print(f"  ✗ {column}")

    # ---------------------------------------------------------
    # Step 3: Read a small sample
    # ---------------------------------------------------------

    sample = pd.read_csv(
        DATA_PATH,
        usecols=available,
        nrows=1000
    )

    print("\nSAMPLE DATA:")
    print(sample.head(5).to_string())

    # ---------------------------------------------------------
    # Step 4: Data types
    # ---------------------------------------------------------

    print("\nDATA TYPES:")
    print(sample.dtypes)

    # ---------------------------------------------------------
    # Step 5: Missing values
    # ---------------------------------------------------------

    print("\nMISSING VALUES IN SAMPLE:")

    missing_values = sample.isnull().sum()

    for column, count in missing_values.items():
        percentage = (count / len(sample)) * 100

        print(
            f"{column:30} "
            f"{count:6} missing "
            f"({percentage:.2f}%)"
        )

    # ---------------------------------------------------------
    # Step 6: Duplicate job IDs
    # ---------------------------------------------------------

    duplicate_jobs = sample["job_id"].duplicated().sum()

    print("\nDUPLICATE JOB IDs IN SAMPLE:")
    print(duplicate_jobs)

    # ---------------------------------------------------------
    # Step 7: Basic statistics
    # ---------------------------------------------------------

    print("\nNUMERIC SUMMARY:")

    numeric_columns = [
        column
        for column in ["views", "applies"]
        if column in sample.columns
    ]

    if numeric_columns:
        print(sample[numeric_columns].describe())

    # ---------------------------------------------------------
    # Step 8: Process larger dataset in chunks
    # ---------------------------------------------------------

    print("\nPROCESSING DATASET IN CHUNKS...")

    total_rows = 0
    total_jobs = 0
    total_views = 0
    total_applies = 0

    for chunk in pd.read_csv(
        DATA_PATH,
        usecols=available,
        chunksize=10000
    ):

        total_rows += len(chunk)

        if "job_id" in chunk.columns:
            total_jobs += chunk["job_id"].nunique()

        if "views" in chunk.columns:
            total_views += pd.to_numeric(
                chunk["views"],
                errors="coerce"
            ).fillna(0).sum()

        if "applies" in chunk.columns:
            total_applies += pd.to_numeric(
                chunk["applies"],
                errors="coerce"
            ).fillna(0).sum()

    print("\nDATASET SUMMARY:")
    print(f"Rows:   {total_rows:,}")
    print(f"Jobs:   {total_jobs:,}")
    print(f"Views:  {total_views:,.0f}")
    print(f"Applies:{total_applies:,.0f}")

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    inspect_postings()