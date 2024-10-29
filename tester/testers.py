from abc import ABC, abstractmethod
from multiprocessing.synchronize import Event
from multiprocessing.connection import Connection
import os
from os import PathLike
import pathlib
from pathlib import Path
import shutil
import time
from typing import Callable, Literal

import docker
import docker.errors
from docker.models.containers import Container

from exceptions import MyContainerError, MyTimeoutError


TEST_SEPARATOR_PATTERN = "<<<ARBUZ{}ARBUZ>>>"

def _parse_log_per_test(
        log: str,
        output: list[str],
        n_tests: int,
        separator_pattern: str,
        check_function: Callable[[str], bool]
):
    """
    Parses log and prepends it to output
    """
    p = 0
    for i in range(n_tests):
        separator = separator_pattern.format(i)
        p = log.find(separator, p)
        if p == -1:
            break
        p += len(separator)
        p_next = log.find(separator_pattern.format(i+1), p)
        if p_next == -1:
            p_next = len(log)
        extra = log[p:p_next].strip()
        if check_function(extra):
            output[i] = extra + '\n\n' + output[i]
        p = p_next


class AbsTester(ABC):
    def __init__(self, work_dir: Path, docker_engine: docker.DockerClient):
        self.work_dir = work_dir.absolute()
        self.docker = docker_engine

    def local(self, *p: str) -> Path:
        return self.work_dir.joinpath(*p)

    def clean(self):
        shutil.rmtree(self.local('prog'), ignore_errors=True)
        self.local('prog').mkdir()
        for i in os.listdir(self.local('data')):
            if i.startswith('output'):
                os.remove(self.local('data', i))

    def start(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        self.clean()
        self.setup(file_name)

        log = self.run_container_for_tests(n_tests, timeout)
        return self.process_log(self.read_output(n_tests), log)

    def start_interactive(
            self,
            n_tests: int,
            timeout: int,
            file_name: PathLike[str],
            stop: Event,
            log_pipe: Connection | None = None,
    ) -> str:
        self.clean()
        self.setup_interactive(file_name)

        container: Container | None = None
        try:
            container = self.start_interactive_container(n_tests)
            stop.wait(timeout)
            time.sleep(0.1)
            container.reload()
            if container.status != 'exited':
                raise MyTimeoutError()

            log = container.logs().decode()
            if log_pipe is not None:
                log_pipe.send(log)
                log_pipe.close()
            return log
        finally:
            if container is not None:
                container.remove(force=True)

    @abstractmethod
    def setup(self, file_name: PathLike[str]):
        pass

    @abstractmethod
    def run_container_for_tests(self, n_tests: int, timeout: int | float) -> str:
        pass

    @abstractmethod
    def setup_interactive(self, file_name: PathLike[str]):
        pass

    @abstractmethod
    def start_interactive_container(self, n_tests: int) -> Container:
        pass

    def process_log(self, outputs: list[str], log: str) -> list[str]:
        if log:
            raise MyContainerError(log)
        return outputs

    def copy_script_and_code(self, file_name: PathLike[str], script_name: str, moved_file_name: str):
        shutil.copyfile(self.local('chore', script_name), self.local('data', script_name))
        shutil.copyfile(file_name, self.local('prog', moved_file_name))

    def start_container(self, container_name: str, command: str) -> Container:
        return self.docker.containers.run(
            container_name,
            detach=True, network_mode='none', working_dir='/work', stderr=True,
            volumes=[f'{self.local("prog")}:/prog:ro',
                     f'{self.local("data")}:/data'],
            command=command,
        )

    def run_container(self, container_name: str, command: str, timeout: int | float) -> str:
        container: Container | None = None
        try:
            container = self.start_container(container_name, command)
            t_start = time.time()
            while container.status != 'exited':
                # refresh info
                container.reload()
                time.sleep(1)
                if time.time() - t_start > timeout:
                    container.stop(timeout=5)
                    raise MyTimeoutError()

            return container.logs().decode()

        finally:
            if container is not None:
                try:
                    # I will be happy if someone explain to me why the second container
                    # does not produce output without a delay.
                    # Works fine on the server
                    if os.getenv('DEBUG'):
                        time.sleep(5)

                    container.remove(force=True)
                except docker.errors.NotFound:
                    pass

    def read_output(self, n_tests: int) -> list[str]:
        output = []
        for i in range(n_tests):
            try:
                with open(self.local('data', f'output{i}.txt')) as file:
                    output.append(file.read().strip())
            except FileNotFoundError:
                output.append("")
        return output


class JavaTester(AbsTester):
    def setup(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_java.sh', 'Main.java')

    def run_container_for_tests(self, n_tests: int, timeout: int | float) -> str:
        return self.run_container(
            'gigatester/java:latest',
            f'/bin/bash /data/run_java.sh {n_tests} /prog/Main.java Main',
            timeout,
        )

    def setup_interactive(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_java_int.sh', 'Main.java')

    def start_interactive_container(self, n_tests: int) -> Container:
        return self.start_container(
            "gigatester/java:latest",
            f'/bin/bash /data/run_java_int.sh {n_tests} /prog/Main.java Main',
        )


class CppTester(AbsTester):
    version: str

    def __init__(self, work_dir: Path, docker_engine: docker.DockerClient, /, *, version: str):
        super().__init__(work_dir, docker_engine)
        self.version = version

    def setup(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_cpp.sh', 'main.cpp')

    def run_container_for_tests(self, n_tests: int, timeout: int | float) -> str:
        return self.run_container(
            'gigatester/cpp:latest',
            f'/bin/bash /data/run_cpp.sh {n_tests} {self.version} /prog/main.cpp',
            timeout,
        )

    def process_log(self, outputs: list[str], log: str) -> list[str]:
        # Add segmentation faults etc. from the log
        _parse_log_per_test(log, outputs, len(outputs), TEST_SEPARATOR_PATTERN, lambda extra: bool(extra))
        return outputs

    def setup_interactive(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_cpp_int.sh', 'main.cpp')

    def start_interactive_container(self, n_tests: int) -> Container:
        return self.start_container(
            "gigatester/cpp:latest",
            f'/bin/bash /data/run_cpp_int.sh {n_tests} {self.version} /prog/main.cpp',
        )


class CSharpTester(AbsTester):
    def setup(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_cs.sh', 'main.cs')
        shutil.copyfile(self.local('chore', 'cs.csproj'), self.local('data', 'cs.csproj'))

    def run_container_for_tests(self, n_tests: int, timeout: int | float) -> str:
        return self.run_container(
            'gigatester/cs:latest',
            f'/bin/bash /data/run_cs.sh {n_tests} /prog/main.cs Program',
            timeout,
        )

    def process_log(self, outputs: list[str], log: str) -> list[str]:
        # Add errors etc. from the log
        # Exclude 'core dumped' since dotnet prints its own error message
        _parse_log_per_test(
            log,
            outputs,
            len(outputs),
            TEST_SEPARATOR_PATTERN,
            lambda extra: bool(extra) and 'core dumped' not in extra,
        )
        return outputs

    def setup_interactive(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_cs_int.sh', 'main.cs')
        shutil.copyfile(self.local('chore', 'cs.csproj'), self.local('data', 'cs.csproj'))

    def start_interactive_container(self, n_tests: int) -> Container:
        return self.start_container(
            "gigatester/cs:latest",
            f'/bin/bash /data/run_cs_int.sh {n_tests} /prog/main.cs Program',
        )


class PythonTester(AbsTester):
    def setup(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_py.sh', 'main.py')

    def run_container_for_tests(self, n_tests: int, timeout: int | float) -> str:
        return self.run_container(
            'gigatester/py:latest',
            f'/bin/bash /data/run_py.sh {n_tests} /prog/main.py',
            timeout,
        )

    def setup_interactive(self, file_name: PathLike[str]):
        self.copy_script_and_code(file_name, 'run_py_int.sh', 'main.py')

    def start_interactive_container(self, n_tests: int) -> Container:
        return self.start_container(
            "gigatester/py:latest",
            f'/bin/bash /data/run_py_int.sh {n_tests} /prog/main.py',
        )


if os.getenv('DEBUG'):
    _docker_engine = docker.DockerClient(base_url='unix://home/max/.docker/desktop/docker.sock')
else:
    _docker_engine = docker.DockerClient()

work_dir = pathlib.Path().absolute()
java_tester = JavaTester(work_dir, _docker_engine)
cpp17_tester = CppTester(work_dir, _docker_engine, version='17')
cpp20_tester = CppTester(work_dir, _docker_engine, version='20')
cs_tester = CSharpTester(work_dir, _docker_engine)
py_tester = PythonTester(work_dir, _docker_engine)

TESTER_DICT: dict[Literal['java', 'cpp17', 'cpp20', 'cs', 'py'], AbsTester] = {
    'java': java_tester,
    'cpp17': cpp17_tester,
    'cpp20': cpp20_tester,
    'cs': cs_tester,
    'py': py_tester,
}

__all__ = ['AbsTester', 'TESTER_DICT']
