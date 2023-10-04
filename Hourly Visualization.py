import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.dataloader import load_indirect_WUE, load_direct_WUE

def load_total_water(loc_name):
    fuel_mix_path = "MIDW_IA.csv"
    weather_path  = "DSM_IA.csv"
    dc_loc        = loc_name

    indirectWue = load_indirect_WUE(fuel_mix_path, dc_loc)
    indirectWue = np.roll(indirectWue, -7)

    directWue = load_direct_WUE(weather_path)
    directWue = np.roll(directWue, -7)

    return directWue, indirectWue

def prepare_data_for_boxplot(indirectWue, directWue):
    min_length = min(len(indirectWue), len(directWue))
    indirectWue = indirectWue[:min_length]
    directWue = directWue[:min_length]

    date_rng = pd.date_range(start='2021-09-01', end='2022-07-31 23:00:00', freq='H')[:min_length]
    df = pd.DataFrame({'date': date_rng, 'indirectWue': indirectWue, 'directWue': directWue})
    df.set_index('date', inplace=True)
    
    df['totalWue'] = df['indirectWue'] + df['directWue']
    df['hour'] = df.index.hour+1
    
    return df[['hour', 'totalWue']]

loc_name = "DSM"
directWue, indirectWue = load_total_water(loc_name)
data_for_boxplot = prepare_data_for_boxplot(indirectWue, directWue)

plt.figure(figsize=(12, 6))
box_plot_ax = data_for_boxplot.boxplot(column='totalWue', by='hour', grid=True, return_type='axes')

# Calculate the average water usage for each hour
avg_hourly = data_for_boxplot.groupby('hour')['totalWue'].mean()

# Overlay a line plot of the average water usage
plt.plot(range(1, 25), avg_hourly, color='red', label='Average', linewidth=2)

plt.title('Hourly Water Usage Statistics')
plt.suptitle('')  # Suppress the automatic title
plt.xlabel('Hour of the Day')
plt.ylabel('Water Usage')
plt.legend()
plt.xticks(rotation=0)
plt.grid(True)
plt.show()