from abc import ABC, abstractmethod


class AbsChecker(ABC):
    @staticmethod
    @abstractmethod
    def check(expected: str, output: str, input_: str) -> bool:
        pass


class ComparisonChecker(AbsChecker):
    @staticmethod
    def check(expected: str, output: str, input_: str) -> bool:
        expected = expected.strip()
        output = output.strip()
        expected = '\n'.join(s.strip() for s in expected.splitlines())
        output = '\n'.join(s.strip() for s in output.splitlines())
        return expected == output


class WordConcatenatorChecker(AbsChecker):
    @staticmethod
    def check(expected: str, output: str, input_: str) -> bool:
        return expected.replace(' ', '') == output.replace(' ', '')
