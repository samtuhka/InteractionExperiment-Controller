#!/usr/bin/env python3
import zmq, msgpack, time
from msgpack import loads
import json
import sys
import os
import time
from multiprocessing import Process
import subprocess
import threading
import hr_plot
import ast
import numpy as np

def create_dir(sub, session):
    dirpath = r'sessions/session_{}/subject_{}'.format(session, sub) 
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    return dirpath

def create_log_files(sub, session):
    newpath = create_dir(sub, session)
    pupil_file = open(newpath + '/pupil_' + str(time.time()) + '.txt', 'w', encoding='utf-8')
    nexus_path = (newpath + '/nexus_' + str(time.time()) + '.txt')
    return pupil_file, nexus_path

def read_nexus(nexus_mac, nexus_path, pool, sub):
    process = subprocess.Popen(["./nexus10/physiology", nexus_mac, nexus_path], shell = False, stdout=subprocess.PIPE)
    while True:
        out = process.stdout.readline()
        if out == '' and process.poll() != None:
            break
        out = out.decode("utf-8")
        if 'HRate' in out:
            out = ast.literal_eval(out)
            if type(out) == type(list()):
                pool.nexus.bvp[sub - 1][0][-1] = float(out[0][1])
                pool.nexus.bvp[sub - 1][1][-1] = float(out[1]['F'])
                pool.nexus.bvp[sub - 1][0] = np.roll(pool.nexus.bvp[sub - 1][0], 1)
                pool.nexus.bvp[sub - 1][1] = np.roll(pool.nexus.bvp[sub - 1][1], 1)

                eda = float(out[1]['E'])
                if eda != 0:
                    eda = 1/eda

                pool.nexus.eda[sub - 1][0][-1] = float(out[0][1])
                pool.nexus.eda[sub - 1][1][-1] = eda
                pool.nexus.eda[sub - 1][0] = np.roll(pool.nexus.eda[sub - 1][0], 1)
                pool.nexus.eda[sub - 1][1] = np.roll(pool.nexus.eda[sub - 1][1], 1)

        if pool.stop[sub - 1]:
            process.terminate()
            return

def log(req, address, sub, nexus_mac, pool, session = 0):
    pupil_file, nexus_path = create_log_files(sub, session)

    time.sleep(0.5)
    proc2 = threading.Thread(target=read_nexus, args=(nexus_mac, nexus_path, pool, sub,))
    proc2.start()

    #req.send_string('SUB_PORT')
    #sub_port = req.recv_string()
    #proc1 = Process(target=pupil_dumper, args=(sub_port, address, pupil_file, session,))
    #proc1.start()
    return proc2, proc2

def pupil_dumper(sub_port, address, file, session = 0):
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect("tcp://{}:{}".format(address, sub_port))
    sub.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        topic = sub.recv_string()
        recv_ts_mono = time.monotonic()
        recv_ts = time.time()

        msg = sub.recv()
        data = loads(msg, encoding='utf-8')
        msg = dict(
            recv_ts=recv_ts,
            recv_ts_mono=recv_ts_mono,
            topic=topic,
            data=data
        )
        json.dump(msg, file, ensure_ascii=False)
        file.write('\n')
