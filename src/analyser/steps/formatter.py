def format_analysis(series) -> str:
    """
    Format analysis output for printing.

    Args:
        series (pd.Series): The analysis result (e.g., quotes by age, gender).

    Returns:
        str: The formatted string.
    """
    if series.dtype == 'float64':
        return series.sort_values().apply(lambda x: f"£{x:.2f}").to_string()
    else:
        return series.sort_values(ascending=False).to_string()
