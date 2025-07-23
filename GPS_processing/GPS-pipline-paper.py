import os
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

pd.set_option("mode.copy_on_write", True)
Image.MAX_IMAGE_PIXELS = None

def pos_to_dataframe(file):
    """Converts .pos data to dataframe with timestamp, latitude, longitude and height"""
    df = pd.read_table(file, sep="\s+", header=9, parse_dates={"Timestamp": [0, 1]})
    df = df.rename(
        columns={
            "Timestamp": "time",
            "longitude(deg)": "longitude",
            "latitude(deg)": "latitude",
        }
    )
    return df

def find_folders_with_prefixes(root_folder, prefixes):
    """Finds folders with given Exploration prefixes in the the given root folder. 
        Parameters:
            root_folder (string): Root directory
            prefixes (list): Name of Exploration folders to be included
        Returns:
            matched_files (dict): Exploration prefixes as keys and df with gps data as value 
    """
    matched_files = {}
    
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for dirname in dirnames:
            if any(dirname.startswith(prefix) for prefix in prefixes):

                prefix = next(p for p in prefixes if dirname.startswith(p))

                folder_path = os.path.join(dirpath, dirname)
                
                # Search for .pos '_events' files in this directory
                for filename in os.listdir(folder_path):
                    if filename.endswith('.pos') and '_events' not in filename:
                        matched_files[prefix] = pos_to_dataframe(os.path.join(folder_path, filename))
                        break  # Stop after finding the first matching file in this directory
    return matched_files

# Function to slice DataFrames based on slicing points
def slice_dataframes(dataframes, slicing_df):
    """Slices the dataframes on indices given by the slicing_df
        dataframe: dictionary of GPS-data dfs
        slicing_df: dataframe including the Start/End points of calibration
        returns sliced_dataframes: dictionary of sliced dfs"""
    sliced_dataframes = {}

    for _, row in slicing_df.iterrows():
        prefix = row['session']
        start_index = row['C1_end']
        end_index = row['C2_start']
        
        if prefix in dataframes:
            # Slice the DataFrame
            sliced_dataframes[prefix] = dataframes[prefix].iloc[start_index:end_index]
    
    return sliced_dataframes

# speed calculation
def calculate_speed(df):
    """Iterates over the DataFrame to first calculate the distance and time between consecutive data points. 
        Using that information, the speed in km/h is calculated. 
        
        Parameters: df: Dataframe with GPS data
        Returns: df: Dataframe with GPS data including a speed_km_h column """

    #print(df)
    df.loc[:,'time'] = pd.to_datetime(df['time'])
    df['speed_km_h'] = 0.0
    df['time_diff_seconds'] = 0.0
    #df['distance'] = 0.0
    print(len(df)-1)
    for i in range(1,len(df)-1):        
        #prev_coords = (df.iloc[i - 1]['latitude'], df.iloc[i - 1]['longitude'])
        #curr_coords = (df.iloc[i]['latitude'], df.iloc[i]['longitude'])
        
        prev_coords = (df.iloc[i - 1, 1], df.iloc[i - 1, 2])
        curr_coords = (df.iloc[i, 1], df.iloc[i, 2])
        #print(prev_coords, curr_coords)
        
        #calculate distance (in km)
        distance = geodesic(prev_coords, curr_coords).km
        
        # Calculate the time difference (in seconds)
        time_diff_seconds = (df.iloc[i]['time'] - df.iloc[i - 1]['time']).total_seconds() 

        time_diff = time_diff_seconds/ 3600

        #Calculate speed (km/h) (making sure that no error occurse because division by 0)
        speed = distance / time_diff if time_diff > 0 else 0 

        df.iloc[i, 14] = speed
        df.iloc[i, 15] = time_diff_seconds

    return df

#check with time threshold
def flag_consecutive_outliers(df, seconds_threshold=30): 
    """
    Checks for consecutive outliers which would not pass the set 
    thresholds regarding speed, Q value, number of satellites.
    
    If there are parts of the data with consecutive outlier, adding up
    to 30 seconds of recording, those parts are flagged.
    
    """
    df.reset_index(drop=True, inplace=True)
    count = 0
    start_time = df["time"].iloc[0]
    flag = False
    flagged_indices = []
    patch_id = 0
    patch_ids = []

    for i in range(len(df)):
        if df['Q'][i] == 5 or df["ns"][i] < 5 or df["speed_km_h"][i] > 6:
            count += 1
            if not flag:
                start_time = df["time"].iloc[i]
                flag = True
                #print(start_time)
                start_index = i - count + 1
            if (df["time"].iloc[i] - start_time).total_seconds() >= seconds_threshold:
                flagged_indices.extend(range(start_index, i + 1))
                patch_ids.extend([patch_id] * (i - start_index + 1))
                patch_id += 1 #does not work right now
                #print(count)
        else:
            count = 0
            flag = False
    #print(flagged_indices)

    df['flagged'] = False
    df.loc[flagged_indices, 'flagged'] = True
    df.loc[flagged_indices, 'patch_id'] = patch_ids

    return df

# cleaning function using the flagged df
def flag_rows(row):
    strict_reasons = []

    if row['Q'] == 5:  
        strict_reasons.append('Q_value')
    if row['speed_km_h'] > 6:
        strict_reasons.append('speed')
    if row['ns'] < 5:
        strict_reasons.append('num_satellites')

    if row['flagged']:
        relaxed_reasons = []
        if row['Q'] == 5:  
            relaxed_reasons.append('relaxed Q_value')
        if row['speed_km_h'] > 7:
            relaxed_reasons.append('relaxed speed')
        if row['ns'] < 4:
            relaxed_reasons.append('relaxed num_satellites')    
        
        if relaxed_reasons:
            combined_reasons = strict_reasons + relaxed_reasons
            return ', '.join(combined_reasons)
        else:
            complete_str = strict_reasons + ['relaxed passed']
            return ', '.join(complete_str)
    
    return ', '.join(strict_reasons) if strict_reasons else 'passed'
    



def flag_gps_data(df):

    df['fail_reasons'] = df.apply(flag_rows, axis=1)

    removed_satellites_strict = df[df['fail_reasons'].str.contains('num_satellites', na=False)].shape[0]
    removed_q_value_strict = df[df['fail_reasons'].str.contains('Q_value', na=False)].shape[0]
    removed_speed_strict = df[df['fail_reasons'].str.contains('speed', na=False)].shape[0]
    entries_with_relaxed_criteria = df[df['fail_reasons'].str.contains('relaxed passed', na=False)].shape[0]
    remaining_entries = df[df['fail_reasons'].str.contains('passed', na=False)].shape[0]

    #get number and reason of removed entries
    report = {
        "total_entries": len(df),
        "removed_satellites_strict": removed_satellites_strict,
        "removed_q_value_strict": removed_q_value_strict,
        "removed_speed_strict": removed_speed_strict,
        "entries_with_relaxed_criteria": entries_with_relaxed_criteria,
        "remaining_entries": remaining_entries,
    }

    print("Report:", report)

    return df, report

def interpolation(cleaned_df):
    """Removes latitude and longitude values from failed rows and interpoates these. Sets speed values from failed rows to -1.
        Does not change the first row of each dataframe."""

    #set failed values to NaN
    not_passed_mask = ~cleaned_df['fail_reasons'].str.contains('passed', na=False)
    not_passed_mask.iloc[0] = False

    #get copy of df an set entries in to Nan
    interp_df = cleaned_df.copy()
    interp_df.loc[not_passed_mask, ['latitude', 'longitude']] = np.nan
    interp_df.loc[not_passed_mask, 'speed_km_h'] = -1

    #interpolate
    interp_df['latitude'] = interp_df['latitude'].interpolate(method='linear')
    interp_df['longitude'] = interp_df['longitude'].interpolate(method='linear')
    
    return interp_df

if __name__ == "__main__":
    current_path = os.getcwd()
    print(current_path)
    #path to GPS files
    GPS_path = '../raw_data/GPS_UTC/'
    included_Expl = ['Expl_1_ET_1', 'Expl_1_ET_2', 'Expl_1_ET_3', 'Expl_2_ET_1', 'Expl_2_ET_2', 'Expl_3_ET_1',
                     'Expl_3_ET_2', 'Expl_3_ET_3', 'Expl_4_ET_1', 'Expl_4_ET_2', 'Expl_5_ET_1', 'Expl_5_ET_2']


    #search for wanted exploration/session in GPS folder+subfolders
    GPS_folder = os.listdir(GPS_path)
    print(GPS_folder)

    GPS_dfs = find_folders_with_prefixes(GPS_path, included_Expl)

    #for synced GPS.csv files
    #folder_path = "../synchro-ET-GPS/new_slicing_synced-GPS"
    #
    #GPS_dfs = {}
    #
    ## Iterate over all files in the folder
    #for filename in os.listdir(folder_path):
    #    # Remove the file extension to get the dictionary key
    #    file_key = filename.split("_", 2)[-1].rsplit(".", 1)[0]
    #    print(file_key)
    #
    #    # Read the CSV file into a DataFrame and store it in the dictionary
    #    GPS_dfs[file_key] = pd.read_csv(os.path.join(folder_path, filename), index_col=0)


    #path to slicing files
    slicing_path = 'new_gps_slicing.csv'
    slicing_df = pd.read_csv(slicing_path)

    # Apply slicing
    sliced_dfs = slice_dataframes(GPS_dfs, slicing_df)

    speed_dfs = {}
    # Apply the function to each DataFrame in the dictionary
    for key in sliced_dfs.keys():
        speed_dfs[key] = calculate_speed(sliced_dfs[key])
        print(key)

    flagged_dfs = {}
    for key in speed_dfs.keys():
        flagged_dfs[key] = flag_consecutive_outliers(speed_dfs[key])
        print(key)

    cleaned_dfs = {}
    reports = {}
    for key in flagged_dfs.keys():
        cleaned_dfs[key], reports[key] = flag_gps_data(flagged_dfs[key])
        print(key)

    save = False

    interpol_dfs = {}
    for key in cleaned_dfs.keys():
        interpol_dfs[key] = interpolation(cleaned_dfs[key])
        print(key)
        if save:
            interpol_dfs[key].to_csv("new-slicing/cleaned-interpol-%s.csv" %key)