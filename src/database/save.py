# src/database/save.py

import pandas as pd
from sqlalchemy import create_engine

def save_to_postgres(df):
    # Database connection details (👀 load securely in production)
    db_user = 'keith'
    db_password = 'ArrestedDevelopment'
    db_host = 'metaad-campaign-db.cl4qg28aywnx.eu-north-1.rds.amazonaws.com'
    db_port = '5432'
    db_name = 'metaads'

    try:
        print("🗃️ Connecting to PostgreSQL database...")
        engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
        
        print("📤 Uploading data to campaign_data table...")
        df.to_sql('campaign_data', engine, if_exists='append', index=False)
        print("✅ Data successfully uploaded to PostgreSQL.")
    
    except Exception as e:
        print("❌ Error while uploading to PostgreSQL:", e)
        raise
