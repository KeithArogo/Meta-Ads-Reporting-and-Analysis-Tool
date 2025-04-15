import pandas as pd

def split_and_clean_columns(df):
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

    return df, ad_split