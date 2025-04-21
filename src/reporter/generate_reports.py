# src/reporter/generate_reports.py

# src/reporter/generate_reports.py

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.engine import Engine
import os

# src/reporter/generate_reports.py

import pandas as pd
import os
from datetime import datetime

def fetch_monthly_data(engine, year, month=None):
    if month is not None:
        query = f"""
        SELECT * FROM campaign_data
        WHERE EXTRACT(YEAR FROM starts) = {year}
          AND EXTRACT(MONTH FROM starts) = {month};
        """
        print(f"📦 Fetching data for {year}-{month:02d}...")
    else:
        query = f"""
        SELECT * FROM campaign_data
        WHERE EXTRACT(YEAR FROM starts) = {year};
        """
        print(f"📦 Fetching data for full year {year}...")

    return pd.read_sql(query, engine)


def summarize_level(df, group_cols, level_name):
    print(f"📊 Summarizing {level_name}-level data...")
    summary = df.groupby(group_cols).agg(
        Amount_Spent=('amount_spent_gbp', 'sum'),
        Results=('results', 'sum'),
        Impressions=('impressions', 'sum'),
        Link_Clicks=('link_clicks', 'sum')
    ).reset_index()

    summary['Cost_per_Results'] = summary['Amount_Spent'] / summary['Results'].replace(0, pd.NA)
    summary['CPM'] = (summary['Amount_Spent'] / summary['Impressions'].replace(0, pd.NA)) * 1000
    summary['CPC'] = summary['Amount_Spent'] / summary['Link_Clicks'].replace(0, pd.NA)
    summary['Link_Clicks_to_Results_Ratio'] = (summary['Link_Clicks'] / summary['Results'].replace(0, pd.NA)) * 100
    return summary

def compute_percent_change(current, previous):
    print("📈 Calculating percent change vs previous month...")
    merged = pd.merge(current, previous, on=current.columns[0], suffixes=('', '_prev'), how='left')
    for col in ['Amount_Spent', 'Results', 'Cost_per_Results', 'Impressions', 'CPM', 'Link_Clicks', 'CPC', 'Link_Clicks_to_Results_Ratio']:
        if f"{col}_prev" in merged.columns:
            merged[f"%_change_{col}"] = ((merged[col] - merged[f"{col}_prev"]) / merged[f"{col}_prev"]).replace([pd.NA, float('inf'), -float('inf')], 0) * 100
    return merged

def compute_benchmark_comparison(current, benchmark):
    print("📏 Calculating benchmark comparison...")
    comp = current.copy()
    for col in ['Cost_per_Results', 'CPM', 'CPC', 'Link_Clicks_to_Results_Ratio']:
        if col in benchmark and benchmark[col] != 0:
            comp[f"%_vs_benchmark_{col}"] = ((comp[col] - benchmark[col]) / benchmark[col]) * 100
    return comp

def generate_monthly_report(engine, output_dir, year, month):
    os.makedirs(output_dir, exist_ok=True)

    df = fetch_monthly_data(engine, year, month)
    if df.empty:
        print("🚫 No data found for the selected month.")
        return

    # Add fallback columns if missing
    for col in ['link_clicks']:
        if col not in df.columns:
            df[col] = 0

    # Level 1: Campaign
    campaign_level = summarize_level(df, ['campaign_name'], 'campaign')

    # Level 2: Ad-set
    adset_level = summarize_level(df, ['campaign_name', 'ad_set_name'], 'ad-set')

    # Level 3: Ad
    ad_level = summarize_level(df, ['campaign_name', 'ad_name', 'ad_set_name'], 'ad')

    # Fetch previous month data
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_df = fetch_monthly_data(engine, prev_year, prev_month)

    if not prev_df.empty:
        prev_campaign = summarize_level(prev_df, ['campaign_name'], 'campaign-prev')
        campaign_level = compute_percent_change(campaign_level, prev_campaign)

    # Benchmarks (average for current year)
    full_year_df = fetch_monthly_data(engine, year, month=None)
    if not full_year_df.empty:
        benchmark = summarize_level(full_year_df, ['campaign_name'], 'campaign-benchmark')
        avg_benchmark = benchmark[['Cost_per_Results', 'CPM', 'CPC', 'Link_Clicks_to_Results_Ratio']].mean()
        campaign_level = compute_benchmark_comparison(campaign_level, avg_benchmark)

    # Save outputs
    month_name = datetime(year, month, 1).strftime('%B').upper()
    print(f"💾 Saving report files for {month_name}...")
    campaign_level.to_csv(os.path.join(output_dir, f"{month_name}_campaign_level.csv"), index=False)
    adset_level.to_csv(os.path.join(output_dir, f"{month_name}_adset_level.csv"), index=False)
    ad_level.to_csv(os.path.join(output_dir, f"{month_name}_ad_level.csv"), index=False)
    print("✅ Monthly report generation complete!")


def generate_timed_reports_old(engine: Engine, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.today()

    # Monthly: Generate report for previous month
    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - timedelta(days=1)
    last_month = last_month_end.month
    last_month_year = last_month_end.year

    monthly_query = f"""
    SELECT * FROM campaign_data
    WHERE EXTRACT(MONTH FROM starts) = {last_month}
    AND EXTRACT(YEAR FROM starts) = {last_month_year};
    """
    df_month = pd.read_sql(monthly_query, engine)
    month_file = f"monthly_report_{last_month_year}_{str(last_month).zfill(2)}.csv"
    df_month.to_csv(os.path.join(output_dir, month_file), index=False)

    # Weekly: Generate report for previous week
    last_sunday = today - timedelta(days=today.weekday() + 1)
    week_start = last_sunday - timedelta(days=6)

    weekly_query = f"""
    SELECT * FROM campaign_data
    WHERE starts::date BETWEEN DATE '{week_start.date()}' AND DATE '{last_sunday.date()}';
    """
    df_week = pd.read_sql(weekly_query, engine)
    week_file = f"weekly_report_{week_start.date()}_to_{last_sunday.date()}.csv"
    df_week.to_csv(os.path.join(output_dir, week_file), index=False)

    print(f"📅 Monthly report saved as: {month_file}")
    print(f"🗓️ Weekly report saved as: {week_file}")
