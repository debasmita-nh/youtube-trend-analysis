"""YouTube Trending Video Analysis Dashboard.

An interactive Streamlit web dashboard analyzing 105K+ trending YouTube videos
across the United States (US), Great Britain (GB), and India (IN).
"""

from pathlib import Path
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import streamlit as st

# Apply consistent aesthetic styling to Matplotlib and Seaborn figures
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.family": "sans-serif",
    "figure.autolayout": True,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

# ==============================================================================
# 1. Page Configuration
# ==============================================================================
st.set_page_config(
    page_title="YouTube Trending Video Analysis",
    layout="wide",
    page_icon="📊",
)


# ==============================================================================
# 2. Data Loading with Caching & Error Handling
# ==============================================================================
@st.cache_data(show_spinner="Loading and parsing YouTube trending dataset...")
def load_data(data_path: str = "data/sample_youtube_data.csv") -> pd.DataFrame:
    """Loads and caches the sampled YouTube trending dataset.

    Parses temporal columns ('trending_date', 'publish_time') and computes
    the engagement rate metric if not already present. Includes error
    handling to alert the user if the dataset has not been generated.

    Args:
        data_path (str): Relative or absolute path to the sampled CSV file.

    Returns:
        pd.DataFrame: Cleaned DataFrame with parsed dates and engagement rate.
    """
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        # Fallback to path relative to the script file location
        resolved_path = Path(__file__).resolve().parent / data_path

    # Error handling: check file existence before attempting to read
    if not resolved_path.exists():
        st.error(
            "❌ **Sample dataset not found!** "
            f"Unable to locate `{data_path}`.\n\n"
            "Please generate the sample dataset by executing:\n"
            "```powershell\n"
            "python src/preprocess.py        # If processed data is not yet generated\n"
            "python create_sample_data.py   # Creates the 21,000-row stratified sample\n"
            "```"
        )
        st.stop()
        return pd.DataFrame()

    df = pd.read_csv(
        resolved_path,
        parse_dates=["trending_date", "publish_time"],
    )

    # Calculate engagement_rate if not already in dataframe:
    # engagement_rate = (likes + dislikes + comment_count) / views
    if "engagement_rate" not in df.columns:
        df["engagement_rate"] = (
            df["likes"] + df["dislikes"] + df["comment_count"]
        ) / df["views"]

    return df


# ==============================================================================
# 3. Main Header & Description
# ==============================================================================
def render_header():
    """Renders the dashboard title and introductory description."""
    st.title("📊 YouTube Trending Video Analysis Dashboard")
    st.markdown(
        "Analyze viewership dynamics, audience engagement patterns, and category trends "
        "across **105,000+** trending YouTube videos in three key markets: the **United States (US)**, "
        "**Great Britain (GB)**, and **India (IN)**."
    )
    st.caption(
        "Note: This dashboard uses a representative random sample of 21,000 videos "
        "(7,000 per country) for optimized performance."
    )


# ==============================================================================
# 4. Sidebar Filters
# ==============================================================================
def render_sidebar(df: pd.DataFrame):
    """Renders interactive filtering widgets in the sidebar.

    Args:
        df (pd.DataFrame): Unfiltered dataset used to populate filter options.

    Returns:
        tuple[list[str], list[str]]: Selected countries and categories.
    """
    st.sidebar.header("🔍 Filter Options")

    # Multiselect filter for country (US, GB, IN)
    available_countries = ["US", "GB", "IN"]
    selected_countries = st.sidebar.multiselect(
        "Select Country:",
        options=available_countries,
        default=available_countries,
        help="Filter trending videos by country region.",
    )

    # Multiselect filter for category_name (limited to top 15 categories by count)
    top_15_categories = (
        df["category_name"].value_counts().nlargest(15).index.tolist()
    )
    selected_categories = st.sidebar.multiselect(
        "Select Category:",
        options=top_15_categories,
        default=top_15_categories,
        help="Filtered to top 15 categories by total video count.",
    )

    return selected_countries, selected_categories


# ==============================================================================
# 5. Data Filtering
# ==============================================================================
def filter_data(
    df: pd.DataFrame, selected_countries: list[str], selected_categories: list[str]
) -> pd.DataFrame:
    """Filters the dataset based on sidebar selections."""
    if not selected_countries or not selected_categories:
        return pd.DataFrame(columns=df.columns)

    return df[
        (df["country"].isin(selected_countries))
        & (df["category_name"].isin(selected_categories))
    ]


# ==============================================================================
# 6. KPI Metric Cards
# ==============================================================================
def render_kpis(filtered_df: pd.DataFrame, num_countries_selected: int):
    """Displays 4 KPI metric cards across a single horizontal row."""
    col1, col2, col3, col4 = st.columns(4)

    if filtered_df.empty:
        col1.metric("Total Videos", "0")
        col2.metric("Average Views", "0.00M")
        col3.metric("Avg Engagement Rate", "0.00%")
        col4.metric("Countries Selected", f"{num_countries_selected}")
        st.warning("⚠️ No videos match the current filter selection. Please broaden your filters.")
        return

    total_videos = len(filtered_df)
    avg_views = filtered_df["views"].mean()
    avg_views_str = f"{avg_views / 1_000_000:.2f}M"
    avg_engagement = filtered_df["engagement_rate"].mean() * 100
    avg_engagement_str = f"{avg_engagement:.2f}%"

    col1.metric("Total Videos", f"{total_videos:,}")
    col2.metric("Average Views", avg_views_str)
    col3.metric("Avg Engagement Rate", avg_engagement_str)
    col4.metric("Countries Selected", f"{num_countries_selected}")


# ==============================================================================
# 7. Tab 1: Category Insights
# ==============================================================================
def render_category_tab(filtered_df: pd.DataFrame):
    """Renders category view analysis and top 10 categories bar chart."""
    st.subheader("Top Categories by Average Views")

    if filtered_df.empty:
        st.info("No data available for the current filter criteria.")
        return

    # Group by category_name, calculate mean views, mean engagement, count
    cat_summary = (
        filtered_df.groupby("category_name")
        .agg(
            mean_views=("views", "mean"),
            mean_engagement_rate=("engagement_rate", "mean"),
            count=("views", "count"),
        )
        .sort_values(by="mean_views", ascending=False)
        .head(10)
        .reset_index()
    )

    # Horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=cat_summary,
        y="category_name",
        x="mean_views",
        palette="crest",
        ax=ax,
    )
    ax.set_title("Top 10 Categories by Average Views", fontweight="bold", pad=12)
    ax.set_xlabel("Average Views (Millions)", labelpad=8)
    ax.set_ylabel("Category", labelpad=8)
    ax.xaxis.set_major_formatter(
        ticker.FuncFormatter(lambda x, pos: f"{x * 1e-6:.1f}M")
    )

    # Add data labels at the end of each bar
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(
                f"{width * 1e-6:.2f}M",
                (width, p.get_y() + p.get_height() / 2.0),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=9,
                color="#333333",
            )

    st.pyplot(fig)
    plt.close(fig)

    # Underlying formatted DataFrame
    st.markdown("##### Detailed Category Performance Table")
    display_df = cat_summary.copy()
    display_df["Average Views"] = display_df["mean_views"].map(lambda x: f"{x:,.0f}")
    display_df["Avg Engagement Rate"] = display_df["mean_engagement_rate"].map(
        lambda x: f"{x * 100:.2f}%"
    )
    display_df["Video Count"] = display_df["count"].map(lambda x: f"{x:,}")
    display_df = display_df.rename(columns={"category_name": "Category Name"})[
        ["Category Name", "Average Views", "Avg Engagement Rate", "Video Count"]
    ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ==============================================================================
# 8. Tab 2: Time Trends
# ==============================================================================
def render_time_trends_tab(filtered_df: pd.DataFrame):
    """Renders Day-of-Week and Publish-Hour viewership trends in two columns."""
    st.subheader("Publishing Timing vs. Viewership")

    if filtered_df.empty:
        st.info("No data available for the current filter criteria.")
        return

    col_day, col_hour = st.columns(2)

    # Left Column: Day of Week Bar Chart (ordered Monday to Sunday)
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    with col_day:
        st.markdown("##### Average Views by Day of the Week")
        day_summary = (
            filtered_df.groupby("publish_day_of_week")["views"]
            .mean()
            .reindex(day_order)
            .reset_index()
        )

        fig_day, ax_day = plt.subplots(figsize=(7, 5))
        sns.barplot(
            data=day_summary,
            x="publish_day_of_week",
            y="views",
            palette="Blues_r",
            ax=ax_day,
        )
        ax_day.set_title("Average Views by Day of Week", fontweight="bold", pad=12)
        ax_day.set_xlabel("Day of Week", labelpad=8)
        ax_day.set_ylabel("Average Views (Millions)", labelpad=8)
        ax_day.set_xticklabels(
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], rotation=0
        )
        ax_day.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: f"{y * 1e-6:.1f}M")
        )

        # Highlight highest day with label
        max_val = day_summary["views"].max()
        for p in ax_day.patches:
            height = p.get_height()
            if height == max_val:
                ax_day.annotate(
                    f"Peak: {height * 1e-6:.2f}M",
                    (p.get_x() + p.get_width() / 2.0, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=9,
                    color="#1b4f72",
                )

        st.pyplot(fig_day)
        plt.close(fig_day)

    # Right Column: Publish Hour Line Chart (0-23)
    with col_hour:
        st.markdown("##### Average Views by Publish Hour (UTC)")
        hour_summary = (
            filtered_df.groupby("publish_hour")["views"]
            .mean()
            .reindex(range(24))
            .reset_index()
        )

        fig_hour, ax_hour = plt.subplots(figsize=(7, 5))
        ax_hour.plot(
            hour_summary["publish_hour"],
            hour_summary["views"],
            color="#e67e22",
            marker="o",
            linewidth=2.5,
            markersize=5,
        )
        ax_hour.set_title("Average Views by Publish Hour (0-23)", fontweight="bold", pad=12)
        ax_hour.set_xlabel("Hour of Day (UTC)", labelpad=8)
        ax_hour.set_ylabel("Average Views (Millions)", labelpad=8)
        ax_hour.set_xticks(range(0, 24, 2))
        ax_hour.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: f"{y * 1e-6:.1f}M")
        )

        st.pyplot(fig_hour)
        plt.close(fig_hour)


# ==============================================================================
# 9. Tab 3: Country Comparison
# ==============================================================================
def render_country_tab(df: pd.DataFrame, selected_categories: list[str]):
    """Compares views and engagement across all 3 countries filtered only by category."""
    st.subheader("Cross-Country Market Comparison")
    st.caption(
        "Note: This comparison incorporates all 3 countries (US, GB, IN) filtered "
        "by the selected category set to provide an unbiased benchmark."
    )

    if not selected_categories:
        st.info("Please select at least one category from the sidebar.")
        return

    # Filter by category only (ignore country filter so all 3 countries are benchmarked)
    cat_filtered_df = df[df["category_name"].isin(selected_categories)]

    if cat_filtered_df.empty:
        st.info("No records match the selected category filter.")
        return

    # Group by country
    country_summary = (
        cat_filtered_df.groupby("country")
        .agg(
            mean_views=("views", "mean"),
            mean_engagement_rate=("engagement_rate", "mean"),
            video_count=("views", "count"),
        )
        .reindex(["US", "GB", "IN"])
        .dropna(subset=["mean_views"])
        .reset_index()
    )

    # Grouped / Styled Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    country_colors = {"US": "#2980b9", "GB": "#27ae60", "IN": "#e67e22"}
    palette = [country_colors.get(c, "#34495e") for c in country_summary["country"]]

    bars = ax.bar(
        country_summary["country"],
        country_summary["mean_views"],
        color=palette,
        width=0.45,
        edgecolor="#333333",
        linewidth=0.8,
    )
    ax.set_title("Mean Views Comparison Across Countries", fontweight="bold", pad=12)
    ax.set_xlabel("Country Code", labelpad=8)
    ax.set_ylabel("Average Views (Millions)", labelpad=8)
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda y, pos: f"{y * 1e-6:.1f}M")
    )

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height * 1e-6:.2f}M",
            (bar.get_x() + bar.get_width() / 2.0, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    st.pyplot(fig)
    plt.close(fig)

    # Underlying Table
    st.markdown("##### Country Metrics Summary")
    display_country_df = country_summary.copy()
    display_country_df["Mean Views"] = display_country_df["mean_views"].map(
        lambda x: f"{x:,.0f}"
    )
    display_country_df["Mean Engagement Rate"] = display_country_df[
        "mean_engagement_rate"
    ].map(lambda x: f"{x * 100:.2f}%")
    display_country_df["Video Count"] = display_country_df["video_count"].map(
        lambda x: f"{x:,}"
    )
    display_country_df = display_country_df.rename(
        columns={"country": "Country"}
    )[["Country", "Mean Views", "Mean Engagement Rate", "Video Count"]]

    st.dataframe(display_country_df, use_container_width=True, hide_index=True)


# ==============================================================================
# 10. Tab 4: Title Analysis
# ==============================================================================
def render_title_analysis_tab(filtered_df: pd.DataFrame):
    """Analyzes the viewership impact of sensational title formatting."""
    st.subheader("Impact of Title Formatting on Views")

    if filtered_df.empty:
        st.info("No data available for the current filter criteria.")
        return

    # Recreate boolean feature columns on the filtered slice
    title_df = filtered_df.copy()
    title_df["has_caps_words"] = title_df["title"].apply(
        lambda t: bool(re.search(r"\b[A-Z]{3,}\b", str(t)))
    )
    title_df["has_exclamation"] = (
        title_df["title"].astype(str).str.contains("!", regex=False)
    )

    col_caps, col_excl = st.columns(2)

    # 1. ALL-CAPS Words Analysis
    with col_caps:
        st.markdown("##### ALL-CAPS Words in Title")
        caps_stats = (
            title_df.groupby("has_caps_words")["views"]
            .agg(["mean", "count"])
            .rename(index={False: "Without ALL-CAPS", True: "With ALL-CAPS"})
        )

        fig_caps, ax_caps = plt.subplots(figsize=(7, 5))
        bars_caps = ax_caps.bar(
            caps_stats.index,
            caps_stats["mean"],
            color=["#3498db", "#e74c3c"],
            width=0.45,
            edgecolor="#333333",
            linewidth=0.8,
        )
        ax_caps.set_title("Average Views: ALL-CAPS Words", fontweight="bold", pad=12)
        ax_caps.set_ylabel("Average Views (Millions)", labelpad=8)
        ax_caps.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: f"{y * 1e-6:.1f}M")
        )

        for bar in bars_caps:
            height = bar.get_height()
            ax_caps.annotate(
                f"{height * 1e-6:.2f}M",
                (bar.get_x() + bar.get_width() / 2.0, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=9,
            )

        st.pyplot(fig_caps)
        plt.close(fig_caps)

        # Percentage Difference Info Box
        if "Without ALL-CAPS" in caps_stats.index and "With ALL-CAPS" in caps_stats.index:
            mean_no_caps = caps_stats.loc["Without ALL-CAPS", "mean"]
            mean_with_caps = caps_stats.loc["With ALL-CAPS", "mean"]
            if mean_no_caps > 0:
                diff_pct = ((mean_with_caps - mean_no_caps) / mean_no_caps) * 100
                if diff_pct < 0:
                    st.info(
                        f"📉 **{abs(diff_pct):.1f}% lower average views** for titles with ALL-CAPS words "
                        f"({mean_with_caps * 1e-6:.2f}M vs. {mean_no_caps * 1e-6:.2f}M)."
                    )
                else:
                    st.info(
                        f"📈 **{diff_pct:.1f}% higher average views** for titles with ALL-CAPS words "
                        f"({mean_with_caps * 1e-6:.2f}M vs. {mean_no_caps * 1e-6:.2f}M)."
                    )

    # 2. Exclamation Mark (!) Analysis
    with col_excl:
        st.markdown("##### Exclamation Mark (`!`) in Title")
        excl_stats = (
            title_df.groupby("has_exclamation")["views"]
            .agg(["mean", "count"])
            .rename(index={False: "Without '!'", True: "With '!'"})
        )

        fig_excl, ax_excl = plt.subplots(figsize=(7, 5))
        bars_excl = ax_excl.bar(
            excl_stats.index,
            excl_stats["mean"],
            color=["#2ecc71", "#e67e22"],
            width=0.45,
            edgecolor="#333333",
            linewidth=0.8,
        )
        ax_excl.set_title("Average Views: Exclamation Mark (!)", fontweight="bold", pad=12)
        ax_excl.set_ylabel("Average Views (Millions)", labelpad=8)
        ax_excl.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda y, pos: f"{y * 1e-6:.1f}M")
        )

        for bar in bars_excl:
            height = bar.get_height()
            ax_excl.annotate(
                f"{height * 1e-6:.2f}M",
                (bar.get_x() + bar.get_width() / 2.0, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=9,
            )

        st.pyplot(fig_excl)
        plt.close(fig_excl)

        # Percentage Difference Info Box
        if "Without '!'" in excl_stats.index and "With '!'" in excl_stats.index:
            mean_no_excl = excl_stats.loc["Without '!'", "mean"]
            mean_with_excl = excl_stats.loc["With '!'", "mean"]
            if mean_no_excl > 0:
                diff_excl_pct = ((mean_with_excl - mean_no_excl) / mean_no_excl) * 100
                if diff_excl_pct < 0:
                    st.info(
                        f"📉 **{abs(diff_excl_pct):.1f}% lower average views** for titles containing '!' "
                        f"({mean_with_excl * 1e-6:.2f}M vs. {mean_no_excl * 1e-6:.2f}M)."
                    )
                else:
                    st.info(
                        f"📈 **{diff_excl_pct:.1f}% higher average views** for titles containing '!' "
                        f"({mean_with_excl * 1e-6:.2f}M vs. {mean_no_excl * 1e-6:.2f}M)."
                    )


# ==============================================================================
# 11. Footer
# ==============================================================================
def render_footer():
    """Renders the dashboard footer with attribution and project links."""
    st.divider()
    st.markdown(
        "<div style='text-align: center; color: #666666; font-size: 0.9em; padding-bottom: 20px;'>"
        "Built with Streamlit | Data source: Kaggle YouTube Trending Video Statistics | "
        "<a href='https://github.com/debasmita-nh/youtube-trend-analysis' target='_blank'>GitHub Repo</a>"
        "</div>",
        unsafe_allow_html=True,
    )


# ==============================================================================
# Main Application Flow
# ==============================================================================
def main():
    # Load cached dataset with error handling
    df = load_data()
    if df.empty:
        return

    # Sidebar controls
    selected_countries, selected_categories = render_sidebar(df)

    # Main dashboard header
    render_header()

    # Filtered dataframe for tabs honoring sidebar country and category selections
    filtered_df = filter_data(df, selected_countries, selected_categories)

    # Display KPI metric cards
    render_kpis(filtered_df, len(selected_countries))

    # Horizontal divider
    st.divider()

    # Tabbed Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Category Insights",
        "⏰ Time Trends",
        "🌍 Country Comparison",
        "📝 Title Analysis",
    ])

    with tab1:
        render_category_tab(filtered_df)

    with tab2:
        render_time_trends_tab(filtered_df)

    with tab3:
        render_country_tab(df, selected_categories)

    with tab4:
        render_title_analysis_tab(filtered_df)

    # Footer section
    render_footer()


if __name__ == "__main__":
    main()

# Run this dashboard locally with:
# streamlit run app.py
