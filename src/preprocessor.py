import os
import pandas as pd
from src.utils import download_files_from_s3, process_campaign_data, clean_string, encode_categorical_fast

def preprocess_campaign_data(bucket_name, base_key, files):
    """
    Full preprocessing pipeline for campaign data: download, process, clean, and encode.

    Args:
    - bucket_name (str): The S3 bucket name where the data is stored.
    - base_key (str): The base path/key within the S3 bucket.
    - files (list): List of file names to download from the S3 bucket.

    Returns:
    - encoded_df (pd.DataFrame): The processed and encoded DataFrame.
    """
    # Constants for file paths
    mapping_dir = "data/encoded_data"  # Relative path to the encoded data directory
    output_file = "data/encoded_data/encoded_df.csv"  # Output path for the encoded CSV file
    raw_data_dir = "data/raw"

    # Step 1: Download files from S3
    print("Downloading files from S3...")
    download_files_from_s3(bucket_name=bucket_name, base_key=base_key, files=files)

    # Debugging: Check current working directory and raw data folder contents
    print(f"Current working directory: {os.getcwd()}")
    print(f"Contents of {raw_data_dir}: {os.listdir(raw_data_dir)}")

    # Step 2: Check if the file exists
    raw_file_path = os.path.join(raw_data_dir, files[0])
    if not os.path.exists(raw_file_path):
        raise FileNotFoundError(f"File not found: {raw_file_path}. Please check if the file is downloaded properly.")

    # Load the data into a pandas DataFrame
    df = pd.read_csv(raw_file_path)

    # Step 3: Process the campaign data
    df = process_campaign_data(df)

    # Step 4: Drop the 'Cost per result' column
    df = df.drop(columns=['Cost per result'])

    # Step 5: Handle missing values
    df['Result Type'] = df['Result Type'].fillna('none').replace('', 'none')
    df['Results'] = df['Results'].fillna(0)

    # Step 6: Clean column names: lowercase + underscores
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(r'([a-z])([A-Z])', r'\1_\2', regex=True)
        .str.replace(r'[ \-]+', '_', regex=True)
    )

    # Step 7: Clean string columns
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].applymap(clean_string)

    # Step 8: Drop unnecessary columns
    df = df.drop(columns=['campaign_name', 'ad_set_name', 'ad_name'])

    # Step 9: Encode categorical features
    encoded_df, mappings = encode_categorical_fast(df, mapping_dir)

    # Step 10: Save the encoded DataFrame to CSV
    encoded_df.to_csv(output_file)

    return encoded_df
