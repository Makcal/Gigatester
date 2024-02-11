import pathlib
import typing

from generators import GeneratorWeek3A, GeneratorWeek3B
from testers import java_tester

if typing.TYPE_CHECKING:
    from generators import AbsGenerator
    from testers import AbsTester


class Task:
    def __init__(self, generator: "AbsGenerator", reference: tuple[str, "AbsTester"], n_tests: int, timeout: int):
        self.generator = generator
        self.reference_file: pathlib.Path = pathlib.Path().absolute().joinpath('reference', reference[0])
        self.default_tester = reference[1]
        self.n_tests = n_tests
        self.timeout = timeout


week3A = Task(GeneratorWeek3A(), ('week3A.java', java_tester), 100, 60)
week3B = Task(GeneratorWeek3B(), ('week3B.java', java_tester), 100, 60)
TASK_DICT: dict[str, Task] = {
    'week3A': week3A,
    'week3B': week3B,
}

__all__ = ['Task', 'TASK_DICT']
