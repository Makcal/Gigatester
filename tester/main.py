import json
import os
import pathlib
import re
import shutil
import time

from websockets import ConnectionClosed
from websockets.sync.client import connect

from exceptions import MyContainerError, MyTimeoutError
from tasks import Task, TASK_DICT
from testers import AbsTester, TESTER_DICT


def compare(output: list[str], expected: list[str], n) -> tuple[bool, dict[str, any]]:
    different_inputs = []
    different_outputs = []
    different_expected = []
    different = False
    for i in range(n):
        test_output = output[i]
        test_expected = expected[i]
        if test_output != test_expected:
            fin = open(f'data/input{i}.txt')
            test = fin.read()
            fin.close()

            different = True
            different_inputs.append(test)
            different_outputs.append(test_output)
            different_expected.append(test_expected)
    if different:
        return False, {'code': 1,
                       'input': different_inputs,
                       'expected': different_expected,
                       'output': different_outputs, 'tests': n}
    return True, {'code': 0, 'tests': n}


def do_test(file: str, tester: AbsTester, task: Task) -> dict[str, any]:
    """
    Codes:
    -1 - internal error
    0 - success
    1 - difference found
    2 - timeout error
    """
    try:
        try:
            shutil.rmtree(pathlib.Path().absolute().joinpath('data'))
            shutil.rmtree(pathlib.Path().absolute().joinpath('prog'))
        except FileNotFoundError:
            pass
        pathlib.Path().absolute().joinpath('data').mkdir()
        pathlib.Path().absolute().joinpath('prog').mkdir()
        for i in range(task.n_tests):
            fin = open(f'data/input{i}.txt', 'w')
            test = task.generator.generate()
            fin.write(test)
            fin.close()

        try:
            first_expected = task.default_tester.start(1, task.reference_file, 10)
            first_output = tester.start(1, pathlib.Path().absolute().joinpath('queue', file), 10)
            first_res = compare(first_output, first_expected, 1)
            if not first_res[0]:
                return first_res[1]

            expected = task.default_tester.start(task.n_tests, task.reference_file, task.timeout)
            output = tester.start(task.n_tests, pathlib.Path().absolute().joinpath('queue', file), task.timeout)
        except MyContainerError as e:
            print("ContainerError", e)
            return {'code': -1, 'error': e.message}
        except MyTimeoutError:
            return {'code': 2}

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
                        # timestamp, user id, task, language
                        query_info = re.match('[0-9]+_([0-9a-f]{64})_([a-zA-Z0-9]+)_([a-z]+).txt', first).groups()
                        user_id = query_info[0]
                        task = TASK_DICT[query_info[1]]
                        tester = TESTER_DICT[query_info[2]]

                        time_start = time.time()
                        print(f"Do for {user_id}", flush=True)
                        resp = do_test(first, tester, task)

                        resp['task'] = query_info[1]
                        resp['language'] = query_info[2]
                        resp['time'] = time.time() - time_start
                        resp['user_id'] = user_id
                        os.remove('queue/' + first)

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
            ws.close(reason="KeyboardInterrupt")
            print()
            exit()
        except Exception as e:
            print("out_error", type(e), e)
            time.sleep(3)


if __name__ == '__main__':
    main()
