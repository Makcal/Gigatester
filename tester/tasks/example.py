from random import randint
from typing import Any

from ..simple_task import AbsGenerator, SimpleTask
from ..interactive_task import AbsEnvironmentGenerator, AbsLoggingInteractor, AbsEnvironmentPresenter, InteractiveTask
from ..simple_task import ComparisonChecker
from ..testers import TESTER_DICT


class ExampleGenerator(AbsGenerator):
    def generate(self) -> str:
        return str(randint(1, 2))


example_task = SimpleTask(ExampleGenerator(), ComparisonChecker(), ('example.cpp', TESTER_DICT['cpp17']), 100, 30)


"""
Interactive task
"""

class ExampleEnvGenerator(AbsEnvironmentGenerator):
    def generate(self) -> Any:
        return randint(1, 10)


class ExampleEnvPresenter(AbsEnvironmentPresenter):
    def to_string(self, env: Any) -> str:
        return f"{env} was generated\n"


class ExampleInteractor(AbsLoggingInteractor):
    def run_test(self, env: Any) -> bool:
        communicator = self.communicator
        n = int(communicator.receive_line())
        communicator.send(str(env + n))
        n2 = int(communicator.receive_line())
        if n2 != (env + n) * 2:
            return False
        return True


example_interactive_task = InteractiveTask(
    ExampleEnvGenerator(),
    lambda com: ExampleInteractor(com),
    ExampleEnvPresenter(),
    ('example_int.py', TESTER_DICT['py']),
    10,
    1
)

