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


class AglaIgnoreNegativeZerosChecker(AbsChecker):
    @staticmethod
    def check(expected: str, output: str, input_: str) -> bool:
        output = output.replace('-0.00', '0.00')
        expected = expected.replace('-0.00', '0.00')
        return ComparisonChecker.check(expected, output, input_)
