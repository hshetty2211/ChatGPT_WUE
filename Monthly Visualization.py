import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Assuming the utils.dataloader module and functions are correctly implemented
from utils.dataloader import load_indirect_WUE, load_direct_WUE

def estimate_total_water(power, indirectWue, directWue):
    min_length = min(len(indirectWue), len(directWue))
    indirectWue = indirectWue[:min_length]
    directWue = directWue[:min_length]

    date_rng = pd.date_range(start='2021-09-01', end='2022-07-31 23:00:00', freq='H')[:min_length]
    df = pd.DataFrame({'date': date_rng, 'indirectWue': indirectWue, 'directWue': directWue})
    df.set_index('date', inplace=True)
    
    monthly_data = df.resample('M').sum()
    monthly_data['totalWue'] = (monthly_data['indirectWue'] + monthly_data['directWue']) * power
    
    wue_array = monthly_data['totalWue'].values
    return wue_array

def load_total_water(loc_name):
    fuel_mix_path = "MIDW_IA.csv"
    weather_path  = "DSM_IA.csv"
    dc_loc        = loc_name

    indirectWue = load_indirect_WUE(fuel_mix_path, dc_loc)
    indirectWue = np.roll(indirectWue, -7)

    directWue = load_direct_WUE(weather_path)
    directWue = np.roll(directWue, -7)

    return directWue, indirectWue

loc_name = "DSM"
power    = 295

directWue, indirectWue = load_total_water(loc_name)
wue_array = estimate_total_water(power, indirectWue, directWue)

wue_array = wue_array / 10**6

total_wue = np.sum(wue_array)

plt.figure()
plt.plot(wue_array, linewidth=5, color='blue')

# Set the x-axis labels
plt.xticks([0, 3, 6, 9], ['Sept', 'Dec', 'Mar', 'Jun'])

# Set the y-axis range
plt.ylim([0, wue_array.max() + 0.1 * wue_array.max()])

# Add a legend
plt.legend(['Des Moines, Iowa'])

# Label the y-axis
plt.ylabel('Total water consumption (X10^6L)')

# Add a plot title
plt.title('Monthly Water Use')

plt.show()