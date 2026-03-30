# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 17:38:00 2026

@author: User
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from dm4bem import read_epw, sol_rad_tilt_surf

filename = 'FRA_Lyon.074810_IWEC.epw'

[data, meta] = read_epw(filename, coerce_year=None)
data

# select columns of interest
weather_data = data[["temp_air", "dir_n_rad", "dif_h_rad"]]


# replace year with 2000 in the index 
weather_data.index = weather_data.index.map(
    lambda t: t.replace(year=2000))

# Define months and walls
months = {
    "January": ("2000-01-01 00:00", "2000-01-30 23:00"),
    "July": ("2000-07-01 00:00", "2000-07-30 23:00")
}

# Azimuths for 4 walls (assuming vertical walls, slope=90°)
# 0° South, 90° West, 180° North, 270° East
wall_azimuths = {
    "South": 0,
    "West": 90,
    "North": 180,
    "East": 270
}

# Store results
results = []

# Loop over months and walls
for month_name, (start_date, end_date) in months.items():
    # Filter weather data for this month
    month_data = weather_data.loc[start_date:end_date]
    
    for wall_name, azimuth in wall_azimuths.items():
        surface_orientation = {
            "slope": 90,       # vertical wall
            "azimuth": azimuth,
            "latitude": 45.8   # Lyon latitude
        }
        
        rad_surf = sol_rad_tilt_surf(month_data, surface_orientation, albedo=0.2)
        col_mean = rad_surf.mean()
        sum_of_means = col_mean.sum()
        
        # Append result to list
        results.append({
            "Month": month_name,
            "Wall": wall_name,
            "Direct_mean": col_mean["direct"],
            "Diffuse_mean": col_mean["diffuse"],
            "Reflected_mean": col_mean["reflected"],
            "Total_mean": sum_of_means
        })

# Add roof (slope=0) for January and July
for month_name, (start_date, end_date) in months.items():
    month_data = weather_data.loc[start_date:end_date]
    
    surface_orientation = {
        "slope": 0,        # horizontal roof
        "azimuth": 0,      # azimuth doesn't matter for horizontal surface
        "latitude": 45.8
    }
    
    rad_surf = sol_rad_tilt_surf(month_data, surface_orientation, albedo=0.2)
    col_mean = rad_surf.mean()
    sum_of_means = col_mean.sum()
    
    # Append roof result
    results.append({
        "Month": month_name,
        "Wall": "Roof",
        "Direct_mean": col_mean["direct"],
        "Diffuse_mean": col_mean["diffuse"],
        "Reflected_mean": col_mean["reflected"],
        "Total_mean": sum_of_means
    })

# Convert results to a DataFrame for easy display
results_df = pd.DataFrame(results)
# Set pandas display format to 2 decimals
pd.options.display.float_format = '{:.2f}'.format

# Print the updated DataFrame including roof
print(results_df)

# Mean air temperature for each selected month
for month_name, (start_date, end_date) in months.items():
    month_data = weather_data.loc[start_date:end_date]
    mean_temp = month_data['temp_air'].mean()
    
    print(f"The mean air temperature in {month_name} is {mean_temp:.2f} °C")
