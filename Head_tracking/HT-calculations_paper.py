import os
import bisect
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("mode.copy_on_write", True)

#calculate cardinal degrees (only needed once)
#df = pd.read_excel("nort_calc_median.ods", engine="odf")
#calculate cardinal_degrees from compass/survey file picture value 
#df['cardinal_degr_pic'] = 360-df['value_picture']
#df.to_csv('compass_data.csv')

def get_timestamp_last_value(df, is_median=False):
    #get synced IMU dfs
    IMU_path = '../GPS-ET-Synchro/new_slicing_synced-IMU'

    files = os.listdir(IMU_path)

    if is_median:
        df['ET_median'] = None
        df['n_values_median'] = None
        df['mad'] = None
    else: 
        df['ET_single'] = None


    df_first_frame_compass = pd.read_excel("ET-compass-frames.ods",engine="odf", index_col=0)
    print(df_first_frame_compass)

    for index, row in df.iterrows():

        id_value = row['Id']
        print(id_value)
        # split Id to folder name  
        beg_end = id_value.rsplit('_', 1)[1]
        folder_name = id_value.rsplit('_', 1)[0]

        matched_file = next((file for file in files if folder_name in file), None)

        

        if matched_file:
            file_path = os.path.join(IMU_path, matched_file)
            print(id_value, file_path)
            #get last value IMU
            imu_df = pd.read_csv(file_path)
            #print(imu_df)
            imu_df['timestamp [ns]'] = pd.to_datetime(imu_df['timestamp [ns]'])
            last_imu_timestamp = imu_df["timestamp [ns]"].iloc[-1]
            df.loc[index, 'last_imu_timestamp'] = pd.to_datetime(last_imu_timestamp)
            

        matching_folders_frames = [folder for folder in all_folders if folder.startswith(folder_name)]
        if matching_folders_frames:
            matching_folder_frames = matching_folders_frames[0]
            print(matching_folder_frames)
            folder_path = os.path.join(parent_folder, matching_folder_frames)
            video_file = os.path.join(folder_path, "world_timestamps.csv")
            print(video_file)
            df_video = pd.read_csv(video_file)
            last_video_timestamp = df_video["timestamp [ns]"].iloc[-1]
            last_video_timestamp = pd.to_datetime(last_video_timestamp)

            frame_nr = df_first_frame_compass.loc[folder_name,'frame ET on compass']
            print(frame_nr)
            et_on_compass_time = pd.to_datetime(df_video["timestamp [ns]"].iloc[frame_nr])
            df.loc[index, 'time_ET_on_compass'] = et_on_compass_time

            df.loc[index, 'last_video_timestamp'] = last_video_timestamp
        
            df['IMU data (end)'] = df['last_imu_timestamp'] > df['time_ET_on_compass']

            if beg_end == 'beg':
                    if is_median == True:
                        column_values = imu_df["yaw [deg]"].head(n_values_imu)
                        median_value = column_values.median()
                        mad_value = calculate_mad(column_values, median_value)
                        df.loc[index, 'ET_median'] = median_value
                        df.loc[index, 'mad'] = mad_value
                    else:
                        column_values = imu_df["yaw [deg]"].iloc[0]
                        df.loc[index, 'ET_single'] = column_values

            elif beg_end == 'end': 
                if df.loc[index, "IMU data (end)"]:
                    et_on_compass_index = bisect.bisect_right(imu_df["timestamp [ns]"], et_on_compass_time)

                    last_index_median = et_on_compass_index + n_values_imu
                    
                    if is_median == True: 
                        column_values = imu_df['yaw [deg]'][et_on_compass_index:last_index_median]
                        print("These are the median values:", column_values.shape)
                        df.loc[index, 'n_values_median'] = column_values.shape[0]
                        median_value = column_values.median()
                        mad_value = calculate_mad(column_values, median_value)
                        df.loc[index, 'ET_median'] = median_value
                        df.loc[index, 'mad'] = mad_value
                    else:
                        #column_values = imu_df['yaw [deg]'][et_on_compass_index-1]
                        column_values = imu_df['yaw [deg]'][et_on_compass_index]
                        #df['ET_single'][index] = column_values
                        df.loc[index, 'ET_single',] = column_values
            #print(column_values)
            #column_values = None
    print(df)
    df.to_csv('compass_last_timestamps.csv')
    return df 

# Calculate difference
def calculate_degr_error(degr_1, degr_2):
    if degr_1 == None or degr_2 == None:
        pass
    dif = degr_1 - degr_2 % 360
    if (dif > 180) or (dif < -180):
        dif = 360 - dif
    return dif 

def calculate_mad(series, median_value):
    mad = (series - median_value).abs().median()
    return mad

if __name__ == "__main__":
    df = pd.read_csv("compass_data.csv", index_col=False)

    df['last_imu_timestamp'] = None
    df['last_video_timestamp'] = None
    df['time_ET_on_compass'] = None

    # List all folders in the parent folder
    parent_folder = "../raw_data/ET"

    all_folders = os.listdir(parent_folder)

    n_values_imu = 55

    df = get_timestamp_last_value(df, is_median=True)

    df['ET_median_conv'] = df['ET_median'].apply(lambda x: (-x % 360) if x is not None else None)

    df['diff_median_abs'] = df.apply(lambda row: calculate_degr_error(row['cardinal_degr_pic'], row['ET_median_conv']), axis=1)

    ET_median_median = df.loc[:, 'diff_median_abs'].median()

    print("Median error median: {}".format(ET_median_median))

    df.to_csv("error_with_correct_IMU_mad.csv")