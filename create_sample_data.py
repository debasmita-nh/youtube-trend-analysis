"""Script to generate a balanced stratified sample of YouTube trending data.

Samples up to 7,000 records per country (US, GB, IN) with random_state=42
for reproducible lightweight analysis, testing, and deployment.
"""

from pathlib import Path
import pandas as pd


def create_sample_data(
    input_path: str = "data/processed_youtube_data.csv",
    output_path: str = "data/sample_youtube_data.csv",
    samples_per_country: int = 7000,
    random_state: int = 42,
) -> pd.DataFrame:
    """Creates a balanced stratified sample by country and saves to CSV.

    Args:
        input_path (str): Path to processed full dataset.
        output_path (str): Path to save the sampled CSV.
        samples_per_country (int): Max rows to sample per country.
        random_state (int): Seed for reproducibility.

    Returns:
        pd.DataFrame: Stratified sampled DataFrame.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        input_file = Path(__file__).resolve().parent / input_path

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file.resolve()}")

    print(f"[+] Loading full dataset from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"[+] Full dataset loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")

    # Stratified sampling per country
    sampled_dfs = []
    for country, group in df.groupby("country"):
        n_samples = min(len(group), samples_per_country)
        sampled_group = group.sample(n=n_samples, random_state=random_state)
        sampled_dfs.append(sampled_group)
        print(f"    - {country}: sampled {len(sampled_group):,} of {len(group):,} rows")

    sample_df = pd.concat(sampled_dfs, ignore_index=True)

    # Save to output file
    output_file = Path(output_path)
    if not output_file.is_absolute():
        output_file = Path(__file__).resolve().parent / output_path

    output_file.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(output_file, index=False)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 50)
    print("STRATIFIED SAMPLE GENERATION SUMMARY")
    print("=" * 50)
    print(f"Final Shape: {sample_df.shape[0]:,} rows, {sample_df.shape[1]} columns")
    print(f"Output File: {output_file.resolve()}")
    print(f"File Size  : {file_size_mb:.2f} MB")
    print("\nValue Counts by Country in Sample:")
    for country, count in sample_df["country"].value_counts().items():
        print(f"    {country:>3}: {count:>6,} rows ({count / len(sample_df):.2%})")
    print("=" * 50)

    return sample_df


if __name__ == "__main__":
    create_sample_data()
