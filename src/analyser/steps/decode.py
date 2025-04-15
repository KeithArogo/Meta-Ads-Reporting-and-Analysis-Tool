import pandas as pd
import os
import numpy as np

def decode_categorical_fast(encoded_df: pd.DataFrame, mapping_dir: str) -> pd.DataFrame:
    """
    Decode the categorical columns based on mappings stored in `mapping_dir`.

    Args:
        encoded_df (pd.DataFrame): The encoded dataframe.
        mapping_dir (str): Directory where mapping files are stored.

    Returns:
        pd.DataFrame: The decoded dataframe.
    """
    # Load the mappings from CSV (not pickle)
    mappings = pd.read_csv(
        f'{mapping_dir}/encoding_mappings.csv',
        index_col=0
    ).to_dict(orient='index')

    decoded_df = encoded_df.copy()

    # Iterate through the columns in mappings and decode
    for col, mapping in mappings.items():
        if col not in decoded_df.columns:
            continue
        
        if mapping['encoder_type'] == 'label':
            # Reverse label encoding
            reverse_map = {v: k for k, v in eval(mapping['mapping']).items()}
            decoded_df[col] = decoded_df[col].map(reverse_map)
        
        elif mapping['encoder_type'] == 'frequency':
            # Reverse frequency encoding
            reverse_map = {v: k for k, v in eval(mapping['mapping']).items()}
            decoded_df[col] = decoded_df[col].map(reverse_map)

    return decoded_df
