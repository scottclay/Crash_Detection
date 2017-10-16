#import python modules
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pylab

def find_events(files, sorted_dfs, rolling_mean, rolling_std, variable, window, sigma=2.75):
#function looks for anomalies in the data as raw events more than sigma standard deviations
#away from the rolling mean
#and returns these events as a new dataframe
    events_df = pd.DataFrame()
    drivers = []
    filenames = []
    for i in range(0,len(sorted_dfs)): #all data files
        for j in range(0,len(sorted_dfs[i].index)): #timesteps
            if sorted_dfs[i][variable][j] > (rolling_mean[i][variable][j]+(sigma*rolling_std[i][variable][j])): #sigma*std + mean
                if sorted_dfs[i][variable][j] > (sorted_dfs[i][variable].mean()+(5.0*sorted_dfs[i][variable].std())): #remove noise
                    events_df = events_df.append(sorted_dfs[i].iloc[j]) #store anomaly in new dataframe
                    drivers.append(i) #keep track of which file it came from
                    filenames.append(files[i].split('/')[-1])
    events_df['driver']=drivers
    events_df['filename'] = filenames
    return events_df    

def gather_info(event, dfs, gps, time):
#function that gathers various information on the anomalies by making various time
#cuts around the data 
    speed_mean_before=[]
    speed_mean_after =[]
    acc_mean_before=[]
    acc_mean_after =[]    
    distance_sum_after = []
    bearing_range_before = []
    bearing_range_after = []
    
    for i in range(0,len(event.index)):
        
        #speed and acceleration
        #30 seconds before 
        before = dfs[event.driver[i]][ (dfs[event.driver[i]].index> (event.index[i]-timedelta(seconds=time) )) & 
                       (dfs[event.driver[i]].index< (event.index[i]))]
		#after the event
        after = dfs[event.driver[i]][(dfs[event.driver[i]].index> (event.index[i]))]
        
        speed_mean_before.append(before.speed.mean())
        speed_mean_after.append(after.speed.mean())
        acc_mean_before.append(before.mag.mean())
        acc_mean_after.append(after.mag.mean())
        
        #distance travelled after the event
        gps_after = gps[event.driver[i]][ gps[event.driver[i]].index> (event.index[i])]
        distance_sum_after.append(gps_after.distance.sum())
        
        #bearing change in the 10 seconds after the event
        gps_before = gps[event.driver[i]][ (gps[event.driver[i]].index> (event.index[i]-timedelta(seconds=10) )) & 
                       (gps[event.driver[i]].index< (event.index[i]))]
        
        gps_after = gps[event.driver[i]][ (gps[event.driver[i]].index> (event.index[i])) & 
                       (gps[event.driver[i]].index< (event.index[i]+timedelta(seconds=10) ))]
        
        bearing_range_before.append(gps_before.bearing.max() - gps_before.bearing.min())
        bearing_range_after.append(gps_after.bearing.max() - gps_after.bearing.min())        
    
    #new columns in the events dataframe    
    event['speed_before'] = speed_mean_before
    event['speed_after']  = speed_mean_after     
    event['mag_before']   = acc_mean_before    
    event['mag_after']    = acc_mean_after
    event['distance_after'] = distance_sum_after
    event['bearing_before'] = bearing_range_before
    event['bearing_after'] = bearing_range_after
    
    return event
    
    
def calc_distance(dfs):
#function calculates the distance from the gps coords
    new_df = []
    for df in dfs:
        _df = df[['lat','lon','bearing']].dropna(axis=0) #drop NaNs
        distance = []
        distance.append(0.)
        summed_distance = []
        summed_distance.append(0.)
        for i in range(1,len(_df.index)):
            lat1 = np.radians(_df.lat.iloc[i-1])
            lat2 = np.radians(_df.lat.iloc[i])
            lon1 = np.radians(_df.lon.iloc[i-1])
            lon2 = np.radians(_df.lon.iloc[i])
            
            #we use the Haversine formula expressed as a two-argument inverge tangent
            #function to calculate the short distance between two points on a sphere
            a = (np.sin((lat2 - lat1)/2))**2 + (np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1)/2))**2)
            c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1 - a))
            d = (6371.0*c) #radius of the Earth * c
            distance.append(d)
            summed_distance.append(d + summed_distance[i-1])
        _df['distance'] = distance
        _df['summed_distance'] = summed_distance
        new_df.append(_df)
    return new_df
            

def plot_crash(output_path, i, event, driver, raw_profile, rolling_mean, gps_dfs):
#function plots an event profile for each potential crash event
    fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(9,13.5))
    
    plt.subplots_adjust(hspace = 0.5)
    plt.suptitle(str(driver)+'\n'+str(event.index[0]))
     
    ax1.plot(raw_profile.index,raw_profile.mag)
    ax1.plot(rolling_mean.index, rolling_mean.mag)
    ax1.plot(event.index,event.mag, marker='*',markersize=20,c='k')
    ax1.set_title("Acceleration - Full profile")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Acceleration (g)")

    ax2.plot(raw_profile.index,raw_profile.mag)
    ax2.plot(rolling_mean.index, rolling_mean.mag)
    ax2.plot(event.index,event.mag, marker='*',markersize=20,c='k')
    ax2.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax2.set_title("Acceleration - -30sec to +30sec of event")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Acceleration (g)")
             
    speed_df = raw_profile[['speed','lat','lon','height']].dropna(axis=0)
    ax3.plot(speed_df.index,speed_df.speed)
    ax3.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    ax3.set_title("Speed - Full profile")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Speed (units?)")
    
    ax4.plot(speed_df.index,speed_df.speed)
    ax4.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    ax4.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax4.set_title("Speed - -30sec to +30sec of event")
    ax4.set_xlabel("Time")
    ax4.set_ylabel("Speed (units?)")
        
    ax5.plot(gps_dfs.index, gps_dfs.distance)
    ax5.plot([event.index,event.index],[gps_dfs.distance.min(),gps_dfs.distance.max()],c='k')
    ax5.set_title("Distance - -30sec to end of journey")
    ax5.set_xlim([event.index - timedelta(seconds=30),gps_dfs.index.max()])
    ax5.set_xlabel("Time")
    ax5.set_ylabel("Distance (km)")
        
    ax6.plot(gps_dfs.index, gps_dfs.bearing)
    ax6.plot([event.index,event.index],[gps_dfs.bearing.min(),gps_dfs.bearing.max()],c='k')
    ax6.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax6.set_title("Bearing - -30sec to +30sec of event")
    ax6.set_xlabel("Time")
    ax6.set_ylabel("Bearing (degrees)")
 
	#make axes bold and sort xlabels out for datetime format
    import matplotlib.dates as mdates
    myFmt = mdates.DateFormatter('%H:%M:%S')
    axes = fig.get_axes()
    for ax in axes:
        [i.set_linewidth(2.1) for i in ax.spines.values()]
        ax.xaxis.set_major_formatter(myFmt)
        plt.sca(ax)
        plt.xticks(rotation=30)
        

    
    pylab.savefig(output_path+'/figs/'+str(event.iloc[0:1].driver[0])+str(driver)+'.png', bbox_inches=0)
