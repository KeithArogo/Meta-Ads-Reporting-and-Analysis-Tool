import pandas as pd

def service_analysis(decoded_df: pd.DataFrame) -> pd.Series:
    """
    Perform service performance analysis (cost per quote by service).

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        pd.Series: Service cost per quote.
    """
    return (decoded_df.groupby('ad_service')['amount_spent_(gbp)'].sum() / 
            decoded_df.groupby('ad_service')['results'].sum())
