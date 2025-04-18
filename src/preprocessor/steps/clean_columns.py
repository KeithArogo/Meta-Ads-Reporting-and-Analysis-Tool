# steps/clean_columns.py

"""
Functions to clean column values — nulls, casing, whitespace, etc.
"""

import pandas as pd

def clean_strings(value):
    """
    Strips whitespace and lowercases all string/object columns.
    """
    return str(value).strip().lower().replace(" ", "")  # Remove ALL spaces (adjust as needed)

def fill_missing(df: pd.DataFrame, fill_value: str = "unknown") -> pd.DataFrame:
    """
    Fills missing values in object columns with a default value.
    """
    obj_cols = df.select_dtypes(include="object").columns
    df[obj_cols] = df[obj_cols].fillna(fill_value)
    return df
