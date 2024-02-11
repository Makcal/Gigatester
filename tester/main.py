import json
import os
import pathlib
import re
import shutil
import time

from websockets import ConnectionClosed
from websockets.sync.client import connect

from exceptions import MyContainerError
from tasks import Task, week3A
from testers import AbsTester, java_tester


def compare(output: list[str], expected: list[str], n):
    for i in range(n):
        test_output = output[i]
        test_expected = expected[i]
        if test_output != test_expected:
            fin = open(f'data/input{i}.txt')
            test = fin.read()
            fin.close()
            return False, {'code': 1, 'input': test, 'expected': test_expected, 'output': test_output}
    return True, {'code': 0}


def do_test(file: str, tester: AbsTester, task: Task) -> dict[str, any]:
    try:
        shutil.rmtree(pathlib.Path().absolute().joinpath('data'))
        pathlib.Path().absolute().joinpath('data').mkdir()
        for i in range(task.n_tests):
            fin = open(f'data/input{i}.txt', 'w')
            test = task.generator.generate()
            fin.write(test)
            fin.close()

        try:
            first_expected = task.default_tester.start(1, task.reference_file, 6)
            time.sleep(5)
            first_output = tester.start(1, pathlib.Path().absolute().joinpath('queue', file), 6)
            res = compare(first_output, first_expected, 1)
            if not res[0]:
                return res[1]

            expected = task.default_tester.start(task.n_tests, task.reference_file, task.timeout)
            # i will be happy if someone explain me why the second container does not produce output without a delay
            # todo: check on the server
            time.sleep(5)
            output = tester.start(task.n_tests, pathlib.Path().absolute().joinpath('queue', file), task.timeout)
        except MyContainerError as e:
            return {'code': -1, 'error': e.message}

        return compare(output, expected, task.n_tests)[1]

    except Exception as e:
        print("Critical error", type(e), e)
        return {'code': -1, 'error': "Critical error"}


SECRET = 'eb8d5498f143d53df55ce37fb3d944a3076f757b1268bfb4ce54959f3c2b5c1d'


def main():
    while True:
        try:
            with connect("ws://0.0.0.0:80/ws") as ws:
                ws.send(SECRET)
                if ws.recv(3) != 'ok':
                    raise Exception("Connection error")
                print("Connected. Start scanning...", flush=True)
                while True:
                    ws.ping()
                    queue = sorted(os.listdir('queue'))
                    if len(queue) != 0:
                        first = queue[0]
                        user_id = re.match('[0-9]+_([0-9a-f]{64}).txt', first).groups()[0]

                        time_start = time.time()
                        print(f"Do for {user_id}", flush=True)
                        resp = do_test(first, java_tester, week3A)
                        resp['time'] = time.time() - time_start
                        resp['tests'] = week3A.n_tests
                        os.remove('queue/' + first)
                        resp['user_id'] = user_id
                        while True:
                            try:
                                ws.ping()
                                ws.send(json.dumps(resp))
                                break
                            except ConnectionClosed as e:
                                print("in_error", type(e), e)
                                ws = connect("ws://0.0.0.0:80/ws")
                                ws.send(SECRET)
                                if ws.recv(3) != 'ok':
                                    raise Exception("Connection error")
                        print("Done", flush=True)
                    time.sleep(3)
        except ConnectionClosed:
            pass
        except KeyboardInterrupt:
            print()
            exit()
        except Exception as e:
            print("out_error", type(e), e)
            time.sleep(3)


if __name__ == '__main__':
    main()
