"""
src/fetch_fema.py
Live data fetcher from FEMA OpenFEMA API.

No API key needed. Completely open.
Docs: https://www.fema.gov/about/openfema/api
Data: https://www.fema.gov/api/open/v2/disasterDeclarationsSummaries

The OpenFEMA dataset covers every major disaster declaration
since 1953. Over 25,000 records total.
"""

import requests
import pandas as pd
from pathlib import Path

FEMA_BASE = "https://www.fema.gov/api/open/v2"


def fetch_declarations(state: str = None,
                       year_start: int = 2000,
                       year_end: int = 2023,
                       limit: int = 1000) -> pd.DataFrame:
    """
    Fetch disaster declarations from FEMA OpenFEMA API.

    Args:
        state: Two-letter state code e.g. 'TX', 'LA'. None = all states.
        year_start: Start year filter.
        year_end: End year filter.
        limit: Max records per request.

    Returns:
        DataFrame with declaration details.
    """
    url = f"{FEMA_BASE}/disasterDeclarationsSummaries"

    filters = [
        f"declarationDate gt '{year_start}-01-01'",
        f"declarationDate lt '{year_end+1}-01-01'",
    ]
    if state:
        filters.append(f"state eq '{state}'")

    params = {
        "$filter":  " and ".join(filters),
        "$orderby": "declarationDate desc",
        "$top":     limit,
        "$format":  "json",
    }

    print(f"  Fetching FEMA declarations{' for ' + state if state else ''}...")
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    records = data.get("DisasterDeclarationsSummaries", [])
    df = pd.DataFrame(records)

    if save_raw and len(df) > 0:
        Path("data/raw").mkdir(parents=True, exist_ok=True)
        fname = f"data/raw/fema_declarations{'_'+state if state else '_all'}.csv"
        df.to_csv(fname, index=False)
        print(f"  Saved → {fname}")

    print(f"  {len(df)} declarations fetched")
    return df


def fetch_housing_assistance(disaster_number: str) -> pd.DataFrame:
    """Fetch housing assistance for a specific disaster."""
    url = f"{FEMA_BASE}/HousingAssistanceOwners"
    params = {
        "$filter": f"disasterNumber eq '{disaster_number}'",
        "$format": "json",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return pd.DataFrame(data.get("HousingAssistanceOwners", []))


if __name__ == "__main__":
    print("FEMA OpenFEMA API Fetcher")
    print("No API key required — https://www.fema.gov/about/openfema/api")
    print()
    try:
        df = fetch_declarations(state="LA", year_start=2005, year_end=2006, limit=5)
        if len(df) > 0:
            print(f"Sample: {df['incidentType'].values[0]} in {df['state'].values[0]}")
    except Exception as e:
        print(f"  Note: {e}")
        print("  Using embedded data from src/fema_data.py")

save_raw = False  # set True to write raw CSV files
