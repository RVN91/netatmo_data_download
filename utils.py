#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Rasmus Nielsen
Instituion: SMHI, Sweden
Date: 29-08-2018

This module contains the function for converting the html-response from
netatmo into a dataframe.
"""
import pandas as pd
import numpy as np

def convert_netatmo_getpublicdata_response_to_dataframe(response, convert_to_datetime):
    """
    Reads the response from Netatmo API
    and converts it to a dataframe
    
    Input:
        response (json):                         json formatted respone 
                                                 from Netatmo API
        convert_to_datetime (True, False, Bool): If true: Convert 
                                                 timestamp to datime
    Returns:
        pandas.DataFrame: Response converted to a data frame
    """    
    # Get the list of stations
    stations = response['body']
    
    # Initialize a dictionary to hold the data
    station_dict = {
        "mac_id": [],
        "altitude": [],
        "longitude": [],
        "latitude": [],
        "timezone": [],
    }
    
    # Iterate through stations and process the data
    for station in stations:
        station_id = station['_id']               # Get the MAC address  
        station_dict["mac_id"].append(station_id) # Add id to dict
    
        # Gather positional information
        place = station["place"]
        location = place["location"]
        longitude, latitude = location            # Get longitude and latitude
        altitude = place["altitude"]
        timezone = place["timezone"]
        # add position to dict
        station_dict["altitude"].append(altitude)
        station_dict["longitude"].append(longitude)
        station_dict["latitude"].append(latitude)
        station_dict["timezone"].append(timezone)
        
        # Iterate through all measurements (TODO: implement wind data...)
        measdict = {} # Empty dictionary to hold all the measurements
        for module_id, measure in station["measures"].items():
            # print(module_id, measure) # Sanity check
            
            # If there is temperature and humidity data available
            try:
                types = measure["type"]
                res = measure["res"]  # The time and values
                timestamp = list(res.keys())[0]
                measurements = res[timestamp]
            except: # The case if no records or station is malfunctioning
                types = []
                res = []
            
            if not len(res) == 1:  # Something is wrong
                res = {np.nan: [np.nan] * len(types)}
            
            # If there is rain data available
            if list(measure.keys())[0] == 'rain_60min':
                try:
                    types = ['rain_60min', 'rain_24h', 'rain_live']
                    res = measure[types[0]]
                    timestamp = measure['rain_timeutc']
                    measurements = [measure[types[0]], measure[types[1]], measure[types[2]]]
                except:  # The case if no records or station is malfunctioning
                    types = []
                    res = []
                    
            # Update the dictionary with data
            measdict.update(zip(types, measurements))
            timedict = {"{}_utc_timestamp".format(t): int(timestamp) for t in types}
            measdict.update(timedict)
            
        # Add measurements to station dictionary
        for key, val in measdict.items():
            try:
                station_dict[key].append(val)
            except BaseException:
                station_dict[key] = [val]
                
        # Fill the remaining values for the stations,
        # which did not have a or any type of data.
        # This is simply adding "empty" values to the data
        # to account for the data series not having the same
        # sizes due to missing data.
        length = max([len(x) for x in station_dict.values()])
        for key, val in station_dict.items():
            while len(val) < length:
                val.append(np.nan)
            
    # Create data frame
    df = pd.DataFrame(station_dict)
    # Convert times to datetime?
    if convert_to_datetime:
        for col in df.columns:
            if col.endswith("_timestamp"):
                df[col] = pd.to_datetime(df[col], unit="s", utc=True)
        
    return df