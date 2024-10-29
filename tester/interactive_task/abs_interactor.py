__all__ = [
    "AbsCommunicator",
    "NamedPipeCommunicator",
    "AbsInteractor",
    "AbsLoggingInterractor",
    "LoggingCommunicatorDecorator"
]

from abc import ABC, abstractmethod
from pathlib import Path
import os
import shutil
from typing import Any


class AbsCommunicator(ABC):
    def setup(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def finish(self):
        pass

    @abstractmethod
    def receive_line(self) -> str:
        pass

    @abstractmethod
    def send(self, message: str, append_newline = True) -> None:
        pass

    def __enter__(self):
        self.start()

    def __exit__(self, *_):
        self.finish()


class NamedPipeCommunicator(AbsCommunicator):
    def __init__(self, workdir: str | os.PathLike = 'data'):
        workdir = Path(workdir)
        self.prog_in_path = workdir / 'prog_in'
        self.prog_out_path = workdir / 'prog_out'
        self.pipe = None

    def setup(self):
        shutil.rmtree(self.prog_in_path, ignore_errors=True)
        shutil.rmtree(self.prog_out_path, ignore_errors=True)
        prev_umask = os.umask(0)
        os.mkfifo(self.prog_in_path)
        os.mkfifo(self.prog_out_path)
        os.umask(prev_umask)

    def start(self):
        prog_in = open(self.prog_in_path, 'w')
        prog_out = open(self.prog_out_path)
        self.pipe = prog_out, prog_in

    def finish(self):
        if self.pipe is None:
            raise RuntimeError("Start session first")
        self.pipe[0].close()
        self.pipe[1].close()
        self.pipe = None

    # analoge of `input()` - the only high-level way to handle input in Python (no scanners)
    def receive_line(self) -> str:
        if self.pipe is None:
            raise RuntimeError("Start session first")
        return self.pipe[0].readline()

    def send(self, message: str, append_newline = True) -> None:
        if self.pipe is None:
            raise RuntimeError("Start session first")
        if append_newline and (not message or message[-1] != '\n'):
            message += '\n'
        self.pipe[1].write(message)
        self.pipe[1].flush()


class LoggingCommunicatorDecorator(AbsCommunicator):
    def __init__(self, communicator: AbsCommunicator):
        self.communicator = communicator
        self.log = ""

    def append_log(self, s: str):
        self.log += s
        if s and s[-1] != '\n':
            self.log += '\n'

    def get_log(self) -> str:
        return self.log

    def reset(self):
        self.log = ""

    def start(self):
        self.reset()
        self.communicator.start()

    def finish(self):
        self.communicator.finish()

    def receive_line(self) -> str:
        message = self.communicator.receive_line()
        self.append_log(message)
        return message

    def send(self, message: str, append_newline = True) -> None:
        self.communicator.send(message, append_newline)
        self.append_log(message)


class AbsInteractor(ABC):
    def __init__(self, communicator: AbsCommunicator):
        self.communicator = communicator

    @abstractmethod
    def run(self, env: Any) -> bool:
        """
        :param env: any start data
        :return: success
        """
        pass

    @abstractmethod
    def get_log(self) -> str:
        pass


class AbsLoggingInterractor(AbsInteractor):
    def __init__(self, communicator: AbsCommunicator):
        logger = LoggingCommunicatorDecorator(communicator)
        super().__init__(logger)
        self.logger = logger

    @abstractmethod
    def run_test(self, env: Any) -> bool:
        pass

    def run(self, env: Any) -> bool:
        with self.communicator:
            success = self.run_test(env)
            return success

    def get_log(self) -> str:
        return self.logger.get_log()

