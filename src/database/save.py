# src/database/save.py

import pandas as pd
from sqlalchemy import create_engine

def save_to_postgres(df, is_weekly=False):
    # Database connection details (👀 load securely in production)
    db_user = 'keith'
    db_password = 'ArrestedDevelopment'
    db_host = 'metaad-campaign-db.cl4qg28aywnx.eu-north-1.rds.amazonaws.com'
    db_port = '5432'
    db_name = 'metaads'

    table_name = 'weekly_campaign_data' if is_weekly else 'monthly_campaign_data'

    try:
        print("🗃️ Connecting to PostgreSQL database...")
        engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        
        print(f"📤 Uploading data to `{table_name}` table...")
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"✅ Data successfully uploaded to `{table_name}`.")
    
    except Exception as e:
        print("❌ Error while uploading to PostgreSQL:", e)
        raise
