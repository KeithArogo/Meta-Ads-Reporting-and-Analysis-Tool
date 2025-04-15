# steps/load_columns.py

"""
Functions to split campaign, adset, and ad names into structured components.
"""

import pandas as pd

def split_campaign_components(df: pd.DataFrame, column: str = "campaign_name") -> pd.DataFrame:
    """
    Splits campaign_name into components like objective, region, and date.
    Assumes components are separated by underscores or hyphens.
    """
    # Example format: 'conversion_us_apr' -> ['conversion', 'us', 'apr']
    components = df[column].str.split(r'[_\-]', expand=True)
    for i in range(components.shape[1]):
        df[f"{column}_part_{i+1}"] = components[i]
    return df
