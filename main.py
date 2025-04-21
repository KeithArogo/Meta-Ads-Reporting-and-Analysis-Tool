# main.py
from src.reporter.generate_reports import generate_monthly_report
from src.preprocessor.core import preprocess_campaign_data
from src.analyser.core import analyze_campaign_data_from_db
from src.database.save import save_to_postgres  # 🚀 NEW import
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from src.reporter.generate_reports import generate_weekly_report
import os
import pandas as pd

def main():
    input_path = "local_run/input" # "/opt/ml/processing/input" # "local_run/input"
    output_path = "local_run/output" # "/opt/ml/processing/output" # "local_run/output"
    #img_output_dir = os.path.join(output_path, 'figures')

    print(f"🚀 Starting analysis. Reading files from {input_path}")

    # Load the dataset
    input_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    if not input_files:
        raise FileNotFoundError("No CSV files found in the input path.")

    file_path = os.path.join(input_path, input_files[0])
    df = pd.read_csv(file_path)

    # Run preprocessing
    print("🧼 Preprocessing the data...")
    df = preprocess_campaign_data(df, output_path)

    # Save to PostgreSQL
    print("💾 Saving to database...")
    save_to_postgres(df)

    # Run analysis
    print("📊 Analyzing the campaign data...")
    
    # Connect to DB
    engine = create_engine("postgresql+psycopg2://keith:ArrestedDevelopment@metaad-campaign-db.cl4qg28aywnx.eu-north-1.rds.amazonaws.com:5432/metaads")

    # Run analysis from DB
    analyze_campaign_data_from_db(engine, output_path)

    #output_report_path = os.path.join(output_path, 'analysis_report.txt')
    #analyze_campaign_data(df, output_path, output_report_path, img_output_dir)

    print("✅ Analysis complete!")

    # Generate monthly and weekly reports
    print("📅 Generating monthly reports...")
    generate_monthly_report(engine, "reports/monthly", 2025, 3)

    # Generate weekly report for the last Sunday
    # Assuming the last Sunday is the last day of the previous week
    today = datetime.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)  # Sunday of the previous week
    print("📅 Generating weekly reports...")
    generate_weekly_report(engine, "reports/weekly", last_sunday)

if __name__ == "__main__":
    main()
