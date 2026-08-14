# PlaceMux Marketplace Metric Dictionary

## 1. Job Application Coverage

### Definition
Percentage of jobs that have received at least one application.

### Formula

Jobs with at least one application / Total jobs × 100

### Source
- jobs
- job_metrics

### Decision
A low value indicates that a significant portion of marketplace supply is not receiving candidate demand.

---

## 2. View-to-Application Rate

### Definition
Percentage of job views that result in an application.

### Formula

Total applications / Total job views × 100

### Source
job_metrics.views
job_metrics.applies

### Decision
Helps identify whether candidates are converting after discovering a job.

---

## 3. Jobs Without Applications

### Definition
Number of jobs that have received zero applications.

### Source
job_metrics.applies

### Decision
Used to identify jobs with weak marketplace demand or discovery.

---

## 4. Average Applications per Job

### Definition
Average number of applications received per job.

### Formula

Total applications / Total jobs

### Source
job_metrics.applies

### Decision
Used as a high-level indicator of candidate demand.

---

## 5. Average Views per Job

### Definition
Average number of views received per job.

### Formula

Total views / Total jobs

### Source
job_metrics.views

### Decision
Helps evaluate job discovery and visibility.

---

# Data Source

The raw source is the public LinkedIn Job Postings dataset.

The raw dataset is preserved in:

data/postings.csv

The data is transformed into the PlaceMux analytics database:

data/placemux.db

The dashboard will query the processed database rather than modifying the raw source.