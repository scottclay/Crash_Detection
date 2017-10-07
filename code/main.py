import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime, timedelta

datapath = '../data/'

from read_data import fetch_data
from read_data import Find_events
from read_data import prepare_dfs
from functions import Gather_info
from functions import Plot_crash
from functions import Calc_distance

files, dfs, sorted_dfs, rolling_mean, rolling_std = fetch_data(datapath,'1s')
                    
    
new_dfs = Calc_distance(dfs)
sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,'1s')
gps_dfs = Calc_distance(sorted_dfs)
#event = Find_events(dfs,'mag','1s')
event = Find_events(files, sorted_dfs, rolling_mean, rolling_std,'mag','1s')
event = Gather_info(event, sorted_dfs, gps_dfs, 30)



event_cut = event[(event.speed_before>event.speed_after) & (event.distance_after<10) & ((event.bearing_after - event.bearing_before)>100)]

event_cut = event_cut.drop_duplicates(subset=['driver'],keep='first')


for i in range(0,len(event_cut.index)):
    Plot_crash(i, event_cut.iloc[i:i+1],event_cut.filename[i],sorted_dfs[event_cut.driver[i]], rolling_mean[event_cut.driver[i]], gps_dfs[event_cut.driver[i]])


print

