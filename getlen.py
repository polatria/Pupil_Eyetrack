import numpy as np
import pandas as pd
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import os

eyeside = ['./Right', './Left']
eyepos = ['/elps', '/eybl']

EXT_MAT = [  # 外部パラメータによる変換行列
    np.array([[-0.892004, 0.340027, 0.297843, -4.536258],
              [0.450213, 0.609317, 0.652718, -19.413169],
              [0.040460, 0.716320, -0.696598, 18.947337],
              [0.000000, 0.000000, 0.000000, 1.000000]]),
    np.array([[0.865237, 0.334394, -0.373558, 22.454160],
              [0.500189, -0.626702, 0.597541, -17.850285],
              [-0.034295, -0.703864, -0.709506, 18.718809],
              [0.000000, 0.000000, 0.000000, 1.000000]])
]
PAL = np.array([[1, 0, 0, -60], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])  # 平行移動用行列

# 世界座標系への変換
def getWLDVec(arr, eyeid):
    cam = np.array([np.insert(arr, len(arr), 1)]).T
    wld = np.dot(EXT_MAT[eyeid], cam)
    if eyeid == 1:
        wld = np.dot(PAL, wld)
    return np.reshape(np.delete(wld, 3, 0), -1)

# 注視位置算出
def getGazePoint(eyeballn, ellipsen):
    xz = [np.zeros(3), np.zeros(3)]
    mv = [np.zeros(3), np.zeros(3)]
    for i in range(len(eyeside)):
        xz[i] = getWLDVec(eyeballn[i], i)
        mv[i] = getWLDVec(ellipsen[i], i) - xz[i]
        mv[i] /= np.linalg.norm(mv[i])
    Dv = np.dot(mv[0], mv[1])
    D = [np.dot(xz[1] - xz[0], mv[0]), np.dot(xz[1] - xz[0], mv[1])]
    near = [np.zeros(3), np.zeros(3)]
    for i in range(len(eyeside)):
        denom = D[i] - D[i ^ 1] * Dv
        numer = pow(-1, i) * (1 - pow(Dv, 2))
        near[i] = xz[i] + (denom / numer) * mv[i]
    gaze = np.zeros(3)
    for i in range(len(eyeside)):
        gaze += near[i] / 2
    return gaze

trials = 0
while True:
    path = eyeside[0] + eyepos[0] + '/' + str(trials) + '.csv'
    if os.path.exists(path):
        trials += 1
    else:
        break

data = [[[], []], [[], []]]  # 0: elps, 1: eybl

for n in range(trials):
    for i in range(len(eyeside)):
        for j in range(len(eyepos)):
            path = eyeside[i] + eyepos[j] + f'/{n}.csv'
            data[i][j].append(pd.read_csv(path, names=['x', 'y', 'z'], dtype=float))

lngt = int(input('Which length of trial, 0:1m, 1:50cm, 2:20cm'))

elps = [np.array(data[0][0][lngt][data[0][0][lngt]['z'] != 0].describe().loc['mean']), np.array(data[1][0][lngt][data[1][0][lngt]['z'] != 0].describe().loc['mean'])]
eybl = [np.array(data[0][1][lngt][data[0][1][lngt]['z'] != 0].describe().loc['mean']), np.array(data[1][1][lngt][data[1][1][lngt]['z'] != 0].describe().loc['mean'])]

print(np.linalg.norm(getGazePoint(elps, eybl)))
