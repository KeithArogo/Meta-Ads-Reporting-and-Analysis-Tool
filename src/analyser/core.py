# src.analyser.core.py

from datetime import datetime
from pathlib import Path
import os
from tabulate import tabulate

from src.analyser.sql_metrics import (
    cost_per_quote_by_asset_type,
    cost_per_quote_by_service,
    quotes_by_age_group,
    quotes_by_gender,
    cost_per_quote_by_gender,
    impression_analytics,
    aggregate_performance_by_time
)

def analyze_campaign_data_from_db(engine, output_path):
    report = {}
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = Path(output_path) / f"campaign_report_{timestamp}.txt"
    
    # Run all metrics (same as before)
    report["Cost per Quote by Asset Type"] = cost_per_quote_by_asset_type(engine)
    report["Cost per Quote by Service"] = cost_per_quote_by_service(engine)
    report["Quotes by Age Group"] = quotes_by_age_group(engine)
    report["Quotes by Gender"] = quotes_by_gender(engine)
    report["Cost per Quote by Gender"] = cost_per_quote_by_gender(engine)

    report["Impression Analysis by Gender"] = impression_analytics(engine, ['gender'])
    report["Impression Analysis by Age"] = impression_analytics(engine, ['age'])
    report["Impression Analysis by Campaign + Gender"] = impression_analytics(engine, ['campaign_name', 'gender'])
    report["Impression Analysis by Ad Set + Age"] = impression_analytics(engine, ['ad_set_name', 'age'])

    # ** New Section: Aggregate performance by temporal features (week, month, year) **
    temporal_metrics = aggregate_performance_by_time(engine)
    report["Performance by Week"] = temporal_metrics['week']
    report["Performance by Month"] = temporal_metrics['month']
    report["Performance by Year"] = temporal_metrics['year']

    # Format + save report
    lines = []
    for title, df in report.items():
        lines.append(f"\n{'='*60}\n{title}\n{'='*60}")
        lines.append(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

    final_text = "\n".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"📊 Report generated at: {output_file}")
    return report


def analyze_campaign_data_from_db_old(engine, output_path):
    report = {}
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = Path(output_path) / f"campaign_report_{timestamp}.txt"
    
    # Run all metrics
    report["Cost per Quote by Asset Type"] = cost_per_quote_by_asset_type(engine)
    report["Cost per Quote by Service"] = cost_per_quote_by_service(engine)
    report["Quotes by Age Group"] = quotes_by_age_group(engine)
    report["Quotes by Gender"] = quotes_by_gender(engine)
    report["Cost per Quote by Gender"] = cost_per_quote_by_gender(engine)

    report["Impression Analysis by Gender"] = impression_analytics(engine, ['gender'])
    report["Impression Analysis by Age"] = impression_analytics(engine, ['age'])
    report["Impression Analysis by Campaign + Gender"] = impression_analytics(engine, ['campaign_name', 'gender'])
    report["Impression Analysis by Ad Set + Age"] = impression_analytics(engine, ['ad_set_name', 'age'])

    # Format + save report
    lines = []
    for title, df in report.items():
        lines.append(f"\n{'='*60}\n{title}\n{'='*60}")
        lines.append(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

    final_text = "\n".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"📊 Report generated at: {output_file}")
    return report
