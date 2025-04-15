import pandas as pd 
#from src.preprocessor.steps.split_and_clean_columns import split_and_clean_columns
from src.preprocessor.steps.clean_columns import clean_strings

def drop_and_fix_rows(df, ad_split):
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

    # clean up whitespace
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Drop the 'Cost per result' column if it exists
    if 'Cost per result' in df.columns:
        df = df.drop(columns=['Cost per result'])

    # Handle missing values
    df['Result Type'] = df['Result Type'].fillna('none').replace('', 'none')
    df['Results'] = df['Results'].fillna(0)

    # Step 4: Clean column names: lowercase + underscores
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(r'([a-z])([A-Z])', r'\1_\2', regex=True)
        .str.replace(r'[ \-]+', '_', regex=True)
    )

    # Step 5: Clean string columns
    string_cols = df.select_dtypes(include=['object']).columns
    df[string_cols] = df[string_cols].applymap(clean_strings)

    # Step 6: Drop unnecessary columns
    for col in ['campaign_name', 'ad_set_name', 'ad_name']:
        if col in df.columns:
            df = df.drop(columns=[col])
    
    return df