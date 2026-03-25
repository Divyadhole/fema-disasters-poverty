# When Disaster Strikes the Poor — FEMA + Census Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite)](https://sqlite.org)
[![Data](https://img.shields.io/badge/Data-FEMA%20OpenFEMA%20+%20Census%20SAIPE-orange)](https://www.fema.gov/about/openfema/api)
[![Dashboard](https://img.shields.io/badge/🌐%20Live%20Dashboard-Click%20Here-brightgreen)](https://divyadhole.github.io/fema-disasters-poverty/)
[![CI](https://github.com/Divyadhole/fema-disasters-poverty/workflows/FEMA%20Poverty%20Analysis%20Validation/badge.svg)](https://github.com/Divyadhole/fema-disasters-poverty/actions)

## Live Dashboard
**[https://divyadhole.github.io/fema-disasters-poverty/](https://divyadhole.github.io/fema-disasters-poverty/)**

---

## What This Is

I pulled 24 years of FEMA disaster declarations (2000-2023) and crossed
them with Census Bureau poverty rates at the state level to ask a simple
question: does being poor make disasters worse?

The short answer is yes — and not just during the disaster itself.
High-poverty counties take 4.7 times longer to fully recover.
That's the finding that kept me going on this one.

---

## Data

**FEMA OpenFEMA API** — no key required
```
https://www.fema.gov/api/open/v2/disasterDeclarationsSummaries
```
Every disaster declaration since 1953. Filter by state, year,
declaration type, incident type. Returns JSON. Rate limit is lenient.

**Census Bureau SAIPE** — Small Area Income and Poverty Estimates
```
https://www.census.gov/data/datasets/time-series/demo/saipe/
```
Annual poverty rates at state and county level, updated each December.

---

## Numbers

| Metric | Value |
|---|---|
| Total US disaster cost 2000-2023 | **$1.49 Trillion** |
| Worst single year | **2017 — $312.7B** (Harvey + Irma + Maria) |
| Most disaster-prone state | **Texas** (382 declarations) |
| Recovery time: high vs low poverty | **4.7x longer** in high-poverty counties |
| Poverty-disaster correlation | **Spearman r=0.475, p=0.019** |
| Tornadoes hitting low-income counties | **72%** of all tornado declarations |
| Annual cost trend | **+$4.64B per year** and rising |

---

## SQL Highlights

```sql
-- Running total disaster cost with rolling 5-year average
SELECT year, cost_B,
    ROUND(SUM(cost_B) OVER (ORDER BY year), 1)                       AS running_total,
    ROUND(AVG(cost_B) OVER (ORDER BY year ROWS 4 PRECEDING), 1)      AS rolling_5yr_avg
FROM annual_disasters ORDER BY year;

-- Which states carry both high poverty AND high disaster burden
SELECT state, total, poverty,
    ROUND(total * poverty / 100.0, 1)  AS combined_burden_score,
    RANK() OVER (ORDER BY total DESC)  AS disaster_rank,
    RANK() OVER (ORDER BY poverty DESC) AS poverty_rank
FROM state_disasters ORDER BY combined_burden_score DESC;

-- Poverty band recovery time with tier classification
SELECT poverty_band, avg_recovery_months,
    ROUND(avg_recovery_months / 8.2, 2)   AS multiplier_vs_low_poverty,
    CASE
        WHEN avg_recovery_months <= 10 THEN 'Fast'
        WHEN avg_recovery_months <= 20 THEN 'Moderate'
        WHEN avg_recovery_months <= 30 THEN 'Slow'
        ELSE 'Very Slow'
    END AS recovery_category
FROM poverty_correlation ORDER BY avg_recovery_months;
```

---

## Project Layout

```
fema-disasters-poverty/
├── src/
│   ├── fema_data.py          # State, annual, type, poverty tables
│   ├── fetch_fema.py         # Live FEMA OpenFEMA API fetcher
│   ├── charts.py             # 6 charts
│   ├── stats_analysis.py     # Spearman, regression, Mann-Whitney
│   └── build_website.py      # GitHub Pages generator
├── sql/analysis/
│   └── fema_analysis.sql     # 7 SQL queries
├── .github/workflows/
│   └── validate.yml          # CI — 4 assertions run on every push
├── data/processed/
│   └── data_dictionary.md
├── docs/index.html           # Live dashboard
├── outputs/charts/           # 6 PNG charts
├── outputs/excel/            # 6-sheet workbook
├── FINDINGS.md
└── run_analysis.py
```

---

## Run It

```bash
git clone https://github.com/Divyadhole/fema-disasters-poverty.git
cd fema-disasters-poverty
pip install -r requirements.txt
python run_analysis.py
```

---

*Project 13 of 40 — FEMA OpenFEMA and Census SAIPE data are public domain.*
