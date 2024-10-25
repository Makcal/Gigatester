import pathlib
import shutil
import time
from abc import ABC, abstractmethod
import os
from os import PathLike
from pathlib import Path
from typing import Literal, Callable

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

    @abstractmethod
    def _test(self, n_tests: int, timeout: int) -> list[str]:
        pass

    def clean(self):
        shutil.rmtree(self.local('prog'))
        self.local('prog').mkdir()
        for i in os.listdir(self.local('data')):
            if i.startswith('output'):
                os.remove(self.local('data', i))

    def start(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        self.clean()
        self.setup(file_name)
        return self._test(n_tests, timeout)

    @abstractmethod
    def setup(self, file_name: PathLike[str]):
        pass

    def copy_script_and_code(self, file_name: PathLike[str], script_name: str, moved_file_name: str):
        shutil.copyfile(self.local('chore', script_name), self.local('data', script_name))
        shutil.copyfile(file_name, self.local('prog', moved_file_name))

    def run_container(self, container_name: str, command: str, timeout: int | float) -> str:
        container: Container | None = None
        try:
            container = self.docker.containers.run(
                container_name,
                detach=True, network_mode='none', working_dir='/work', stderr=True,
                volumes=[f'{self.local("prog")}:/prog:ro',
                         f'{self.local("data")}:/data'],
                command=command,
            )

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
        super().setup(file_name)
        self.copy_script_and_code(file_name, 'run_java.sh', 'Main.java')

    def _test(self, n_tests: int, timeout: int) -> list[str]:
        log = self.run_container(
            'gigatester/java:latest', f'/bin/bash /data/run_java.sh {n_tests} /prog/Main.java Main', timeout
        )
        if log:
            raise MyContainerError(log)

        return self.read_output(n_tests)


class CppTester(AbsTester):
    version: str

    def __init__(self, work_dir: Path, docker_engine: docker.DockerClient, /, *, version: str):
        super().__init__(work_dir, docker_engine)
        self.version = version

    def setup(self, file_name: PathLike[str]):
        super().setup(file_name)
        self.copy_script_and_code(file_name, 'run_cpp.sh', 'main.cpp')

    def _test(self, n_tests: int, timeout: int) -> list[str]:
        log = self.run_container(
            'gigatester/cpp:latest',
            f'/bin/bash /data/run_cpp.sh {n_tests} {self.version} /prog/main.cpp',
            timeout
        )
        output = self.read_output(n_tests)

        # Add segmentation faults etc. from the log
        _parse_log_per_test(log, output, n_tests, TEST_SEPARATOR_PATTERN, lambda extra: extra)

        return output


class CSharpTester(AbsTester):
    def setup(self, file_name: PathLike[str]):
        super().setup(file_name)
        self.copy_script_and_code(file_name, 'run_cs.sh', 'main.cs')
        shutil.copyfile(self.local('chore', 'cs.csproj'), self.local('data', 'cs.csproj'))

    def _test(self, n_tests: int, timeout: int) -> list[str]:
        log = self.run_container(
            'gigatester/cs:latest', f'/bin/bash /data/run_cs.sh {n_tests} /prog/main.cs Program', timeout
        )
        output = self.read_output(n_tests)

        # Add errors etc. from the log
        # Exclude 'core dumped' since dotnet prints its own error message
        _parse_log_per_test(
            log, output, n_tests, TEST_SEPARATOR_PATTERN, lambda extra: extra and 'core dumped' not in extra
        )

        return output


class PythonTester(AbsTester):
    def setup(self, file_name: PathLike[str]):
        super().setup(file_name)
        self.copy_script_and_code(file_name, 'run_py.sh', 'main.py')

    def _test(self, n_tests: int, timeout: int) -> list[str]:
        log = self.run_container('gigatester/py:latest', f'/bin/bash /data/run_py.sh {n_tests} /prog/main.py', timeout)
        return self.read_output(n_tests)


if os.getenv('DEBUG'):
    _docker_engine = docker.DockerClient(base_url='unix://home/max/.docker/desktop/docker.sock')
else:
    _docker_engine = docker.DockerClient()

java_tester = JavaTester(pathlib.Path().absolute(), _docker_engine)
cpp17_tester = CppTester(pathlib.Path().absolute(), _docker_engine, version='17')
cpp20_tester = CppTester(pathlib.Path().absolute(), _docker_engine, version='20')
cs_tester = CSharpTester(pathlib.Path().absolute(), _docker_engine)
py_tester = PythonTester(pathlib.Path().absolute(), _docker_engine)

TESTER_DICT: dict[Literal['java', 'cpp17', 'cpp20', 'cs', 'py'], AbsTester] = {
    'java': java_tester,
    'cpp17': cpp17_tester,
    'cpp20': cpp20_tester,
    'cs': cs_tester,
    'py': py_tester,
}

__all__ = ['AbsTester', 'TESTER_DICT']
