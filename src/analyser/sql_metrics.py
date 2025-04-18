# src/analyser/sql_metrics.py

import pandas as pd

def cost_per_quote_by_asset_type(engine):
    query = """
    SELECT
        ad_assettype,
        SUM("amount_spent_gbp") / NULLIF(SUM(results), 0) AS cost_per_quote
    FROM campaign_data
    GROUP BY ad_assettype;
    """
    return pd.read_sql(query, engine)

def cost_per_quote_by_service(engine):
    query = """
    SELECT
        ad_service,
        SUM("amount_spent_gbp") / NULLIF(SUM(results), 0) AS cost_per_quote
    FROM campaign_data
    GROUP BY ad_service;
    """
    return pd.read_sql(query, engine)

def quotes_by_age_group(engine):
    query = """
    SELECT
        age,
        SUM(results) AS total_quotes
    FROM campaign_data
    GROUP BY age;
    """
    return pd.read_sql(query, engine)

def quotes_by_gender(engine):
    query = """
    SELECT
        gender,
        SUM(results) AS total_quotes
    FROM campaign_data
    GROUP BY gender;
    """
    return pd.read_sql(query, engine)

def cost_per_quote_by_gender(engine):
    query = """
    SELECT
        gender,
        SUM("amount_spent_gbp") / NULLIF(SUM(results), 0) AS cost_per_quote
    FROM campaign_data
    GROUP BY gender;
    """
    return pd.read_sql(query, engine)

def aggregate_performance_by_time(engine):
    """
    Aggregates campaign performance by week, month, and year.
    Returns a dictionary of dataframes with temporal performance metrics.
    """
    # Performance by Week
    query_week = """
    SELECT
        campaign_week,
        SUM(amount_spent_gbp) AS total_spent,
        SUM(results) AS total_results
    FROM campaign_data
    GROUP BY campaign_week
    ORDER BY campaign_week;
    """
    performance_week = pd.read_sql(query_week, engine)
    
    # Performance by Month
    query_month = """
    SELECT
        campaign_month,
        SUM(amount_spent_gbp) AS total_spent,
        SUM(results) AS total_results
    FROM campaign_data
    GROUP BY campaign_month
    ORDER BY campaign_month;
    """
    performance_month = pd.read_sql(query_month, engine)

    # Performance by Year
    query_year = """
    SELECT
        campaign_year,
        SUM(amount_spent_gbp) AS total_spent,
        SUM(results) AS total_results
    FROM campaign_data
    GROUP BY campaign_year
    ORDER BY campaign_year;
    """
    performance_year = pd.read_sql(query_year, engine)

    # Returning as a dictionary for easy reporting
    return {
        'week': performance_week,
        'month': performance_month,
        'year': performance_year
    }


def impression_analytics(engine, groupby_cols):
    group = ', '.join(groupby_cols)
    query = f"""
    SELECT
        {group},
        SUM(impressions) AS Impressions,
        SUM(CASE WHEN LOWER(TRIM(result_type)) = 'linkclicks' THEN results ELSE 0 END) AS "Link Clicks",
        SUM(CASE WHEN LOWER(TRIM(result_type)) = 'quotereceived' THEN results ELSE 0 END) AS "Quotes",
        SUM(CASE WHEN LOWER(TRIM(result_type)) = 'metaleads' THEN results ELSE 0 END) AS "Meta Leads",
        SUM(CASE WHEN LOWER(TRIM(result_type)) = 'actions:visit_instagram_profile' THEN results ELSE 0 END) AS "Instagram Visits"
    FROM campaign_data
    GROUP BY {group}
    ORDER BY {group};
    """
    df = pd.read_sql(query, engine)

    # Add rates
    df["CTR (%)"] = (df["Link Clicks"] / df["impressions"]) * 100
    df["Quote Rate (%)"] = (df["Quotes"] / df["impressions"]) * 100
    df["Meta Leads Rate (%)"] = (df["Meta Leads"] / df["impressions"]) * 100
    df["Instagram Visits Rate (%)"] = (df["Instagram Visits"] / df["impressions"]) * 100

    return df
