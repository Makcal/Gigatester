import pathlib
import shutil
import time
from abc import ABC, abstractmethod
import os
from os import PathLike
from pathlib import Path

import docker
import docker.errors

from exceptions import MyContainerError


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
            self.docker.containers.run(
                'openjdk:23-slim-bullseye',
                remove=True, network_mode='none', working_dir='/work', stderr=True,
                volumes=[f'{self.local("prog")}:/prog:ro',
                         f'{self.local("data")}:/data'],
                command=f'/bin/bash /data/run_java.sh {n_tests} /prog/Main.java Main'
            )

            output = []
            for i in range(n_tests):
                file = open(self.local('data', f'output{i}.txt'))
                output.append(file.read().strip())
                file.close()
            return output

        except docker.errors.ContainerError as e:
            error_message = e.stderr.decode()
            if error_message:
                raise MyContainerError(error_message)
            else:
                try:
                    file = open(self.local('data', 'output0.txt'))
                    error_message = file.read()
                    file.close()
                    raise MyContainerError(error_message)
                except IOError:
                    raise MyContainerError("Unknown error.")


_docker_engine = docker.DockerClient(base_url='unix://home/max/.docker/desktop/docker.sock')

java_tester = JavaTester(pathlib.Path().absolute(), _docker_engine)

__all__ = ['AbsTester', 'java_tester']
