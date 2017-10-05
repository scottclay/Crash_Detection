import glob
import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime, timedelta

def read_data(datapath='../data/'):

    files = glob.glob(datapath+'*.csv')

    dfs = [pd.read_csv(f) for f in files]
    
    
    dfs[1] = dfs[1].rename(columns={" timestamp ": "timestamp"})



    for df in dfs:
        df['mag'] = np.sqrt(df['x']**2+df['y']**2+df['z']**2)
        df['time'] = pd.to_datetime(df['timestamp'], unit='ms')

    return dfs


def prepare_dfs(dfs,window):
    sorted_dfs = []
    rolling_mean = []
    rolling_std = []
    for df in dfs:
        _temp = df.sort_values(by='time')
        _temp = _temp.set_index(['time'])

        _mean = _temp.rolling(window).mean()
        _std = _temp.rolling(window).std()
    
        sorted_dfs.append(_temp)
        rolling_mean.append(_mean)
        rolling_std.append(_std)
    
    return sorted_dfs, rolling_mean, rolling_std


def Find_events(sorted_dfs, rolling_mean, rolling_std, variable, window):
    events_df = pd.DataFrame()
    drivers = []
    for i in range(0,25):
        for j in range(0,len(sorted_dfs[i].index)):
            if sorted_dfs[i][variable][j] > (rolling_mean[i][variable][j]+(2.75*rolling_std[i][variable][j])):
                if sorted_dfs[i][variable][j] > (sorted_dfs[i][variable].mean()+(5.0*sorted_dfs[i][variable].std())):
                    events_df = events_df.append(sorted_dfs[i].iloc[j])
                    drivers.append(i)
    events_df['driver']=drivers
    return events_df    
    
        
    
def fetch_data(datapath='../data/',window='1s'):
    dfs = read_data(datapath)
    sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,window)
    
    return dfs, sorted_dfs, rolling_mean, rolling_std

'''    
def calc_distance(dfs):
    
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
'''