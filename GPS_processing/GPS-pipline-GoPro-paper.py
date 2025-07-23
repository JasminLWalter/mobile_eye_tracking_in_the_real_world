import os
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

pd.set_option("mode.copy_on_write", True)
Image.MAX_IMAGE_PIXELS = None

#load data
GPS_df_1 = pd.read_csv("../raw_data/GoPro_GPS-Expl2_ET3/Expl_2_ET_3_Part_1_gps_100Hz.csv")
GPS_df_2 = pd.read_csv("../raw_data/GoPro_GPS-Expl2_ET3/Expl_2_ET_3_Part_2_gps_100Hz.csv")

GPS_df = pd.concat([GPS_df_1, GPS_df_2], ignore_index=True)
print(GPS_df)

GPS_df['date'] = pd.to_datetime(GPS_df['date'])


# Define the target date, which is date[0] plus 3 minutes and 9 seconds
target_date = GPS_df['date'][0] + pd.Timedelta(minutes=3, seconds=9)

# Calculate the difference between the target date and each date in the DataFrame
GPS_df['difference'] = abs(GPS_df['date'] - target_date)

# Find the index of the minimum difference
calIndex_start = GPS_df['difference'].idxmin()


last_date = GPS_df['date'].iloc[-1]
#target_date2 = last_date - pd.Timedelta(minutes=1, seconds=38) # 1:38
target_date2 = last_date - pd.Timedelta(seconds=40)

# Calculate the difference between the target date and each date in the DataFrame
GPS_df['difference'] = abs(GPS_df['date'] - target_date2)

# Find the index of the minimum difference
calIndex_end = GPS_df['difference'].idxmin()


# # Print the results
print(f"Target date: {target_date}")
print(f"Target date: {target_date2}")
print(f"Closest start calibration index: {calIndex_start}")
print(f"Closest end calibration index: {calIndex_end}")
# print(f"Closest date: {df['date'][closest_index]}")

# am Anfang 3:13 abziehen (ende start calibration)
# am Ende 1:35 min abziehen (beginn end calibration)

GPS_df = GPS_df[calIndex_start:calIndex_end]

#clean df

def flag_rows(row, precision_threshold):
    reason = []
    if row['speed_km_h'] > 6:
        reason.append('speed')
    if row['precision'] > precision_threshold:
        reason.append('precision')
    return ', '.join(reason) if reason else 'passed'

def flag_gps_data(df):
    #convert speed to m/s
    GPS_df['speed_km_h'] = GPS_df['GPS (2D speed) [m/s]'] * 3.6

    #calculate precision threshold (mean + (std*3))
    precision_threshold = GPS_df['precision'].mean() + (GPS_df['precision'].std() * 3)

    df['fail_reasons'] = df.apply(flag_rows, precision_threshold=precision_threshold, axis=1)

    removed_speed = df[df['fail_reasons'].str.contains('speed', na=False)].shape[0]
    removed_precision = df[df['fail_reasons'].str.contains('precision', na=False)].shape[0]

    report = {"removed_speed": removed_speed, "removed_precision": removed_precision}

    return df, report

df_cleaned, report = flag_gps_data(GPS_df)
#print(df_cleaned)
#df_cleaned.to_csv('cleaned_GPS_Expl_2_ET_3_GoPro.csv')

#interpolation
def interpolation(cleaned_df):
    """Removes latitude and longitude values from failed rows and interpoates these. Sets speed values from failed rows to -1.
        Does not change the first row of each dataframe."""

    #set failed values to NaN
    not_passed_mask = ~cleaned_df['fail_reasons'].str.contains('passed', na=False)
    not_passed_mask.iloc[0] = False
    print(not_passed_mask)

    #get copy of df and set entries in to Nan
    interp_df = cleaned_df.copy()
    interp_df.loc[not_passed_mask, ['GPS (Lat.) [deg]', 'GPS (Long.) [deg]']] = np.nan
    interp_df.loc[not_passed_mask, 'GPS (2D speed) [m/s]'] = -1

    #interpolate
    interp_df['GPS (Lat.) [deg]'] = interp_df['GPS (Lat.) [deg]'].interpolate(method='linear')
    interp_df['GPS (Long.) [deg]'] = interp_df['GPS (Long.) [deg]'].interpolate(method='linear')
    
    return interp_df

interpol_df = interpolation(df_cleaned)

#save df to csv in right format 'latitude', 'longitude'
def save_formatted(cleaned_df):
    cleaned_df.rename(columns={'date': 'time', 'GPS (Lat.) [deg]': 'latitude', 'GPS (Long.) [deg]':'longitude'}, inplace=True)
    cleaned_df.to_csv('sliced-cleaned-interpol-Expl_2_ET_3-GoPro.csv')

save_formatted(interpol_df)