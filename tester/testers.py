import pathlib
import shutil
import time
from abc import ABC, abstractmethod
import os
from os import PathLike
from pathlib import Path
from typing import Literal

import docker
import docker.errors
from docker.models.containers import Container

from exceptions import MyContainerError, MyTimeoutError


class AbsTester(ABC):
    def __init__(self, work_dir: Path, docker_engine: docker.DockerClient):
        self.work_dir = work_dir.absolute()
        self.docker = docker_engine

    def local(self, *p: str) -> Path:
        return self.work_dir.joinpath(*p)

    @abstractmethod
    def _test(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        pass

    def clean(self):
        shutil.rmtree(self.local('prog'))
        self.local('prog').mkdir()
        for i in os.listdir(self.local('data')):
            if i.startswith('output'):
                os.remove(self.local('data', i))

    def start(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        self.clean()
        return self._test(n_tests, file_name, timeout)


class JavaTester(AbsTester):
    def _test(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        shutil.copyfile(self.local('chore', 'run_java.sh'), self.local('data', 'run_java.sh'))
        shutil.copyfile(file_name, self.local('prog', 'Main.java'))

        try:
            d: Container = self.docker.containers.run(
                'gigatester/java:latest',
                detach=True, network_mode='none', working_dir='/work', stderr=True,
                volumes=[f'{self.local("prog")}:/prog:ro',
                         f'{self.local("data")}:/data'],
                command=f'/bin/bash /data/run_java.sh {n_tests} /prog/Main.java Main'
            )
            t1 = time.time()
            while d.status != 'exited':
                d.reload()
                time.sleep(1)
                if time.time() - t1 > timeout:
                    d.stop(timeout=5)
                    raise MyTimeoutError()

            if d.logs():
                raise MyContainerError(d.logs().decode())

            output = []
            for i in range(n_tests):
                try:
                    with open(self.local('data', f'output{i}.txt')) as file:
                        output.append(file.read().strip())
                except FileNotFoundError:
                    output.append("")

            # I will be happy if someone explain to me why the second container does not produce output without a delay
            # works fine on the server
            if os.getenv('DEBUG'):
                time.sleep(5)

            return output

        except docker.errors.ContainerError as e:
            error_message = e.stderr.decode()
            if error_message:
                return [error_message] + ['' for _ in range(n_tests-1)]
            else:
                try:
                    file = open(self.local('data', 'output0.txt'))
                    error_message = file.read()
                    file.close()
                    return [error_message] + ['' for _ in range(n_tests-1)]
                except IOError:
                    raise MyContainerError("Unknown error.")

        finally:
            if 'd' in locals():
                try:
                    # noinspection PyUnboundLocalVariable
                    d.remove()
                except docker.errors.NotFound:
                    pass


class CppTester(AbsTester):
    version: str
    test_separator_pattern = "<<<ARBUZ{}ARBUZ>>>"

    def __init__(self, work_dir: Path, docker_engine: docker.DockerClient, /, *, version: str):
        super().__init__(work_dir, docker_engine)
        self.version = version

    def _test(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        shutil.copyfile(self.local('chore', 'run_cpp.sh'), self.local('data', 'run_cpp.sh'))
        shutil.copyfile(file_name, self.local('prog', 'main.cpp'))

        try:
            d: Container = self.docker.containers.run(
                'gigatester/cpp:latest',
                detach=True, network_mode='none', working_dir='/work', stderr=True,
                volumes=[f'{self.local("prog")}:/prog:ro',
                         f'{self.local("data")}:/data'],
                command=f'/bin/bash /data/run_cpp.sh {n_tests} {self.version} /prog/main.cpp main'
            )
            t1 = time.time()
            while d.status != 'exited':
                d.reload()
                time.sleep(1)
                if time.time() - t1 > timeout:
                    d.stop(timeout=5)
                    raise MyTimeoutError()

            output = []
            for i in range(n_tests):
                try:
                    with open(self.local('data', f'output{i}.txt')) as file:
                        output.append(file.read().strip())
                except FileNotFoundError:
                    output.append("")

            logs: str = d.logs().decode()
            p = 0
            for i in range(n_tests):
                separator = CppTester.test_separator_pattern.format(i)
                p = logs.find(separator, p)
                if p == -1:
                    p = len(logs)
                else:
                    p += len(separator)
                p_next = logs.find(CppTester.test_separator_pattern.format(i+1), p)
                if p_next == -1:
                    p_next = len(logs)
                extra = logs[p:p_next].strip()
                if extra:
                    output[i] = extra + '\n\n' + output[i]
                p = p_next

            # I will be happy if someone explain to me why the second container does not produce output without a delay
            # works fine on the server
            if os.getenv('DEBUG'):
                time.sleep(5)

            return output

        except docker.errors.ContainerError as e:
            error_message = e.stderr.decode()
            if error_message:
                return [error_message] + ['' for _ in range(n_tests-1)]
            else:
                try:
                    file = open(self.local('data', 'output0.txt'))
                    error_message = file.read()
                    file.close()
                    return [error_message] + ['' for _ in range(n_tests-1)]
                except IOError:
                    raise MyContainerError("Unknown error.")

        finally:
            if 'd' in locals():
                try:
                    # noinspection PyUnboundLocalVariable
                    d.remove()
                except docker.errors.NotFound:
                    pass


class CSharpTester(AbsTester):
    def _test(self, n_tests: int, file_name: PathLike[str], timeout: int) -> list[str]:
        shutil.copyfile(self.local('chore', 'run_cs.sh'), self.local('data', 'run_cs.sh'))
        shutil.copyfile(self.local('chore', 'cs.csproj'), self.local('data', 'cs.csproj'))
        shutil.copyfile(file_name, self.local('prog', 'main.cs'))

        try:
            d: Container = self.docker.containers.run(
                'gigatester/cs:latest',
                detach=True, network_mode='none', working_dir='/work', stderr=True,
                volumes=[f'{self.local("prog")}:/prog:ro',
                         f'{self.local("data")}:/data'],
                command=f'/bin/bash /data/run_cs.sh {n_tests} /prog/main.cs Program'
            )
            t1 = time.time()
            while d.status != 'exited':
                d.reload()
                time.sleep(1)
                if time.time() - t1 > timeout:
                    d.stop(timeout=5)
                    raise MyTimeoutError()

            output = []
            for i in range(n_tests):
                try:
                    with open(self.local('data', f'output{i}.txt')) as file:
                        output.append(file.read().strip())
                except FileNotFoundError:
                    output.append("")

            logs: str = d.logs().decode()
            p = 0
            for i in range(n_tests):
                separator = CppTester.test_separator_pattern.format(i)
                p = logs.find(separator, p)
                if p == -1:
                    p = len(logs)
                else:
                    p += len(separator)
                p_next = logs.find(CppTester.test_separator_pattern.format(i+1), p)
                if p_next == -1:
                    p_next = len(logs)
                extra = logs[p:p_next].strip()
                if extra and 'core dumped' not in extra:
                    output[i] = extra + '\n\n' + output[i]
                p = p_next

            # I will be happy if someone explain to me why the second container does not produce output without a delay
            # works fine on the server
            if os.getenv('DEBUG'):
                time.sleep(5)

            return output

        except docker.errors.ContainerError as e:
            error_message = e.stderr.decode()
            if error_message:
                return [error_message] + ['' for _ in range(n_tests-1)]
            else:
                try:
                    file = open(self.local('data', 'output0.txt'))
                    error_message = file.read()
                    file.close()
                    return [error_message] + ['' for _ in range(n_tests-1)]
                except IOError:
                    raise MyContainerError("Unknown error.")

        finally:
            if 'd' in locals():
                try:
                    # noinspection PyUnboundLocalVariable
                    d.remove()
                except docker.errors.NotFound:
                    pass


if os.getenv('DEBUG'):
    _docker_engine = docker.DockerClient(base_url='unix://home/max/.docker/desktop/docker.sock')
else:
    _docker_engine = docker.DockerClient()

java_tester = JavaTester(pathlib.Path().absolute(), _docker_engine)
cpp17_tester = CppTester(pathlib.Path().absolute(), _docker_engine, version='17')
cpp20_tester = CppTester(pathlib.Path().absolute(), _docker_engine, version='20')
cs_tester = CSharpTester(pathlib.Path().absolute(), _docker_engine)
TESTER_DICT: dict[Literal['java', 'cpp17', 'cpp20', 'cs'], AbsTester] = {
    'java': java_tester,
    'cpp17': cpp17_tester,
    'cpp20': cpp20_tester,
    'cs': cs_tester,
}

__all__ = ['AbsTester', 'TESTER_DICT']
