__all__ = ["TesterResult", "Success", "Difference", "Timeout", "Error"]

from abc import ABC, abstractmethod
from typing import Any


class TesterResult(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass


class Success(TesterResult):
    def __init__(self, n_tests: int):
        self.n_tests = n_tests

    def to_dict(self) -> dict:
        return {'code': 0, 'tests': self.n_tests}


class Difference(TesterResult):
    def __init__(
        self,
        n_tests: int,
        inputs: list[str],
        expecteds: list[str],
        outputs: list[str],
        interactive: bool = False,
    ):
        self.inputs = inputs
        self.expecteds = expecteds
        self.outputs = outputs
        self.n_tests = n_tests
        self.interactive = interactive

    def to_dict(self) -> dict:
        return {
            'code': 1,
            'tests': self.n_tests,
            'input': self.inputs,
            'expected': self.expecteds,
            'output': self.outputs,
            'interactive': self.interactive,
        }


class Timeout(TesterResult):
    def __init__(self, n_tests: int, inputs: list[str] | None = None):
        self.inputs = inputs
        self.n_tests = n_tests

    def to_dict(self) -> dict:
        result: dict[str, Any] = {'code': 2, 'tests': self.n_tests}
        if self.inputs is not None:
            result['input'] = self.inputs
        return result


class Error(TesterResult):
    def __init__(self, message: str) -> None:
        self.message = message

    def to_dict(self) -> dict:
        return {'code': -1, 'error': self.message}

