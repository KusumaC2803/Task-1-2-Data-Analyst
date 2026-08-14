-- ============================================================
-- PlaceMux Marketplace Liquidity Metrics
-- ============================================================


-- ============================================================
-- 1. TOTAL MARKETPLACE SUPPLY
-- ============================================================

SELECT
    COUNT(*) AS total_jobs
FROM jobs;


-- ============================================================
-- 2. TOTAL JOB VIEWS
-- ============================================================

SELECT
    SUM(views) AS total_job_views
FROM job_metrics;


-- ============================================================
-- 3. TOTAL APPLICATIONS
-- ============================================================

SELECT
    SUM(applies) AS total_applications
FROM job_metrics;


-- ============================================================
-- 4. JOBS RECEIVING AT LEAST ONE APPLICATION
-- ============================================================

SELECT
    COUNT(*) AS jobs_with_applications
FROM job_metrics
WHERE applies > 0;


-- ============================================================
-- 5. JOBS WITH ZERO APPLICATIONS
-- ============================================================

SELECT
    COUNT(*) AS jobs_without_applications
FROM job_metrics
WHERE applies = 0;


-- ============================================================
-- 6. JOB APPLICATION COVERAGE
-- ============================================================

SELECT
    ROUND(
        COUNT(
            CASE
                WHEN applies > 0 THEN 1
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS job_application_coverage_pct
FROM job_metrics;


-- ============================================================
-- 7. VIEW-TO-APPLICATION CONVERSION
-- ============================================================

SELECT
    ROUND(
        SUM(applies) * 100.0 /
        NULLIF(SUM(views), 0),
        2
    ) AS application_conversion_pct
FROM job_metrics;


-- ============================================================
-- 8. AVERAGE VIEWS PER JOB
-- ============================================================

SELECT
    ROUND(
        AVG(views),
        2
    ) AS average_views_per_job
FROM job_metrics;


-- ============================================================
-- 9. AVERAGE APPLICATIONS PER JOB
-- ============================================================

SELECT
    ROUND(
        AVG(applies),
        2
    ) AS average_applications_per_job
FROM job_metrics;


-- ============================================================
-- 10. TOP JOBS BY APPLICATIONS
-- ============================================================

SELECT
    j.job_id,
    j.title,
    j.location,
    jm.views,
    jm.applies
FROM jobs j
JOIN job_metrics jm
    ON j.job_id = jm.job_id
ORDER BY jm.applies DESC
LIMIT 10;


-- ============================================================
-- 11. JOBS WITH HIGH VIEWS BUT ZERO APPLICATIONS
-- ============================================================

SELECT
    j.job_id,
    j.title,
    j.location,
    jm.views,
    jm.applies
FROM jobs j
JOIN job_metrics jm
    ON j.job_id = jm.job_id
WHERE jm.views > 100
  AND jm.applies = 0
ORDER BY jm.views DESC
LIMIT 20;


-- ============================================================
-- 12. JOBS WITH HIGH APPLICATION ACTIVITY
-- ============================================================

SELECT
    j.job_id,
    j.title,
    j.location,
    jm.views,
    jm.applies,
    ROUND(
        jm.applies * 100.0 /
        NULLIF(jm.views, 0),
        2
    ) AS conversion_pct
FROM jobs j
JOIN job_metrics jm
    ON j.job_id = jm.job_id
WHERE jm.views > 0
ORDER BY conversion_pct DESC
LIMIT 20;