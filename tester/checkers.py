from abc import ABC, abstractmethod
from typing import Callable
import re


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
        output = re.sub(r'-(0\.0+)(?=\s)', lambda m: m.group(1), output)
        expected = re.sub(r'-(0\.0+)(?=\s)', lambda m: m.group(1), expected)
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
        return (True, max(l_info[1], r_info[1]) + 1, (graph[i][0] if li == -2 else l_info[2]),
                (graph[i][0] if ri == -2 else r_info[3]))

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


class IntersectingSegmentsChecker(AbsChecker):
    def check(self, expected: str, output: str, input_: str) -> bool:
        if "NO INTERSECTIONS" in expected:
            return ComparisonChecker().check(expected, output, input_)

        output = output.splitlines()
        if len(output) != 3 or output[0] != "INTERSECTION":
            return False
        seg1, seg2 = [tuple(int(j) for j in i.split()) for i in output[1:]]

        input_ = input_.splitlines()
        input_ = set(tuple(int(i) for i in j.split()) for j in input_[1:])

        if seg1 not in input_ or seg2 not in input_:
            return False
        if seg1[0] == seg1[2] and seg2[0] == seg2[2]:
            return seg1[0] == seg2[0] and (min(seg1[1], seg1[3]) <= min(seg2[1], seg2[3]) <= max(seg1[1], seg1[3])
                                           or min(seg2[1], seg2[3]) <= min(seg1[1], seg1[3]) <= max(seg2[1], seg2[3]))
        if seg1[0] == seg1[2]:
            seg2, seg1 = seg1, seg2
        if seg2[0] == seg2[2]:
            k = (seg1[1] - seg1[3]) / (seg1[0] - seg1[2])
            b = seg1[1] - k * seg1[0]
            y = k * seg2[0] + b
            y = round(y, 10)
            return min(seg2[1], seg2[3]) <= y <= max(seg2[1], seg2[3]) \
                and min(seg1[0], seg1[2]) <= seg2[0] <= max(seg1[0], seg1[2])

        k1 = (seg1[1] - seg1[3]) / (seg1[0] - seg1[2])
        k2 = (seg2[1] - seg2[3]) / (seg2[0] - seg2[2])
        b1 = seg1[1] - k1 * seg1[0]
        b2 = seg2[1] - k2 * seg2[0]
        x = -(b2 - b1) / (k2 - k1)
        x = round(x, 10)
        return min(seg1[0], seg1[2]) <= x <= max(seg1[0], seg1[2]) and min(seg2[0], seg2[2]) <= x <= max(seg2[0], seg2[2])
