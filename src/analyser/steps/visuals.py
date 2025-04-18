import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import pandas as pd

def plot_conversion_by_campaign(df: pd.DataFrame, output_dir: str) -> str:
    """
    Plot conversions by campaign.

    Args:
        df (pd.DataFrame): The dataframe.
        output_dir (str): Directory to save the plot.

    Returns:
        str: Path to the saved plot.
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='campaign_id', y='conversions', ci=None)
    plt.xticks(rotation=45)
    plt.title('Conversions by Campaign')
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(output_dir, f'conversions_by_campaign_{timestamp}.png')
    plt.savefig(filepath)
    plt.close()
    return filepath
