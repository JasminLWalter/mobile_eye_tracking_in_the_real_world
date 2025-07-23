#from convert_pos_in_df import pos_to_dataframe
#from bearing import get_start_target_angle, get_angles_answer
from PIL import Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from cmcrameri import cm

Image.MAX_IMAGE_PIXELS = None

def extend_line_to_axes(ax, x0, y0, angle_rad):
    """Berechnet den Schnittpunkt einer Linie mit dem Rand der Achse"""
    # Grenzen des Plots holen
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # Richtungsvektor
    dx = np.sin(angle_rad)
    dy = np.cos(angle_rad)

    # Vermeide Division durch 0
    if dx == 0:
        dx = 1e-10
    if dy == 0:
        dy = 1e-10

    # max. mögliche Skalierungen in x und y, um an Rand zu kommen
    t_x_pos = (x_max - x0) / dx
    t_x_neg = (x_min - x0) / dx
    t_y_pos = (y_max - y0) / dy
    t_y_neg = (y_min - y0) / dy

    # Alle möglichen t's berechnen
    t_values = [t for t in [t_x_pos, t_x_neg, t_y_pos, t_y_neg] if t > 0]

    # kleinstes positives t wählen → der Punkt, wo Linie zuerst die Achse verlässt
    t_final = min(t_values)

    # Endpunkt berechnen
    x_end = x0 + t_final * dx
    y_end = y0 + t_final * dy
    return [x_end, y_end]


def plot_lines(angles, correct_angles=False):
    """ Plotten der Linien vom Startpunkt aus"""
    for i in range(len(angles)):
        if pd.notna(angles[i]):
            
            angle_rad = np.deg2rad(-angles[i]+180)
            #angle_rad = np.deg2rad(-90)

            if correct_angles:
                if i == 5:  #9
                    north_lat = (corner_lat_top - corner_lat_top) * lat_to_pixel
                    end_point = [start_locs['x'][t], north_lat]
                    plt.text(start_locs['x'][t]+500, north_lat+500, 'N', fontsize=12, fontweight='bold', ha='center', va='center')
                else:
                   end_point = [part_taskB['x'][i], part_taskB['y'][i]]
            else: 
                end_point = extend_line_to_axes(ax, start_locs['x'][t], start_locs['y'][t], angle_rad)
            
            cmap = cm.roma
            list_of_colors = [cmap(i) for i in [0.0, 0.7, 1.0, 0.3, 0.9]]
            list_of_colors.append('k')
            #list_of_colors = ['b','g','r','c','m', 'k']

            label = angles.index[t]
            if correct_angles:
                plt.plot([start_locs['x'][t], end_point[0]], [start_locs['y'][t], end_point[1]], linestyle='--', color=list_of_colors[i])
            else:
                plt.plot([start_locs['x'][t], end_point[0]], [start_locs['y'][t], end_point[1]], color=list_of_colors[i], ) #label=angles.index[i] color=list_of_colors[i]


if __name__ == '__main__':
#give the information on filepath of map image 
    filepath_map_general = "../"
    filename_map = "plot_map"
    outname = 'task_performance_map'
    #put together the filepath name
    filepath_map = filepath_map_general + filename_map + ".jpg"
    filepath_img_save = filepath_map_general + outname + ".jpg"

    # Load an image from file
    img = Image.open(filepath_map) 

    #print(img.size)

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

    # Plot these points on the map image
    plt.imshow(img, alpha=0.4)
    ax = plt.gca()


    task_building_coord = pd.read_excel("../taskB-coords.ods", engine="odf") #index_col=0, header=0
    taskB_order = [1,2,3,4,5,6,7,8,0,9]
    task_building_coord = task_building_coord.loc[taskB_order]
    task_building_coord.reset_index(inplace=True)
    print(task_building_coord)
    
    start_locs = pd.read_excel("../postion-per-location.ods", engine="odf")

    # Assuming task_building_coord contains 'latitude' and 'longitude' columns
    # Convert GPS coordinates to pixel coordinates
    task_building_coord['x'] = (task_building_coord['longitude'] - corner_lon_left) * lon_to_pixel
    task_building_coord['y'] = (corner_lat_top - task_building_coord['latitude']) * lat_to_pixel

    start_locs['x'] = (start_locs['longitude']- corner_lon_left) * lon_to_pixel
    start_locs['y'] = (corner_lat_top - start_locs['latitude']) * lat_to_pixel



    cmap = cm.roma
    part_color_buildings = [cmap(i) for i in [0.0, 0.7, 1.0, 0.3, 0.9]]
    part_color_buildings.append('k')

    t = 4
    correct_angles_df = pd.read_csv('task_correct_angles.csv', index_col=0, na_values="")

    angle_this_point = correct_angles_df.iloc[t]
    print("correct angles here:", angle_this_point)
    
    answer_angles = pd.read_csv("answer_cardinal_degrees_north.csv", index_col=0, na_values="")

    answer_angles_t = answer_angles.iloc[t]
    print(answer_angles_t)
    print(answer_angles_t.index)

    part_taskB = task_building_coord.drop([0,1,5,8])
    part_correct_angles = angle_this_point.drop(['Target 2', 'Target 6','Target 1', 'Starting_point'])
    part_answer_angles_t = answer_angles_t.drop(['Trial 2', 'Trial 6','Trial 1','start_loc'])
    print(part_taskB)
    print(part_correct_angles)
    print(part_answer_angles_t)
    
    part_taskB.reset_index(inplace=True)
    plt.scatter(part_taskB['x'], part_taskB['y'], c=part_color_buildings, marker='.', s=15)
    
    locations_visited = ['Target 4', 'Target 5', 'Target 6', 'Target 7']
    
    plot_lines(part_correct_angles, correct_angles=True)
    plot_lines(part_answer_angles_t)
    
    # Hide the axes
    plt.axis("off")
    plt.legend()
    plt.tight_layout()

    # Save the figure as an image with a specific DPI
    plt.savefig("angles_map_new_x", dpi=500, bbox_inches="tight", pad_inches=0)  # Set the output file and resolution (dpi)
    
    plt.show()