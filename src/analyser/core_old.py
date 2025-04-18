# src/analyser/core.py

import os
from datetime import datetime
import pandas as pd
from src.analyser.steps.decode import decode_categorical_fast
from src.analyser.steps.cpq_analysis import cost_per_quote_by_asset, cost_per_quote_by_service
from src.analyser.steps.demographic_analysis import age_analysis, gender_analysis
from src.analyser.steps.service_analysis import service_analysis
from src.analyser.steps.efficiency import efficiency_metrics
from src.analyser.steps.visuals import plot_conversion_by_campaign
from src.analyser.steps.formatter import format_analysis
from src.analyser.steps.writer import save_report


def analyze_campaign_data(encoded_df: pd.DataFrame, mapping_dir='data/encoded_data', output_report_path='reports/ad_analysis_report.txt', output_img_dir='reports/images/') -> None:
    """
    Master analysis function, calling all other analysis steps and saving the report and images.
    
    Args:
        encoded_df (pd.DataFrame): The preprocessed and encoded dataframe.
        mapping_dir (str): Directory for encoding mappings.
        output_report_path (str): Path to save the generated report.
        output_img_dir (str): Directory to save the generated images.
    """
    
    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    os.makedirs(output_img_dir, exist_ok=True)

    # Decode the dataframe
    decoded_df = decode_categorical_fast(encoded_df, mapping_dir)

    # Generate cost per quote analysis
    cpq_by_asset = cost_per_quote_by_asset(decoded_df)
    cpq_by_service = cost_per_quote_by_service(decoded_df)

    # Perform demographic analysis (age & gender)
    age_quotes = age_analysis(decoded_df)
    gender_quotes, gender_cost = gender_analysis(decoded_df)

    # Service analysis (performance by service)
    service_cost = service_analysis(decoded_df)

    # Efficiency metrics (total spent, quotes, etc.)
    total_spent, total_quotes, current_cpq, predicted_quotes = efficiency_metrics(decoded_df)

    # Generate visualizations
    #plot_path = plot_conversion_by_campaign(decoded_df, output_img_dir)

    # Format and save the report
    report = [
        "CAMPAIGN DATA ANALYSIS REPORT",
        "=" * 40,
        "\n[1] Cost Per Quote by Asset Type:\n" + cpq_by_asset,
        "\n[2] Cost Per Quote by Service:\n" + cpq_by_service,
        "\n[3] Quotes by Age Group:\n" + format_analysis(age_quotes),
        "\n[4] Gender Analysis:\n" + format_analysis(gender_quotes),
        "\n[5] Cost Per Quote by Gender:\n" + format_analysis(gender_cost),
        "\n[6] Service Performance Analysis:\n" + format_analysis(service_cost),
        "\n[7] Efficiency Metrics:\n" + f"Total Spend: {total_spent} | Total Quotes: {total_quotes} | Predicted Monthly Quotes: {predicted_quotes}",
        #"\n[8] Visualizations:\n" + f"Saved plot to: {plot_path}"
    ]
    save_report(report, output_report_path)

    print(f"Analysis report written to: {output_report_path}")
