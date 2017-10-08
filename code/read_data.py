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

    return files, dfs


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
        
    
def fetch_data(datapath='../data/',window='1s'):
    files, dfs = read_data(datapath)
    sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,window)
    
    return files, dfs, sorted_dfs, rolling_mean, rolling_std

