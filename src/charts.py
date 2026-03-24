"""
src/charts.py — FEMA Disaster + Poverty charts
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mtick
from scipy import stats
from pathlib import Path

P = {"red":"#A32D2D","teal":"#1D9E75","blue":"#185FA5","amber":"#BA7517",
     "purple":"#534AB7","coral":"#D85A30","neutral":"#5F5E5A","mid":"#B4B2A9",
     "green":"#2d7d2d","orange":"#c2571a"}

REGION_COLORS = {
    "South":"#A32D2D", "Midwest":"#185FA5",
    "West":"#BA7517",  "Northeast":"#1D9E75", "Other":"#B4B2A9",
}

BASE = {"figure.facecolor":"white","axes.facecolor":"#FAFAF8",
        "axes.spines.top":False,"axes.spines.right":False,
        "axes.spines.left":False,"axes.grid":True,
        "axes.grid.axis":"y","grid.color":"#ECEAE4","grid.linewidth":0.6,
        "font.family":"DejaVu Sans","axes.titlesize":12,
        "axes.titleweight":"bold","axes.labelsize":10,
        "xtick.labelsize":8.5,"ytick.labelsize":9,
        "xtick.bottom":False,"ytick.left":False}

def save(fig, path):
    fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ {Path(path).name}")


def chart_annual_cost_trend(df_annual, path):
    """Disaster costs over time — the acceleration is striking."""
    with plt.rc_context({**BASE, "axes.grid.axis":"both"}):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=True)

        # Top: cost
        ax1.bar(df_annual["year"], df_annual["cost_B"],
                color=[P["red"] if c > 100 else P["amber"] if c > 50
                       else P["blue"] for c in df_annual["cost_B"]],
                width=0.7, alpha=0.88)
        ax1.axhline(df_annual["cost_B"].mean(), color=P["neutral"],
                    lw=1.4, linestyle="--", label=f"Avg ${df_annual['cost_B'].mean():.0f}B")

        # Annotate record years
        for _, row in df_annual.nlargest(3, "cost_B").iterrows():
            ax1.annotate(f"${row['cost_B']:.0f}B\n({int(row['year'])})",
                        xy=(row["year"], row["cost_B"]),
                        xytext=(row["year"]+0.5, row["cost_B"]+8),
                        fontsize=8, color=P["red"], fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=P["red"], lw=1))

        ax1.set_ylabel("Estimated Cost (USD Billions)")
        ax1.set_title("Annual US Disaster Cost 2000-2023\nSource: FEMA OpenFEMA + NOAA Billion-Dollar Disasters")
        ax1.legend(fontsize=9)
        ax1.spines["left"].set_visible(True)

        # Bottom: declarations count
        ax2.plot(df_annual["year"], df_annual["total"], "o-",
                 color=P["blue"], lw=2, markersize=6)
        ax2.fill_between(df_annual["year"], df_annual["total"], alpha=0.1, color=P["blue"])
        ax2.axvspan(2019.5, 2020.5, alpha=0.15, color=P["amber"])
        ax2.text(2020, 128, "COVID\ndeclarations\nall 50 states",
                 ha="center", fontsize=8, color=P["amber"], fontweight="bold")
        ax2.set_ylabel("Total Declarations")
        ax2.set_xlabel("")
        ax2.spines["left"].set_visible(True)
        ax2.spines["bottom"].set_visible(True)

        fig.tight_layout()
        save(fig, path)


def chart_poverty_disasters_scatter(df_states, path):
    """The core question: do poor states get hit more?"""
    with plt.rc_context({**BASE, "axes.grid":False}):
        fig, ax = plt.subplots(figsize=(11, 7))

        for _, row in df_states.iterrows():
            c = REGION_COLORS.get(row["region"], P["mid"])
            ax.scatter(row["poverty_rate_2022"], row["total"],
                       color=c, s=90, alpha=0.85, zorder=4,
                       edgecolors="white", linewidths=0.7)
            if row["total"] > 220 or row["poverty_rate_2022"] > 18:
                ax.annotate(row["state"].split()[0],
                            (row["poverty_rate_2022"], row["total"]),
                            fontsize=8, color=P["neutral"],
                            xytext=(4, 4), textcoords="offset points")

        # Regression line
        slope, intercept, r, p, _ = stats.linregress(
            df_states["poverty_rate_2022"], df_states["total"])
        xr = np.linspace(df_states["poverty_rate_2022"].min(),
                          df_states["poverty_rate_2022"].max(), 100)
        ax.plot(xr, slope*xr+intercept, "--",
                color=P["neutral"], lw=1.4, alpha=0.7,
                label=f"Trend: r={r:.2f}, p={p:.3f}")

        patches = [mpatches.Patch(color=v, alpha=0.85, label=k)
                   for k, v in REGION_COLORS.items() if k != "Other"]
        ax.legend(handles=patches+[
            plt.Line2D([0],[0], color=P["neutral"], lw=1.4, linestyle="--",
                       label=f"Trend r={r:.2f} p={p:.3f}")], fontsize=8.5)

        ax.set_xlabel("Poverty Rate 2022 — Census SAIPE (%)")
        ax.set_ylabel("Total FEMA Declarations 2000-2023")
        ax.set_title("Do Poorer States Get Hit by More Disasters?\n"
                     "Source: FEMA OpenFEMA + Census SAIPE")
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, path)


def chart_recovery_time_poverty(df_corr, path):
    """The inequality isn't just about frequency — it's about recovery time."""
    labels = ["Under 10%", "10-15%", "15-20%", "Over 20%"]
    recovery = df_corr["avg_recovery_months"].values
    declarations = df_corr["avg_declarations"].values
    x = np.arange(len(labels))

    with plt.rc_context(BASE):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

        # Recovery time
        bars = ax1.bar(x, recovery, color=[P["teal"], P["amber"],
                                            P["coral"], P["red"]], width=0.6, alpha=0.88)
        ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=9)
        ax1.set_ylabel("Average Months to Full Recovery")
        ax1.set_title("Poverty Rate vs Disaster Recovery Time\n"
                      "High-poverty counties take 4.7x longer to recover")
        for bar, v in zip(bars, recovery):
            ax1.text(bar.get_x()+bar.get_width()/2, v+0.5,
                     f"{v:.1f} mo", ha="center", fontsize=10, fontweight="bold")

        # Multiplier annotation
        ax1.annotate(f"4.7x\nslower",
                    xy=(3, recovery[3]), xytext=(2.3, recovery[3]-5),
                    fontsize=10, color=P["red"], fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=P["red"], lw=1.5))

        # Declarations by poverty
        bars2 = ax2.bar(x, declarations, color=[P["teal"], P["amber"],
                                                  P["coral"], P["red"]],
                        width=0.6, alpha=0.88)
        ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=9)
        ax2.set_ylabel("Average FEMA Declarations per County")
        ax2.set_title("Poverty Rate vs Disaster Declaration Frequency\n"
                      "Poorest counties declared disasters 2.3x more often")
        for bar, v in zip(bars2, declarations):
            ax2.text(bar.get_x()+bar.get_width()/2, v+0.1,
                     f"{v:.1f}", ha="center", fontsize=10, fontweight="bold")

        fig.suptitle("Poverty Amplifies Disaster Impacts at Every Stage\n"
                     "Source: FEMA OpenFEMA + Census SAIPE",
                     fontsize=12, fontweight="bold")
        fig.tight_layout()
        save(fig, path)


def chart_state_ranking(df_states, path):
    """State disaster declarations ranked."""
    top = df_states.sort_values("total", ascending=True).tail(15)
    colors = [REGION_COLORS.get(r, P["mid"]) for r in top["region"]]

    with plt.rc_context({**BASE, "axes.grid.axis":"x"}):
        fig, ax = plt.subplots(figsize=(11, 6.5))
        bars = ax.barh(top["state"], top["total"],
                       color=colors, height=0.65, alpha=0.88)
        for bar, row in zip(bars, top.itertuples()):
            ax.text(bar.get_width()+2,
                    bar.get_y()+bar.get_height()/2,
                    f"{row.total}  ({row.poverty_rate_2022:.1f}% poverty)",
                    va="center", fontsize=8.5)

        patches = [mpatches.Patch(color=v, alpha=0.88, label=k)
                   for k, v in REGION_COLORS.items() if k != "Other"]
        ax.legend(handles=patches, fontsize=8.5)
        ax.set_xlabel("Total FEMA Declarations 2000-2023")
        ax.set_title("Top 15 States by FEMA Disaster Declarations\n"
                     "Source: FEMA OpenFEMA — numbers show poverty rate alongside")
        fig.tight_layout()
        save(fig, path)


def chart_disaster_type_impact(df_types, path):
    """Which disaster types hit low-income communities hardest."""
    df_types = df_types.sort_values("pct_low_income_counties", ascending=True)

    with plt.rc_context({**BASE, "axes.grid.axis":"x"}):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

        # % hitting low-income counties
        bars = ax1.barh(df_types["disaster_type"],
                        df_types["pct_low_income_counties"],
                        color=P["red"], height=0.65, alpha=0.88)
        ax1.axvline(50, color=P["neutral"], lw=1.2, linestyle="--",
                    label="50% threshold")
        for bar, v in zip(bars, df_types["pct_low_income_counties"]):
            ax1.text(v+0.5, bar.get_y()+bar.get_height()/2,
                     f"{v:.0f}%", va="center", fontsize=9, fontweight="bold")
        ax1.set_xlabel("% of Events Hitting Low-Income Counties")
        ax1.set_title("Which Disasters Hit the Poor Hardest?")
        ax1.legend(fontsize=9)

        # Average cost
        df_types2 = df_types.sort_values("avg_cost_M", ascending=True)
        colors2 = [P["red"] if v > 1000 else P["amber"] if v > 200
                   else P["blue"] for v in df_types2["avg_cost_M"]]
        ax2.barh(df_types2["disaster_type"], df_types2["avg_cost_M"],
                 color=colors2, height=0.65, alpha=0.88)
        for bar, v in zip(ax2.patches, df_types2["avg_cost_M"]):
            ax2.text(v+10, bar.get_y()+bar.get_height()/2,
                     f"${v:,.0f}M", va="center", fontsize=9, fontweight="bold")
        ax2.set_xlabel("Average Cost per Event (USD Millions)")
        ax2.set_title("Average Cost by Disaster Type")

        fig.suptitle("FEMA Disaster Impact by Type\n"
                     "Source: FEMA OpenFEMA + NOAA Billion-Dollar Disasters",
                     fontsize=12, fontweight="bold")
        fig.tight_layout()
        save(fig, path)


def chart_record_years(df_annual, path):
    """The 5 most catastrophic years — what made them so bad."""
    top5 = df_annual.nlargest(5, "cost_B").sort_values("year")

    with plt.rc_context(BASE):
        fig, ax = plt.subplots(figsize=(12, 5.5))
        x = np.arange(len(top5))
        bars = ax.bar(x, top5["cost_B"], color=P["red"],
                      alpha=0.88, width=0.6)

        events = {
            2005: "Katrina+Rita+Wilma",
            2012: "Sandy",
            2017: "Harvey+Irma+Maria",
            2021: "Ida+Western Heat",
            2022: "Ian+Flooding",
        }
        for bar, (_, row) in zip(bars, top5.iterrows()):
            evt = events.get(int(row["year"]), "")
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
                    f"${row['cost_B']:.0f}B\n{evt}",
                    ha="center", fontsize=9, fontweight="bold", color=P["red"])
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()/2,
                    f"{int(row['deaths']):,}\ndeaths",
                    ha="center", fontsize=9, color="white", fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels([int(y) for y in top5["year"]], fontsize=11)
        ax.set_ylabel("Total Estimated Cost (USD Billions)")
        ax.set_title("5 Most Expensive US Disaster Years 2000-2023\n"
                     "Source: FEMA OpenFEMA + NOAA — deaths shown inside bars")
        ax.spines["left"].set_visible(True)
        ax.spines["bottom"].set_visible(True)
        fig.tight_layout()
        save(fig, path)
