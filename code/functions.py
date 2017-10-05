import glob
import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime, timedelta
import pylab
    
def Gather_info(event, dfs, gps, time):
    
    speed_mean_before=[]
    speed_mean_after =[]
    acc_mean_before=[]
    acc_mean_after =[]    
    distance_sum_after = []
    bearing_range_before = []
    bearing_range_after = []
    
    for i in range(0,len(event.index)):
        
        before = dfs[event.driver[i]][ (dfs[event.driver[i]].index> (event.index[i]-timedelta(seconds=time) )) & 
                       (dfs[event.driver[i]].index< (event.index[i]))]

        after = dfs[event.driver[i]][ (dfs[event.driver[i]].index> (event.index[i])) & 
                       (dfs[event.driver[i]].index< (event.index[i]+timedelta(seconds=time) ))]
        
        speed_mean_before.append(before.speed.mean())
        speed_mean_after.append(after.speed.mean())
        acc_mean_before.append(before.mag.mean())
        acc_mean_after.append(after.mag.mean())
        
        
        gps_after = gps[event.driver[i]][ gps[event.driver[i]].index> (event.index[i])]
        distance_sum_after.append(gps_after.distance.sum())
        
        gps_before = gps[event.driver[i]][ (gps[event.driver[i]].index> (event.index[i]-timedelta(seconds=10) )) & 
                       (gps[event.driver[i]].index< (event.index[i]))]
        
        gps_after = gps[event.driver[i]][ (gps[event.driver[i]].index> (event.index[i])) & 
                       (gps[event.driver[i]].index< (event.index[i]+timedelta(seconds=10) ))]
        
        bearing_range_before.append(gps_before.bearing.max() - gps_before.bearing.min())
        bearing_range_after.append(gps_after.bearing.max() - gps_after.bearing.min())        
        
    event['speed_before'] = speed_mean_before
    event['speed_after']  = speed_mean_after     
    event['mag_before']   = acc_mean_before    
    event['mag_after']    = acc_mean_after
    event['distance_after'] = distance_sum_after
    event['bearing_before'] = bearing_range_before
    event['bearing_after'] = bearing_range_after
    
    return event
    
    
def Calc_distance(dfs):
    new_df = []
    for df in dfs:
        _df = df[['lat','lon','bearing']].dropna(axis=0)
        distance = []
        distance.append(0.)
        summed_distance = []
        summed_distance.append(0.)
        for i in range(1,len(_df.index)):
            lat1 = _df.lat.iloc[i-1]
            lat2 = _df.lat.iloc[i]
            lon1 = _df.lon.iloc[i-1]
            lon2 = _df.lon.iloc[i]

            a = (np.sin((lat2 - lat1)/2))**2 + (np.cos(lat1) * np.cos(lat2) * (np.sin((lon2 - lon1)/2))**2)
            c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1 - a))
            #sofar = np.sum(distance)
            d = (6371.0*c)
            distance.append(d)
            summed_distance.append(d + summed_distance[i-1])
        _df['distance'] = distance
        _df['summed_distance'] = summed_distance
        new_df.append(_df)
    return new_df
            


def Plot_crash(i, event, raw_profile, rolling_mean, gps_dfs):
    f, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(9,13.5))
    
    ax1.plot(raw_profile.index,raw_profile.mag)
    ax1.plot(rolling_mean.index, rolling_mean.mag)
    ax1.plot(event.index,event.mag, marker='*',markersize=20,c='k')
    ax1.set_title("Acceleration - Full profile")
 
    ax2.plot(raw_profile.index,raw_profile.mag)
    ax2.plot(rolling_mean.index, rolling_mean.mag)
    ax2.plot(event.index,event.mag, marker='*',markersize=20,c='k')
    ax2.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax2.set_title("Acceleration - -30sec to +30sec of event")
             
    speed_df = raw_profile[['speed','lat','lon','height']].dropna(axis=0)
    ax3.plot(speed_df.index,speed_df.speed)
    ax3.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    ax3.set_title("Speed - Full profile")
    
    ax4.plot(speed_df.index,speed_df.speed)
    ax4.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    ax4.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax4.set_title("Speed - -30sec to +30sec of event")
    
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-1, event.speed_before[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-3, event.speed_after[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-5, event.mag_before[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-7, event.mag_after[0])
    
    ax5.plot(gps_dfs.index, gps_dfs.distance)
    ax5.plot([event.index,event.index],[gps_dfs.distance.min(),gps_dfs.distance.max()],c='k')
    ax5.set_title("Distance - Full profile")
    ax5.set_xlim([event.index - timedelta(seconds=30),gps_dfs.index.max()])
    ax5.text(event.index+timedelta(seconds=5), gps_dfs.distance.max(), event.distance_after[0])
    
    #ax6.plot(gps_dfs.index, gps_dfs.distance)
    #ax6.plot([event.index,event.index],[gps_dfs.distance.min(),gps_dfs.distance.max()],c='k')
    #ax6.set_xlim([event.index - timedelta(seconds=30),gps_dfs.index.max()])
    
    ax6.plot(gps_dfs.index, gps_dfs.bearing)
    ax6.plot([event.index,event.index],[gps_dfs.bearing.min(),gps_dfs.bearing.max()],c='k')
    ax6.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    ax6.set_title("Bearing - -30sec to +30sec of event")
    ax6.text(event.index+timedelta(seconds=5), 250, event.bearing_before[0])
    ax6.text(event.index+timedelta(seconds=5), 230, event.bearing_after[0])
    
    pylab.savefig('../figs/'+str(event.iloc[0:1].driver[0])+'_'+str(i)+'.png', bbox_inches=0)
    plt.close()
    
    
    
    
    #plt.show()