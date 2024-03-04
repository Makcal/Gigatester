from abc import ABC, abstractmethod
from typing import Callable


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


class WordConcatenatorChecker(AbsChecker):
    def check(self, expected: str, output: str, input_: str) -> bool:
        return expected.replace(' ', '') == output.replace(' ', '')


class AglaIgnoreNegativeZerosChecker(AbsChecker):
    def check(self, expected: str, output: str, input_: str) -> bool:
        output = output.replace('-0.00', '0.00')
        expected = expected.replace('-0.00', '0.00')
        return ComparisonChecker().check(expected, output, input_)


class BalancedTreeChecker(AbsChecker):
    bf_check: Callable[[int, int], bool]
    visited: set[int]

    def __init__(self, bf_check: Callable[[int, int], bool]) -> None:
        self.bf_check = bf_check
        self.visited = set()

    def check_balance(self, graph: list[list[int]], i: int) -> tuple[bool, int, int, int]:
        if i == -2:
            return True, 0, -1, 10**9
        if i in self.visited:
            return False, -1, -1, -1
        self.visited.add(i)
        li = graph[i][1] - 1
        ri = graph[i][2] - 1
        if li == -2 and ri == -2:
            return True, 1, graph[i][0], graph[i][0]
        l_info = self.check_balance(graph, li)
        r_info = self.check_balance(graph, ri)
        if not (l_info[0] and r_info[0]) or not self.bf_check(l_info[1], r_info[1]) \
                or not (l_info[3] <= graph[i][0] or li == -2) or not (graph[i][0] <= r_info[2] or ri == -2):
            return False, -1, -1, -1
        return True, max(l_info[1], r_info[1]) + 1, (graph[i][0] if li == -2 else l_info[2]), (graph[i][0] if ri == -2 else r_info[3])

    def check(self, expected: str, output: str, input_: str) -> bool:
        self.visited = set()
        output = output.splitlines()
        if int(output[0]) != int(input_.splitlines()[0]):
            return False
        graph = [list(map(int, line.split())) for line in output[1:-1]]
        root = int(output[-1]) - 1
        checked = self.check_balance(graph, root)[0]
        return checked and len(self.visited) == len(graph) and \
            sorted(i[0] for i in graph) == sorted(int(i) for i in input_.splitlines()[1].split())
