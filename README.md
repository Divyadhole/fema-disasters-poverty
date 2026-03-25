# When Disaster Strikes the Poor — FEMA + Census Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![SQL](https://img.shields.io/badge/SQL-SQLite-lightgrey?logo=sqlite)](https://sqlite.org)
[![Data](https://img.shields.io/badge/Data-FEMA%20OpenFEMA%20%2B%20Census%20SAIPE-orange)](https://www.fema.gov/about/openfema/api)
[![Dashboard](https://img.shields.io/badge/🌐%20Live%20Dashboard-Click%20Here-brightgreen)](https://divyadhole.github.io/fema-disasters-poverty/)
[![CI](https://github.com/Divyadhole/fema-disasters-poverty/workflows/FEMA%20Poverty%20Analysis%20Validation/badge.svg)](https://github.com/Divyadhole/fema-disasters-poverty/actions)

## Live Dashboard

**[https://divyadhole.github.io/fema-disasters-poverty/](https://divyadhole.github.io/fema-disasters-poverty/)**

---

## What This Is

I crossed FEMA's OpenFEMA disaster declaration data with Census Bureau poverty rates
to answer one question: do poor communities get hit harder by disasters and take
longer to recover?

They do. The recovery gap is the part that surprised me most — not the frequency difference
but the 4.7x difference in how long full recovery takes. Counties with over 20% poverty
average 39 months to close FEMA cases. Counties under 10% poverty average 8 months.

---

## Data

**FEMA OpenFEMA API** — https://www.fema.gov/api/open/v2/disasterDeclarationsSummaries

No API key. No registration. Completely open. Every disaster declaration since 1953.

```python
import requests
resp = requests.get(
    "https://www.fema.gov/api/open/v2/disasterDeclarationsSummaries",
    params={"$filter": "state eq 'TX'", "$top": 100, "$format": "json"}
)
declarations = resp.json()["DisasterDeclarationsSummaries"]
```

**Census Bureau SAIPE** — https://www.census.gov/data/datasets/time-series/demo/saipe/

Annual state and county poverty estimates built from tax records, SNAP data, and survey data.
More reliable than survey-only estimates for small areas.

---

## Numbers

| Metric | Value |
|---|---|
| Total disaster cost 2000-2023 | **$1.49 Trillion** |
| Worst single year | **2017 — $312.7B** (Harvey + Irma + Maria) |
| State with most declarations | **Texas (382)** |
| Recovery gap | **4.7x longer** in high-poverty vs low-poverty counties |
| Poverty-disaster correlation | **Spearman r=0.475, p=0.019** |
| Tornado low-income hit rate | **72%** of events hit low-income counties |
| Projected annual cost by 2030 | **~$150B/year** (regression) |

---

## SQL That Does Work

```sql
-- Running total disaster cost with 5-year rolling average
SELECT year, cost_B,
    ROUND(SUM(cost_B) OVER (ORDER BY year), 1)           AS running_total,
    ROUND(AVG(cost_B) OVER (ORDER BY year ROWS 4 PRECEDING), 1) AS rolling_5yr_avg
FROM annual_disasters;

-- States where flood + poverty combine for highest risk
SELECT state, flood, poverty,
    CASE WHEN poverty > 15 AND flood_share > 30
         THEN 'High Risk / High Poverty'
         ELSE 'Other' END AS risk_category
FROM state_disasters
ORDER BY flood_share DESC;

-- Recovery time bracket classification
SELECT poverty_band, avg_recovery_months,
    ROUND(avg_recovery_months / 8.2, 2) AS multiplier_vs_low_poverty,
    CASE WHEN avg_recovery_months <= 10  THEN 'Fast'
         WHEN avg_recovery_months <= 20  THEN 'Moderate'
         ELSE 'Slow' END AS recovery_tier
FROM poverty_correlation;
```

---

## Project Layout

```
fema-disasters-poverty/
├── src/
│   ├── fema_data.py         # 25 states, 24 years, 8 disaster types
│   ├── fetch_fema.py        # Live FEMA OpenFEMA API fetcher
│   ├── charts.py            # 6 charts
│   ├── stats_analysis.py    # Spearman, regression, Mann-Whitney
│   └── build_website.py
├── sql/analysis/
│   └── fema_analysis.sql    # 7 queries with RANK, LAG, rolling AVG
├── .github/workflows/
│   └── validate.yml         # CI — validates data + stats on every push
├── data/processed/
│   └── data_dictionary.md
├── docs/index.html          # Live dashboard
├── outputs/charts/          # 6 PNGs
├── outputs/excel/           # 6-sheet workbook
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

*Project 13 of 40 — FEMA OpenFEMA and Census SAIPE are public domain.*
