# src/database/save.py

import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def save_to_postgres(df, is_weekly=False):
    # Get credentials from environment variables
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

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