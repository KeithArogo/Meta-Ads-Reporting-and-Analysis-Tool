# src/utils.py
import boto3
import os

def download_files_from_s3(bucket_name: str, base_key: str, files: list, local_dir: str = "data/raw"):
    """
    Download multiple files from an S3 bucket to a local directory.

    Args:
        bucket_name (str): Name of the S3 bucket.
        base_key (str): Path prefix inside the S3 bucket.
        files (list): List of filenames to download.
        local_dir (str): Local directory to save the files (default: /tmp).
    """
    s3_client = boto3.client('s3')

    os.makedirs(local_dir, exist_ok=True)

    for file in files:
        s3_key = f"{base_key}{file}"
        local_path = os.path.join(local_dir, file)

        try:
            s3_client.download_file(bucket_name, s3_key, local_path)
            print(f"[INFO] Downloaded {file} to {local_path}")
        except Exception as e:
            print(f"[ERROR] Failed to download {file}: {e}")


import pandas as pd

def process_campaign_data(df):
    """
    Processes the campaign, ad set, and ad data within the provided DataFrame.
    This function splits columns, cleans data, and assigns new feature columns based on specific rules.

    Args:
    df (pd.DataFrame): The input DataFrame containing campaign and ad data.

    Returns:
    pd.DataFrame: The modified DataFrame with new columns and cleaned data.
    """
    
    # --- Split Campaign Name ---
    df[['Campaign_Location', 'Campaign_Date', 'Campaign_Funnel', 
        'Campaign_Goal', 'Campaign_Tactic', 'Campaign_Description']] = (
        df['Campaign name'].str.split('|', expand=True)
    )

    # --- Split Ad Set Name ---
    df[['AdSet_Location', 'AdSet_Gender', 'AdSet_Age', 'AdSet_AudienceSegment', 
        'AdSet_AudienceDetail', 'AdSet_Platform', 'AdSet_Placement']] = (
        df['Ad set name'].str.split('|', expand=True)
    )

    # --- Clean & Split Ad Name ---
    ad_split = df['Ad name'].str.split('|')

    # Drop rows with only 1 or 2 parts (unusable)
    df = df[~ad_split.apply(lambda x: len(x) in [1, 2])].copy()
    ad_split = df['Ad name'].str.split('|')  # Re-split after filtering

    # Fix rows with 5 parts by merging the first two
    ad_split_fixed = ad_split.apply(lambda x: [x[0] + ' ' + x[1]] + x[2:] if len(x) == 5 else x)

    # Keep only rows with exactly 4 parts
    df = df[ad_split_fixed.apply(len) == 4].copy()
    ad_split_final = ad_split_fixed[ad_split_fixed.apply(len) == 4]

    # Assign new features
    df[['Ad_Service', 'Ad_Format', 'Ad_AssetType', 'Ad_Description']] = pd.DataFrame(ad_split_final.tolist(), index=ad_split_final.index)

    # Optional: clean up whitespace
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    return df

# Strip whitespace + lowercase for ALL string columns
def clean_string(value):
    return str(value).strip().lower().replace(" ", "")  # Remove ALL spaces (adjust as needed)

def count_unique_string_values(df):
    """
    Analyzes string columns in a DataFrame and returns the count of unique values for each.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        A dictionary with column names as keys and unique counts as values
    """
    # Select only string columns
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    
    unique_counts = {}
    
    for col in string_cols:
        # Get unique values and count
        unique_values = df[col].nunique()
        unique_counts[col] = unique_values
        
        # Print value frequencies (optional)
        print(f"\nColumn: {col}")
        print(f"Unique values: {unique_values}")
        print("Value frequencies:")
        print(df[col].value_counts(dropna=False))
    
    return unique_counts


def analyze_non_string_features(df):
    # Get non-string features (numeric, boolean, datetime, etc.)
    non_string_cols = df.select_dtypes(exclude=['object', 'string']).columns
    
    print(f"Found {len(non_string_cols)} non-string features:")
    print("="*50)
    
    for col in non_string_cols:
        dtype = df[col].dtype
        unique_count = df[col].nunique()
        sample_values = df[col].dropna().unique()[:5]
        
        print(f"Column: {col}")
        print(f"Type: {dtype}")
        print(f"Unique values: {unique_count}")
        print(f"Sample values: {sample_values}")
        print(f"Missing values: {df[col].isna().sum()} ({df[col].isna().mean():.1%})")
        
        # Basic stats for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            print(f"Min: {df[col].min()}")
            print(f"Max: {df[col].max()}")
            print(f"Mean: {df[col].mean():.2f}")
            print(f"Median: {df[col].median():.2f}")
        
        print("-"*50)


from sklearn.preprocessing import LabelEncoder
import os

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

def decode_categorical_fast(encoded_df, mapping_dir):
    # Load mappings
    mappings = pd.read_csv(
        f'{mapping_dir}/encoding_mappings.csv',
        index_col=0
    ).to_dict(orient='index')
    
    decoded_df = encoded_df.copy()
    
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
