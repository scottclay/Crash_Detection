import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime, timedelta

datapath = '../data/'

from read_data import fetch_data
from read_data import Find_events
from functions import Gather_info
from functions import Plot_crash

dfs, sorted_dfs, rolling_mean, rolling_std = fetch_data(datapath,'1s')
                
event = Find_events(sorted_dfs,rolling_mean, rolling_std,'mag','1s')

event = Gather_info(event, sorted_dfs, 30)


for i in range(0,len(event.index)):
    Plot_crash(i,event.iloc[i:i+1],sorted_dfs[event.driver[i]], rolling_mean[event.driver[i]], rolling_std[event.driver[i]])
    
    
    
    

'''    

distance = []
distance.append(0)
for i in range(1,len(test.index)):
    lat1 = test.lat.iloc[i-1]
    lat2 = test.lat.iloc[i]
    lon1 = test.lon.iloc[i-1]
    lon2 = test.lon.iloc[i]
    
    
    
    a = (np.sin((lat2 - lat1)/2))**2 + (np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1)/2))**2)
    c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1 - a))
    sofar = np.sum(distance)
    d = (6371.0*c)
    #distance.append((6371.0 * c))
    distance.append(d)
    #print(lat1,lat2,lon1,lon2)
    print (sofar,d)
    
#print(i,d)





for i in range(0,len(event2.index)):
    print(event2.mag[i])
    SD = event2.speed_before[i] / (2.0 * 0.6 * 9.81)
    a = (event2.speed_before[i]**2)/(2. * SD)
    print(a/10)
    if a/10 < event2.mag[i]:
        Plot_crash(event2.iloc[i:i+1],sorted_dfs[event2.driver[i]], rolling_mean[event2.driver[i]])

'''  
