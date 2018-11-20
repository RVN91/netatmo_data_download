# -*- coding: utf-8 -*-
"""
Author: Rasmus Nielsen
Instituion: SMHI, Sweden
Date: 29-08-2018

Downloads and prepare the data from Netatmo's weather stations within a
bounding box giving by a set of latitudes and longitudes.
"""

import requests
import pandas as pd
from datetime import datetime
import time
from utils import convert_netatmo_getpublicdata_response_to_dataframe

# Create URL for Netatmo API endpoint
url = "https://api.netatmo.com/oauth2/token"
 
# Netatmo connect developer credentials
credentials = {
     "grant_type": "password",
     "password":"YOURPASSWORD",
     "username":"YOUREMAIL",
     "client_id":    "YOURCLIENTID",
     "client_secret":"YOURLCIENTSECRET",
     "scope": "read_station"
}

# Get access token 
resp = requests.post(url, data=credentials)
if resp.status_code == 200:
    token = resp.json()
    token['expiry'] = int(time.time()) + token['expires_in']
print(token)
  
# Set bounding box for station selection
region = {
     "lat_ne" : "56.2330",
     "lat_sw" : "56.0843",
     "lon_ne" : "10.3324",
     "lon_sw" : "10.0344",
}
  
# Get public data
resp = requests.post("https://api.netatmo.com/api/getpublicdata?access_token=" + 
                     token["access_token"] +"&lat_ne=" +  region["lat_ne"] + 
                     "&lon_ne=" + region["lon_ne"] + "&lat_sw=" +
                     region["lat_sw"] + "&lon_sw=" + region["lon_sw"])

# Read data as json
data_output = resp.json()

# Format to a data frame 
df = convert_netatmo_getpublicdata_response_to_dataframe(data_output, False)
    
# Save data to disk
the_time = datetime.now()
the_time = the_time.replace(microsecond=0)
df.to_csv(str(the_time) + '.csv')