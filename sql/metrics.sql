DROP VIEW IF EXISTS metric_overview;
DROP VIEW IF EXISTS metric_monthly;
DROP VIEW IF EXISTS metric_issues;
DROP VIEW IF EXISTS metric_subproducts;
DROP VIEW IF EXISTS metric_companies;
DROP VIEW IF EXISTS metric_responses;
DROP VIEW IF EXISTS metric_issue_detail;

CREATE VIEW metric_overview AS
SELECT
    COUNT(*) AS complaint_count,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate,
    SUM(has_relief) AS relief_response_count
FROM complaints;

CREATE VIEW metric_monthly AS
SELECT
    received_month,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    SUM(has_relief) AS relief_response_count,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate
FROM complaints
GROUP BY received_month
ORDER BY received_month;

CREATE VIEW metric_issues AS
SELECT
    issue,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS complaint_share,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    SUM(has_relief) AS relief_response_count,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate
FROM complaints
GROUP BY issue
ORDER BY complaint_count DESC, issue ASC;

CREATE VIEW metric_subproducts AS
SELECT
    sub_product,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    SUM(has_relief) AS relief_response_count,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate
FROM complaints
GROUP BY sub_product
ORDER BY complaint_count DESC, sub_product ASC;

CREATE VIEW metric_companies AS
SELECT
    company,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS complaint_share,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    SUM(has_relief) AS relief_response_count,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate
FROM complaints
GROUP BY company
ORDER BY complaint_count DESC, company ASC;

CREATE VIEW metric_responses AS
SELECT
    company_response,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS complaint_share
FROM complaints
GROUP BY company_response
ORDER BY complaint_count DESC, company_response ASC;

CREATE VIEW metric_issue_detail AS
SELECT
    issue,
    COALESCE(sub_issue, 'Not specified') AS sub_issue,
    COUNT(*) AS complaint_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS complaint_share,
    ROUND(100.0 * AVG(is_timely), 2) AS timely_response_rate,
    SUM(CASE WHEN is_timely = 0 THEN 1 ELSE 0 END) AS not_timely_count,
    ROUND(100.0 * AVG(CASE WHEN is_timely = 0 THEN 1.0 ELSE 0.0 END), 2)
        AS not_timely_rate,
    SUM(has_relief) AS relief_response_count,
    ROUND(100.0 * AVG(has_relief), 2) AS relief_response_rate
FROM complaints
GROUP BY issue, COALESCE(sub_issue, 'Not specified')
ORDER BY complaint_count DESC, issue ASC, sub_issue ASC;
