import pandas as pd

def cost_per_quote_by_asset(decoded_df: pd.DataFrame) -> str:
    """
    Calculate cost per quote by asset type.

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        str: The formatted string of the cost per quote by asset type.
    """
    cpq = (decoded_df.groupby('ad_assettype')['amount_spent_(gbp)'].sum() / 
           decoded_df.groupby('ad_assettype')['results'].sum())
    return cpq.to_string()

def cost_per_quote_by_service(decoded_df: pd.DataFrame) -> str:
    """
    Calculate cost per quote by service.

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        str: The formatted string of the cost per quote by service.
    """
    cpq = (decoded_df.groupby('ad_service')['amount_spent_(gbp)'].sum() / 
           decoded_df.groupby('ad_service')['results'].sum())
    return cpq.to_string()
