import zmq
from msgpack import loads
import time
import numpy as np
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

ellipse = [[], []]
eyeball = [[], []]
eyeside = ['Right', 'Left']

input("Press Return key to start measurement...\n")
start_time = time.time()
while True:
    try:
        topic = sub.recv_string()
        msg = sub.recv()
        msg = loads(msg, encoding='utf-8')
        if msg[u'confidence'] > 0.6:
            eyeball[msg[u'id']].append(msg[u'sphere'][u'center'])
            ellipse[msg[u'id']].append(msg[u'circle_3d'][u'center'])
        else:
            eyeball[msg[u'id']].append([0., 0., 0.])
            ellipse[msg[u'id']].append([0., 0., 0.])
        if time.time() - start_time > 10:  # 経過時間, unit: sec
            break
    except KeyboardInterrupt:
        break
input("Press Return key to next...\n")

ans = input('Do you want to save this data? (y/n)')
if ans == 'y':
    for i in range(2):
        file = f'elps{eyeside[i]}.csv'
        with open(file, mode='a') as f:
            w = csv.writer(f, lineterminator='\n')
            for j in range(len(ellipse[i])):
                el = ellipse[i][j]
                w.writerow(el)
        file = f'eybl{eyeside[i]}.csv'
        with open(file, mode='a') as f:
            w = csv.writer(f, lineterminator='\n')
            for j in range(len(eyeball[i])):
                w.writerow(eyeball[i][j])
