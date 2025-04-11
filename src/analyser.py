import sys
import os
import pandas as pd
from datetime import datetime
from src.utils import decode_categorical_fast
import matplotlib.pyplot as plt

def analyze_campaign_data(encoded_df, mapping_dir='data/encoded_data', age_map=None, gender_map=None, reverse_service_map=None):
    """
    Analyze the campaign data to compute various metrics including cost per quote, quotes by demographics, and service analysis.

    Args:
    - encoded_df (pd.DataFrame): The preprocessed and encoded dataframe.
    - mapping_dir (str): The directory where the encoding mappings are stored.
    - age_map (dict, optional): Mapping for the 'age' column to human-readable labels.
    - gender_map (dict, optional): Mapping for the 'gender' column to human-readable labels.
    - reverse_service_map (dict, optional): Mapping for the 'ad_service' column to human-readable labels.

    Returns:
    - None: The function prints the results to the console and saves the report to a file.
    """
    # Decode the dataframe first
    decoded_df = decode_categorical_fast(encoded_df, mapping_dir)

    # Cost per quote by asset type
    cost_per_quote = (decoded_df.groupby('ad_assettype')['amount_spent_(gbp)'].sum() / 
                     decoded_df.groupby('ad_assettype')['results'].sum())

    print("Cost per quote by asset type:")
    print(cost_per_quote.sort_values())

    # Cost per quote by service
    service_cost = (decoded_df.groupby('ad_service')['amount_spent_(gbp)'].sum() / 
                   decoded_df.groupby('ad_service')['results'].sum())

    print("\nCost per quote by service:")
    print(service_cost.sort_values())

    # Age analysis (now uses decoded labels directly)
    age_quotes = decoded_df.groupby('age')['results'].sum().sort_values(ascending=False)

    print("\nQuotes by age group:")
    print(age_quotes)

    # Gender analysis (uses decoded labels directly)
    gender_quotes = decoded_df.groupby('gender')['results'].sum()
    gender_cost = (decoded_df.groupby('gender')['amount_spent_(gbp)'].sum() / 
                  decoded_df.groupby('gender')['results'].sum())

    print("\nQuotes by gender:")
    print(gender_quotes)
    print("\nCost per quote by gender:")
    print(gender_cost)

    # Bonus: Add formatted output
    def format_analysis(series, title):
        print(f"\n{title}:")
        if series.dtype == 'float64':
            print(series.sort_values().apply(lambda x: f"£{x:.2f}"))
        else:
            print(series.sort_values(ascending=False))

    format_analysis(age_quotes, "Quotes by age group (formatted)")
    format_analysis(gender_quotes, "Quotes by gender (formatted)")
    format_analysis(gender_cost, "Cost per quote by gender (formatted)")

    # Redirect print output to a file
    original_stdout = sys.stdout  # Save original stdout
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report_file_path = f'reports/ad_analysis_report_{timestamp}.txt'
    image_dir = f'reports/images/{timestamp}'
    os.makedirs(image_dir, exist_ok=True)


    with open(report_file_path, 'w') as f:
        sys.stdout = f  # Change stdout to file
        
        # Print report header
        print("="*60)
        print(" AD PERFORMANCE ANALYSIS REPORT".center(60))
        print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(60))
        print("="*60)

        # 0. Asset Type Analysis
        print("\n\n" + " ASSET TYPE PERFORMANCE ".center(60, '-'))
        cost_per_quote = (decoded_df.groupby('ad_assettype')['amount_spent_(gbp)'].sum() / 
                          decoded_df.groupby('ad_assettype')['results'].sum())
        print("\nCost per quote by asset type:")
        print(cost_per_quote.sort_values().to_string())

        cost_per_quote.plot(kind='bar', color='skyblue')
        plt.title('Cost per Quote by Asset Type')
        plt.ylabel('Cost (£)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{image_dir}/cpq_by_asset_type.png')
        plt.close()
        print("Saving images to:", os.path.abspath(image_dir))

        # 1. Age Analysis
        print("\n\n" + " AGE GROUP PERFORMANCE ".center(60, '-'))
        age_quotes = decoded_df.groupby('age')['results'].sum().sort_values(ascending=False)
        if age_map:
            age_quotes.index = age_quotes.index.map(age_map)
        print("\nQuotes by age group:")
        print(age_quotes.to_string())

        age_quotes.plot(kind='bar', color='mediumseagreen')
        plt.title('Quotes by Age Group')
        plt.ylabel('Number of Quotes')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{image_dir}/quotes_by_age.png')
        plt.close()

        
        # 2. Gender Analysis
        print("\n\n" + " GENDER PERFORMANCE ".center(60, '-'))
        gender_quotes = decoded_df.groupby('gender')['results'].sum()
        gender_cost = (decoded_df.groupby('gender')['amount_spent_(gbp)'].sum() / 
                      decoded_df.groupby('gender')['results'].sum())
        if gender_map:
            gender_quotes = gender_quotes.rename(gender_map)
            gender_cost = gender_cost.rename(gender_map)
        print("\nQuotes by gender:")
        print(gender_quotes.to_string())
        print("\nCost per quote by gender:")
        print(gender_cost.to_string())

        gender_cost.plot(kind='bar', color='slateblue')
        plt.title('Cost per Quote by Gender')
        plt.ylabel('Cost (£)')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f'{image_dir}/cpq_by_gender.png')
        plt.close()

        gender_quotes.plot(kind='bar', color='coral')
        plt.title('Quotes by Gender')
        plt.ylabel('Number of Quotes')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f'{image_dir}/quotes_by_gender.png')
        plt.close()

        # 3. Service Analysis
        print("\n\n" + " SERVICE PERFORMANCE ".center(60, '-'))
        service_cost = (decoded_df.groupby('ad_service')['amount_spent_(gbp)'].sum() / 
                       decoded_df.groupby('ad_service')['results'].sum())
        if reverse_service_map:
            service_cost.index = service_cost.index.map(reverse_service_map)
        print("\nCost per quote by service:")
        print(service_cost.sort_values().to_string())

        service_cost.plot(kind='bar', color='orchid')
        plt.title('Cost per Quote by Service')
        plt.ylabel('Cost (£)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{image_dir}/cpq_by_service.png')
        plt.close()

        
        # 4. Efficiency Metrics
        total_spent = decoded_df['amount_spent_(gbp)'].sum()
        total_quotes = decoded_df['results'].sum()
        current_cpq = total_spent / total_quotes
        predicted_quotes = total_quotes + (30 * current_cpq)  # Assume daily performance continues
        
        print("\n\n" + " EFFICIENCY METRICS ".center(60, '-'))
        print(f"\nTotal Amount Spent: £{total_spent:,.2f}")
        print(f"Total Quotes Received: {total_quotes:,.0f}")
        print(f"\nCurrent Cost Per Quote (CPQ): £{current_cpq:.2f}")
        print(f"Quotes per £100 spent: {(total_quotes/total_spent)*100:.1f}")
        print(f"\nPredicted Monthly Quotes @ £30/day: {predicted_quotes:,.0f}")
        
        print("\n\n" + " END OF REPORT ".center(60, '='))

    sys.stdout = original_stdout  # Reset stdout

    print(f"Analysis report saved to '{report_file_path}'")
