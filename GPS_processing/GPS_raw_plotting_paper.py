import os
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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

def plot_map_flagged(df, save=False, outname=''):
    
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

    print(df)

    # Boolean mask: True where status includes "passed"
    passed_mask = df['fail_reasons'].str.contains("passed", case=False)

    # Define colors 
    cmap = cm.roma
    colors = [cmap(1.0) if passed else cmap(0.0) for passed in passed_mask]

    sc = plt.scatter(df['x'], df['y'], 
                     c=colors,  # use color mask
                     s=0.3, alpha=0.6)

    legend_elements = [
    Line2D([0], [0], marker='o', linestyle='None', label='Passed', markerfacecolor=cmap(1.0), markeredgewidth=0, markersize=10),
    Line2D([0], [0], marker='o', linestyle='None', label='Failed', markerfacecolor=cmap(0.0), markeredgewidth=0, markersize=10)]

    plt.legend(handles=legend_elements)

    if save:
        plt.savefig(filepath_img_save, dpi=500, bbox_inches="tight") 
    
    plt.show()

if __name__ == "__main__":
    GPS_folder = 'only_flagged'

    complete_df = concat_GPS(GPS_folder)
    print(complete_df)
    plot_map_flagged(complete_df, save=True, outname='raw_GPS')