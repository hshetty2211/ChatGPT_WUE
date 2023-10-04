""" 
This code downloads fuel mix data from EIA for the Midwestern region for 
2021 and 2022 calender years

Date: October 2023

"""

#%% Import Functions 

import pandas as pd
import numpy as np
from utils.download_eia import download_whole_year

#%% Download Fuel mix data

api_key  = "ABEAFl4rDDER6PhyaHWvMWCpNeSgJejqaQWe2Ewh"

# Download data for 2021
year_1 = 2021
region_code = "MIDW"
df_year_1 = download_whole_year(year_1, region_code, api_key)

# Download data for 2022
year_2 = 2022
region_code = "MIDW"
df_year_2 = download_whole_year(year_2, region_code, api_key)

#%% Organize Index, Merge dfs and Export


# Convert the period column to datetime
df_year_1['period'] = pd.to_datetime(df_year_1['period'], format='%Y-%m-%dT%H')

df_year_2['period'] = pd.to_datetime(df_year_2['period'], format='%Y-%m-%dT%H')

# Set Index
df_year_1 = df_year_1.set_index('period')

df_year_2 = df_year_2.set_index('period')

df_eia_raw = pd.concat([df_year_1,df_year_2])

# Extract the desired date range
start_date = '2021-09-01 00:00:00'
end_date = '2022-07-31 23:00:00'

# Use boolean indexing to filter the DataFrame
df_eia = df_eia_raw[(df_eia_raw.index >= start_date) & (df_eia_raw.index <= end_date)]

df_eia.to_csv('MIDW.csv')

