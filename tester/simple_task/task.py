import typing

from ..tasks.task_base import TaskBase

if typing.TYPE_CHECKING:
    from .abs_generator import AbsGenerator
    from ..testers import AbsTester
    from .checkers import AbsChecker


class SimpleTask(TaskBase):
    def __init__(
            self,
            generator: "AbsGenerator",
            checker: "AbsChecker",
            reference: tuple[str, "AbsTester"],
            n_tests: int,
            timeout: int,
    ):
        super().__init__(reference, n_tests)
        self.generator = generator
        self.checker = checker
        self.timeout = timeout

