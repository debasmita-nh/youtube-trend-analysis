# YouTube Trending Video Analysis

## Overview

This repository contains an end-to-end data analytics internship project investigating the dynamics behind trending YouTube videos across three major international markets: the United States (**US**), Great Britain (**GB**), and India (**IN**). By analyzing over **105,000** records, the project uncovers empirical patterns in audience engagement, optimal release timing, regional content preferences, and title engineering strategies. The findings provide actionable, data-backed guidance for digital marketing teams, creators, and media strategists.

---

## Project Structure

```text
youtube-trend-analysis/
│
├── data/              # Storage for raw and preprocessed datasets
│   ├── *videos.csv                  # Raw regional trending CSV files
│   ├── *_category_id.json           # Regional YouTube category mapping files
│   └── processed_youtube_data.csv   # Cleaned, merged, and feature-engineered dataset
│
├── notebooks/         # Modular Jupyter notebooks for interactive analysis
│   ├── 01_eda_overview.ipynb        # Exploratory Data Analysis & category/country trends
│   ├── 02_text_analysis.ipynb       # NLP, WordClouds, title length & formatting analysis
│   └── 03_summary_insights.ipynb    # Executive summary, key findings & highlight visuals
│
├── outputs/           # Exported publication-ready charts and visual assets (PNG, 300 DPI)
│   ├── category_avg_views.png
│   ├── publish_hour_trends.png
│   ├── day_of_week_views.png
│   ├── country_comparison.png
│   ├── category_country_heatmap.png
│   ├── title_length_vs_views.png
│   ├── wordcloud_global.png
│   ├── wordcloud_by_country.png
│   └── caps_exclamation_comparison.png
│
├── src/               # Reusable Python modules and data processing pipelines
│   ├── __init__.py                  # Package initializer
│   ├── data_loader.py               # Robust CSV and JSON loading utilities
│   └── preprocess.py                # Automated data cleaning, enrichment, and merge pipeline
│
├── INSIGHTS_REPORT.md # Comprehensive business report with in-depth strategic analysis
├── requirements.txt   # Project dependencies and analytical libraries
├── .gitignore         # Version control exclusion rules
└── README.md          # Project documentation and setup guide
```

---

## Dataset

- **Source**: Kaggle — [YouTube Trending Video Statistics](https://www.kaggle.com/datasets/datasnaek/youtube-new)
- **Countries Analyzed**: United States (**US**), Great Britain (**GB**), and India (**IN**)
- **Volume**: **105,220** unique records after deduplication and data cleaning (from 117,217 raw entries)
- **Timeframe Covered**: November 14, 2017 – June 14, 2018

---

## Key Analyses Performed

- **Automated Preprocessing & Pipeline Architecture** (`src/preprocess.py`):
  - Built an encoding-resilient data loader (`utf-8` with fallback to `latin1`) handling international character sets.
  - Linked regional JSON category hierarchies to trending video records.
  - Parsed multi-format timestamps, engineered temporal features (`publish_hour`, `publish_day_of_week`), deduplicated `(video_id, trending_date)` pairs, and handled null values.
- **Category-Wise Performance Analysis**:
  - Aggregated view counts, video frequency, and engagement rates across 16+ video categories.
- **Publishing Time Optimization**:
  - Quantified viewership cycles across all 24 hours of the day (UTC) and days of the week (Monday–Sunday).
- **Cross-Country Engagement Comparison**:
  - Evaluated audience reach versus interaction density across US, GB, and IN with dual-axis comparative metrics.
- **Title Text & Linguistic Analysis**:
  - Generated global and regional WordClouds to identify viral keyword themes.
  - Measured Pearson correlation between title length/word count and video views.
  - Statistically analyzed the viewership impact of sensational formatting (ALL-CAPS words and exclamation marks).

---

## Key Findings

- **Music Dominates Viewership**: **Music** averages **9.15M views per trending video**—nearly **3×** that of any other genre (Movies at **3.19M**, Nonprofits & Activism at **2.96M**, and Entertainment at **1.64M**).
- **Friday is the Peak Publishing Window**: Videos released on **Friday** capture the highest average views (**4.58M**), followed by **Thursday** (**3.31M**), whereas **Saturday** yields the lowest average views (**1.78M**). Early off-peak uploads (**04:00 UTC**, **6.73M avg views**) significantly outperform congested afternoon hours (**14:00–17:00 UTC**).
- **Reach vs. Engagement Tradeoff by Region**: **Great Britain** commands the largest raw audience reach (**5.79M avg views**, 3.84% engagement), whereas the **United States** drives the highest engagement rate (**4.05%**, 2.36M views). **India** exhibits high content velocity (**792K avg views**, 2.55% engagement) heavily concentrated in Entertainment (**44.8%**) and News & Politics.
- **The Clickbait Penalty**:
  - Titles featuring **ALL-CAPS words** average **2.35M views** vs. **3.22M views** for standard case titles (**27.0% lower views**).
  - Titles containing **exclamation marks (`!`)** average **1.40M views** vs. **3.09M views** without (**54.6% lower views**).
  - Title character length exhibits a weak negative correlation (**-0.0782**) with viewership.

*(For detailed breakdowns and statistical methodology, refer to [INSIGHTS_REPORT.md](INSIGHTS_REPORT.md).)*

---

## How to Run This Project

### 1. Clone / Download the Repository
```bash
git clone https://github.com/your-username/youtube-trend-analysis.git
cd youtube-trend-analysis
```

### 2. Set Up Environment & Install Dependencies
```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Obtain the Dataset
Download the regional dataset files from [Kaggle](https://www.kaggle.com/datasets/datasnaek/youtube-new) and place the following files into the `data/` directory:
- `USvideos.csv` & `US_category_id.json`
- `GBvideos.csv` & `GB_category_id.json`
- `INvideos.csv` & `IN_category_id.json`

### 4. Execute the Preprocessing Pipeline
Run the automated ETL script to clean, merge, and generate `data/processed_youtube_data.csv`:
```bash
python src/preprocess.py
```

### 5. Launch Analysis Notebooks
Start JupyterLab or Jupyter Notebook to interactively explore the analysis:
```bash
jupyter notebook
```
Open and run:
1. `notebooks/01_eda_overview.ipynb` — Full exploratory data analysis and category/country visualizations.
2. `notebooks/02_text_analysis.ipynb` — Text mining, WordClouds, and title formatting studies.
3. `notebooks/03_summary_insights.ipynb` — Consolidated findings and business highlight charts.

All charts will automatically save at high resolution (300 DPI) into the `outputs/` directory upon execution.

---

## Tools & Technologies

| Layer | Technologies |
| :--- | :--- |
| **Language** | Python 3.11 |
| **Data Processing & ETL** | Pandas, NumPy |
| **Data Visualization** | Matplotlib, Seaborn |
| **Text Mining & NLP** | WordCloud, Regular Expressions (`re`) |
| **Interactive Computing** | Jupyter Notebook / JupyterLab |
| **Environment & Tooling** | Git, PowerShell, Venv |

---

## Full Insights Report

For an in-depth strategic analysis including executive implications, category benchmarks, regional content breakdowns, and actionable guidance for content marketing teams, read the complete report:

👉 **[Read the Full Insights Report (INSIGHTS_REPORT.md)](INSIGHTS_REPORT.md)**

---

## Author

**[Your Name]** — *Data Analytics Internship Project*  
- Portfolio / GitHub: `https://github.com/your-username`  
- LinkedIn: `https://linkedin.com/in/your-profile`
