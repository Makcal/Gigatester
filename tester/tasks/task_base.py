import pathlib
import typing

if typing.TYPE_CHECKING:
    from ..testers import AbsTester


class TaskBase:
    def __init__(
            self,
            reference: tuple[str, "AbsTester"],
            n_tests: int,
    ):
        self.reference_file: pathlib.Path = pathlib.Path().absolute().joinpath('reference', reference[0])
        self.default_tester = reference[1]
        self.n_tests = n_tests

