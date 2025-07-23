import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cmcrameri import cm

plt.rcParams['font.family'] = 'Arial'


pd.set_option('display.precision', 13)
df = pd.read_csv('error_with_correct_IMU_mad.csv', float_precision='round_trip', index_col=0)
df = df.iloc[:-6,:]

df_beginning = df.iloc[::2]
print(df_beginning)
df_end = df.iloc[1::2]
print(df_end)

df_beginning['label'] = df_beginning['Id'].str.extract(r'Expl_(\d+)_ET_(\d+)_beg') \
                        .agg('_'.join, axis=1)
df_end['label'] = df_end['Id'].str.extract(r'Expl_(\d+)_ET_(\d+)_end') \
                        .agg('_'.join, axis=1)
print(df_beginning)
print(df_end)

def bar_plot_median_only(df_beginning, df_end):

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 4))

    cmap = cm.roma
    list_of_colors = [cmap(i) for i in [0.3, 1.0]]
        
    bar2_beg = ax.bar(df_beginning['label'], df_beginning["diff_median_abs"], label='beg', alpha=0.75, color=list_of_colors[0])
    erorr_beg = ax.errorbar(df_beginning['label'], df_beginning["diff_median_abs"], yerr=df_beginning['mad'], fmt='none', color=list_of_colors[0])
    bar2_end = ax.bar(df_end['label'], df_end["diff_median_abs"], label='end', alpha=0.75, color=list_of_colors[1])
    error_end = ax.errorbar(df_end['label'], df_end["diff_median_abs"], yerr=df_end['mad'], fmt='none', color=list_of_colors[1])
    
    ax.set_xticklabels(df_beginning['label'], rotation=90)


    for i, (beg_val, end_val) in enumerate(zip(df_beginning["diff_median_abs"], df_end["diff_median_abs"])):
        if np.isnan(end_val):
            bar2_beg[i].set_edgecolor('black')
            bar2_beg[i].set_linewidth(3)

    ax.tick_params(axis='x', which='major', pad=-25, rotation=90)
    ax.legend()
    ax.set_ylim(-20, 20)
    
    plt.ylabel('Error (degrees)')
    plt.show()
    fig.savefig('paper-HT-median', dpi=500, bbox_inches="tight")

bar_plot_median_only(df_beginning, df_end)
