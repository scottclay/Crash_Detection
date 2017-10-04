import glob
import pandas as pd

import matplotlib.pyplot as plt

import numpy as np

from datetime import datetime, timedelta
import pylab
def Gather_info(event, dfs, time):
    
    speed_mean_before=[]
    speed_mean_after =[]
    force_mean_before=[]
    force_mean_after =[]    
    
    for i in range(0,len(event.index)):
        
        before = dfs[event.driver[i]][ (dfs[event.driver[i]].index> (event.index[i]-timedelta(seconds=time) )) & 
                       (dfs[event.driver[i]].index< (event.index[i]))]

        after = dfs[event.driver[i]][ (dfs[event.driver[i]].index> (event.index[i])) & 
                       (dfs[event.driver[i]].index< (event.index[i]+timedelta(seconds=time) ))]
        
        speed_mean_before.append(before.speed.mean())
        speed_mean_after.append(after.speed.mean())
        force_mean_before.append(before.mag.mean())
        force_mean_after.append(after.mag.mean())        
        
    event['speed_before'] = speed_mean_before
    event['speed_after']  = speed_mean_after     
    event['mag_before']   = force_mean_before    
    event['mag_after']    = force_mean_after
    
    return event
    
    



def Plot_crash(i, event, raw_profile, rolling_mean, rolling_std):
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(9,9))
    
    ax1.plot(raw_profile.index,raw_profile.mag)
    ax1.plot(rolling_mean.index, rolling_mean.mag)
    ax1.plot(event.index,event.mag, marker='*',markersize=20,c='k')
 
    ax2.plot(raw_profile.index,raw_profile.mag)
    ax2.plot(rolling_mean.index, rolling_mean.mag)
    ax2.plot(event.index,event.mag, marker='*',markersize=20,c='k')
    ax2.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    
    ax1.set_title(str(i)+' '+str(rolling_mean[rolling_mean.index ==event.iloc[0:1].index[0]].mag[0]))
    ax2.set_title(str(rolling_std[rolling_std.index ==event.iloc[0:1].index[0]].mag[0]))

    speed_df = raw_profile[['speed','lat','lon','height']].dropna(axis=0)
    ax3.plot(speed_df.index,speed_df.speed)
    ax3.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    
    ax4.plot(speed_df.index,speed_df.speed)
    ax4.plot([event.index,event.index],[speed_df.speed.min(),speed_df.speed.max()],c='k')
    ax4.set_xlim([event.index - timedelta(seconds=30),event.index + timedelta(seconds=30)])
    
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-1, event.speed_before[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-3, event.speed_after[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-5, event.mag_before[0])
    ax4.text(event.index+timedelta(seconds=5), speed_df.speed.max()-7, event.mag_after[0])
    
    pylab.savefig('../figs/'+str(event.iloc[0:1].driver[0])+'_'+str(i)+'.png', bbox_inches=0)
    plt.close()
    
    
