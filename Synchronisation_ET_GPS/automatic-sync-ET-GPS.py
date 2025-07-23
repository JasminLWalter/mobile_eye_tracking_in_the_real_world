# - Input: IMU-path, GPS-path, CSV with slicing points and time difference between IMU and ET start
# - find and reads in GPS + IMU data files (within given paths + file names) as pandas dataframes
# - synchronises IMU files with ET timestamps (Solves problem with IMU data) on given Time differences
# - synchronises GPS to IMU through given startpoints of calibration
# - saves synced GPS and IMU dfs as csv
# - plots synced data streams with special emphasis on calibrations

import os 
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("mode.copy_on_write", True)

# read-in (cleaned) GPS
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


#converting .pos file to dataframe
def pos_to_dataframe(file):
    """ Converts .pos data to dataframe with timestamp, latitude, longitude and height """
    df = pd.read_table(file, sep="\s+", header=9, parse_dates={"Timestamp": [0, 1]})
    df = df.rename(
        columns={
            "Timestamp": "time",
            "longitude(deg)": "longitude",
            "latitude(deg)": "latitude",
            # "height(m)": "altitude",
            # "Q": "Q",
            # "ns": "ns",
            # "age(s)": "age",
            # "ratio": "ratio",
        }
    )
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S.%f') #
    return df


# add time diff to GPS
def sync_GPS(session, GPS_df, time_diff_df):
    if session == 'Expl_3_ET_3' or session == 'Expl_5_ET_2':
        id = str(session + "_C2")
        time_diff = time_diff_df.loc[id]['time_diff_start']
        GPS_df['synced_time'] = GPS_df['time'] - time_diff
    else:
        id = str(session + "_C1")
        time_diff = time_diff_df.loc[id]['time_diff_start']
        # make new coloumn GPS (time + time diff)
        GPS_df['synced_time'] = GPS_df['time'] - time_diff

    return GPS_df

def save_synced_dfs(dict_dfs, type):
    for key in dict_dfs.keys():
        print(key)
        print("new_slicing_synced-%s/synced_%s_%s.csv" %(type, type, key))
        dict_dfs[key].to_csv("new_slicing_synced-%s/synced_%s_%s.csv" %(type, type, key))

def find_imu_files(root_folder, prefixes):
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
                    if filename == "imu.csv":
                        print(os.path.join(folder_path, filename))
                        matched_files[prefix] = pd.read_csv(os.path.join(folder_path, filename))
                        break  # Stop after finding the first matching file in this directory
    return matched_files

def sync_imu(session, imu_df, df_timediff_et_imu):
    # check if Time Difference start coloum is bigger 10 sec
        #if bigger add time diff to imu 
    imu_df['timestamp [ns]'] = pd.to_datetime(imu_df['timestamp [ns]'], unit='ns')
    if df_timediff_et_imu.loc[session, 'Time Difference start'] > pd.Timedelta(10, "s"):
        time_diff = df_timediff_et_imu.loc[session, 'Time Difference start']
        imu_df['timestamp [ns]'] = imu_df['timestamp [ns]'] - time_diff
    
    return imu_df


def plot_sync_GPS_IMU(session, GPS_df, IMU_df, slicing_points):
    # Determine the range of imu
    min_imu = IMU_df['yaw [deg]'].min()
    max_imu = IMU_df['yaw [deg]'].max()

    # Normalize lat, long to the IMU range
    GPS_df['latitude_nor'] =  (GPS_df['latitude'] - GPS_df['latitude'].min()) /  (GPS_df['latitude'].max() - GPS_df['latitude'].min()) * (max_imu - min_imu) + min_imu
    GPS_df['longitude_nor'] =  (GPS_df['longitude'] - GPS_df['longitude'].min()) /  (GPS_df['longitude'].max() - GPS_df['longitude'].min()) * (max_imu - min_imu) + min_imu
    
    #plotting
    fig, axs = plt.subplots(nrows=3, ncols=1)

    #plot yaw with long, lat normalized
    axs[0].plot(IMU_df['timestamp [ns]'], IMU_df['yaw [deg]'], label='yaw')
    axs[0].plot(GPS_df['synced_time'], GPS_df['latitude_nor'], label='lat_norm')
    axs[0].plot(GPS_df['synced_time'], GPS_df['longitude_nor'], label='long_norm')
    axs[0].title.set_text('yaw, lat + long (normalized)')
    #for x in i_points_df['time_diff']:
        #axs[0].axvline(x=x, color='b', linestyle='--', linewidth=1)
    #for point in GPS_slicing_points:
        #axs[0].axvline(x=merged_df['time_diff'].iloc[point], color='r', linestyle='--', label='GPS')


    #plot C1
    #--> get slicing point ET + GPS
    row_C1 = session + '_C1'
    print(row_C1)
    C1_ET_slicing = [slicing_points.loc[row_C1]['ET_start_time'], slicing_points.loc[row_C1]['ET_end_time']]
    C1_GPS_slicing = [slicing_points.loc[row_C1]['GPS_start'], slicing_points.loc[row_C1]['GPS_end']]

    C1_IMU = IMU_df[(IMU_df["timestamp [ns]"] >= pd.to_datetime(C1_ET_slicing[0], format='%Y-%m-%d %H:%M:%S.%f')) & (IMU_df["timestamp [ns]"] <= pd.to_datetime(C1_ET_slicing[1], format='%Y-%m-%d %H:%M:%S.%f'))]
    C1_GPS = GPS_df.iloc[C1_GPS_slicing[0]:C1_GPS_slicing[1]]

    ## Determine the range of imu
    C1_end_min_imu = C1_IMU['yaw [deg]'].min()
    C1_end_max_imu = C1_IMU['yaw [deg]'].max()
    #
    ## Normalize lat, long to the IMU range
    C1_GPS['latitude_nor'] = (C1_GPS['latitude'] - C1_GPS['latitude'].min()) / (C1_GPS['latitude'].max() - C1_GPS['latitude'].min()) * (C1_end_max_imu - C1_end_min_imu) + C1_end_min_imu
    C1_GPS['longitude_nor'] = (C1_GPS['longitude'] - C1_GPS['longitude'].min()) / (C1_GPS['longitude'].max() - C1_GPS['longitude'].min()) * (C1_end_max_imu - C1_end_min_imu) + C1_end_min_imu
    
    axs[1].plot(C1_IMU['timestamp [ns]'], C1_IMU['yaw [deg]'], label='yaw')
    axs[1].plot(C1_GPS['synced_time'], C1_GPS['latitude_nor'], label='lat_norm')
    axs[1].plot(C1_GPS['synced_time'], C1_GPS['longitude_nor'], label='long_norm')
    axs[1].title.set_text('%s C1' %key)

    ## plot C2_df
    row_C2 = session + '_C2'
    print(row_C2)
    C2_ET_slicing = [slicing_points.loc[row_C2]['ET_start_time'], slicing_points.loc[row_C2]['ET_end_time']]
    C2_GPS_slicing = [slicing_points.loc[row_C2]['GPS_start'], slicing_points.loc[row_C2]['GPS_end']]

    C2_IMU = IMU_df[(IMU_df["timestamp [ns]"] >= pd.to_datetime(C2_ET_slicing[0], format='%Y-%m-%d %H:%M:%S.%f')) & (IMU_df["timestamp [ns]"] <= pd.to_datetime(C2_ET_slicing[1], format='%Y-%m-%d %H:%M:%S.%f'))]
    C2_GPS = GPS_df.iloc[C2_GPS_slicing[0]:C2_GPS_slicing[1]]

    ## Determine the range of imu
    C2_end_min_imu = C2_IMU['yaw [deg]'].min()
    C2_end_max_imu = C2_IMU['yaw [deg]'].max()
    #
    ## Normalize lat, long to the IMU range
    C2_GPS['latitude_nor'] = (C2_GPS['latitude'] - C2_GPS['latitude'].min()) / (C2_GPS['latitude'].max() - C2_GPS['latitude'].min()) * (C2_end_max_imu - C2_end_min_imu) + C2_end_min_imu
    C2_GPS['longitude_nor'] = (C2_GPS['longitude'] - C2_GPS['longitude'].min()) / (C2_GPS['longitude'].max() - C2_GPS['longitude'].min()) * (C2_end_max_imu - C2_end_min_imu) + C2_end_min_imu
    
    axs[2].plot(C2_IMU['timestamp [ns]'], C2_IMU['yaw [deg]'], label='yaw')
    axs[2].plot(C2_GPS['synced_time'], C2_GPS['latitude_nor'], label='lat_norm')
    axs[2].plot(C2_GPS['synced_time'], C2_GPS['longitude_nor'], label='long_norm')
    axs[2].title.set_text('%s C2' %key)

    plt.tight_layout()
    plt.show()
    


if __name__ == "__main__":
    #load all GPS + make df dict with expl_session as key
    #path to GPS files
    GPS_path = '../raw_data/GPS_UTC/'
    included_Expl = ['Expl_2_ET_3']
    #['Expl_1_ET_1', 'Expl_1_ET_2', 'Expl_1_ET_3', 'Expl_2_ET_1', 'Expl_2_ET_2', 'Expl_3_ET_1',
                #'Expl_3_ET_2', 'Expl_3_ET_3', 'Expl_4_ET_1', 'Expl_4_ET_2', 'Expl_5_ET_1', 'Expl_5_ET_2']
    
    #search for wanted exploration/session in GPS folder+subfolders
    GPS_dfs = find_folders_with_prefixes(GPS_path, included_Expl)

    #load time diff file, reindex and reformat time coloumn 
    time_diff_file = 'new_slicing-GPS-ET-timediff.csv'
    time_diff_df = pd.read_csv(time_diff_file)
    #time_diff_df.drop('Unnamed: 0', axis=1, inplace=True)
    time_diff_df['time_diff_start'] = pd.to_timedelta(time_diff_df['time_diff_start']) 
    time_diff_df.set_index('session', inplace=True)
    
    synced_GPS_dfs = {}
    for key in GPS_dfs.keys():
        synced_GPS_dfs[key] = sync_GPS(session=key, GPS_df=GPS_dfs[key], time_diff_df=time_diff_df)

    #save synced GPS files
    #save_synced_dfs(synced_GPS_dfs, 'GPS')

    #slicing_file = 'slicing_gps_imu.csv'
    slicing_file = 'new_slicing-GPS-ET-timediff.csv'
    slicing_df = pd.read_csv(slicing_file, index_col="session")

    #read in time-diff IMU and ET
    time_diff_ET_IMU = pd.read_csv('new_ET_IMU_time_differences.csv', index_col='Folder')
    time_diff_ET_IMU['Time Difference start'] = pd.to_timedelta(time_diff_ET_IMU['Time Difference start'])

    #load all imu files
    imu_path = "../data/ET/"
    imu_dfs = find_imu_files(imu_path, included_Expl)
    #print(imu_dfs.keys())

    #sync imu files when needed
    synced_imus = {}
    for key in imu_dfs.keys():
        synced_imus[key] = sync_imu(session=key, imu_df=imu_dfs[key], df_timediff_et_imu=time_diff_ET_IMU)

    save_synced_dfs(synced_imus, 'IMU')

    for key in synced_GPS_dfs.keys():
        plot_sync_GPS_IMU(session=key, GPS_df=synced_GPS_dfs[key], IMU_df=synced_imus[key], slicing_points=slicing_df)