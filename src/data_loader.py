"""Data loading module for YouTube trending video analysis.

This module provides functions to load trending video CSV datasets with automatic
encoding fallback and parse category ID to title mappings from YouTube API JSON files.
"""

import json
from pathlib import Path
import sys
from typing import Dict, Union

import pandas as pd

# Ensure standard output can handle Unicode characters (e.g. emojis, symbols in YouTube titles) on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_video_data(filepath: Union[str, Path]) -> pd.DataFrame:
    """Reads a YouTube trending CSV file using pandas, handling encoding issues.

    Attempts to load the CSV using standard 'utf-8' encoding. If a UnicodeDecodeError
    occurs (common in datasets containing international character sets or special
    characters), it automatically falls back to 'latin1' (ISO-8859-1).

    Args:
        filepath (Union[str, Path]): Path to the YouTube trending CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame containing trending video statistics.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        pd.errors.ParserError: If the file cannot be parsed as a CSV.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Video data file not found: {path.resolve()}")

    try:
        # First attempt reading with UTF-8 encoding
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to latin1 for non-UTF8 characters
        df = pd.read_csv(path, encoding="latin1")

    return df


def load_category_mapping(json_filepath: Union[str, Path]) -> Dict[int, str]:
    """Reads a YouTube category JSON file and extracts category ID to title mapping.

    Parses the standard YouTube API category JSON structure and creates a lookup
    dictionary matching integer category IDs to their human-readable title names.

    Args:
        json_filepath (Union[str, Path]): Path to the YouTube category JSON file.

    Returns:
        Dict[int, str]: Dictionary mapping category ID (int) to category name (str).

    Raises:
        FileNotFoundError: If the specified JSON file does not exist.
        KeyError: If expected keys ('items', 'id', 'snippet', 'title') are missing.
    """
    path = Path(json_filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Category mapping file not found: {path.resolve()}")

    with open(path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    category_mapping: Dict[int, str] = {}
    for item in data.get("items", []):
        try:
            cat_id = int(item["id"])
            cat_title = item["snippet"]["title"]
            category_mapping[cat_id] = cat_title
        except (KeyError, ValueError) as err:
            # Handle potential malformed items gracefully
            continue

    return category_mapping


if __name__ == "__main__":
    # Resolve directory path relative to project structure (youtube-trend-analysis/data/)
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"

    sample_csv_path = data_dir / "USvideos.csv"
    sample_json_path = data_dir / "US_category_id.json"

    print("=" * 70)
    print("YOUTUBE TRENDING DATA LOADER")
    print("=" * 70)

    # 1. Load and display category mapping
    if sample_json_path.exists():
        print(f"\n[+] Loading category mapping from: {sample_json_path.name}")
        category_mapping = load_category_mapping(sample_json_path)
        print(f"Total categories identified: {len(category_mapping)}")
        print("Category Mapping Dictionary:")
        for cat_id, cat_name in sorted(category_mapping.items()):
            print(f"  ID {cat_id:>2}: {cat_name}")
    else:
        print(f"\n[!] Category JSON file not found at: {sample_json_path}")

    # 2. Load and display trending video dataset
    if sample_csv_path.exists():
        print(f"\n[+] Loading trending video data from: {sample_csv_path.name}")
        df = load_video_data(sample_csv_path)

        print(f"\n[+] DataFrame Shape: {df.shape} (rows: {df.shape[0]:,}, columns: {df.shape[1]})")
        print("\n[+] First 5 Rows:")
        print(df.head())
    else:
        print(f"\n[!] Video CSV file not found at: {sample_csv_path}")

    print("\n" + "=" * 70)
