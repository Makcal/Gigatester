__all__ = ["AbsChecker", "ComparisonChecker"]

from abc import ABC, abstractmethod


class AbsChecker(ABC):
    @abstractmethod
    def check(self, expected: str, output: str, input_: str) -> bool:
        pass


class ComparisonChecker(AbsChecker):
    def check(self, expected: str, output: str, input_: str) -> bool:
        expected = expected.strip()
        output = output.strip()
        expected = '\n'.join(s.strip() for s in expected.splitlines())
        output = '\n'.join(s.strip() for s in output.splitlines())
        return expected == output
