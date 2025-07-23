import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib.gridspec as gridspec
from cmcrameri import cm

plt.rcParams['font.family'] = 'Arial'

imu_df = pd.read_csv('../raw_data/ET/Expl_4_ET_1/imu.csv')
imu_df['new time'] = pd.to_datetime(imu_df['timestamp [ns]'], unit='ns')
# Convert ET values from [-180;0;180] to [0, 360]
imu_df['yaw [deg]'] = (-imu_df['yaw [deg]'] % 360) #-5.39

gps_df = pd.read_csv('new_slicing_synced-GPS/synced_GPS_Expl_4_ET_1.csv')
gps_df['new time'] = pd.to_datetime(gps_df['synced_time'], unit='ns')
gps_df['time'] = pd.to_datetime(gps_df['time'], unit='ns')

slice_GPS = [1804,1897]

gps_sliced = gps_df[slice_GPS[0]:slice_GPS[1]]

#slice imu df
start_time = gps_sliced['new time'].iloc[0] 
end_time = gps_sliced['new time'].iloc[-1]  

imu_sliced = imu_df[(imu_df['new time'] >= start_time) & (imu_df['new time'] <= end_time)]

def merg_imu_gps(imu_df, gps_df):
    merged_df = pd.merge_asof(
        gps_df,
        imu_df,
        on='new time',
        direction='nearest',
        #tolerance=pd.Timedelta("0.2s")
    )
    return merged_df


merged_df = merg_imu_gps(imu_df, gps_sliced)


def plot_GPS_HT_paper(gps_df,merged_df):

    #plot GPS(lat-lon-time)
    fig = plt.figure(figsize=(15,6))
    gs = gridspec.GridSpec(3,2)

    # First coloumn spanning all 3 rows
    ax1 = fig.add_subplot(gs[:3, 0])  # First column, all three rows
    

    # Second coloumn with three rows
    ax2 = fig.add_subplot(gs[0, 1])  # First row
    ax3 = fig.add_subplot(gs[1, 1])  # Second row
    ax4 = fig.add_subplot(gs[2, 1])  #Third row
    
    # Plot GPS alltogether
    scatter = ax1.scatter(gps_df['longitude'], gps_df['latitude'], c=gps_df["new time"], marker='.', s=15, cmap=cm.roma)
    cbar = fig.colorbar(scatter, ax=ax1)
    cbar.set_label('Time')

    ax1.set_xlabel('Longitude', labelpad=15)
    ax1.set_ylabel('Latitude')
    ax1.set_title("GPS", pad=15, fontname='Arial')
    # Use scientific notation for the y-axis
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.5f'))

    #list of colors
    cmap = cm.roma
    list_of_colors = [cmap(i) for i in [1.0, 0.8, 0.0]]

    #plot lat + long seperate but in one plot
    ax2.plot(gps_df['time'], gps_df['longitude'], color=list_of_colors[0])
    ax2.set_ylabel('Latitude', color=list_of_colors[0] )
    ax2.tick_params(axis='y', color=list_of_colors[0])

    ax2_1 = ax2.twinx()
    ax2_1.plot(gps_df['time'], gps_df['latitude'], color=list_of_colors[1])
    ax2_1.set_ylabel('Longitude', color=list_of_colors[1])
    ax2_1.tick_params(axis='y', color=list_of_colors[1])
    
    #ax2.set_ylabel('Longitude + Latitude')
    ax2.set_xlabel('Time')
    ax2.set_title("Longitude + Latitude", fontname='Arial')

    #Plot yaw individually
    ax3.plot(merged_df['new time'], merged_df['yaw [deg]'], color=list_of_colors[2])
    ax3.set_title('Yaw', fontname='Arial')
    ax3.set_ylabel('yaw [deg]')
    ax3.set_xlabel('Time')

    # Determine the range of imu
    min_imu = merged_df['yaw [deg]'].min()
    max_imu = merged_df['yaw [deg]'].max()

    # Normalize lat, long to the IMU range
    merged_df['latitude_nor'] = (merged_df['latitude'] - merged_df['latitude'].min()) / (merged_df['latitude'].max() - merged_df['latitude'].min()) * (max_imu - min_imu) + min_imu
    merged_df['longitude_nor'] = (merged_df['longitude'] - merged_df['longitude'].min()) / (merged_df['longitude'].max() - merged_df['longitude'].min()) * (max_imu - min_imu) + min_imu

    ax4.plot(merged_df['new time'], merged_df['yaw [deg]'], label='yaw', color=list_of_colors[2])
    ax4.plot(merged_df['new time'], merged_df['latitude_nor'], label='lat_norm', color=list_of_colors[0])
    ax4.plot(merged_df['new time'], merged_df['longitude_nor'], label='long_norm', color=list_of_colors[1])

    ax4.set_title('Synchronized', fontname='Arial')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Normalised angle (°)')
    
    plt.tight_layout()
    plt.savefig('GPS+HT-paper', dpi=500, bbox_inches="tight")
    plt.show()

plot_GPS_HT_paper(gps_sliced,merged_df)
