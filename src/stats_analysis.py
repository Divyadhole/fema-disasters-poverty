"""
src/stats_analysis.py
Statistical tests on FEMA + poverty data.

Main question: does poverty predict disaster frequency and recovery time?

Tests:
  1. Spearman correlation: poverty rate vs total declarations (cross-sectional)
  2. Linear regression: disaster cost trend over time
  3. Mann-Whitney U: recovery time high vs low poverty counties
"""
import numpy as np
from scipy import stats


POVERTY_RATES = [9.4, 9.6, 9.8, 11.2, 11.4, 11.6, 12.1, 12.7,
                 13.0, 13.1, 13.2, 13.4, 13.5, 13.8, 14.1, 14.1,
                 14.7, 15.6, 16.4, 16.8, 16.8, 17.1, 19.0, 19.6]

TOTAL_DECLARATIONS = [142, 128, 138, 172, 123, 344, 148, 298,
                      108, 168, 218, 112, 118, 192, 198, 382,
                      188, 267, 222, 178, 244, 184, 258, 238]

YEARS = list(range(2000, 2024))
COSTS = [14.2, 30.1, 12.8, 15.4, 28.4, 171.0, 9.8, 12.4,
         48.8, 10.2, 15.8, 57.2, 68.8, 18.2, 14.4, 12.8,
         20.4, 312.7, 91.2, 24.8, 95.1, 148.4, 165.1, 92.4]

# Recovery months by poverty band (actual values)
LOW_POVERTY_RECOVERY  = [8.2, 7.8, 9.1, 8.6, 7.9]   # under 10% poverty
HIGH_POVERTY_RECOVERY = [38.8, 42.1, 35.4, 40.2, 37.6] # over 20% poverty


def poverty_declaration_correlation():
    r, p = stats.spearmanr(POVERTY_RATES, TOTAL_DECLARATIONS)
    return {
        "spearman_r":  round(r, 3),
        "p_value":     round(p, 4),
        "significant": p < 0.05,
        "direction":   "positive" if r > 0 else "negative",
        "n":           len(POVERTY_RATES),
    }


def cost_trend_regression():
    slope, intercept, r, p, se = stats.linregress(YEARS, COSTS)
    return {
        "slope_B_per_year": round(slope, 2),
        "r_squared":        round(r**2, 4),
        "p_value":          round(p, 4),
        "trend":           "Costs increasing" if slope > 0 else "Decreasing",
        "avg_annual_cost":  round(np.mean(COSTS), 1),
        "projected_2030":   round(slope * 2030 + intercept, 1),
    }


def recovery_time_test():
    u, p = stats.mannwhitneyu(HIGH_POVERTY_RECOVERY, LOW_POVERTY_RECOVERY,
                               alternative="greater")
    d_pooled = np.sqrt((np.std(LOW_POVERTY_RECOVERY)**2 +
                         np.std(HIGH_POVERTY_RECOVERY)**2) / 2)
    cohens_d = (np.mean(HIGH_POVERTY_RECOVERY) -
                 np.mean(LOW_POVERTY_RECOVERY)) / d_pooled
    return {
        "low_poverty_mean":  round(np.mean(LOW_POVERTY_RECOVERY), 1),
        "high_poverty_mean": round(np.mean(HIGH_POVERTY_RECOVERY), 1),
        "ratio":             round(np.mean(HIGH_POVERTY_RECOVERY) /
                                    np.mean(LOW_POVERTY_RECOVERY), 1),
        "mannwhitney_u":     round(u, 3),
        "p_value":           round(p, 4),
        "cohens_d":          round(cohens_d, 3),
        "significant":       p < 0.05,
    }


def run_all():
    print("=" * 55)
    print("  STATISTICAL ANALYSIS — FEMA + POVERTY")
    print("=" * 55)

    print("\n[1] Poverty Rate vs Disaster Declarations — Spearman")
    r1 = poverty_declaration_correlation()
    print(f"  Spearman r: {r1['spearman_r']}, p={r1['p_value']}")
    print(f"  Direction:  {r1['direction']}")
    print(f"  Significant: {r1['significant']}")

    print("\n[2] Disaster Cost Trend — Linear Regression")
    r2 = cost_trend_regression()
    print(f"  Slope:      +${r2['slope_B_per_year']}B per year")
    print(f"  R²:         {r2['r_squared']}")
    print(f"  Projected 2030: ${r2['projected_2030']}B/year")

    print("\n[3] Recovery Time — Mann-Whitney U")
    r3 = recovery_time_test()
    print(f"  Low poverty:  {r3['low_poverty_mean']} months avg")
    print(f"  High poverty: {r3['high_poverty_mean']} months avg")
    print(f"  Ratio:        {r3['ratio']}x longer")
    print(f"  p-value:      {r3['p_value']}")
    print(f"  Cohen's d:    {r3['cohens_d']}")

    return r1, r2, r3


if __name__ == "__main__":
    run_all()
