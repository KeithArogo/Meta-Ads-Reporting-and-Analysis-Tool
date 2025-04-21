# src/preprocessor/core.py

"""
Main preprocessing pipeline for campaign data.
"""

import pandas as pd
from .steps.split_and_clean_columns import split_and_clean_columns
from .steps.drop_and_fix_rows import drop_and_fix_rows
#from .steps.encode_categorical import encode_categorical_fast
#from .steps.clean_columns import clean_strings, fill_missing
#from .steps.load_columns import split_campaign_components
import os

def preprocess_campaign_data(df: pd.DataFrame, mapping_dir: str) -> pd.DataFrame:
    """
    Full preprocessing pipeline for campaign data: process, clean, and encode.

    Args:
    - df (pd.DataFrame): Raw campaign data as a pandas DataFrame.

    Returns:
    - df (pd.DataFrame): The processed DataFrame, including temporal features.
    """
    # Constants for file paths
    mapping_dir = mapping_dir  # Directory for encoding mappings
    #output_file = f"{mapping_dir}/encoded_df.csv"  # Output path for the encoded CSV

    # Step 1: Clean column names
    df, ad_split = split_and_clean_columns(df)

    # Step 2: Drop and fix rows
    df = drop_and_fix_rows(df, ad_split)

    # Replace 'ongoing' with a NULL-equivalent or placeholder date
    df['ends'] = df['ends'].replace('ongoing', pd.NaT)

    # Convert 'starts' and 'ends' columns to datetime
    df['starts'] = pd.to_datetime(df['starts'], errors='coerce')
    df['ends'] = pd.to_datetime(df['ends'], errors='coerce')

    # Step 3: Add temporal features (week, month, year)
    df['campaign_week'] = df['starts'].dt.isocalendar().week
    df['campaign_month'] = df['starts'].dt.month
    df['campaign_year'] = df['starts'].dt.year

    # Optionally, you can add similar features for the 'ends' column if needed
    # df['ad_end_week'] = df['ends'].dt.isocalendar().week
    # df['ad_end_month'] = df['ends'].dt.month
    # df['ad_end_year'] = df['ends'].dt.year

    # Step 4: Rename columns
    df.rename(columns={"amount_spent_(gbp)": "amount_spent_gbp"}, inplace=True)
    df.rename(columns={"cpc_(cost_per_link_click)": "cost_per_link_click"}, inplace=True)
    df.rename(columns={"cpm_(cost_per_1,000_impressions)": "cost_per_thousand_impressions"}, inplace=True)
    df.rename(columns={"ctr_(all)": "click_through_rate"}, inplace=True)

    # Encode categorical features (if needed)
    # os.makedirs(mapping_dir, exist_ok=True)
    # encoded_df, mappings = encode_categorical_fast(df, mapping_dir)

    # Step 5: Save the encoded DataFrame - remove if not needed
    # encoded_df.to_csv(output_file, index=False)

    return df  # return the DataFrame with the new temporal features
