# src/reporter/generate_reports.py

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.engine import Engine
import os
import calendar
from pathlib import Path  # Optional but recommended

def fetch_monthly_data(engine, year, month=None):
    if month is not None:
        query = f"""
        SELECT * FROM monthly_campaign_data
        WHERE EXTRACT(YEAR FROM reporting_starts) = {year}
          AND EXTRACT(MONTH FROM reporting_starts) = {month}
          AND results > 0;
        """
        print(f"📦 Fetching data for {year}-{month:02d}...")
    else:
        query = f"""
        SELECT * FROM monthly_campaign_data
        WHERE EXTRACT(YEAR FROM reporting_starts) = {year}
          AND results > 0;
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
    print(f"💾 Saving unified report file for {month_name}...")

    # Create a new Excel writer object
    with pd.ExcelWriter(os.path.join(output_dir, f"{month_name}_monthly_report.xlsx"), engine='xlsxwriter') as writer:
        
        # Write each DataFrame to a different section within the same sheet
        campaign_level['level'] = 'Campaign'
        adset_level['level'] = 'Ad Set'
        ad_level['level'] = 'Ad'

        # Combine DataFrames with a separating label row for each
        campaign_level.to_excel(writer, sheet_name='Report', startrow=0, index=False)
        adset_level.to_excel(writer, sheet_name='Report', startrow=len(campaign_level) + 2, index=False)
        ad_level.to_excel(writer, sheet_name='Report', startrow=len(campaign_level) + len(adset_level) + 4, index=False)
        
        # Get access to the workbook and worksheet to adjust formatting
        workbook  = writer.book
        worksheet = writer.sheets['Report']
        
        # Set title formatting for each table
        worksheet.write('A1', f'{month_name} Campaign Level', workbook.add_format({'bold': True, 'underline': True}))
        worksheet.write(f'A{len(campaign_level) + 2}', f'{month_name} Ad Set Level', workbook.add_format({'bold': True, 'underline': True}))
        worksheet.write(f'A{len(campaign_level) + len(adset_level) + 4}', f'{month_name} Ad Level', workbook.add_format({'bold': True, 'underline': True}))

        print("✅ Monthly report generation complete!")

def fetch_weekly_data(engine, start_date: datetime, end_date: datetime):
    query = f"""
    SELECT * FROM weekly_campaign_data
    WHERE reporting_starts >= '{start_date.strftime('%Y-%m-%d')}'
    AND reporting_ends <= '{end_date.strftime('%Y-%m-%d')}'
    AND results > 0;
    """
    return pd.read_sql(query, engine)

def generate_weekly_report_old(engine, output_dir, week_start_date: datetime):
    try:
        # Create output directory (using pathlib for better path handling)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        week_end_date = week_start_date + timedelta(days=6)
        week_range_str = f"{week_start_date.strftime('%Y-%m-%d')}_to_{week_end_date.strftime('%Y-%m-%d')}"
        
        print(f"📊 Generating weekly report for {week_range_str}...")
        
        # Fetch data
        df = fetch_weekly_data(engine, week_start_date, week_end_date)

        if df.empty:
            print("🚫 No data found for the selected week.")
            return

        # Ensure required columns exist
        for col in ['link_clicks']:
            if col not in df.columns:
                df[col] = 0
                print(f"⚠️ Column '{col}' not found - initialized with zeros")

        # Generate summaries
        campaign_level = summarize_level(df, ['campaign_name'], 'campaign')
        adset_level = summarize_level(df, ['campaign_name', 'ad_set_name'], 'ad-set')
        ad_level = summarize_level(df, ['campaign_name', 'ad_name', 'ad_set_name'], 'ad')

        # Add identifier columns
        campaign_level.insert(0, 'level', 'Campaign')
        adset_level.insert(0, 'level', 'Ad Set')
        ad_level.insert(0, 'level', 'Ad')

        # Create separator rows with better formatting
        def create_separator(title):
            return pd.DataFrame({'level': [f"===== {title} ====="], **{col: '' for col in campaign_level.columns[1:]}})

        # Combine all data more efficiently
        combined_data = [
            create_separator('CAMPAIGN LEVEL PERFORMANCE'),
            campaign_level,
            create_separator('AD SET LEVEL PERFORMANCE'),
            adset_level,
            create_separator('AD LEVEL PERFORMANCE'),
            ad_level
        ]

        final_combined_df = pd.concat(combined_data, ignore_index=True)

        # Save the report
        output_file = output_path / f"{week_range_str}_weekly_report.csv"
        final_combined_df.to_csv(output_file, index=False)
        
        print(f"✅ Weekly report saved to: {output_file}")
        return output_file

    except Exception as e:
        print(f"❌ Error generating weekly report: {str(e)}")
        raise

def generate_weekly_report(engine, output_dir, week_start_date: datetime):
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        week_end_date = week_start_date + timedelta(days=6)
        week_range_str = f"{week_start_date.strftime('%Y-%m-%d')}_to_{week_end_date.strftime('%Y-%m-%d')}"
        print(f"📊 Generating weekly report for {week_range_str}...")

        # Fetch data
        df = fetch_weekly_data(engine, week_start_date, week_end_date)
        df = df[df['results'] > 0]  # Filter to keep only rows with results > 0

        if df.empty:
            print("🚫 No data found for the selected week.")
            return

        # Ensure required columns exist
        for col in ['link_clicks']:
            if col not in df.columns:
                df[col] = 0
                print(f"⚠️ Column '{col}' not found - initialized with zeros")

        # Summaries
        campaign_level = summarize_level(df, ['campaign_name'], 'campaign')
        adset_level = summarize_level(df, ['campaign_name', 'ad_set_name'], 'ad-set')
        ad_level = summarize_level(df, ['campaign_name', 'ad_name', 'ad_set_name'], 'ad')

        # Set level identifiers
        campaign_level['level'] = 'Campaign'
        adset_level['level'] = 'Ad Set'
        ad_level['level'] = 'Ad'

        print(f"💾 Saving unified report file for {week_range_str}...")

        output_file = output_path / f"{week_range_str}_weekly_report.xlsx"
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Write to Excel
            campaign_level.to_excel(writer, sheet_name='Report', startrow=0, index=False)
            adset_level.to_excel(writer, sheet_name='Report', startrow=len(campaign_level) + 2, index=False)
            ad_level.to_excel(writer, sheet_name='Report', startrow=len(campaign_level) + len(adset_level) + 4, index=False)

            # Title formatting
            workbook  = writer.book
            worksheet = writer.sheets['Report']

            worksheet.write('A1', f'{week_range_str} Campaign Level', workbook.add_format({'bold': True, 'underline': True}))
            worksheet.write(f'A{len(campaign_level) + 2}', f'{week_range_str} Ad Set Level', workbook.add_format({'bold': True, 'underline': True}))
            worksheet.write(f'A{len(campaign_level) + len(adset_level) + 4}', f'{week_range_str} Ad Level', workbook.add_format({'bold': True, 'underline': True}))

        print(f"✅ Weekly report saved to: {output_file}")
        return output_file

    except Exception as e:
        print(f"❌ Error generating weekly report: {str(e)}")
        raise

def get_existing_report_ranges(engine, table_name):
    query = f"""
    SELECT DISTINCT reporting_starts, reporting_ends FROM {table_name}
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)).fetchall()
    return {(row[0], row[1]) for row in result}

def is_new_report(df, existing_ranges):
    if df.empty:
        return False
    start = pd.to_datetime(df['reporting_starts'].iloc[0])
    end = pd.to_datetime(df['reporting_ends'].iloc[0])
    return (start, end) not in existing_ranges