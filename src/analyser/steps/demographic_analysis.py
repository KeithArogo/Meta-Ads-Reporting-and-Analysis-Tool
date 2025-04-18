import pandas as pd

def age_analysis(decoded_df: pd.DataFrame) -> pd.Series:
    """
    Perform quotes analysis by age group.

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        pd.Series: Age group quotes.
    """
    return decoded_df.groupby('age')['results'].sum().sort_values(ascending=False)

def gender_analysis(decoded_df: pd.DataFrame) -> tuple:
    """
    Perform quotes and cost per quote analysis by gender.

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        tuple: Gender quotes and cost per quote.
    """
    gender_quotes = decoded_df.groupby('gender')['results'].sum()
    gender_cost = (decoded_df.groupby('gender')['amount_spent_(gbp)'].sum() / 
                   decoded_df.groupby('gender')['results'].sum())
    return gender_quotes, gender_cost
