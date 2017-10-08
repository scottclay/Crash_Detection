#import python modules
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta


def read_data(datapath):
#function reads in the data into pandas dataframes and also calculates
#the magnitude of the acceleration from the x,y,z accelerometer values
#and the actual date and time from the unix time stamp

    files = glob.glob(datapath+'*.csv') #list of filepaths to each csv file
    dfs = [pd.read_csv(f) for f in files] #list of pandas dataframes
    
    for df in dfs:
        df.columns = df.columns.str.strip() #removes any white space from column headers
        df['mag'] = np.sqrt(df['x']**2+df['y']**2+df['z']**2)
        df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        #check units on acceleration, if mean >5 then need to convert to g
        if df['mag'].mean() > 5.0 :
        	df['mag'] = df['mag']/9.81 
    return files, dfs


def prepare_dfs(dfs,window):
#function changes the index of the dataframes to time and sorted them in 
#chronological order
#it then calculates the rolling mean and the rolling standard deviation
#and returns these 3 quantities as lists of dataframes
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
        
    
def fetch_data(datapath,window='1s'):
#function that calls the two functions above
    files, dfs = read_data(datapath)
    sorted_dfs, rolling_mean, rolling_std = prepare_dfs(dfs,window)
    
    if len(files)==0:
    	print("No files found in /data/")
    
    return files, dfs, sorted_dfs, rolling_mean, rolling_std

