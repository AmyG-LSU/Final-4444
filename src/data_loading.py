"""
data_loading.py

Centralized data loading and five-year panel construction for the
Home Value Prediction project.

Five-Year Period Extraction
- Determine the correct 5-year window
- Extract, validate, and store this period as a working dataset
- Ensure alignment across income, crime, school, and home-value series
"""

from pathlib import Path
from functools import reduce
from typing import List, Tuple
import re

import pandas as pd

# ---------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------

# Base /data directory (project_root/data)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Subdirectories
MHI_DIR = DATA_DIR / "Median Household Income"
SCHOOL_DIR = DATA_DIR / "School Data Year"

# Standardized column names
YEAR_COL = "year"
LOCATION_COL = "parish"  # normalized location name for all datasets


# ---------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------

def _standardize_parish_from_crime(name: str) -> str | None:
    """
    Convert crime 'Parish' names like 'East Baton Rouge', 'DE SOTO'
    into a consistent format like 'East Baton Rouge Parish', 'De Soto Parish'.
    """
    if not isinstance(name, str):
        return None
    name = name.strip().title()
    if not name.endswith("Parish"):
        name = name + " Parish"
    return name


def _extract_year_from_period_label(label: str) -> int:
    """
    Parse a year out of strings such as 'Jan-15', '2015-01', or '201506'.
    Prefers 4-digit matches but falls back to 2-digit suffixes (assumed 2000s).
    """
    token = str(label).strip()
    if not token:
        raise ValueError(f"Empty period label: {label!r}")

    digit_chunks = re.findall(r"\d+", token)

    for chunk in digit_chunks:
        if len(chunk) >= 4:
            return int(chunk[:4])

    if digit_chunks:
        suffix = digit_chunks[-1]
        if len(suffix) == 2:
            return 2000 + int(suffix)

    raise ValueError(f"Cannot parse year from label: {label!r}")


# ---------------------------------------------------------------------
# Median Household Income (2014–2023, one CSV per year)
# ---------------------------------------------------------------------

def load_median_income() -> pd.DataFrame:
    """
    Load and stack median household income CSVs (2014–2023) into one DataFrame.

    Expected file pattern:
      data/Median Household Income/2014.csv
      ...
      data/Median Household Income/2023.csv

    Expected columns (per file):
      - 'NAME' (e.g., 'Acadia Parish, Louisiana')
      - 'S1903_C02_001E' (Median household income in dollars, total)

    Output columns:
      - parish
      - year
      - median_income
    """
    dfs: List[pd.DataFrame] = []

    for year in range(2014, 2024):  # 2014–2023 inclusive
        path = MHI_DIR / f"{year}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Median income file not found: {path}")

        df = pd.read_csv(path)

        # adjust this if the specific CSV format differs
        df = df.iloc[1:].copy()

        # standardize parish name: "Acadia Parish, Louisiana" -> "Acadia Parish"
        if "NAME" not in df.columns:
            raise ValueError(f"Expected 'NAME' column in {path.name}, got {df.columns.tolist()}")

        df[LOCATION_COL] = (
            df["NAME"]
                .astype(str)
                .str.replace(", Louisiana", "", regex=False)
                .str.strip()
        )

        # median household income in dollars
        if "S1903_C02_001E" not in df.columns:
            raise ValueError(
                f"Expected 'S1903_C02_001E' in {path.name} for median income; "
                f"columns: {df.columns.tolist()}"
            )

        df["median_income"] = pd.to_numeric(df["S1903_C02_001E"], errors="coerce")

        # add year
        df[YEAR_COL] = year

        dfs.append(df[[LOCATION_COL, YEAR_COL, "median_income"]])

    income = pd.concat(dfs, ignore_index=True)
    return income


# ---------------------------------------------------------------------
# School Ratings (2014–2023, one XLSX per year)
# ---------------------------------------------------------------------

def load_school_ratings() -> pd.DataFrame:
    """
    Load and stack school rating spreadsheets into one DataFrame.

    Handles:
      - 2014–2017 files with 'District' column
      - 2018+ files with 'School System' column
      - Letter grade column name changes across years

    Output columns:
      - parish
      - year
      - dps_score
      - dps_letter (best-effort, may be NaN for some years)
    """
    dfs: list[pd.DataFrame] = []

    # detect available year files dynamically (2014, 2015, etc)
    year_files = sorted(
        p for p in SCHOOL_DIR.glob("*.xlsx")
        if p.stem.isdigit()
    )
    if not year_files:
        raise FileNotFoundError(f"No school rating .xlsx files found in {SCHOOL_DIR}")

    for path in year_files:
        year = int(path.stem)
        df = pd.read_excel(path)

        # location column
        location_candidates = ["District", "School System", "School System Name", "System Name"]
        loc_col = next((c for c in location_candidates if c in df.columns), None)
        if loc_col is None:
            raise ValueError(
                f"Expected one of {location_candidates} columns in {path.name}, "
                f"got: {df.columns.tolist()}"
            )

        df[LOCATION_COL] = df[loc_col].astype(str).str.strip()

        # DPS numeric score
        if "DPS" not in df.columns:
            raise ValueError(f"Expected 'DPS' column in {path.name}")
        df["dps_score"] = pd.to_numeric(df["DPS"], errors="coerce")

        # find a "letter grade" column
        letter_cols = [
            c for c in df.columns
            if str(year) in str(c) and "Letter Grade" in str(c)
        ]

        if letter_cols:
            letter_col = letter_cols[0]
            df["dps_letter"] = df[letter_col].astype(str).str.strip()
        else:
            df["dps_letter"] = pd.NA

        df[YEAR_COL] = year

        dfs.append(df[[LOCATION_COL, YEAR_COL, "dps_score", "dps_letter"]])

    school = pd.concat(dfs, ignore_index=True)
    return school


# ---------------------------------------------------------------------
# Crime Data (monthly, collapsed to annual per parish)
# ---------------------------------------------------------------------

def load_crime_annual() -> pd.DataFrame:
    """
    Convert monthly crime data into annual crime totals per parish.

    Expected file:
      data/Crime Data Month Year.csv

    Expected columns:
      - 'Parish'
      - monthly columns like 'Jan-15', 'Feb-15', etc

    Output columns:
      - parish
      - year
      - crime_total
    """
    path = DATA_DIR / "Crime Data Month Year.csv"
    if not path.exists():
        raise FileNotFoundError(f"Crime data file not found: {path}")

    df = pd.read_csv(path)

    if "Parish" not in df.columns:
        raise ValueError(f"Expected 'Parish' column in {path.name}")

    df[LOCATION_COL] = df["Parish"].apply(_standardize_parish_from_crime)

    # all monthly columns are everything except 'Parish' and our new 'parish'
    value_cols = [c for c in df.columns if c not in ["Parish", LOCATION_COL]]
    long_df = df.melt(
        id_vars=[LOCATION_COL],
        value_vars=value_cols,
        var_name="month_year",
        value_name="crime_value",
    ).dropna(subset=["crime_value"])

    long_df[YEAR_COL] = long_df["month_year"].apply(_extract_year_from_period_label)

    # aggregate annual totals per parish
    crime_annual = (
        long_df.groupby([LOCATION_COL, YEAR_COL], as_index=False)["crime_value"]
        .sum()
        .rename(columns={"crime_value": "crime_total"})
    )

    return crime_annual


# ---------------------------------------------------------------------
# Home Values (monthly, collapsed to annual avg per parish)
# ---------------------------------------------------------------------

def load_home_values_annual() -> pd.DataFrame:
    """
    Convert monthly home values into annual average home value per parish.

    Expected file:
      data/Home Values Month Year.csv

    Expected columns:
      - 'RegionName' (e.g., 'East Baton Rouge Parish')
      - monthly columns like 'Jan-00', 'Feb-00',etc

    Output columns:
      - parish
      - year
      - home_value_avg
    """
    path = DATA_DIR / "Home Values Month Year.csv"
    if not path.exists():
        raise FileNotFoundError(f"Home values data file not found: {path}")

    df = pd.read_csv(path)

    if "RegionName" not in df.columns:
        raise ValueError(f"Expected 'RegionName' column in {path.name}")

    df[LOCATION_COL] = df["RegionName"].astype(str).str.strip()

    # identifier columns
    id_cols = [LOCATION_COL]
    if "SizeRank" in df.columns:
        id_cols.append("SizeRank")

    month_col_pattern = re.compile(r".*-\d{2,4}$")
    value_cols = [
        c for c in df.columns
        if c not in id_cols and month_col_pattern.match(str(c).strip())
    ]
    if not value_cols:
        raise ValueError(
            "No monthly columns found in home value data; "
            "expected headers like 'Jan-15' or '2015-01'."
        )

    long_df = df.melt(
        id_vars=id_cols,
        value_vars=value_cols,
        var_name="month_year",
        value_name="home_value",
    ).dropna(subset=["home_value"])

    long_df[YEAR_COL] = long_df["month_year"].apply(_extract_year_from_period_label)

    home_annual = (
        long_df.groupby([LOCATION_COL, YEAR_COL], as_index=False)["home_value"]
        .mean()
        .rename(columns={"home_value": "home_value_avg"})
    )

    return home_annual


# ---------------------------------------------------------------------
# Mortgage Rates (time series, collapsed to annual avg)
# ---------------------------------------------------------------------

def load_mortgage_rates_annual() -> pd.DataFrame:
    """
    Convert mortgage rate time series into annual average rates.

    Expected file:
      data/Home Mortgage Rates.xlsx

    Expected columns:
      - 'observation_date' (YYYY-MM-DD)
      - 'MORTGAGE30US' (rate)

    Output columns:
      - year
      - mortgage_rate_avg
    """
    path = DATA_DIR / "Home Mortgage Rates.xlsx"
    if not path.exists():
        raise FileNotFoundError(f"Mortgage rates file not found: {path}")

    df = pd.read_excel(path)

    if "observation_date" not in df.columns or "MORTGAGE30US" not in df.columns:
        raise ValueError(
            f"Expected 'observation_date' and 'MORTGAGE30US' columns in {path.name}"
        )

    df["observation_date"] = pd.to_datetime(df["observation_date"])
    df[YEAR_COL] = df["observation_date"].dt.year

    rates_annual = (
        df.groupby(YEAR_COL, as_index=False)["MORTGAGE30US"]
        .mean()
        .rename(columns={"MORTGAGE30US": "mortgage_rate_avg"})
    )

    return rates_annual


# ---------------------------------------------------------------------
# Five-year window helpers
# ---------------------------------------------------------------------

def get_years(df: pd.DataFrame) -> set[int]:
    """Return the set of years present in a dataframe."""
    if YEAR_COL not in df.columns:
        raise ValueError(f"Dataframe missing '{YEAR_COL}' column.")
    return set(df[YEAR_COL].unique())


def get_common_years(*dfs: pd.DataFrame) -> List[int]:
    """Return sorted list of years that are common to all provided dataframes."""
    year_sets = [get_years(df) for df in dfs]
    common = set.intersection(*year_sets)
    return sorted(common)


def choose_five_year_window(common_years: List[int]) -> Tuple[int, int]:
    """
    Given a list of common years, pick the most recent contiguous 5-year span.

    If no perfectly contiguous span is found, default to the last 5 years.
    """
    if len(common_years) < 5:
        raise ValueError(f"Not enough common years for a 5-year window: {common_years}")

    years = sorted(common_years)

    # walk from the end backwards looking for a block of 5 consecutive years
    for i in range(len(years) - 4, -1, -1):
        window = years[i : i + 5]
        if window == list(range(window[0], window[0] + 5)):
            return window[0], window[-1]

    # fallback: last 5 years (even if not perfectly contiguous)
    return years[-5], years[-1]


def filter_to_year_range(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """Filter a DataFrame to rows with YEAR_COL between start_year and end_year inclusive."""
    return df[(df[YEAR_COL] >= start_year) & (df[YEAR_COL] <= end_year)].copy()


# ---------------------------------------------------------------------
# Core: Build the aligned five-year panel (your feature)
# ---------------------------------------------------------------------

def build_five_year_panel() -> Tuple[pd.DataFrame, int, int]:
    """
    Core function for the five-year period extraction role.

    Steps:
      - Load all datasets (income, school, crime, home values, mortgage rates)
      - Determine the common years across all of them
      - Choose a 5-year window from those common years
      - Filter each dataset to that window
      - Align and merge parish-level data on (parish, year)
      - Merge mortgage rates on year
      - Return the final panel and the start/end years

    Returns:
        panel_df: final aligned 5-year dataset
        start_year: beginning of the chosen 5-year window
        end_year: end of the chosen 5-year window
    """
    # Load datasets
    income = load_median_income()
    school = load_school_ratings()
    crime = load_crime_annual()
    home = load_home_values_annual()
    rates = load_mortgage_rates_annual()

    # Determine common years
    common_years = get_common_years(income, school, crime, home, rates)
    print("Common years across all datasets:", common_years)

    # Choose the 5-year window
    start_year, end_year = choose_five_year_window(common_years)
    print(f"Selected 5-year window: {start_year}–{end_year}")

    # Filter each dataset
    income_5 = filter_to_year_range(income, start_year, end_year)
    school_5 = filter_to_year_range(school, start_year, end_year)
    crime_5 = filter_to_year_range(crime, start_year, end_year)
    home_5 = filter_to_year_range(home, start_year, end_year)
    rates_5 = filter_to_year_range(rates, start_year, end_year)

    # Merge parish-level data on (parish, year)
    parish_dfs = [income_5, school_5, crime_5, home_5]

    def merge_on_parish_year(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(
            left,
            right,
            on=[LOCATION_COL, YEAR_COL],
            how="inner"
        )

    parish_panel = reduce(merge_on_parish_year, parish_dfs)

    # Merge mortgage rates on year only
    panel_df = pd.merge(
        parish_panel,
        rates_5,
        on=YEAR_COL,
        how="inner"
    )

    print("Final 5-year panel shape:", panel_df.shape)
    return panel_df, start_year, end_year


# ---------------------------------------------------------------------
# Module-level "working dataset" variables
# ---------------------------------------------------------------------

try:
    FIVE_YEAR_PANEL, FIVE_YEAR_START, FIVE_YEAR_END = build_five_year_panel()
except Exception as e:
    print("Warning: could not build five-year panel at import time:", e)
    FIVE_YEAR_PANEL = None
    FIVE_YEAR_START = None
    FIVE_YEAR_END = None


# manual test when running this file directly
if __name__ == "__main__":
    panel, s, e = build_five_year_panel()
    print(f"Five-year window: {s}–{e}")
    print(panel.head())