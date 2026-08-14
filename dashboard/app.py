import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "placemux.db"


st.set_page_config(
    page_title="PlaceMux Marketplace Health",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# =========================================================
# MARKETPLACE KPI DATA
# =========================================================

@st.cache_data(ttl=60)
def get_marketplace_metrics():

    connection = get_connection()

    query = """
        SELECT
            COUNT(*) AS total_jobs,

            COALESCE(SUM(jm.views), 0)
                AS total_views,

            COALESCE(SUM(jm.applies), 0)
                AS total_applications,

            SUM(
                CASE
                    WHEN jm.applies > 0
                    THEN 1
                    ELSE 0
                END
            ) AS jobs_with_applications,

            SUM(
                CASE
                    WHEN jm.applies = 0
                    THEN 1
                    ELSE 0
                END
            ) AS jobs_without_applications,

            COALESCE(AVG(jm.views), 0)
                AS average_views,

            COALESCE(AVG(jm.applies), 0)
                AS average_applications

        FROM jobs j

        JOIN job_metrics jm
            ON j.job_id = jm.job_id
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return result.iloc[0]


# =========================================================
# TOP JOBS
# =========================================================

@st.cache_data(ttl=60)
def get_top_jobs():

    connection = get_connection()

    query = """
        SELECT
            j.job_id,
            j.title,
            j.location,
            j.work_type,
            jm.views,
            jm.applies,

            ROUND(
                jm.applies * 100.0 /
                NULLIF(jm.views, 0),
                2
            ) AS conversion_rate

        FROM jobs j

        JOIN job_metrics jm
            ON j.job_id = jm.job_id

        WHERE jm.applies > 0

        ORDER BY jm.applies DESC

        LIMIT 10
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data


# =========================================================
# HIGH VIEW / ZERO APPLICATION JOBS
# =========================================================

@st.cache_data(ttl=60)
def get_zero_application_jobs():

    connection = get_connection()

    query = """
        SELECT
            j.job_id,
            j.title,
            j.location,
            jm.views,
            jm.applies

        FROM jobs j

        JOIN job_metrics jm
            ON j.job_id = jm.job_id

        WHERE jm.views > 0
          AND jm.applies = 0

        ORDER BY jm.views DESC

        LIMIT 20
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data


# =========================================================
# EVENT SUMMARY
# =========================================================

@st.cache_data(ttl=60)
def get_event_summary():

    connection = get_connection()

    query = """
        SELECT
            event_name,
            COUNT(*) AS event_count

        FROM marketplace_events

        GROUP BY event_name

        ORDER BY event_count DESC
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data


# =========================================================
# DATA QUALITY
# =========================================================

def run_quality_checks():

    connection = get_connection()

    checks = {
        "NULL Job IDs": """
            SELECT COUNT(*)
            FROM jobs
            WHERE job_id IS NULL
        """,

        "NULL Company IDs": """
            SELECT COUNT(*)
            FROM jobs
            WHERE company_id IS NULL
        """,

        "Duplicate Job IDs": """
            SELECT COUNT(*)
            FROM (
                SELECT job_id
                FROM jobs
                GROUP BY job_id
                HAVING COUNT(*) > 1
            )
        """,

        "Missing Company Reference": """
            SELECT COUNT(*)
            FROM jobs j
            LEFT JOIN companies c
                ON j.company_id = c.company_id
            WHERE c.company_id IS NULL
        """,

        "Negative Views": """
            SELECT COUNT(*)
            FROM job_metrics
            WHERE views < 0
        """,

        "Negative Applications": """
            SELECT COUNT(*)
            FROM job_metrics
            WHERE applies < 0
        """,

        "Applications Greater Than Views": """
            SELECT COUNT(*)
            FROM job_metrics
            WHERE applies > views
        """
    }

    results = []

    for check_name, query in checks.items():

        value = connection.execute(
            query
        ).fetchone()[0]

        results.append({
            "Check": check_name,
            "Issues": value,
            "Status": "PASS" if value == 0 else "CHECK"
        })

    connection.close()

    return pd.DataFrame(results)


# =========================================================
# EVENT FRESHNESS
# =========================================================

def get_event_health():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM marketplace_events
    """)

    event_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MAX(event_time)
        FROM marketplace_events
    """)

    latest_event = cursor.fetchone()[0]

    connection.close()

    return event_count, latest_event


# =========================================================
# HEADER
# =========================================================

st.title("📊 PlaceMux Marketplace Health")

st.caption(
    "Marketplace liquidity, discovery and event-tracking dashboard"
)

st.divider()


# =========================================================
# LOAD METRICS
# =========================================================

metrics = get_marketplace_metrics()

total_jobs = int(metrics["total_jobs"])

total_views = int(metrics["total_views"])

total_applications = int(
    metrics["total_applications"]
)

jobs_with_applications = int(
    metrics["jobs_with_applications"]
)

jobs_without_applications = int(
    metrics["jobs_without_applications"]
)

average_views = float(
    metrics["average_views"]
)

average_applications = float(
    metrics["average_applications"]
)


# =========================================================
# CALCULATED LIQUIDITY METRICS
# =========================================================

application_coverage = (
    jobs_with_applications * 100.0 / total_jobs
    if total_jobs > 0
    else 0
)

view_to_application_rate = (
    total_applications * 100.0 / total_views
    if total_views > 0
    else 0
)


# =========================================================
# MAIN KPIs
# =========================================================

st.subheader("Marketplace Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Published Jobs",
        f"{total_jobs:,}"
    )

with col2:

    st.metric(
        "Job Views",
        f"{total_views:,}"
    )

with col3:

    st.metric(
        "Applications",
        f"{total_applications:,}"
    )

with col4:

    st.metric(
        "Application Coverage",
        f"{application_coverage:.2f}%"
    )


col5, col6, col7, col8 = st.columns(4)

with col5:

    st.metric(
        "View → Application",
        f"{view_to_application_rate:.2f}%"
    )

with col6:

    st.metric(
        "Zero-Application Jobs",
        f"{jobs_without_applications:,}"
    )

with col7:

    st.metric(
        "Avg Views / Job",
        f"{average_views:.2f}"
    )

with col8:

    st.metric(
        "Avg Applications / Job",
        f"{average_applications:.2f}"
    )


st.divider()


# =========================================================
# MARKETPLACE INTERPRETATION
# =========================================================

st.subheader("Marketplace Decision Signal")

if application_coverage < 20:

    st.warning(
        f"Only {application_coverage:.2f}% of jobs have "
        "received at least one application. This suggests "
        "a marketplace liquidity problem on the demand side."
    )

elif application_coverage < 40:

    st.info(
        f"{application_coverage:.2f}% of jobs have received "
        "at least one application. Candidate demand is "
        "present but coverage can be improved."
    )

else:

    st.success(
        f"{application_coverage:.2f}% of jobs have received "
        "at least one application."
    )


st.markdown(
    """
### What should the team investigate?

- **High views + zero applications:** possible job quality,
  relevance or conversion problem.
- **Low views + zero applications:** possible discovery/search
  problem.
- **High applications:** useful supply-demand signal.
- **Low application coverage:** investigate marketplace
  matching and candidate discovery.
"""
)


# =========================================================
# ZERO APPLICATION JOBS
# =========================================================

st.subheader(
    "Jobs With Visibility but No Applications"
)

zero_jobs = get_zero_application_jobs()

if not zero_jobs.empty:

    st.dataframe(
        zero_jobs,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "These jobs are useful candidates for investigation "
        "because they have received views but no applications."
    )

else:

    st.success(
        "No zero-application jobs found."
    )


st.divider()


# =========================================================
# TOP JOBS
# =========================================================

st.subheader("Top Jobs by Applications")

top_jobs = get_top_jobs()

if not top_jobs.empty:

    fig = px.bar(
        top_jobs.sort_values("applies"),
        x="applies",
        y="title",
        orientation="h",
        hover_data=[
            "location",
            "views",
            "conversion_rate"
        ],
        title="Jobs Receiving the Most Applications"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# EVENT TRACKING
# =========================================================

st.subheader("Marketplace Event Tracking")

events = get_event_summary()

if not events.empty:

    col1, col2 = st.columns([2, 1])

    with col1:

        fig = px.bar(
            events,
            x="event_name",
            y="event_count",
            title="Tracked Marketplace Events"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True
        )

else:

    st.warning(
        "No marketplace events have been recorded."
    )


# =========================================================
# EVENT HEALTH
# =========================================================

st.subheader("Event Pipeline Health")

event_count, latest_event = get_event_health()

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Tracked Events",
        f"{event_count:,}"
    )

with col2:

    st.metric(
        "Latest Event",
        latest_event if latest_event else "No events"
    )


if event_count > 0:

    st.success(
        "Marketplace event data is flowing into the database."
    )

else:

    st.error(
        "No marketplace events detected."
    )


# =========================================================
# DATA QUALITY
# =========================================================

st.subheader("Data Quality")

quality_df = run_quality_checks()

st.dataframe(
    quality_df,
    use_container_width=True,
    hide_index=True
)

failed_checks = quality_df[
    quality_df["Status"] != "PASS"
]

if failed_checks.empty:

    st.success(
        "All current marketplace data-quality checks passed."
    )

else:

    st.warning(
        f"{len(failed_checks)} data-quality check(s) "
        "need attention."
    )


# =========================================================
# METRIC DEFINITIONS
# =========================================================

st.subheader("Metric Dictionary")

metric_dictionary = pd.DataFrame([
    {
        "Metric": "Application Coverage",
        "Definition": "Jobs receiving at least one application / total jobs",
        "Decision": "Measures whether marketplace supply is receiving candidate demand"
    },
    {
        "Metric": "View → Application Rate",
        "Definition": "Total applications / total job views",
        "Decision": "Measures conversion after job discovery"
    },
    {
        "Metric": "Zero-Application Jobs",
        "Definition": "Jobs with zero recorded applications",
        "Decision": "Identifies marketplace supply that is not receiving demand"
    },
    {
        "Metric": "Average Applications / Job",
        "Definition": "Total applications / total jobs",
        "Decision": "Tracks overall candidate demand"
    },
    {
        "Metric": "Average Views / Job",
        "Definition": "Total views / total jobs",
        "Decision": "Tracks overall job visibility"
    }
])

st.dataframe(
    metric_dictionary,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# SOURCE / TRACEABILITY
# =========================================================

st.subheader("Data Source & Traceability")

st.markdown(
    """
**Raw source:** Public LinkedIn Job Postings dataset.

**Raw file:** `data/postings.csv`

**Processed database:** `data/placemux.db`

**Main tables:**

- `companies`
- `jobs`
- `job_metrics`
- `marketplace_events`

**Metric flow:**

`Raw CSV → Processed Tables → SQL → Dashboard`

The raw dataset is preserved separately from the processed
analytics model so that metric calculations can be traced
back to the source.
"""
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "PlaceMux · Week 2 · Phase 2 · Company Onboarding & Marketplace Data"
)