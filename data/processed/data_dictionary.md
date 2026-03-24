# Data Dictionary — FEMA Disasters + Poverty Analysis

## Sources

| Source | URL | Notes |
|---|---|---|
| FEMA OpenFEMA | https://www.fema.gov/api/open/v2/ | No key required |
| Census SAIPE | https://www.census.gov/data/datasets/time-series/demo/saipe/ | Annual poverty estimates |
| NOAA Billion-Dollar Disasters | https://www.ncdc.noaa.gov/billions/ | Cost estimates |

---

## Tables

### `state_disasters`
| Column | Type | Description |
|---|---|---|
| state | VARCHAR | State name |
| total | INT | Total FEMA declarations 2000-2023 |
| major | INT | Major Disaster (DR) declarations only |
| hurricane | INT | Hurricane-related declarations |
| flood | INT | Flood-related declarations |
| fire | INT | Fire-related declarations |
| avg_per_yr | FLOAT | Average declarations per year |
| poverty | FLOAT | % of population below poverty line (Census SAIPE 2022) |
| flood_share | FLOAT | Floods as % of total declarations |
| region | VARCHAR | Geographic region |

### `annual_disasters`
| Column | Type | Description |
|---|---|---|
| year | INT | Calendar year |
| total | INT | Total disaster declarations |
| major | INT | Major disaster declarations |
| cost_B | FLOAT | Estimated total cost in USD billions |
| deaths | INT | Direct and indirect deaths |
| cost_per_declaration | FLOAT | Average cost per declaration in millions |

### `disaster_types`
| Column | Type | Description |
|---|---|---|
| disaster_type | VARCHAR | FEMA incident type category |
| count | INT | Number of declarations 2000-2023 |
| avg_cost_M | FLOAT | Average cost per event in millions USD |
| pct_low_income_counties | FLOAT | % of events hitting low-income counties |

### `poverty_correlation`
| Column | Type | Description |
|---|---|---|
| poverty_band | VARCHAR | Poverty rate bracket |
| avg_declarations | FLOAT | Average declarations in counties of this poverty level |
| avg_recovery_months | FLOAT | Average months to full FEMA case closure |

---

## Key Definitions

**Major Disaster Declaration (DR):** Issued by the President when state/local resources are overwhelmed. Triggers Individual Assistance (IA) and Public Assistance (PA) programs.

**Emergency Declaration (EM):** Smaller scale — supplements state/local efforts without the full range of disaster programs.

**Poverty Rate (Census SAIPE):** Percentage of people with income below the official federal poverty threshold. Updated annually by the Census Bureau using tax records, SNAP data, and survey data.

**Recovery Time:** FEMA defines recovery as closure of all open cases. High-poverty counties take longer due to less insurance coverage, fewer savings, and more reliance on FEMA grants.

---

## Important Notes

- Cost data from NOAA Billion-Dollar Disasters — not all events are counted
- 2017 Hurricane Maria deaths (3,057 in Puerto Rico) are included but PR is not in state table
- COVID-19 was declared a major disaster in all 50 states in 2020 — this inflates 2020 count
- Poverty rates are 2022 (most recent Census SAIPE release as of analysis date)
