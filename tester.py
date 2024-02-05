import json
import os
import re
import shutil
import time

import docker
import docker.errors
from websockets import ConnectionClosed
from websockets.sync.client import connect

from gen_tests import generate

docker_engine = docker.DockerClient()

N_TESTS = 100
MAIN_CLASS = 'Main'


def do_test(file: str):
    shutil.copyfile('run.sh', 'data/run.sh')
    for i in range(N_TESTS):
        fin = open(f'data/input{i}.txt', 'w')
        test = generate()
        fin.write(test)
        fin.close()
    try:
        docker_engine.containers.run(
            'openjdk:23-slim-bullseye',
            remove=True, network_mode='none', working_dir='/work', stderr=True,
            volumes=['/root/gigatester/reference:/prog:ro',
                     '/root/gigatester/data:/data'],
            command=f'/bin/bash /data/run.sh {N_TESTS} /prog/{MAIN_CLASS}.java {MAIN_CLASS}'
        )
        expecteds = []
        for i in range(N_TESTS):
            fe = open(f'data/output{i}.txt')
            expecteds.append(fe.read().strip())
            fe.close()
    except docker.errors.ContainerError as e:
        errmess = e.stderr.decode()
        if errmess:
            return {'code': -1, 'error': errmess}
        else:
            try:
                fo = open('data/output0.txt')
                errmess = fo.read()
                fo.close()
                return {'code': -1, 'error': errmess}
            except IOError:
                return {'code': -1, 'error': "Unknown error."}
    try:
        docker_engine.containers.run(
            'openjdk:23-slim-bullseye',
            remove=True, network_mode='none', working_dir='/work', stderr=True,
            volumes=['/root/gigatester/queue:/prog:ro',
                     '/root/gigatester/data:/data'],
            command=f'/bin/bash /data/run.sh {N_TESTS} /prog/{file} {MAIN_CLASS}'
        )
        outputs = []
        for i in range(N_TESTS):
            fe = open(f'data/output{i}.txt')
            outputs.append(fe.read().strip())
            fe.close()
    except docker.errors.ContainerError as e:
        errmess = e.stderr.decode()
        if errmess:
            return {'code': -1, 'error': errmess}
        else:
            try:
                fo = open('data/output0.txt')
                errmess = fo.read()
                fo.close()
                return {'code': -1, 'error': errmess}
            except IOError:
                return {'code': -1, 'error': "Unknown error."}
    for i in range(N_TESTS):
        output = outputs[i]
        expected = expecteds[i]
        if output != expected:
            fi = open(f'data/input{i}.txt')
            test = fi.read()
            fi.close()
            return {'code': 1, 'input': test, 'expected': expected, 'output': output}
    return {'code': 0}


SECRET = 'eb8d5498f143d53df55ce37fb3d944a3076f757b1268bfb4ce54959f3c2b5c1d'


if __name__ == '__main__':
    while True:
        try:
            with connect("ws://0.0.0.0:80/ws") as ws:
                ws.send(SECRET)
                if ws.recv(3) != 'ok':
                    raise Exception("Connection error")
                print("Connected. Start scanning...", flush=True)
                while True:
                    time.sleep(3)
                    ws.ping()
                    d = sorted(os.listdir('queue'))
                    if len(d) != 0:
                        f = d[0]
                        user_id = re.match('[0-9]+_([0-9a-f]{64}).txt', f).groups()[0]
                        t1 = time.time()
                        print(f"Do for {user_id}", flush=True)
                        resp = do_test(f)
                        resp['time'] = time.time() - t1
                        resp['tests'] = N_TESTS
                        os.remove('queue/' + f)
                        resp['user_id'] = user_id
                        while True:
                            try:
                                ws.ping()
                                ws.send(json.dumps(resp))
                                break
                            except ConnectionClosed as e:
                                print("in", e)
                                ws = connect("ws://0.0.0.0:80/ws")
                                ws.send(SECRET)
                                if ws.recv(3) != 'ok':
                                    raise Exception("Connection error")
                        print("Done", flush=True)
        except ConnectionClosed:
            pass
        except Exception as e:
            print("out", e)
            time.sleep(3)
