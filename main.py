from src.preprocessor import preprocess_campaign_data
from src.analyser import analyze_campaign_data

import os

def main():
    # These env vars will be injected via Lambda
    bucket_name = os.environ['S3_INPUT_BUCKET']
    key = os.environ['S3_INPUT_KEY']
    
    # Parse the file name(s) from the key
    file_name = key.split('/')[-1]
    base_key = '/'.join(key.split('/')[:-1]) + '/'

    print(f"🚀 Starting analysis for {file_name} in bucket {bucket_name}")
    
    df = preprocess_campaign_data(bucket_name, base_key, [file_name])
    analyze_campaign_data(df)
    
    print("✅ Done!")

if __name__ == "__main__":
    main()
