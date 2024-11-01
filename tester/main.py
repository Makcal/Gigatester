import ctypes
from multiprocessing import Event, Manager, Pipe, Process
from multiprocessing.managers import ValueProxy
import os
import pathlib
import re
import select
import shutil
import time
from typing import Any, Callable
import logging

import requests

from .exceptions import MyContainerError, MyTimeoutError
from .interactive_task import (
    AbsCommunicator,
    AbsInteractor,
    InteractiveTask,
    LoggingCommunicatorDecorator,
    NamedPipeCommunicator,
)
from .results import *
from .simple_task import AbsChecker, AbsGenerator, SimpleTask
from .tasks.task_dict import TASK_DICT
from .testers import AbsTester, TESTER_DICT, split_log_by_tests


SECRET = os.environ["SECRET"]
logging.basicConfig()
logger = logging.Logger('tester', os.environ.get("LOG_LEVEL", logging.DEBUG))
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
log_handler = logging.StreamHandler()
log_handler.formatter = formatter
logger.addHandler(log_handler)


def generate_input(generator: AbsGenerator, n: int):
    shutil.rmtree('data', ignore_errors=True)
    os.mkdir('data')
    for i in range(n):
        fin = open(f'data/input{i}.txt', 'w')
        test = generator.generate()
        fin.write(test)
        fin.close()


def compare(checker: AbsChecker, output: list[str], expected: list[str], n: int) -> TesterResult:
    different_inputs = []
    different_outputs = []
    different_expected = []
    different = False
    for i in range(n):
        with open(f'data/input{i}.txt') as fin:
            test = fin.read()
        test_output = output[i]
        test_expected = expected[i]

        ok = False
        try:
            ok = checker.check(test_expected, test_output, test)
        except Exception:
            pass
        if not ok:
            different = True
            different_inputs.append(test)
            different_outputs.append(test_output)
            different_expected.append(test_expected)
    if different:
        return Difference(n, different_inputs, different_expected, different_outputs)
    return Success(n)


def test_simple(task: SimpleTask, tester: AbsTester, file: str) -> TesterResult:
    # try 1 test
    generate_input(task.generator, 1)
    try:
        first_expected = task.default_tester.start(1, task.reference_file, 20)
        first_output = tester.start(1, pathlib.Path('queue') / file, 20)
    except MyTimeoutError:
        with open(f'data/input0.txt') as fin:
            test = fin.read()
        return Timeout(1, [test])
    if not isinstance(first_res := compare(task.checker, first_output, first_expected, 1), Success):
        return first_res

    # try the full set of tests if the first was successfull
    generate_input(task.generator, task.n_tests)
    expected = task.default_tester.start(task.n_tests, task.reference_file, task.timeout)
    output = tester.start(
        task.n_tests,
        pathlib.Path('queue') / file,
        task.timeout,
    )

    return compare(task.checker, output, expected, task.n_tests)


def interactor_process(
        log: ValueProxy[str],
        success: ValueProxy[bool],
        communicator: AbsCommunicator,
        interactor_factory: Callable[[AbsCommunicator], AbsInteractor],
        environment: Any,
):
    class SharingCommunicatorDecorator(LoggingCommunicatorDecorator):
        def append_log(self, s: str):
            super().append_log(s)
            log.value = self.get_log()

    interactor = interactor_factory(SharingCommunicatorDecorator(communicator))
    try:
        success.value = interactor.run(environment)
    except Exception:
        pass


def timeout_read(source: str, timeout: float) -> str | None:
    fd = os.open(source, os.O_NONBLOCK)
    poll = select.poll()
    poll.register(fd)
    poll_result = poll.poll(timeout * 1000)
    if poll_result and poll_result[0][1] & select.POLLIN != 0:
        msg = os.read(fd, 1024).decode()
        os.close(fd)
        return msg
    os.close(fd)
    return None


def run_interactive_program(
        n_tests: int,
        environments: list[Any],
        one_timeout: int,
        task: InteractiveTask,
        tester: AbsTester,
        file: os.PathLike
) -> list[tuple[bool, str]]:
    shutil.rmtree('data', ignore_errors=True)
    os.mkdir('data')
    prev_umask = os.umask(0)
    os.mkfifo('data/to_cont')
    os.mkfifo('data/to_py')
    os.umask(prev_umask)
    interactor_communicator = NamedPipeCommunicator()
    interactor_communicator.setup()

    log_pipe_read, log_pipe_write = Pipe(duplex=False)
    start_timeout = 15 if tester is not TESTER_DICT['cs'] else 25
    container_manager = Process(
        target=tester.start_interactive,
        args=(
            n_tests,
            start_timeout + int(one_timeout * 1.5 * n_tests),
            file,
            log_pipe_write,
        ),
    )
    container_manager.start()
    try:
        container_message = timeout_read('data/to_py', start_timeout)
        if container_message is None:
            raise RuntimeError('Container has not started')
        container_message = container_message.strip()
        if container_message == "CompilationError":
            if log_pipe_read.poll(5):
                return [(False, log_pipe_read.recv())] * n_tests
            raise MyContainerError("")
        elif container_message != "Start":
            raise MyContainerError(container_message)

        results: list[tuple[bool, str]] = []
        for i in range(len(environments)):
            with open('data/to_cont', 'w') as p:
                p.write('next\n')
            with Manager() as manager:
                log = manager.Value(ctypes.c_wchar_p, "")
                success = manager.Value(ctypes.c_bool, False)
                interactor = Process(
                    target=interactor_process,
                    args=(
                        log,
                        success,
                        interactor_communicator,
                        task.interactor_factory,
                        environments[i],
                    ),
                )
                interactor.start()
                interactor.join(one_timeout)

                if interactor.exitcode is None:
                    interactor.terminate()
                    interactor.join()
                    results.append((False, log.value + "\nTimeout..."))
                else:
                    results.append((success.value, log.value))
                with open('data/to_cont', 'w') as p:
                    p.write('stop')

        if log_pipe_read.poll(1):
            full_outputs = split_log_by_tests(log_pipe_read.recv(), [r[1] for r in results], n_tests)
            results = [(results[i][0], full_outputs[i]) for i in range(len(results))]
        return results

    finally:
        container_manager.join()


def test_interactive(task: InteractiveTask, tester: AbsTester, file: str) -> TesterResult:
    file_path = pathlib.Path('queue') / file

    # try 1 test
    environment = task.env_generator.generate()
    try:
        result = run_interactive_program(
            1,
            [environment],
            task.one_timeout,
            task,
            tester,
            file_path
        )[0]
        if not result[0]:
            correct_example = run_interactive_program(
                1,
                [environment],
                task.one_timeout,
                task,
                task.default_tester,
                task.reference_file
            )[0]
            if not correct_example[0]:
                logger.error(f"Reference program {task.reference_file} failed")
            return Difference(
                1,
                [task.env_to_string(environment) or ""],
                [correct_example[1]],
                [result[1]],
                interactive=True,
            )
    except MyTimeoutError:
        env_text = task.env_to_string(environment)
        return Timeout(1, [env_text] if env_text is not None else None)

    # run the full set of tests
    environments = [task.env_generator.generate() for _ in range(task.n_tests)]
    result = run_interactive_program(
        task.n_tests,
        environments,
        task.one_timeout,
        task,
        tester,
        file_path
    )
    errored_results: list[tuple[Any, str]] = []
    for i in range(task.n_tests):
        if not result[i][0]:
            errored_results.append((environments[i], result[i][1]))
    if not errored_results:
        return Success(task.n_tests)

    correct = run_interactive_program(
        len(errored_results),
        [er[0] for er in errored_results],
        task.one_timeout,
        task,
        task.default_tester,
        task.reference_file,
    )
    if not all(map(lambda r: r[0], correct)):
        logger.error(f"Reference program {task.reference_file} failed")
    return Difference(
        task.n_tests,
        [task.env_to_string(er[0]) or "" for er in errored_results],
        [r[1] for r in correct],
        [er[1] for er in errored_results],
        interactive=True,
    )


def do_test(tester: AbsTester, task: SimpleTask | InteractiveTask, file: str) -> TesterResult:
    """
    Codes:
    -1 - internal error
    0 - success
    1 - difference found
    2 - timeout error
    """
    try:
        match task:
            case SimpleTask():
                return test_simple(task, tester, file)
            case InteractiveTask():
                return test_interactive(task, tester, file)
    except MyContainerError as e:
        logger.error(f"ContainerError {e}")
        return Error(e.message)
    except MyTimeoutError:
        return Timeout(task.n_tests)
    except Exception as e:
        logger.error(f"Critical error {type(e)} {e}")
        return Error("Critical error")


def main():
    while True:
        try:
            logger.info("Connecting...")
            while True:
                try:
                    hello = requests.post("http://0.0.0.0:80/ws_hello", json={'token': SECRET})
                    if hello.text == 'ok':
                        break
                    raise RuntimeError("Authorization failed!")
                except requests.RequestException as e:
                    logger.warning(f"Connection failed ({type(e)}). Trying again...")
                time.sleep(2)
            logger.info("Authorized. Start scanning...")

            while True:
                queue = sorted(os.listdir('queue'))
                if len(queue) != 0:
                    first = queue[0]
                    # timestamp, user id, task, language
                    tasks = '|'.join(t for t in TASK_DICT)
                    langs = '|'.join(t for t in TESTER_DICT)
                    match_ = re.match('[0-9]+_([0-9a-f]{64})_(%s)_(%s)\\.txt' % (tasks, langs), first)
                    if not match_:
                        logger.error(f"Trash detected: {first}")
                        time.sleep(2)
                        continue
                    query_info = match_.groups()
                    user_id = query_info[0]
                    task = TASK_DICT[query_info[1]]
                    tester = TESTER_DICT[query_info[2]] # type: ignore

                    time_start = time.time()
                    logger.info(f"Do {query_info[1]} on {query_info[2]} for {user_id}")
                    resp = do_test(tester, task, first).to_dict()
                    work_time = time.time() - time_start
                    logger.info(f"Done: {work_time}")

                    resp['task'] = query_info[1]
                    resp['language'] = query_info[2]
                    resp['time'] = work_time
                    resp['user_id'] = user_id
                    os.remove('queue/' + first)

                    while True:
                        try:
                            resp = requests.post("http://0.0.0.0/ws", json={'token': SECRET, 'data': resp})
                            if resp.text == 'ok':
                                logger.info("Submitted")
                                break
                            logger.error(f"Can't submit: HTTP code {resp.status_code}")
                        except requests.RequestException as e:
                            logger.error(f"Can't submit: {type(e)} {e}")
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Stopped")
            exit()
        except Exception as e:
            logger.error(f"Error: {type(e)} {e}")
            time.sleep(3)


if __name__ == '__main__':
    main()

