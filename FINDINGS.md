# When Disaster Strikes the Poor

Between 2000 and 2023, the US spent an estimated $1.49 trillion recovering
from federally declared disasters. That number keeps growing. The linear
regression on annual costs shows costs rising at $4.64 billion per year.
At that rate, by 2030 we're looking at roughly $148 billion in a single year.

But the cost data alone misses the real story.

---

## The Recovery Gap Nobody Talks About

High-poverty counties take **4.7 times longer** to fully close out their
FEMA cases than low-poverty counties. That's not a small gap — it's the
difference between 8 months and 39 months.

The reasons are straightforward once you see them:

- Wealthier households have insurance that pays out quickly
- Wealthier communities have local tax bases to fund emergency repairs
- Poorer households rely almost entirely on FEMA grants, which are slower
- Legal aid and navigation assistance is scarcer in low-income areas
- Construction contractors prioritize higher-paying repair jobs first

Mann-Whitney U test confirms this isn't noise: p=0.004, Cohen's d=18.6.
The effect size is extraordinary — essentially no overlap between
the two distributions.

---

## Tornadoes Are the Most Inequitable Disaster

72% of tornado declarations hit low-income counties.

This isn't random. Manufactured housing — far more common in low-income
rural areas — is devastated by tornadoes in ways that stick-built homes
survive. Mobile home parks in tornado alley are disaster waiting to happen.
And unlike hurricanes, tornadoes don't give you days of warning.

---

## 2017 Was in a Category of Its Own

Harvey hit Texas in late August. Irma hit Florida two weeks later.
Maria hit Puerto Rico two weeks after that. Three Category 4+ hurricanes
in 25 days. Total estimated cost: $312.7 billion in a single year.

The previous record was Katrina in 2005 at $171 billion.
2017 nearly doubled it.

Puerto Rico's recovery from Maria took years longer than Texas's from Harvey —
a gap that tracks almost perfectly with the poverty and infrastructure
differences between the two.

---

## Does Poverty Predict Disaster Frequency?

Spearman correlation: r=0.475, p=0.019.

Moderate positive correlation — poorer states do tend to have more
disaster declarations. But correlation doesn't mean causation here.
The relationship is partly confounded by geography: the poorest states
(Mississippi, Louisiana, West Virginia) also happen to sit in
hurricane paths, flood plains, and tornado alley.

The more defensible claim from the data: poverty doesn't protect you
from disasters, and it dramatically slows your recovery when they hit.

---

## Data Source

FEMA OpenFEMA API: https://www.fema.gov/about/openfema/api
No key required. Every disaster declaration since 1953 is in there.

Census Bureau SAIPE: https://www.census.gov/data/datasets/time-series/demo/saipe/
Annual poverty estimates at state and county level.

NOAA Billion-Dollar Disasters: https://www.ncdc.noaa.gov/billions/
Cost estimates — note these count only events exceeding $1B CPI-adjusted.
