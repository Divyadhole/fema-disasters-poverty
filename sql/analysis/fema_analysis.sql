-- ============================================================
-- sql/analysis/fema_analysis.sql
-- FEMA Disaster Declarations + Census Poverty Analysis
-- Source: FEMA OpenFEMA API + Census Bureau SAIPE
-- ============================================================

-- 1. State ranking: most disaster declarations vs poverty rate
SELECT state, total, major, poverty_rate_2022,
    RANK() OVER (ORDER BY total DESC)              AS disaster_rank,
    RANK() OVER (ORDER BY poverty_rate_2022 DESC)  AS poverty_rank,
    ROUND(total * poverty_rate_2022 / 100.0, 1)    AS combined_burden_score
FROM state_disasters
ORDER BY total DESC;


-- 2. Year-over-year disaster cost trend with running total
SELECT year, total, cost_B,
    ROUND(cost_B - LAG(cost_B) OVER (ORDER BY year), 1)  AS cost_yoy_change,
    ROUND(SUM(cost_B) OVER (ORDER BY year), 1)            AS running_total_cost_B,
    ROUND(AVG(cost_B) OVER (ORDER BY year ROWS 4 PRECEDING), 1) AS rolling_5yr_avg
FROM annual_disasters
ORDER BY year;


-- 3. Record years: top 5 most expensive disaster years
SELECT year, total, cost_B, deaths,
    RANK() OVER (ORDER BY cost_B DESC) AS cost_rank,
    ROUND(cost_B / total, 2) AS avg_cost_per_event_B
FROM annual_disasters
ORDER BY cost_B DESC
LIMIT 5;


-- 4. Poverty band vs disaster recovery time
SELECT poverty_band, avg_declarations, avg_recovery_months,
    ROUND(avg_recovery_months / 8.2, 2) AS recovery_multiplier_vs_low_poverty,
    CASE
        WHEN avg_recovery_months <= 10  THEN 'Fast Recovery'
        WHEN avg_recovery_months <= 20  THEN 'Moderate Recovery'
        WHEN avg_recovery_months <= 30  THEN 'Slow Recovery'
        ELSE 'Very Slow Recovery'
    END AS recovery_category
FROM poverty_correlation
ORDER BY avg_recovery_months;


-- 5. Disaster type impact on low-income communities
SELECT disaster_type, count, avg_cost_M, pct_low_income_counties,
    RANK() OVER (ORDER BY pct_low_income_counties DESC) AS low_income_impact_rank,
    RANK() OVER (ORDER BY avg_cost_M DESC)               AS cost_rank,
    ROUND(count * avg_cost_M / 1000.0, 1)                AS total_estimated_cost_B
FROM disaster_types
ORDER BY pct_low_income_counties DESC;


-- 6. Flood-prone states: correlation with poverty
SELECT state, flood, total, poverty_rate_2022,
    flood_share,
    ROUND(100.0 * flood / total, 1) AS flood_pct_of_all,
    CASE WHEN poverty_rate_2022 > 15 AND flood_share > 30
         THEN 'High Risk / High Poverty'
         WHEN poverty_rate_2022 > 15
         THEN 'High Poverty'
         WHEN flood_share > 30
         THEN 'Flood Prone'
         ELSE 'Standard'
    END AS risk_category
FROM state_disasters
ORDER BY flood_share DESC;


-- 7. Regional disaster burden comparison
SELECT region,
    COUNT(*)                          AS states,
    SUM(total)                        AS total_declarations,
    ROUND(AVG(total), 1)              AS avg_per_state,
    ROUND(AVG(poverty_rate_2022), 1)  AS avg_poverty_rate,
    ROUND(AVG(avg_per_yr), 1)         AS avg_declarations_per_year
FROM state_disasters
GROUP BY region
ORDER BY avg_per_state DESC;
