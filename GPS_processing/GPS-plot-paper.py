import os
import re
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from cmcrameri import cm

pd.set_option("mode.copy_on_write", True)
Image.MAX_IMAGE_PIXELS = None

plt.rcParams['font.family'] = 'Arial'

def concat_GPS(folder_path):
    # List all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # List to store DataFrames
    df_list = []

    # Loop through each file
    for file in csv_files:
        file_path = os.path.join(folder_path, file)

        # Read CSV into DataFrame
        df = pd.read_csv(file_path)

        # Extract filename without extension as session identifier
        session_id = os.path.splitext(file)[0]

        # Add session identifier column
        df['session_id'] = session_id

        # Append to list
        df_list.append(df)

    # Concatenate all DataFrames into one
    final_df = pd.concat(df_list, ignore_index=True)
    
    return final_df


#plotting with session coloring

def plot_map_session(df, save=False, outname=''):
    
    #give the information on filepath of map image 
    filepath_map_general = "../"
    filename_map = "plot_map"
    outname = outname
    #put together the filepath name
    filepath_map = filepath_map_general + filename_map + ".jpg"
    filepath_img_save = filepath_map_general + outname + ".jpg"

    # Load an image from file
    img = Image.open(filepath_map) 

    # pixel values map picture 
    pixel_width = 24896 # Width of the image in pixels
    pixel_height = 15354  # Height of the image in pixels

    # latitude and longitude of the edges of the map image 
    corner_lat_top = 34.6776114 # Latitude of the top edge of the map
    corner_lat_bottom = 34.6718491  # Latitude of the bottom edge of the map
    corner_lon_left = 33.0379205  # Longitude of the left edge of the map
    corner_lon_right = 33.0492816  # Longitude of the right edge of the map

    # Calculate differences in latitude and longitude
    delta_lat = corner_lat_top - corner_lat_bottom
    delta_lon = corner_lon_right - corner_lon_left

    # Calculate conversion ratio from degrees to pixels
    lat_to_pixel = pixel_height / delta_lat
    lon_to_pixel = pixel_width / delta_lon

    # Assuming df contains 'latitude' and 'longitude' columns
    # Convert GPS coordinates to pixel coordinates
    df['x'] = (df['longitude'] - corner_lon_left) * lon_to_pixel
    df['y'] = (corner_lat_top - df['latitude']) * lat_to_pixel

    # Now, df['x'] and df['y'] contain the pixel coordinates of the GPS points on the image
    # Plot these points on the map image
    plt.imshow(img, alpha=0.6)
    # Hide the axes
    plt.axis("off")

    df['session_name'] = df['session_id'].str.extract(r'Expl_(\d+)_ET_(\d+)') \
                                     .agg('_'.join, axis=1)

    #unique_sessions = df['session_id'].unique()
    df = df.sort_values(by='session_name')

    unique_sessions = df['session_name'].unique()
    num_sessions = len(unique_sessions)

    print(df)

    # Create a colormap with discrete colors
    #cmap = plt.cm.get_cmap('tab20', num_sessions)  # Use a colormap with enough colors
    cmap = cm.roma
    norm = mcolors.BoundaryNorm(range(num_sessions + 1), cmap.N)  # Normalize values

    bounds = range(num_sessions + 1)

    # Create a session-to-index mapping
    session_to_index = {session: i for i, session in enumerate(unique_sessions)}

    # Scatter plot with session-based colors
    sc = plt.scatter(df['x'], df['y'], 
                     c=df['session_name'].map(session_to_index),  # Convert session IDs to indices
                     cmap=cmap, norm=norm, s=0.3, alpha=1)

    # Create colorbar with correct labels
    cbar = plt.colorbar(sc, ticks=np.arange(num_sessions)+0.5, boundaries=bounds, shrink=0.68, pad=0.02) # shrink=0.95(hor), orientation='horizontal'
    cbar.set_label("Session ID")
    cbar.set_ticklabels(unique_sessions)  # Assign session names to ticks

    if save:
        plt.savefig(filepath_img_save, dpi=500, bbox_inches = "tight") # Set the output file and resolution (dpi)
    
    plt.show()

def plot_GoPro_diffcolor(df):
    #give the information on filepath of map image 
    filepath_map_general = "../"
    filename_map = "plot_map"
    outname = "GoPro_highlighted"
    #put together the filepath name
    filepath_map = filepath_map_general + filename_map + ".jpg"
    filepath_img_save = filepath_map_general + outname + ".jpg"

    # Load an image from file
    img = Image.open(filepath_map) 

    # pixel values map picture 
    pixel_width = 24896 # Width of the image in pixels
    pixel_height = 15354  # Height of the image in pixels

    # latitude and longitude of the edges of the map image 
    corner_lat_top = 34.6776114 # Latitude of the top edge of the map
    corner_lat_bottom = 34.6718491  # Latitude of the bottom edge of the map
    corner_lon_left = 33.0379205  # Longitude of the left edge of the map
    corner_lon_right = 33.0492816  # Longitude of the right edge of the map

    # Calculate differences in latitude and longitude
    delta_lat = corner_lat_top - corner_lat_bottom
    delta_lon = corner_lon_right - corner_lon_left

    # Calculate conversion ratio from degrees to pixels
    lat_to_pixel = pixel_height / delta_lat
    lon_to_pixel = pixel_width / delta_lon

    # Assuming df contains 'latitude' and 'longitude' columns
    # Convert GPS coordinates to pixel coordinates
    df['x'] = (df['longitude'] - corner_lon_left) * lon_to_pixel
    df['y'] = (corner_lat_top - df['latitude']) * lat_to_pixel
    #print(df)

    # Now, df['x'] and df['y'] contain the pixel coordinates of the GPS points on the image
    # Plot these points on the map image
    plt.imshow(img, alpha=0.6)
    # Hide the axes
    plt.axis("off")

    # Split into two parts
    df_GoPro = df[df['session_id'] == 'sliced-cleaned-interpol-Expl_2_ET_3-GoPro']
    df_others = df[df['session_id'] != 'sliced-cleaned-interpol-Expl_2_ET_3-GoPro']
    
    # Scatter plot with session-based colors
    sc = plt.scatter(df_others['x'], df_others['y'], c='royalblue', s=0.5, alpha=0.7)

    # Scatter plot with session-based colors
    sc = plt.scatter(df_GoPro['x'], df_GoPro['y'], c='lightskyblue', s=0.5, alpha=0.7)

    plt.savefig(filepath_img_save, dpi=500, bbox_inches = "tight") # Set the output file and resolution (dpi)
    
    plt.show()


if __name__ == "__main__":
    GPS_folder = 'processed-GPS'

    complete_df = concat_GPS(GPS_folder)
    mean_speed = complete_df.loc[complete_df['speed_km_h'] != -1, 'speed_km_h'].mean()
    speed_std = complete_df.loc[complete_df['speed_km_h'] != -1, 'speed_km_h'].std()
    print("mean walking speed:", mean_speed, "walking speed std:", speed_std)

    plot_map_session(complete_df, save=False, outname='all_Session_coloring_new_hor')
    #plot_GoPro_diffcolor(complete_df)