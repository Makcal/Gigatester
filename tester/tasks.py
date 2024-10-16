import pathlib
import typing

from checkers import *
from generators import *
from testers import TESTER_DICT
from checkers import ComparisonChecker

if typing.TYPE_CHECKING:
    from generators import AbsGenerator
    from testers import AbsTester
    from checkers import AbsChecker


class Task:
    def __init__(
            self,
            generator: "AbsGenerator",
            reference: tuple[str, "AbsTester"],
            checker: AbsChecker,
            n_tests: int,
            timeout: int
    ):
        self.generator = generator
        self.reference_file: pathlib.Path = pathlib.Path().absolute().joinpath('reference', reference[0])
        self.default_tester = reference[1]
        self.n_tests = n_tests
        self.timeout = timeout
        self.checker = checker


# Old tasks, generators, and checkers can be found in older commits.
# Check commits <= 63e4ef836053d09d1256db2af1abb5a5084e66c7

exampleTask = Task(ExampleGenerator(), ('example.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 100, 60)

TASK_DICT: dict[str, Task] = {
    'internal_task_id': exampleTask,
}

__all__ = ['Task', 'TASK_DICT']
