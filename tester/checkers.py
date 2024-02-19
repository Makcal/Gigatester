from abc import ABC, abstractmethod


class AbsChecker(ABC):
    @staticmethod
    @abstractmethod
    def check(expected: str, output: str, input_: str) -> bool:
        pass


class ComparisonChecker(AbsChecker):
    @staticmethod
    def check(expected: str, output: str, input_: str) -> bool:
        return expected == output


class WordConcatenatorChecker(AbsChecker):
    @staticmethod
    def check(expected: str, output: str, input_: str) -> bool:
        return expected.replace(' ', '') == output.replace(' ', '')
