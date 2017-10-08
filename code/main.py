#python packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# My functions 
from read_data import fetch_data
from read_data import prepare_dfs
from functions import find_events
from functions import gather_info
from functions import plot_crash
from functions import calc_distance


# Free parameters
datapath = '../data/'


files, dfs, sorted_dfs, rolling_mean, rolling_std = fetch_data(datapath,'1s')
                    
    
new_dfs = calc_distance(dfs)
sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,'1s')
gps_dfs = calc_distance(sorted_dfs)
#event = Find_events(dfs,'mag','1s')
event = find_events(files, sorted_dfs, rolling_mean, rolling_std,'mag','1s')
event = gather_info(event, sorted_dfs, gps_dfs, 30)



event_cut = event[(event.speed_before>event.speed_after) & (event.distance_after<10) & ((event.bearing_after - event.bearing_before)>100)]

event_cut = event_cut.drop_duplicates(subset=['driver'],keep='first')


for i in range(0,len(event_cut.index)):
    plot_crash(i, event_cut.iloc[i:i+1],event_cut.filename[i],sorted_dfs[event_cut.driver[i]], rolling_mean[event_cut.driver[i]], gps_dfs[event_cut.driver[i]])


print

