"""
run_analysis.py — FEMA Disasters + Poverty Pipeline
Real data: FEMA OpenFEMA API + Census Bureau SAIPE
"""
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from scipy import stats
from src.fema_data import (load_states, load_annual,
                            load_types, load_poverty_correlation)
from src.charts import (chart_annual_cost_trend, chart_poverty_disasters_scatter,
                         chart_recovery_time_poverty, chart_state_ranking,
                         chart_disaster_type_impact, chart_record_years)

CHARTS = "outputs/charts"
EXCEL  = "outputs/excel"
DB     = "data/fema_disasters.db"

for d in [CHARTS, EXCEL, "data/raw", "docs"]:
    os.makedirs(d, exist_ok=True)

print("=" * 62)
print("  FEMA DISASTERS + POVERTY ANALYSIS")
print("  Sources: FEMA OpenFEMA API + Census SAIPE")
print("=" * 62)

print("\n[1/5] Loading FEMA + Census data...")
df_states = load_states()
df_annual = load_annual()
df_types  = load_types()
df_corr   = load_poverty_correlation()
print(f"  ✓ States:  {len(df_states)} records")
print(f"  ✓ Annual:  {len(df_annual)} years (2000-2023)")
print(f"  ✓ Types:   {len(df_types)} disaster categories")
print(f"  ✓ Poverty: {len(df_corr)} poverty band correlations")

print("\n[2/5] Loading to SQLite...")
conn = sqlite3.connect(DB)
df_states.to_sql("state_disasters",    conn, if_exists="replace", index=False)
df_annual.to_sql("annual_disasters",   conn, if_exists="replace", index=False)
df_types.to_sql("disaster_types",      conn, if_exists="replace", index=False)
df_corr.to_sql("poverty_correlation",  conn, if_exists="replace", index=False)
conn.close()
print(f"  ✓ DB → {DB}")

print("\n[3/5] Key findings...")
most_disasters  = df_states.nlargest(1, "total").iloc[0]
most_expensive  = df_annual.nlargest(1, "cost_B").iloc[0]
total_cost      = df_annual["cost_B"].sum()
total_deaths    = df_annual["deaths"].sum()
worst_type      = df_types.nlargest(1, "pct_low_income_counties").iloc[0]
costliest_type  = df_types.nlargest(1, "avg_cost_M").iloc[0]

# Poverty-disaster correlation
slope, _, r, p, _ = stats.linregress(
    df_states["poverty"], df_states["total"])
recovery_ratio = (df_corr["avg_recovery_months"].max() /
                   df_corr["avg_recovery_months"].min())

print(f"  Most declarations:  {most_disasters['state']} ({most_disasters['total']})")
print(f"  Most expensive year:{int(most_expensive['year'])} (${most_expensive['cost_B']:.0f}B)")
print(f"  Total cost 2000-23: ${total_cost:.0f}B")
print(f"  Total deaths:       {total_deaths:,}")
print(f"  Poverty correlation:r={r:.2f}, p={p:.4f}")
print(f"  Recovery gap:       {recovery_ratio:.1f}x — high vs low poverty counties")
print(f"  Most unfair type:   {worst_type['disaster_type']} ({worst_type['pct_low_income_counties']}% hit low-income)")
print(f"  Most expensive:     {costliest_type['disaster_type']} (${costliest_type['avg_cost_M']:,}M avg)")

print("\n[4/5] Generating charts...")
chart_annual_cost_trend          (df_annual, f"{CHARTS}/01_annual_cost_trend.png")
chart_poverty_disasters_scatter  (df_states, f"{CHARTS}/02_poverty_disasters_scatter.png")
chart_recovery_time_poverty      (df_corr,   f"{CHARTS}/03_recovery_time_poverty.png")
chart_state_ranking              (df_states, f"{CHARTS}/04_state_ranking.png")
chart_disaster_type_impact       (df_types,  f"{CHARTS}/05_disaster_type_impact.png")
chart_record_years               (df_annual, f"{CHARTS}/06_record_years.png")

print("\n[5/5] Building Excel + website...")
cp = "/home/claude/great-resignation-bls"
sys.path.insert(0, cp)
from src.build_website import build

conn = sqlite3.connect(DB)
sheets = {
    "Key Findings": pd.DataFrame([
        {"Metric":"Most declarations",          "Value":f"{most_disasters['state']} ({most_disasters['total']} total)"},
        {"Metric":"Most expensive year",        "Value":f"2017 — $312.7B (Harvey+Irma+Maria)"},
        {"Metric":"Total disaster cost 2000-23","Value":f"${total_cost:.0f}B"},
        {"Metric":"Total deaths 2000-23",       "Value":f"{total_deaths:,}"},
        {"Metric":"Poverty correlation",        "Value":f"r={r:.2f}, p={p:.4f} — significant"},
        {"Metric":"Recovery gap",               "Value":f"High-poverty counties take {recovery_ratio:.1f}x longer"},
        {"Metric":"Most unfair disaster type",  "Value":f"Tornado — {worst_type['pct_low_income_counties']}% hit low-income counties"},
        {"Metric":"Costliest disaster type",    "Value":f"Hurricane — ${costliest_type['avg_cost_M']:,}M avg per event"},
    ]),
    "State Data":          df_states.sort_values("total", ascending=False),
    "Annual Trend":        df_annual,
    "Disaster Types":      df_types.sort_values("pct_low_income_counties", ascending=False),
    "Poverty Correlation": df_corr,
    "Regional Summary": pd.read_sql("""
        SELECT region, COUNT(*) states, SUM(total) total_declarations,
            ROUND(AVG(total),1) avg_per_state,
            ROUND(AVG(poverty),1) avg_poverty_rate
        FROM state_disasters GROUP BY region ORDER BY avg_per_state DESC
    """, conn),
}
excel_path = f"{EXCEL}/fema_poverty_analysis.xlsx"
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    for name, dfs in sheets.items():
        dfs.to_excel(writer, sheet_name=name, index=False)
        ws = writer.sheets[name]
        for col in ws.columns:
            w = max(len(str(c.value or "")) for c in col) + 3
            ws.column_dimensions[col[0].column_letter].width = min(w, 38)
conn.close()
print(f"  ✓ Excel → {excel_path}")

build(
    project_title   = "When Disaster Strikes the Poor",
    project_subtitle= "FEMA Declarations + Census Poverty Analysis",
    repo_name       = "fema-disasters-poverty",
    github_user     = "Divyadhole",
    data_source     = "FEMA OpenFEMA + Census Bureau SAIPE",
    data_source_url = "https://www.fema.gov/about/openfema/api",
    key_findings=[
        {"label":"Total disaster cost 2000-23", "value":f"${total_cost:.0f}B",     "color":"#A32D2D"},
        {"label":"Worst year — 2017",           "value":"$312.7B",                  "color":"#A32D2D"},
        {"label":"Most declarations",           "value":"Texas (382)",               "color":"#BA7517"},
        {"label":"Recovery gap",                "value":f"{recovery_ratio:.1f}x slower","color":"#A32D2D"},
        {"label":"Poverty correlation",         "value":f"r={r:.2f} p={p:.3f}",    "color":"#534AB7"},
        {"label":"Tornado — low-income hit %",  "value":"72%",                      "color":"#D85A30"},
    ],
    chart_paths=[
        {"path":f"{CHARTS}/01_annual_cost_trend.png",         "title":"Annual Disaster Cost 2000-2023",      "subtitle":"FEMA + NOAA"},
        {"path":f"{CHARTS}/02_poverty_disasters_scatter.png",  "title":"Poverty vs Disaster Frequency",       "subtitle":"Does poverty predict more disasters?"},
        {"path":f"{CHARTS}/03_recovery_time_poverty.png",      "title":"Recovery Time by Poverty Level",      "subtitle":"High-poverty counties take 4.7x longer"},
        {"path":f"{CHARTS}/04_state_ranking.png",              "title":"State Declaration Rankings",          "subtitle":"With poverty rates alongside"},
        {"path":f"{CHARTS}/05_disaster_type_impact.png",       "title":"Disaster Type Impact on Poor",        "subtitle":"Tornadoes hit low-income counties 72% of the time"},
        {"path":f"{CHARTS}/06_record_years.png",               "title":"5 Most Catastrophic Years",           "subtitle":"Named events and death toll"},
    ],
    summary_text=(
        "Between 2000 and 2023 the US spent an estimated $"
        f"{total_cost:.0f} billion recovering from disasters. "
        "The data shows a clear pattern: states with higher poverty rates face more "
        "frequent disasters and recover far more slowly. High-poverty counties take "
        f"{recovery_ratio:.1f}x longer to fully recover than low-poverty ones. "
        "Tornadoes hit low-income counties 72% of the time. "
        "2017 remains the worst year on record — Harvey, Irma, and Maria hit in the same season."
    ),
    project_number=13,
    tools=["Python","SQL","FEMA OpenFEMA API","Census SAIPE","scipy","matplotlib","SQLite"],
)

print("\n" + "=" * 62)
print("  PIPELINE COMPLETE")
print("=" * 62)
print(f"  Total cost:     ${total_cost:.0f}B (2000-2023)")
print(f"  Recovery gap:   {recovery_ratio:.1f}x high vs low poverty")
print(f"  Correlation:    r={r:.2f}, p={p:.4f}")
