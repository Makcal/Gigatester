import pathlib
import typing

from checkers import AbsChecker, WordConcatenatorChecker
from generators import GeneratorWeek3A, GeneratorWeek3B, GeneratorWeek4A, GeneratorWeek5A, GeneratorWeek5B
from testers import TESTER_DICT
from checkers import ComparisonChecker

if typing.TYPE_CHECKING:
    from generators import AbsGenerator
    from testers import AbsTester
    from checkers import AbsChecker


class Task:
    def __init__(
            self, generator: "AbsGenerator",
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


week3A = Task(GeneratorWeek3A(), ('week3A.java', TESTER_DICT['java']), ComparisonChecker(), 100, 60)
week3B = Task(GeneratorWeek3B(), ('week3B.java', TESTER_DICT['java']), ComparisonChecker(), 100, 60)
week4A = Task(GeneratorWeek4A(), ('week4A.cpp', TESTER_DICT['cpp']), ComparisonChecker(), 60, 60)
week5A = Task(GeneratorWeek5A(), ('week5A.cpp', TESTER_DICT['cpp']), WordConcatenatorChecker(), 100, 60)
week5B = Task(GeneratorWeek5B(), ('week5B.cpp', TESTER_DICT['cpp']), ComparisonChecker(), 100, 60)
TASK_DICT: dict[str, Task] = {
    'week3A': week3A,
    'week3B': week3B,
    'week4A': week4A,
    'week5A': week5A,
    'week5B': week5B,
}

__all__ = ['Task', 'TASK_DICT']
