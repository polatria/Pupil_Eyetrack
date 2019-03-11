import numpy as np
import pandas as pd
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

elpsdfs = []
eybldfs = []
eyeside = ['Right', 'Left']

for i in range(2):
    file = f'eybl{eyeside[i]}.csv'
    eybldfs.append(pd.read_csv(file, names=['x', 'y', 'z']))
    # ellipse.append(eybldf.values.tolist())
    file = f'elps{eyeside[i]}.csv'
    elpsdfs.append(pd.read_csv(file, names=['x', 'y', 'z']))

i = int(input('Which data do you use? (R:0/L:1)'))

print('\nEyeball')
print(eybldfs[i][eybldfs[i]['z'] != 0].describe())  # 0を含む列を削除し統計量を表示
print('\nEllipse')
print(elpsdfs[i][elpsdfs[i]['z'] != 0].describe())  # 0を含む列を削除し統計量を表示

fig = plt.figure()
ax = fig.gca(projection='3d')
cmap = plt.get_cmap('tab10')
ax.scatter(eybldfs[i]['x'], eybldfs[i]['y'], eybldfs[i]['z'], label='Eyeball')
ax.scatter(elpsdfs[i]['x'], elpsdfs[i]['y'], elpsdfs[i]['z'], label='Ellipse')
ax.legend(frameon=False)
plt.show()

# input('\nPress any key to exit\n')
