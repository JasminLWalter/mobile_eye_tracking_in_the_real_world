from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from cmcrameri import cm

Image.MAX_IMAGE_PIXELS = None

task_building_coord = pd.read_excel("../taskB-coords.ods", engine="odf") #index_col=0, header=0
print(task_building_coord)

start_locs = pd.read_excel("../postion-per-location.ods", engine="odf")
print("start locs:", start_locs)


def plot_plot_map():
    filepath_map = "../plot_map.jpg"

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

    # Plot the map image
    plt.imshow(img, alpha=0.4)
    ax = plt.gca()

    # Assuming task_building_coord contains 'latitude' and 'longitude' columns
    # Convert GPS coordinates to pixel coordinates
    task_building_coord['x'] = (task_building_coord['longitude'] - corner_lon_left) * lon_to_pixel
    task_building_coord['y'] = (corner_lat_top - task_building_coord['latitude']) * lat_to_pixel

    start_locs['x'] = (start_locs['longitude']- corner_lon_left) * lon_to_pixel
    start_locs['y'] = (corner_lat_top - start_locs['latitude']) * lat_to_pixel
    

    plt.scatter(task_building_coord['x'], task_building_coord['y'], marker='.', s=15)
    plt.show()

def plot_exluded_areas_map():
    filepath_map = "../exluded-areas-map.jpg"

    # Load an image from file
    img = Image.open(filepath_map) 

    # pixel values map picture 
    pixel_width = 24884 # Width of the image in pixels
    pixel_height = 15346  # Height of the image in pixels

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

    # Plot the map image
    plt.imshow(img, alpha=0.8)
    ax = plt.gca()

    # Assuming task_building_coord contains 'latitude' and 'longitude' columns
    # Convert GPS coordinates to pixel coordinates
    task_building_coord['x'] = (task_building_coord['longitude'] - corner_lon_left) * lon_to_pixel
    task_building_coord['y'] = (corner_lat_top - task_building_coord['latitude']) * lat_to_pixel

    start_locs['x'] = (start_locs['longitude']- corner_lon_left) * lon_to_pixel
    start_locs['y'] = (corner_lat_top - start_locs['latitude']) * lat_to_pixel

    locations_visited = ['Target 4', 'Target 5', 'Target 6', 'Target 7']

    cmap = cm.roma
    colors = [cmap(i) for i in [1.0, 0.0, 0.8]] 

    for _, row in task_building_coord.iterrows():
        name = row['Name']
        if name in locations_visited:
            plt.scatter(row['x'], row['y'], marker='X', s=40, color=colors[0])
        elif name == 'Starting_point':
            plt.scatter(row['x'], row['y'], marker='X', s=40, color=colors[1])
        else:
            plt.scatter(row['x'], row['y'], marker='X', s=40, color=colors[2])

    
    #plt.scatter(task_building_coord['x'], task_building_coord['y'], marker='.', s=30)
    
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("/Users/vb/Documents/IKW/Cyprus_Li-map/excludedA_taskB_kreuz_tight", dpi=500, bbox_inches='tight', pad_inches=0)
    plt.show()


plot_exluded_areas_map()