import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('task_error_mean.csv', index_col=0, header=0)
print(df)
#buildings_only = df.drop(['North', 'row_mean'], axis=1)
#buildings_only = buildings_only.drop('mean')
#print(buildings_only)
#mean_buidlings_only = buildings_only.stack().dropna().mean()
#std_buidlings_only = buildings_only.stack().dropna().std()
#print("Mean stack:", mean_buidlings_only)
#print("Std stack:", std_buidlings_only)
#
#mean_buidlings_only_flatten = np.nanmean(buildings_only.values)
#std_buidlings_only_flatten = np.nanstd(buildings_only.values)
#print(mean_buidlings_only_flatten)
#print(std_buidlings_only_flatten)
#
#df_north = df['North']
#df_north = df_north.drop('mean')
#print(df_north)
#mean_north = df_north.mean()
#std_north = df_north.std()
#print("Mean North:", mean_north, "std north:", std_north)

building_1 = df['Target 1']
building_1 = building_1.drop('mean')
print(building_1)
mean_building1 = building_1.mean()
std_building1 = building_1.std()
print('Mean building1:', mean_building1, 'Std building1:', std_building1)

building_2 = df['Target 2']
building_2 = building_2.drop('mean')
print(building_2)
mean_building2 = building_2.mean()
std_building2 = building_2.std()
print('Mean building2:', mean_building2, 'Std building2:', std_building2)