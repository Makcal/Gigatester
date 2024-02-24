import pathlib
import typing

from checkers import AbsChecker, WordConcatenatorChecker
from generators import GeneratorDsaWeek3A, GeneratorDsaWeek3B, GeneratorDsaWeek4A, GeneratorDsaWeek5A, \
    GeneratorDsaWeek5B, GeneratorAgla2Task5
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


DSA_week3A = Task(GeneratorDsaWeek3A(), ('DSA_week3A.java', TESTER_DICT['java']), ComparisonChecker(), 100, 60)
DSA_week3B = Task(GeneratorDsaWeek3B(), ('DSA_week3B.java', TESTER_DICT['java']), ComparisonChecker(), 100, 60)
DSA_week4A = Task(GeneratorDsaWeek4A(), ('DSA_week4A.cpp', TESTER_DICT['cpp']), ComparisonChecker(), 60, 60)
DSA_week5A = Task(GeneratorDsaWeek5A(), ('DSA_week5A.cpp', TESTER_DICT['cpp']), WordConcatenatorChecker(), 100, 120)
DSA_week5B = Task(GeneratorDsaWeek5B(), ('DSA_week5B.cpp', TESTER_DICT['cpp']), ComparisonChecker(), 100, 100)

TASK_DICT: dict[str, Task] = {
    'DSA_week3A': DSA_week3A,
    'DSA_week3B': DSA_week3B,
    'DSA_week4A': DSA_week4A,
    'DSA_week5A': DSA_week5A,
    'DSA_week5B': DSA_week5B,
}

__all__ = ['Task', 'TASK_DICT']
