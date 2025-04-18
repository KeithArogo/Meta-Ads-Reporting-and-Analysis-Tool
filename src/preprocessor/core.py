# src/preprocessor/core.py

"""
Main preprocessing pipeline for campaign data.
"""

import pandas as pd
from .steps.split_and_clean_columns import split_and_clean_columns
from .steps.drop_and_fix_rows import drop_and_fix_rows
from .steps.encode_categorical import encode_categorical_fast
from .steps.clean_columns import clean_strings, fill_missing
from .steps.load_columns import split_campaign_components
#from .steps.encode import label_encode_column, one_hot_encode
import os

def preprocess_campaign_data(df: pd.DataFrame, mapping_dir: str) -> pd.DataFrame:
    """
    Full preprocessing pipeline for campaign data: process, clean, and encode.

    Args:
    - df (pd.DataFrame): Raw campaign data as a pandas DataFrame.

    Returns:
    - encoded_df (pd.DataFrame): The processed and encoded DataFrame.
    """
    # Constants for file paths
    mapping_dir = mapping_dir # Directory for encoding mappings
    output_file = f"{mapping_dir}/encoded_df.csv"  # Output path for the encoded CSV

    # Step 1: Clean column names
    df, ad_split = split_and_clean_columns(df)

    # Step 2: Drop and fix rows
    df = drop_and_fix_rows(df, ad_split)

    # Replace 'ongoing' with a NULL-equivalent or placeholder date
    df['ends'] = df['ends'].replace('ongoing', pd.NaT)

    # Assuming your DataFrame is named `df`
    df.rename(columns={"amount_spent_(gbp)": "amount_spent_gbp"}, inplace=True)

    # Encode categorical features - remove this if not needed
    #os.makedirs(mapping_dir, exist_ok=True)
    #encoded_df, mappings = encode_categorical_fast(df, mapping_dir)

    # Step 8: Save the encoded DataFrame - remove this if not needed
    #encoded_df.to_csv(output_file, index=False)

    return df # encoded_df - enable this for ML tasks