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

def fetch_weekly_data(engine, start_date: datetime, end_date: datetime):
    query = f"""
    SELECT * FROM campaign_data
    WHERE starts >= '{start_date.strftime('%Y-%m-%d')}'
    AND starts < '{end_date.strftime('%Y-%m-%d')}';
    """
    print(f"📦 Fetching weekly data: {start_date.date()} ➡️ {end_date.date()}...")
    return pd.read_sql(query, engine)

def generate_weekly_report(engine, output_dir, week_start_date: datetime):
    os.makedirs(output_dir, exist_ok=True)
    
    week_end_date = week_start_date + timedelta(days=7)
    df = fetch_weekly_data(engine, week_start_date, week_end_date)

    if df.empty:
        print("🚫 No data found for the selected week.")
        return

    for col in ['link_clicks']:
        if col not in df.columns:
            df[col] = 0

    campaign_level = summarize_level(df, ['campaign_name'], 'campaign')
    adset_level = summarize_level(df, ['campaign_name', 'ad_set_name'], 'ad-set')
    ad_level = summarize_level(df, ['campaign_name', 'ad_name', 'ad_set_name'], 'ad')

    week_range_str = f"{week_start_date.strftime('%Y-%m-%d')}_to_{week_end_date.strftime('%Y-%m-%d')}"
    print(f"💾 Saving report files for {week_range_str}...")
    campaign_level.to_csv(os.path.join(output_dir, f"{week_range_str}_campaign_level.csv"), index=False)
    adset_level.to_csv(os.path.join(output_dir, f"{week_range_str}_adset_level.csv"), index=False)
    ad_level.to_csv(os.path.join(output_dir, f"{week_range_str}_ad_level.csv"), index=False)
    print("✅ Weekly report generation complete!")



