# Online Ad Data Analysis
Notebook used to analyse Facebook Ad data for a lingerie company.

# Steps
1. Loading Data from s3
2. Pre-processing the data:
-   Renamed the columns for intuitive understanding
-   Removed NaN values by computing the median (has drawbacks)
3. Analysing the data
4. Test ML models and predict some of the data:
-   How to percieve the predictions - map back the campaigns/ads/add_sets to their original names?
-   The predictions are forecasts for 'purchases' for certain campaigns/ads/add_sets based on the performance of other campaigns/ads/add_sets, are there limitations to this approach? What are some alternatives?
-   Not all campaigns/Ad Sets/Ads are predicted
-   How would the current setup be applicable to a real world application?

Reconfigure Data Sets to Include Ad configurations by adding additional columns

# Next Steps - Create a Pre-processing pipeline.
Understand the relation between campaigns, ad sets and ads before proceeding.