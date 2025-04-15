# main.py

from src.preprocessor.core import preprocess_campaign_data
from src.analyser.core import analyze_campaign_data

import os
import pandas as pd

def main():
    input_path = "/opt/ml/processing/input" #"local_run/input" - for testing on local machines 
    output_path =  "/opt/ml/processing/output" #"local_run/output" - for testing on local machines
    
    #mapping_dir = "local_run"
    img_output_dir = os.path.join(output_path, 'figures')

    print(f"🚀 Starting analysis. Reading files from {input_path}")

    # Load the dataset
    input_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    if not input_files:
        raise FileNotFoundError("No CSV files found in the input path.")

    file_path = os.path.join(input_path, input_files[0])
    df = pd.read_csv(file_path)

    # Run preprocessing and analysis
    print("Preprocessing the data...")
    df = preprocess_campaign_data(df, output_path)

    # Run analysis, passing the output report path & figure directory
    print("Analyzing the campaign data...")
    output_report_path = os.path.join(output_path, 'analysis_report.txt')
    #analyze_campaign_data(df, output_report_path, img_output_dir)
    analyze_campaign_data(df, output_path, output_report_path, img_output_dir)

    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()
