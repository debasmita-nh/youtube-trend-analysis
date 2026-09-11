"""Data preprocessing and transformation pipeline for YouTube trending video data.

This module provides functionality to merge trending datasets across multiple countries,
map category IDs to readable titles, parse datetime components, deduplicate records,
and clean data for downstream analytics.
"""

from pathlib import Path
import sys
from typing import List, Union

import pandas as pd

# Support direct script execution and modular package imports
try:
    from data_loader import load_category_mapping, load_video_data
except ImportError:
    from src.data_loader import load_category_mapping, load_video_data

# Ensure standard output supports Unicode on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def clean_and_merge_data(
    country_codes: List[str], data_dir: Union[str, Path] = "data"
) -> pd.DataFrame:
    """Loads, labels, and merges YouTube trending datasets across multiple countries.

    For each specified country code:
      1. Loads the corresponding trending video CSV (e.g., 'USvideos.csv').
      2. Loads the corresponding category JSON mapping (e.g., 'US_category_id.json').
      3. Maps 'category_id' to human-readable 'category_name'.
      4. Appends a 'country' column with the respective country code.
      5. Concatenates all country datasets into a unified DataFrame.

    Args:
        country_codes (List[str]): List of ISO country codes (e.g., ['US', 'IN', 'GB']).
        data_dir (Union[str, Path], optional): Path to directory containing raw data files.
            Defaults to "data".

    Returns:
        pd.DataFrame: Merged DataFrame containing records from all specified countries.

    Raises:
        FileNotFoundError: If the data directory or required data files do not exist.
        ValueError: If country_codes list is empty.
    """
    if not country_codes:
        raise ValueError("country_codes list cannot be empty.")

    resolved_data_dir = Path(data_dir)
    # If called from within src/ directory and data_dir doesn't exist locally, check parent
    if not resolved_data_dir.exists():
        parent_candidate = Path(__file__).resolve().parent.parent / data_dir
        if parent_candidate.exists():
            resolved_data_dir = parent_candidate
        else:
            raise FileNotFoundError(f"Data directory not found: {resolved_data_dir.resolve()}")

    country_dfs: List[pd.DataFrame] = []

    for country in country_codes:
        csv_path = resolved_data_dir / f"{country}videos.csv"
        json_path = resolved_data_dir / f"{country}_category_id.json"

        print(f"[+] Loading {country} dataset: {csv_path.name}")
        df = load_video_data(csv_path)

        print(f"[+] Mapping categories from: {json_path.name}")
        category_mapping = load_category_mapping(json_path)

        # Map category IDs to titles
        df["category_name"] = df["category_id"].map(category_mapping)

        # Assign country code column
        df["country"] = country

        country_dfs.append(df)

    # Concatenate all loaded country DataFrames
    merged_df = pd.concat(country_dfs, ignore_index=True)
    print(f"[+] Merged {len(country_codes)} countries. Total records: {len(merged_df):,}")
    return merged_df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and enriches the YouTube trending DataFrame.

    Applies the following transformation steps:
      1. Converts 'trending_date' (format 'YY.DD.MM') into datetime.
      2. Converts 'publish_time' (ISO 8601 UTC) into datetime.
      3. Extracts 'publish_hour' (0-23) and 'publish_day_of_week' (e.g. 'Monday').
      4. Removes duplicate rows based on ('video_id', 'trending_date') combination.
      5. Fills missing values in 'description' column with empty strings.
      6. Drops rows where 'views' is zero or negative.

    Args:
        df (pd.DataFrame): Raw or merged DataFrame to be cleaned.

    Returns:
        pd.DataFrame: Cleaned, deduplicated, and feature-enriched DataFrame.
    """
    cleaned = df.copy()

    # 1. Convert trending_date to datetime (Format: YY.DD.MM, e.g. '17.14.11' -> 2017-11-14)
    cleaned["trending_date"] = pd.to_datetime(cleaned["trending_date"], format="%y.%d.%m")

    # 2. Convert publish_time to datetime
    cleaned["publish_time"] = pd.to_datetime(cleaned["publish_time"])

    # 3. Extract temporal features: publish_hour and publish_day_of_week
    cleaned["publish_hour"] = cleaned["publish_time"].dt.hour
    cleaned["publish_day_of_week"] = cleaned["publish_time"].dt.day_name()

    # 4. Remove duplicate rows based on video_id and trending_date combination
    initial_rows = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["video_id", "trending_date"])
    dropped_dupes = initial_rows - len(cleaned)
    if dropped_dupes > 0:
        print(f"[i] Dropped {dropped_dupes:,} duplicate rows based on ('video_id', 'trending_date').")

    # 5. Handle missing values in description
    cleaned["description"] = cleaned["description"].fillna("")

    # 6. Filter out invalid rows with views <= 0
    non_positive_views = (cleaned["views"] <= 0).sum()
    if non_positive_views > 0:
        print(f"[i] Dropping {non_positive_views:,} rows with zero or negative views.")
    cleaned = cleaned[cleaned["views"] > 0]

    return cleaned


if __name__ == "__main__":
    # Resolve directory paths relative to the project root
    project_root = Path(__file__).resolve().parent.parent
    data_directory = project_root / "data"
    output_filepath = data_directory / "processed_youtube_data.csv"

    print("=" * 70)
    print("YOUTUBE TRENDING DATA PREPROCESSING PIPELINE")
    print("=" * 70)

    # 1. Merge datasets for US, IN, and GB
    countries_to_process = ["US", "IN", "GB"]
    merged_data = clean_and_merge_data(countries_to_process, data_dir=data_directory)

    # 2. Clean, deduplicate, and feature engineer
    print("\n[+] Cleaning and formatting DataFrame...")
    cleaned_data = clean_dataframe(merged_data)

    # 3. Display statistics
    print(f"\n[+] Final Cleaned DataFrame Shape: {cleaned_data.shape}")
    print(f"    Total Rows   : {cleaned_data.shape[0]:,}")
    print(f"    Total Columns: {cleaned_data.shape[1]}")

    print("\n[+] Value counts for 'country' column:")
    country_counts = cleaned_data["country"].value_counts()
    for country, count in country_counts.items():
        print(f"    {country:>3}: {count:>8,} records ({count / len(cleaned_data):.2%})")

    # 4. Save processed dataset to CSV
    print(f"\n[+] Saving cleaned dataset to: {output_filepath}")
    cleaned_data.to_csv(output_filepath, index=False)
    print(f"[+] Successfully saved processed data ({output_filepath.stat().st_size / (1024 * 1024):.2f} MB)")

    print("=" * 70)
