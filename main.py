from src.preprocessor import preprocess_campaign_data
from src.analyser import analyze_campaign_data

import os
import pandas as pd

def main():
    input_path = "/opt/ml/processing/input"
    output_path = "/opt/ml/processing/output"

    print(f"🚀 Starting analysis. Reading files from {input_path}")

    # Load the dataset
    input_files = [f for f in os.listdir(input_path) if f.endswith('.csv')]
    if not input_files:
        raise FileNotFoundError("No CSV files found in the input path.")

    file_path = os.path.join(input_path, input_files[0])
    df = pd.read_csv(file_path)

    # Run preprocessing and analysis
    df = preprocess_campaign_data(df)
    analyze_campaign_data(df, output_path)

    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()
