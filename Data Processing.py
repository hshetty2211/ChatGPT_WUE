"""
This code cleans weather data sourced from Iowa Environmental Mesonet and 
Energy Fuel Mix data from EIA

"""

#%% Import functions

import pandas as pd
import numpy as np 

from utils.data_preprocess import convert_str_double, fix_nan_value, detect_missing_values
from utils.data_preprocess import convert_to_TWetBulb
from utils.data_preprocess import round_hour, align_time 
from utils.data_preprocess import repair_single_fuel

#%% Clean Weather Data

file_name = "DSM"
weath_path = "{}.csv".format(file_name)
df = pd.read_csv(weath_path)

# Align time into hours
df = align_time(df)
df = df.drop_duplicates(subset=['valid'])
if file_name in ["DSM"]:
    df = df.iloc[1:,:]

# Data Cleaning, remove "M" values       ######

data_dict = {"station": df["station"],
             "valid"  : df["valid"]   }

# Convert the temperature string list to np.double array
selected_cols = ["tmpf", "dwpf", "relh"]
for k in selected_cols:
    temperature_value = df[k].values
    arr = convert_str_double(temperature_value)
    data_dict[k] = arr

# Convert the pressure list to np.double array 
pressure = df["mslp"].values
if np.all(pressure=="M"):
    # The typical pressure at sea level is 1013.25 millibars or 14.7 pounds per square inch (PSi).
    arr = np.ones(pressure.shape)*1013.25
else:
    arr = convert_str_double(pressure)
data_dict["mslp"] = arr

# Convert the results to a dataframe 
df_res = pd.DataFrame(data_dict)
missed_array = detect_missing_values(df_res["valid"].values)

# Create a data template
dummy_head_i = df_res.iloc[0,:].copy()
selected_cols = ["tmpf", "dwpf", "relh", "mslp"]

# Set all the values in this dummy row as NaN
for k in selected_cols:
    dummy_head_i[k] = np.nan

# Insert all the missed values
for missed_key in missed_array:
    dummy_head_i["valid"]     = missed_key
    df_res = df_res.append(dummy_head_i)

# Only select period data and sort based on time stamp
df_res = df_res.sort_values(["valid"])
df_res = df_res.iloc[5830:13846,:]  


# Fix the NaN values with linear interpolation
for k in selected_cols:
    repaired_arr = fix_nan_value(df_res[k])
    df_res[k]    = repaired_arr
    
#%% Get Wet Bulb Temperature

drytemp      = df_res["tmpf"].values
relh         = df_res["relh"].values
pressure     = df_res["mslp"].values

wettemp      = convert_to_TWetBulb(drytemp, relh, pressure)
df_res.insert(4, 'wbtmp',wettemp)

weather_out = "{}_IA.csv".format(file_name)
df_res.to_csv(weather_out, float_format='%.2f', index=False)

#%% Clean EIA Data

coorp_name = "MIDW"

fuel_mix_path = "{}.csv".format(coorp_name)
num_timeslot  = 24*60

df_raw = pd.read_csv(fuel_mix_path)

# Create data template the the dataframe 
dummy_head = df_raw.iloc[0,:].copy()
dummy_head["value"]     = np.nan
dummy_head["fueltype"]  = "NA"
dummy_head["type-name"] = "NA"

# Create dataframe list
df_list = []
fuel_list = list(set(df_raw["fueltype"].values))

# Drop Non-renewables since Microsoft only uses Renewable Sources to power Iowa Data centre. 
fuel_list = [item for item in fuel_list if item not in ['NUC', 'COL', 'NG']]


for fuel_name in fuel_list:
    
    df_i = df_raw[df_raw["fueltype"]==fuel_name]

    value_inter = fix_nan_value(df_i["value"].values)
    df_i = df_i.assign(value=value_inter)
    
    df_list.append(df_i)

df_fuel = pd.concat(df_list)
df_fuel = df_fuel.sort_values(['period', 'fueltype'])

fuel_mix_out = "{}_IA.csv".format(coorp_name)
df_fuel.to_csv(fuel_mix_out, float_format='%.2f', index=False)