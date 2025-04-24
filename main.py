import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from src.reporter.generate_reports import generate_monthly_report, generate_weekly_report, get_existing_report_ranges, is_new_report
from src.preprocessor.core import preprocess_campaign_data
from src.analyser.core import analyze_campaign_data_from_db
from src.database.save import save_to_postgres

def run_monthly_pipeline(input_path, output_path, engine):
    print(f"\n📅 Running monthly pipeline from {input_path}")
    input_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    if not input_files:
        print("⚠️ No monthly files found.")
        return

    dfs = []
    for file in input_files:
        df = pd.read_csv(os.path.join(input_path, file))
        dfs.append(df)
        print(f"   ✅ Loaded {file} with {len(df)} rows")

    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"🧼 Preprocessing monthly data...")
    df_processed = preprocess_campaign_data(combined_df, output_path)

    print("💾 Checking for duplicates in monthly data...")
    existing = get_existing_report_ranges(engine, "monthly_campaign_data")
    if is_new_report(df_processed, existing):
        save_to_postgres(df_processed)
        print("✅ New monthly data saved to DB.")
    else:
        print("⏭️ Monthly data already exists. Skipping DB insert.")

    now = datetime.now()
    print("📝 Generating monthly report...")
    generate_monthly_report(engine, "reports/monthly", now.year, now.month - 1)

def run_weekly_pipeline(input_path, output_path, engine):
    print(f"\n📆 Running weekly pipeline from {input_path}")
    input_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    if not input_files:
        print("⚠️ No weekly files found.")
        return

    dfs = []
    for file in input_files:
        df = pd.read_csv(os.path.join(input_path, file))
        dfs.append(df)
        print(f"   ✅ Loaded {file} with {len(df)} rows")

    combined_df = pd.concat(dfs, ignore_index=True)

    print(f"🧼 Preprocessing weekly data...")
    df_processed = preprocess_campaign_data(combined_df, output_path)

    print("💾 Checking for duplicates in weekly data...")
    existing = get_existing_report_ranges(engine, "weekly_campaign_data")
    if is_new_report(df_processed, existing):
        save_to_postgres(df_processed, is_weekly=True)
        print("✅ New weekly data saved to DB.")
    else:
        print("⏭️ Weekly data already exists. Skipping DB insert.")

    print("📝 Generating weekly reports (last 4 Sundays)...")
    for i in range(4):
        sunday = datetime.today() - timedelta(days=datetime.today().weekday() + 1 + (7 * i))
        print(f"---------------------------------------{i}----------------------------------------")
        print(f"📅 Attempting report for Sunday: {sunday.strftime('%Y-%m-%d')}")

        try:
            generate_weekly_report(engine, "reports/weekly", sunday)
        except ValueError as e:
            print(f"⚠️ No data found for {sunday.strftime('%Y-%m-%d')}. Skipping...\n")

def main():
    base_data_path = "data"
    base_output_path = "analysis"

    engine = create_engine("postgresql+psycopg2://keith:ArrestedDevelopment@metaad-campaign-db.cl4qg28aywnx.eu-north-1.rds.amazonaws.com:5432/metaads")

    for folder in os.listdir(base_data_path):
        full_input_path = os.path.join(base_data_path, folder)
        full_output_path = os.path.join(base_output_path, folder)

        if not os.path.isdir(full_input_path):
            continue

        if "monthly" in folder:
            run_monthly_pipeline(full_input_path, full_output_path, engine)
        elif "weekly" in folder:
            run_weekly_pipeline(full_input_path, full_output_path, engine)
        else:
            print(f"⚠️ Skipping unknown folder: {folder}")

    print("✅ All pipelines completed.")

if __name__ == "__main__":
    main()
