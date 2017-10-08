#python packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# My functions 
from read_data import fetch_data
from read_data import prepare_dfs
from functions import find_events
from functions import gather_info
from functions import plot_crash
from functions import calc_distance

# Free parameters
sigma = 2.75
time_window = '1s'
test_variable = 'mag'

# Relative path to data
dir = os.path.dirname(__file__)
datapath = os.path.join(dir, '../data/')
output_path = os.path.join(dir, '../output/')

# Read data/Find events
files, dfs, sorted_dfs, rolling_mean, rolling_std = fetch_data(datapath,time_window)    
new_dfs = calc_distance(dfs)
sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,time_window)
gps_dfs = calc_distance(sorted_dfs)
event = find_events(sigma, files, sorted_dfs, rolling_mean, rolling_std,test_variable,time_window)
event = gather_info(event, sorted_dfs, gps_dfs, 30)

# Cut the data based on a selection criteria to find crash events
event_cut = event[(event.speed_before>event.speed_after) & (event.distance_after<10) & ((event.bearing_after - event.bearing_before)>100)]
event_cut = event_cut.drop_duplicates(subset=['driver'],keep='first')

#Produce outputs - plots for each event, and then text output
print("File name \t Time of event \n")
for i in range(0,len(event_cut.index)):
    plot_crash(output_path, i, event_cut.iloc[i:i+1],event_cut.filename[i],sorted_dfs[event_cut.driver[i]], rolling_mean[event_cut.driver[i]], gps_dfs[event_cut.driver[i]])
    print(event_cut.filename[i], '\t', str(event_cut.index[i]))
















