# Online Ad Data Analysis
Notebook used to analyse Facebook Ad data for a TaskHer.

## Steps in function_test.ipynb
Loading Data from s3 - Input yout bucket, base key and file name.
Pre-processing the data - Single function that pre-processes the ad data and saves the processed data to the data/raw folder.
Analysing the data - Single function that analyses the pre-processed data and produces a text report stored in the 'reports' folder.

## Next Steps.
Format Output - include image and txt file storage within folders for all metrics, for easier tracking.
Considerations when adding any new data:
Add email functionality to reporting?
    - Considering temporal factors and how they affect the analysis.
    - How to systematically incorporate it into the current analysis.
Consider additional/more roburst Analysis Implementations.
Machine Learning Pipelines.
Data and dashboard presentation pipelines.

## Current applications of the current implementation.
Facebook campaign datasets that use the same schema can be immediately be pre-processed & analysed to communicate:
    - Quote prediction on a 30 pound buddget.
    - Gender Stats
    - Cheapest Service Areas
    - Cheapest Asset type between Images and Video
Can act as a tool aiding in automatically collating data and insights usefull for periodic reporting (after specific modifications).