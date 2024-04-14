import pathlib
import typing

from checkers import AbsChecker, WordConcatenatorChecker, AglaIgnoreNegativeZerosChecker, BalancedTreeChecker, \
    IntersectingSegmentsChecker, MsfChecker
from generators import GeneratorDsaWeek3A, GeneratorDsaWeek3B, GeneratorDsaWeek4A, GeneratorDsaWeek5A, \
    GeneratorDsaWeek5B, GeneratorAgla2Task1, GeneratorAgla2Task2, GeneratorAgla2Task3, GeneratorAgla2Task4, \
    GeneratorAgla2Task5, GeneratorAgla2Task6, GeneratorDsaWeek6A, GeneratorDsaWeek7A, GeneratorDsaWeek8A, \
    GeneratorAgla2Task7, GeneratorSSADTask2, GeneratorDsaWeek11A, GeneratorDsaWeek12A, GeneratorSSADTask3
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
DSA_week4A = Task(GeneratorDsaWeek4A(), ('DSA_week4A.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 60, 60)
DSA_week5A = Task(GeneratorDsaWeek5A(), ('DSA_week5A.cpp', TESTER_DICT['cpp17']), WordConcatenatorChecker(), 100, 120)
DSA_week5B = Task(GeneratorDsaWeek5B(), ('DSA_week5B.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 100, 100)
DSA_week6A = Task(GeneratorDsaWeek6A(), ('DSA_week6A.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 150, 60)
DSA_week7A = Task(GeneratorDsaWeek7A(), ('DSA_week7A.cpp', TESTER_DICT['cpp17']),
                  BalancedTreeChecker(lambda a, b: max(a, b) - 2*min(a, b) <= 1), 150, 60)
DSA_week8A = Task(GeneratorDsaWeek8A(), ('DSA_week8A.cpp', TESTER_DICT['cpp17']), IntersectingSegmentsChecker(), 150, 70)
DSA_week11A = Task(GeneratorDsaWeek11A(), ('DSA_week11A.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 100, 30)
DSA_week12A = Task(GeneratorDsaWeek12A(), ('DSA_week12A.cpp', TESTER_DICT['cpp17']), MsfChecker(), 50, 150)

AGLA_task1 = Task(GeneratorAgla2Task1(), ('AGLA2_task1.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 70, 30)
AGLA_task2 = Task(GeneratorAgla2Task2(), ('AGLA2_task2.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 70, 30)
AGLA_task3 = Task(GeneratorAgla2Task3(), ('AGLA2_task3.cpp', TESTER_DICT['cpp17']), ComparisonChecker(), 70, 40)
AGLA_task4 = Task(GeneratorAgla2Task4(), ('AGLA2_task4.cpp', TESTER_DICT['cpp17']), AglaIgnoreNegativeZerosChecker(), 100, 50)
AGLA_task5 = Task(GeneratorAgla2Task5(), ('AGLA2_task5.cpp', TESTER_DICT['cpp17']), AglaIgnoreNegativeZerosChecker(), 100, 50)
AGLA_task6 = Task(GeneratorAgla2Task6(), ('AGLA2_task6.cpp', TESTER_DICT['cpp17']), AglaIgnoreNegativeZerosChecker(), 100, 50)
AGLA_task7 = Task(GeneratorAgla2Task7(), ('AGLA2_task7.cpp', TESTER_DICT['cpp17']), AglaIgnoreNegativeZerosChecker(), 100, 50)

SSAD_task2 = Task(GeneratorSSADTask2(), ('SSAD_assignment2.cpp', TESTER_DICT['cpp20']), ComparisonChecker(), 300, 90)
SSAD_task3 = Task(GeneratorSSADTask3(), ('SSAD_assignment3.java', TESTER_DICT['java']), ComparisonChecker(), 80, 120)

TASK_DICT: dict[str, Task] = {
    'DSA_week3A': DSA_week3A,
    'DSA_week3B': DSA_week3B,
    'DSA_week4A': DSA_week4A,
    'DSA_week5A': DSA_week5A,
    'DSA_week5B': DSA_week5B,
    'DSA_week6A': DSA_week6A,
    'DSA_week7A': DSA_week7A,
    'DSA_week8A': DSA_week8A,
    'DSA_week11A': DSA_week11A,
    'DSA_week12A': DSA_week12A,
    'AGLA2_task1': AGLA_task1,
    'AGLA2_task2': AGLA_task2,
    'AGLA2_task3': AGLA_task3,
    'AGLA2_task4': AGLA_task4,
    'AGLA2_task5': AGLA_task5,
    'AGLA2_task6': AGLA_task6,
    'AGLA2_task7': AGLA_task7,
    'SSAD_task2': SSAD_task2,
    'SSAD_task3': SSAD_task3,
}

__all__ = ['Task', 'TASK_DICT']
