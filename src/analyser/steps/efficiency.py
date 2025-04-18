import pandas as pd

def efficiency_metrics(decoded_df: pd.DataFrame) -> tuple:
    """
    Calculate efficiency metrics like total spend, quotes, current cost per quote, and predicted quotes.

    Args:
        decoded_df (pd.DataFrame): The decoded dataframe.

    Returns:
        tuple: total_spent, total_quotes, current_cpq, predicted_quotes
    """
    total_spent = decoded_df['amount_spent_(gbp)'].sum()
    total_quotes = decoded_df['results'].sum()
    current_cpq = total_spent / total_quotes
    predicted_quotes = total_quotes + (30 * current_cpq)  # Assume daily performance continues

    return total_spent, total_quotes, current_cpq, predicted_quotes
