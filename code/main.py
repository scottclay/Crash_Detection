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
sigma = 2.75 #standard deviations away from mean required for anomaly 
time_window = '1s' #time window for calculating the rolling mean
test_variable = 'mag' #the variable for detecting anomalies. mag = magnitude of acceleration

# Relative path to data
dir = os.path.dirname(__file__)
datapath = os.path.join(dir, '../data/')
output_path = os.path.join(dir, '../output/')

# Read data/Find events
print("Reading in and sorting data")
files, dfs, sorted_dfs, rolling_mean, rolling_std = fetch_data(datapath,time_window)    
new_dfs = calc_distance(dfs)
sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,time_window)
gps_dfs = calc_distance(sorted_dfs)
print("Finding potential events")
event = find_events(files, sorted_dfs, rolling_mean, rolling_std, test_variable, time_window, sigma)
event = gather_info(event, sorted_dfs, gps_dfs, 30)

# Cut the data based on a selection criteria to find crash events
print("Cutting the selection")
event_cut = event[(event.speed_before>event.speed_after) & (event.distance_after<10) & ((event.bearing_after - event.bearing_before)>100)]
event_cut = event_cut.drop_duplicates(subset=['driver'],keep='first') #only keep first event for each journey 

if len(event_cut.index) == 0:
    print("0 potential crashes! Try reducing the value of sigma")
else:
    print("Number of potential crash events:", len(event_cut.index))

#Produce outputs - plots for each event, and then text output
text_file = open(output_path+"output.txt", "w")
text_file.write("File name \t Time of event \t Acceleration \n")
print("File name \t Time of event \t Acceleration \n")
for i in range(0,len(event_cut.index)):
    plot_crash(output_path, i, event_cut.iloc[i:i+1],event_cut.filename[i],sorted_dfs[event_cut.driver[i]], rolling_mean[event_cut.driver[i]], gps_dfs[event_cut.driver[i]])
    print(event_cut.filename[i], '\t', str(event_cut.index[i]), '\t', event_cut.mag[i])
    text_file.write("%s \t %s \t %f \n" % (event_cut.filename[i], str(event_cut.index[i]), event_cut.mag[i]))

text_file.close()











