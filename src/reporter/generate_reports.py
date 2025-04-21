# src/reporter/generate_reports.py

import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.engine import Engine

def generate_timed_reports(engine: Engine, output_dir: str):
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
