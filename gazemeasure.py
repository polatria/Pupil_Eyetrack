import zmq
from msgpack import loads
import time
import numpy as np
import os
import csv

context = zmq.Context()
# open a req port to talk to pupil
addr = '127.0.0.1'  # remote ip or localhost
req_port = '50020'  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect(f'tcp://{addr}:{req_port}')
# ask for the sub port
req.send_string('SUB_PORT')
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect(f'tcp://{addr}:{sub_port}')

# set subscriptions to topics
# recv just pupil/gaze/notifications
sub.setsockopt_string(zmq.SUBSCRIBE, 'pupil.')

TRIALTIME = 10  # 試行時間, unit: sec
saveData = [[], []]

input("Press Return key to start measurement...\n")
while True:
    ellipse = [[], []]
    eyeball = [[], []]
    start_time = time.time()
    while True:
        try:
            topic = sub.recv_string()
            msg = sub.recv()
            msg = loads(msg, encoding='utf-8')
            if msg[u'confidence'] > 0.6:
                ellipse[msg[u'id']].append(msg[u'circle_3d'][u'center'])
                eyeball[msg[u'id']].append(msg[u'sphere'][u'center'])
            else:
                ellipse[msg[u'id']].append([0., 0., 0.])
                eyeball[msg[u'id']].append([0., 0., 0.])
            if time.time() - start_time > TRIALTIME:
                break
        except KeyboardInterrupt:
            break
    needs = input('Save this data? (s: Save / d: Delete)')
    if needs == 's':
        saveData[0].append(ellipse)
        saveData[1].append(eyeball)
    next = input("Continue to next measurement? (c: Continue / x: Exit)\n")
    if next == 'x':
        break

eyeside = ['./Right', './Left']
eyepos = ['/elps', '/eybl']
for i in range(2):
    os.makedirs(eyeside[i], exist_ok=True)
    for j in range(2):
        os.makedirs(eyeside[i] + eyepos[j], exist_ok=True)

dataofs = 0
while True:
    path = eyeside[i] + eyepos[j] + '/' + str(dataofs) + '.csv'
    if os.path.exists(path):
        dataofs += 1
    else:
        break

for n in range(len(saveData[0])):
    for i in range(len(eyeside)):
        for j in range(len(eyepos)):
            path = eyeside[i] + eyepos[j] + f'/{n + dataofs}.csv'
            with open(path, mode='a') as f:
                w = csv.writer(f, lineterminator='\n')
                for k in range(len(saveData[j][n][i])):
                    w.writerow(saveData[j][n][i][k])
