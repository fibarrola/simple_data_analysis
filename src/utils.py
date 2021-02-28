# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 12:54:57 2021

@author: frani
"""

from importlib import reload  
import numpy as np
from datetime import datetime
from sklearn.neighbors import LocalOutlierFactor
from scipy import signal



# Check wrong data types within timestamps
def clear_timestamps(df):
    to_drop = []
    dropped = []
    for ind in range(len(df)):
        try:
            datetime.strftime(df['Timestamps'][ind],'%Y')
        except:
            to_drop.append(ind)
            dropped.append(df['Timestamps'][ind])
    df = df.drop(to_drop)
    df = df.reset_index()
    return df, dropped


# Turn timestamps into a series of integers to perform oulier analysis
def tstamps_to_ints(df):
    time_ints = np.empty_like(df['Timestamps'])
    time_ints[0] = 0
    for k in range(1,len(df['Timestamps'])):
        time_gap = df['Timestamps'][k]-df['Timestamps'][k-1]
        time_ints[k] = time_ints[k-1] + time_gap.seconds
    return time_ints


# Get outliers
def get_outliers(time_ints, values, threshold=-2):
    # Fit times to [0,1] because it's seldom a bad idea
    time_ints = (time_ints - time_ints.min())/time_ints.max()
    
    # Local outlier factor analisys
    clf = LocalOutlierFactor(n_neighbors=50)
    clf.fit(np.transpose([time_ints, values/values.max()]))
    neg_of = clf.negative_outlier_factor_
    outliers = []
    values_cleared = values.copy()
    for ind in range(len(values_cleared)):
        if neg_of[ind] < -2:
            outliers.append(ind)
            values_cleared[ind] = np.nan
            
    return outliers, values_cleared


def filter_values(values_cleared, freq):
    
    # Fill missing inputs with mean of surrounding values
    values_filled = values_cleared.copy()
    for ind in range(len(values_cleared)):
        values_filled[ind] = np.nanmean(values_cleared[max(0,ind-10):min(ind+10,len(values_cleared))])
    
    # Heavy filtering on the signal to get overall tendency
    b, a = signal.butter(3, freq, 'low')
    filtered_values = signal.filtfilt(b, a, values_filled)
    
    # Find local minima and maxima of the function
    local_mins = []
    local_maxs = []
    for ind in range(1,len(filtered_values)-1):
        if filtered_values[ind-1]<=filtered_values[ind] and filtered_values[ind+1]<=filtered_values[ind]:
            local_maxs.append(ind)
        elif filtered_values[ind-1]>=filtered_values[ind] and filtered_values[ind+1]>=filtered_values[ind]:
            local_mins.append(ind)
    
    return filtered_values, local_mins, local_maxs


def get_period(filtered_values):
    auto_correlation = np.empty_like(filtered_values)
    for ind in range(len(filtered_values)):
        aux = np.concatenate((filtered_values[ind:-1],filtered_values[0:ind]))
        np.correlate(filtered_values,aux)
        auto_correlation[ind] = np.correlate(filtered_values,aux)[0]
    
    up = False
    for ind in range(len(filtered_values)):
        if auto_correlation[ind] < auto_correlation[ind+1]:
            up = True
        if up and auto_correlation[ind]>auto_correlation[ind+1]:
            period = ind
            break
    
    return auto_correlation, period
    

def sillyPredict(filtered_values, N=120):
    # Cut off the last part, as it is proclive to misstakes
    prediction = filtered_values[:-100]
    
    for k in range((N+100)//5):
        last = prediction[-50:]
        xx = np.array(range(50))
        coefs = np.polyfit(xx,last,1)
        p = np.poly1d(coefs)
        prediction = np.concatenate((prediction,p(np.array(range(50,55)))))
        
    return prediction

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    