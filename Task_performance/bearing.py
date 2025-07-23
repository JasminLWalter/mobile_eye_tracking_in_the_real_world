import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Formula: 	θ = atan2( sin Δλ ⋅ cos φ2 , cos φ1 ⋅ sin φ2 − sin φ1 ⋅ cos φ2 ⋅ cos Δλ )
#where 	φ1,λ1 is the start point, φ2,λ2 the end point (Δλ is the difference in longitude) (in radians)

ordered = ['Target 1', 'Target 2', 'Target 3', 'Target 4', 'Target 5', 'Target 6', 'Target 7', 'Target 8', 'Starting_point']

def calculate_bearing_np(latitude_start, longitude_start, latitude_end, longitude_end):
    longitude_start = math.radians(longitude_start)
    latitude_start = math.radians(latitude_start)

    longitude_end = math.radians(longitude_end)
    latitude_end = math.radians(latitude_end)

    dL = longitude_end - longitude_start
    X = np.cos(latitude_end)* np.sin(dL)
    Y = np.cos(latitude_start)*np.sin(latitude_end) - np.sin(latitude_start)*np.cos(latitude_end)*np.cos(dL)

    bearing = np.arctan2(X, Y)

    return (np.degrees(bearing)+360)%360

def get_start_target_angle():
    task_building_coord = pd.read_excel("../taskB-coords.ods", engine="odf", index_col=0, header=0)

    coords_at_loc = pd.read_excel("../postion-per-location.ods", engine="odf", index_col=0, header=0)

    # get bearing between each start point and every target building
    start_target_bearing_df = pd.DataFrame()

    for start_index, start_row in coords_at_loc.iterrows():
        bearings = []

        for end_index, end_row in task_building_coord.iterrows():
            start_lon, start_lat = start_row['longitude'], start_row['latitude']
            end_lon, end_lat = end_row['longitude'], end_row['latitude']

            bearing = calculate_bearing_np(start_lat,start_lon,end_lat,end_lon)

            bearings.append(bearing)

        start_target_bearing_df[start_index] = bearings

    start_target_bearing_df.set_index(task_building_coord.index, inplace=True)

    # Set new order of coloumns
    ordered = ['Target 1', 'Target 2', 'Target 3', 'Target 4', 'Target 5', 'Target 6', 'Target 7', 'Target 8', 'Starting_point']
    start_target_bearing_df = start_target_bearing_df.T
    start_target_bearing_df_ordered = start_target_bearing_df[ordered]

    # Set NaN values for same starting point - target
    for index in start_target_bearing_df_ordered.index:
            for col in start_target_bearing_df_ordered.columns:
                num_index = index[-1]
                num_col = col[-1]
                if num_index == num_col:
                    start_target_bearing_df_ordered.loc[index, col] = pd.NA

    return start_target_bearing_df_ordered

print('These are the correct angles')
correct_df = get_start_target_angle()
print(correct_df)
correct_df.to_csv('task_correct_angles_new.csv')

#Get task answers
task_results_df = pd.read_excel("Task_survey_data.ods", engine="odf", sheet_name='Sheet2', index_col=0 ,header=[0,1])

#convert degrees in cardinal degrees
df_degrees_pic = task_results_df.copy()
level1_names = df_degrees_pic.columns.get_level_values(0)
for level1_name in level1_names.unique():
    df_degrees_pic.drop((level1_name, 'degree survey'), axis=1, inplace=True)

df_degrees_pic = df_degrees_pic.droplevel(level=1, axis=1)

df_degrees_pic = (360-df_degrees_pic)-5.39
df_degrees_pic.to_csv('answer_cardinal_degrees_north.csv')
north_values = df_degrees_pic.pop('North')
df_degrees_pic = df_degrees_pic.fillna(pd.NA)
df_degrees_pic.to_csv("answers_cardinal_degrees.csv")

error_df = pd.DataFrame(columns=ordered, index=df_degrees_pic.index)

# Calculate difference
def calculate_degr_error(degr_1, degr_2):
    if pd.isna(degr_1) or pd.isna(degr_2):
        return pd.NA
    dif = (degr_1 - degr_2) % 360
    if (dif > 180) or (dif < -180):
        dif = 360 - dif
    return dif 

for index in df_degrees_pic.index:
    for col1, col2 in zip(df_degrees_pic.columns,correct_df.columns):
        error = calculate_degr_error(df_degrees_pic.loc[index, col1], correct_df.loc[index, col2])

        error_df.loc[index, col2] = error

north_values = pd.Series(north_values)

error_no = []
for value in north_values:
    error_n = calculate_degr_error(360, value)
    error_no.append(error_n)

error_df['North'] = error_no

# Calculate the mean of each column while ignoring NaN values
mean_values = error_df.mean(skipna=True)
mean_df = pd.DataFrame(mean_values).T.rename(index={0: 'mean'})
df_error_mean = pd.concat([error_df, mean_df])

#Calculate the mean of every row while ignoring NaN values
row_means = df_error_mean.mean(axis=1, skipna=True)
df_error_mean['row_mean'] = row_means

print("This is the error:")
print(df_error_mean)

df_mean = error_df.stack().mean(skipna=True)
print(df_mean)

error_df.to_csv('task_error.csv')
df_error_mean.to_csv('task_error_mean.csv')
