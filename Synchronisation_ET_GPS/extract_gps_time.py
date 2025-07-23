import os 
import pandas as pd

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
    """ Converts .pos data to dataframe with slicing_dftamp, latitude, longitude and height """
    df = pd.read_table(file, sep="\s+", header=9, parse_dates={"slicing_dftamp": [0, 1]})
    df = df.rename(
        columns={
            "slicing_dftamp": "time",
            "longitude(deg)": "longitude",
            "latitude(deg)": "latitude",
        }
    )
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S.%f') #
    return df

def get_slicing_df_GPS(GPS_dfs, slicing_df):
    # Iterate through indices_df to ensure each row gets the correct slicing_df
    for session, row in slicing_df.iterrows():
        print(session)
        index_start = row["GPS_start"]
        index_end = row["GPS_end"]
        session_cleaned = session.rsplit("_", 1)[0]
        print(session_cleaned)

        if session_cleaned in GPS_dfs.keys():
            print(session)
            df = GPS_dfs[session_cleaned]  # Get the corresponding DataFrame
            # Ensure the index exists in the DataFrame
            slicing_df.at[session, "GPS_start_time"] = df.loc[index_start, "time"] 
            slicing_df.at[session, "GPS_end_time"] = df.loc[index_end, "time"] 

    slicing_df.to_csv(slicing_file, index=True)

def calculate_time_diff(slicing_df):
    cols = ['ET_start_time', 'ET_end_time', 'GPS_start_time', 'GPS_end_time']
    slicing_df[cols] = slicing_df[cols].apply(pd.to_datetime)
    print(slicing_df)
    slicing_df['time_diff_start'] = (slicing_df['GPS_start_time'] - slicing_df['ET_start_time']).astype('timedelta64[ns]')
    slicing_df['time_diff_end'] = (slicing_df['GPS_end_time'] - slicing_df['ET_end_time']).astype('timedelta64[ns]')
    slicing_df.to_csv(slicing_file, index=True)



if __name__ == "__main__":
    slicing_file = 'new_slicing-GPS-ET-timediff.csv'
    slicing_df = pd.read_csv(slicing_file, index_col="session")

    GPS_path = '../raw_data/GPS_UTC/'
    included_Expl = ['Expl_1_ET_1', 'Expl_1_ET_2', 'Expl_1_ET_3', 'Expl_2_ET_1', 'Expl_2_ET_2', 'Expl_3_ET_1',
                'Expl_3_ET_2', 'Expl_3_ET_3', 'Expl_4_ET_1', 'Expl_4_ET_2', 'Expl_5_ET_1', 'Expl_5_ET_2']

    GPS_dfs = find_folders_with_prefixes(GPS_path, included_Expl)

    get_slicing_df_GPS(GPS_dfs, slicing_df)
    calculate_time_diff(slicing_df)