# PlaceMux Marketplace Analytics

A data analytics project focused on understanding marketplace health, job supply, candidate demand, liquidity, marketplace events, and data quality.

The project uses a real-world public job-posting dataset and transforms it into a structured SQLite analytics database. The resulting metrics are displayed through an interactive Streamlit dashboard.

---

## Project Overview

The main objective of this project is to answer:

- How much job supply exists in the marketplace?
- Are jobs receiving candidate demand?
- How many jobs receive no applications?
- How effectively do job views convert into applications?
- What marketplace events are being tracked?
- Is the analytics data reliable enough to use for decision-making?

The project follows this flow:

Raw Dataset → Data Cleaning → SQLite Data Model → SQL Metrics → Event Tracking → Data Quality Checks → Dashboard

---

## Key Results

The initial dataset contained:

- 123,849 job postings
- 24,474 companies
- 1,785,765 job views
- 247,005 applications

Initial marketplace metrics:

| Metric | Result |
|---|---:|
| Total Jobs | 123,849 |
| Total Views | 1,785,765 |
| Total Applications | 247,005 |
| Jobs Receiving Applications | 23,320 |
| Jobs With Zero Applications | 100,529 |
| Application Coverage | 18.83% |
| View → Application Rate | 13.83% |
| Average Views / Job | 14.42 |
| Average Applications / Job | 1.99 |

The processed database excludes source records that could not be reliably connected to a company.

---

## Main Marketplace Metrics

### 1. Application Coverage

Measures the percentage of jobs that have received at least one application.

Formula:

Jobs with at least one application / Total jobs × 100

Business use:

A low value can indicate that a large part of marketplace supply is not receiving candidate demand.

---

### 2. View → Application Rate

Measures how many job views result in applications.

Formula:

Total applications / Total job views × 100

Business use:

Helps identify whether candidates are converting after discovering a job.

---

### 3. Zero-Application Jobs

Counts jobs that have received no applications.

Business use:

These jobs can be investigated for search visibility, job relevance, requirements, or candidate-job fit.

---

### 4. Average Applications per Job

Formula:

Total applications / Total jobs

Business use:

Provides a high-level view of candidate demand across marketplace supply.

---

### 5. Average Views per Job

Formula:

Total job views / Total jobs

Business use:

Provides a high-level indicator of job visibility.

---

## Data Model

The processed SQLite database contains four main tables:

### companies

Stores marketplace company information.

Important fields:

- company_id
- company_name
- location

### jobs

Stores marketplace job supply.

Important fields:

- job_id
- company_id
- title
- location
- work_type
- experience_level
- listed_time
- expiry
- closed_time
- remote_allowed

### job_metrics

Stores job engagement metrics.

Important fields:

- job_id
- views
- applies

### marketplace_events

Stores marketplace activity events.

Important fields:

- event_id
- event_name
- actor_type
- actor_id
- entity_type
- entity_id
- event_time
- properties

---

## Marketplace Event Tracking

The tracking plan covers the main marketplace journey:

Company Signup
→ Profile Completion
→ Job Creation
→ Job Publication
→ Candidate Search
→ Job View
→ Application
→ Shortlist
→ Rejection / Hire

Current tracked events include:

- company_signed_up
- company_profile_completed
- job_created
- job_published
- candidate_search
- job_viewed
- candidate_applied
- candidate_shortlisted
- candidate_rejected
- candidate_hired

The event structure was designed so that product activity can later be connected to marketplace health metrics.

---

## Data Quality

Data quality checks are included before metrics are used.

The project checks for:

- Missing job IDs
- Missing company IDs
- Duplicate job IDs
- Missing company references
- Negative views
- Negative applications
- Applications greater than views
- Missing job metrics
- Duplicate events
- Missing event names
- Missing event timestamps

### Source Data Issue Found

During validation, 1,717 job records were found without a `company_id`.

Instead of modifying the raw dataset, these records were excluded from the processed relational model because they could not be reliably connected to the `companies` table.

The raw source remains unchanged.

This prevents incorrect company-level joins and misleading marketplace metrics.

---

## Dashboard

The Streamlit dashboard provides:

- Marketplace overview
- Total jobs
- Total views
- Total applications
- Application coverage
- View-to-application rate
- Zero-application jobs
- Average views per job
- Average applications per job
- Top jobs by applications
- Marketplace event tracking
- Event pipeline health
- Data quality checks
- Metric definitions
- Data source traceability

---

## Technology Stack

- Python
- Pandas
- SQL
- SQLite
- Streamlit
- Plotly
- Git & GitHub

---

## Project Structure

```text
Task-1-2-Data-Analyst/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── companies/
│   ├── jobs/
│   ├── mappings/
│   └── placemux.db
│
├── docs/
│   ├── metric_dictionary.md
│   ├── tracking_plan.md
│   └── data_quality_notes.md
│
├── sql/
│   └── liquidity_metrics.sql
│
├── src/
│   ├── build_database.py
│   ├── check_database.py
│   ├── check_events.py
│   ├── data_quality.py
│   ├── event_tracker.py
│   ├── inspect_data.py
│   ├── run_metrics.py
│   └── seed_marketplace_events.py
│
├── .gitignore
├── requirements.txt
└── README.md
