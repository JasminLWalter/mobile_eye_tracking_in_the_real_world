import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch

plt.rcParams['font.family'] = 'Helvetica'

error_df = pd.read_csv('task_error.csv')


myFig = plt.figure(figsize=(11, 5))


bp = error_df.boxplot(column=['North', 'Target 1', 'Target 2', 'Target 3', 'Target 4', 'Target 5', 'Target 6', 'Target 7', 'Target 8'], 
                      color='black', showfliers=True, patch_artist=True) 

#bp['boxprops'].set_facecolor('lightcoral')
box_patches = [p for p in bp.patches if isinstance(p, PathPatch)]

for i, patch in enumerate(box_patches):
    patch.set_facecolor('none')       # transparent fill
    patch.set_linewidth(1.5)          # thicker border
    if i == 0:
        patch.set_edgecolor('blue')   # North box = blue
    else:
        patch.set_edgecolor('black')  # others = black
    
for line in bp.lines:
    line.set_linewidth(1.5)


#patch = box_patches[0]
#patch.set_facecolor('None')
#patch.set_edgecolor('blue')


# Get all Line2D objects (box components)
all_lines = [line for line in bp.lines if isinstance(line, plt.Line2D)]

lines_per_box = 5  # usually: 2 whiskers, 2 caps, 1 median
i=0
lines = all_lines[i * lines_per_box:(i + 1) * lines_per_box]
for line in lines:
    line.set_color('blue')
    #line.set_linewidth(1.8)

# Change the color of the first outlier
flier = bp.lines[lines_per_box]  # The first flier line
flier.set_markerfacecolor('None')  # Change color to red or any other color
flier.set_markeredgecolor('blue')  # Change edge color as well if needed

plt.ylabel('Error (degrees)', fontsize=18)


ax.set_xticklabels(['North', 'Target 1', 'Target 2', 'Target 3',
                    'Target 4', 'Target 5', 'Target 6', 'Target 7', 'Target 8'],
                   fontsize=15)
ax.tick_params(axis='y', labelsize=15, width=1.5)

plt.tight_layout()
plt.show()
myFig.savefig('task-error_northfirst_arial', dpi=500)