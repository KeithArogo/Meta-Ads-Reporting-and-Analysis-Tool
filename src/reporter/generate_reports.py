# src/reporter/generate_reports.py

# src/reporter/generate_reports.py

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.engine import Engine
import os

def generate_monthly_report(engine: Engine, output_path, year, month):
    # Define date range for current and previous month
    start_date = datetime(year, month, 1)
    end_date = (start_date + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
    prev_start = start_date - pd.DateOffset(months=1)
    prev_end = start_date - pd.DateOffset(days=1)

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    def fetch_data(start, end):
        query = text(f"""
            SELECT * FROM campaign_data
            WHERE starts >= :start AND starts <= :end
        """)
        return pd.read_sql(query, engine, params={"start": start, "end": end})

    def preprocess(df):
        df['amount_spent_gbp'] = pd.to_numeric(df['amount_spent_gbp'], errors='coerce')
        df['results'] = pd.to_numeric(df['results'], errors='coerce')
        df['impressions'] = pd.to_numeric(df['impressions'], errors='coerce')
        df['link_clicks'] = pd.to_numeric(df['link_clicks'], errors='coerce')

        df['cost_per_result'] = df['amount_spent_gbp'] / df['results']
        df['cpm'] = df['amount_spent_gbp'] / (df['impressions'] / 1000)
        df['cpc'] = df['amount_spent_gbp'] / df['link_clicks']
        df['link_to_result_ratio'] = df['link_clicks'] / df['results']
        return df

    def group_and_aggregate(df, group_cols):
        grouped = df.groupby(group_cols).agg({
            'amount_spent_gbp': 'sum',
            'results': 'sum',
            'impressions': 'sum',
            'link_clicks': 'sum'
        }).reset_index()
        return preprocess(grouped)

    def compare(df, previous_df):
        joined = pd.merge(df, previous_df, on=df.columns[0], suffixes=('', '_prev'))
        for col in ['amount_spent_gbp', 'results', 'cost_per_result', 'impressions', 'cpm', 'link_clicks', 'cpc', 'link_to_result_ratio']:
            current = joined[col]
            prev = joined[f"{col}_prev"]
            joined[f"%_vs_prev_{col}"] = ((current - prev) / prev * 100).round(1)
        return joined

    def benchmark(df, all_2024_df):
        benchmark_df = group_and_aggregate(all_2024_df, [df.columns[0]])
        joined = pd.merge(df, benchmark_df, on=df.columns[0], suffixes=('', '_bm'))
        for col in ['cost_per_result', 'cpm', 'cpc', 'link_to_result_ratio']:
            current = joined[col]
            bm = joined[f"{col}_bm"]
            joined[f"%_vs_benchmark_{col}"] = ((current - bm) / bm * 100).round(1)
        return joined

    # Load datasets
    this_month_df = fetch_data(start_date, end_date)
    prev_month_df = fetch_data(prev_start, prev_end)
    all_2024_df = fetch_data(datetime(2024, 1, 1), end_date)

    # Campaign-Level
    this_month_campaign = group_and_aggregate(this_month_df, ['campaign_name'])
    prev_campaign = group_and_aggregate(prev_month_df, ['campaign_name'])
    full_campaign = compare(this_month_campaign, prev_campaign)
    full_campaign = benchmark(full_campaign, all_2024_df)
    full_campaign.to_csv(f"{output_path}/campaign_level_{year}_{month:02}.csv", index=False)

    # Ad-Set-Level
    this_month_adset = group_and_aggregate(this_month_df, ['ad_set_name'])
    prev_adset = group_and_aggregate(prev_month_df, ['ad_set_name'])
    full_adset = compare(this_month_adset, prev_adset)
    full_adset = benchmark(full_adset, all_2024_df)
    full_adset.to_csv(f"{output_path}/adset_level_{year}_{month:02}.csv", index=False)

    # Ad-Level
    this_month_ad = group_and_aggregate(this_month_df, ['ad_name'])
    prev_ad = group_and_aggregate(prev_month_df, ['ad_name'])
    full_ad = compare(this_month_ad, prev_ad)
    full_ad = benchmark(full_ad, all_2024_df)
    full_ad.to_csv(f"{output_path}/ad_level_{year}_{month:02}.csv", index=False)

    print(f"✅ Reports generated for {start_date.strftime('%B %Y')} and saved to {output_path}")


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
