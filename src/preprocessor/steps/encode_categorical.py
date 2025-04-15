# src/preprocessor/steps/encode.py

"""
Encoding functions for categorical variables.
"""
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def encode_categorical_fast(df, mapping_dir):
    """
    Encodes categorical columns in place and returns the modified DataFrame with mappings.
    Non-string features remain unchanged in the same DataFrame.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame
    mapping_dir (str): Directory to save encoding mappings
    
    Returns:
    pd.DataFrame: DataFrame with encoded categoricals and original non-string features
    dict: Encoding mappings for each column
    """
    # Create directory if it doesn't exist
    os.makedirs(mapping_dir, exist_ok=True)
    
    # Identify string columns (categoricals)
    cat_cols = df.select_dtypes(include=['object', 'string']).columns
    mappings = {}
    
    for col in cat_cols:
        unique_values = df[col].nunique()
        
        if unique_values == 1:
            # Drop columns with only 1 unique value
            df.drop(col, axis=1, inplace=True)
            mappings[col] = {'encoder_type': 'drop'}
            continue
            
        if unique_values == 2:
            # Binary columns - simple 0/1 encoding
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            mappings[col] = {
                'encoder_type': 'label',
                'mapping': dict(zip(le.classes_, le.transform(le.classes_)))
            }
        elif unique_values <= 10:
            # Low cardinality - label encoding
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            mappings[col] = {
                'encoder_type': 'label',
                'mapping': dict(zip(le.classes_, le.transform(le.classes_)))
            }
        else:
            # High cardinality - frequency encoding
            freq_map = df[col].value_counts(normalize=True).to_dict()
            df[col] = df[col].map(freq_map)
            mappings[col] = {
                'encoder_type': 'frequency',
                'mapping': freq_map
            }
    
    # Save mappings
    mappings_df = pd.DataFrame.from_dict(mappings, orient='index')
    mappings_df.to_csv(f'{mapping_dir}/encoding_mappings.csv')
    
    # Return the modified DataFrame (now with encoded categoricals)
    # and original non-string features untouched
    return df, mappings