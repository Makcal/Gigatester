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
        output = re.sub(r'-(0\.0+)(?=\s|$)', lambda m: m.group(1), output)
        expected = re.sub(r'-(0\.0+)(?=\s|$)', lambda m: m.group(1), expected)
        return ComparisonChecker().check(expected, output, input_)


class BalancedTreeChecker(AbsChecker):
    bf_check: Callable[[int, int], bool]
    visited: set[int]

    def __init__(self, bf_check: Callable[[int, int], bool]) -> None:
        self.bf_check = bf_check
        self.visited = set()

    def check_balance(self, graph: list[list[int]], i: int) -> tuple[bool, int, int, int]:
        if i == -2:
            return True, 0, -1, 10 ** 9
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
        return min(seg1[0], seg1[2]) <= x <= max(seg1[0], seg1[2]) and min(seg2[0], seg2[2]) <= x <= max(seg2[0],
                                                                                                         seg2[2])


# DSA week 12 task A
class MsfChecker(AbsChecker):
    class MST:
        vertices: set[int]
        min: int
        weight: int

        def __init__(self):
            self.vertices = set()
            self.weight = 0
            self.min = 99999999

        def add_vertex(self, vertex: int) -> None:
            self.vertices.add(vertex)
            self.min = min(self.min, vertex)

        def add_edge(self, vertex1: int, vertex2: int, weight: int) -> None:
            self.add_vertex(vertex1)
            self.add_vertex(vertex2)
            self.weight += weight

    def check(self, expected: str, output: str, input_: str) -> bool:
        input_ = [line.strip() for line in input_.strip().splitlines()]
        n_vertices, n_edges = map(int, input_[0].split())
        graph = [[0] * n_vertices for _ in range(n_vertices)]
        for i in range(1, n_edges + 1):
            f, t, w = map(int, input_[i].split())
            graph[f - 1][t - 1] = graph[t - 1][f - 1] = w

        expected = [line.strip() for line in expected.strip().splitlines()]
        output = [line.strip() for line in output.strip().splitlines()]
        if expected[0] != output[0]:
            return False
        components = int(expected[0])
        trees1, trees2 = [], []

        line_i = 1
        for i in range(components):
            msf = MsfChecker.MST()
            n_tree_vertices, v = map(int, expected[line_i].split())
            line_i += 1
            msf.add_vertex(v)
            for j in range(n_tree_vertices - 1):
                f, t, w = map(int, expected[line_i].split())
                line_i += 1
                msf.add_edge(f, t, w)
            trees1.append(msf)

        line_i = 1
        for i in range(components):
            msf = MsfChecker.MST()
            n_tree_vertices, v = map(int, output[line_i].split())
            line_i += 1
            if not 1 <= v <= n_vertices:
                return False
            msf.add_vertex(v)
            for j in range(n_tree_vertices - 1):
                f, t, w = map(int, output[line_i].split())
                line_i += 1
                if not 1 <= f <= n_vertices or not 1 <= t <= n_vertices or graph[f - 1][t - 1] != w:
                    return False
                msf.add_edge(f, t, w)
            if len(msf.vertices) != n_tree_vertices:
                return False
            trees2.append(msf)

        check = set()
        for i in trees2:
            if check & i.vertices:
                return False
            check |= i.vertices
        if len(check) != n_vertices:
            return False
        trees1.sort(key=lambda x: x.min)
        trees2.sort(key=lambda x: x.min)
        for i in range(components):
            if trees1[i].vertices != trees2[i].vertices or trees1[i].weight != trees2[i].weight:
                return False
        return True


class FloatFixedPrecisionChecker(AbsChecker):
    precision: float
    digits: int
    regex: re.Pattern[str] | str

    def __init__(self, digits: int):
        self.precision = 10**(-digits) * 1.5
        self.digits = digits
        self.regex = r"\d+\.\d{%s}" % digits

    def check(self, expected: str, output: str, input_: str) -> bool:
        output_floats = re.finditer(self.regex, output)
        expected_floats = re.finditer(self.regex, expected)
        while True:
            out = next(output_floats, None)
            exp = next(expected_floats, None)
            if out is None and exp is None:
                break
            if out is None or exp is None:
                return False
            if abs(float(out.group()) - float(exp.group())) < self.precision:
                continue
            return False

        output = re.sub(self.regex, "", output)
        expected = re.sub(self.regex, "", expected)
        return ComparisonChecker().check(expected, output, input_)


class NegativeCycleChecker(AbsChecker):
    def check(self, expected: str, output: str, input_: str) -> bool:
        expected = [line.strip() for line in expected.strip().splitlines()]
        output = [line.strip() for line in output.strip().splitlines()]
        if expected[0] != output[0]:
            return False
        if expected[0] == "NO":
            return True
        m = int(output[1])
        cycle = list(map(int, output[2].split()))
        if len(cycle) != m:
            return False

        input_ = [line.strip() for line in input_.strip().splitlines()]
        n = int(input_[0])
        graph = [list(map(int, line.split())) for line in input_[1:]]
        total_weight = 0
        for i in range(-1, m-1):
            w = graph[cycle[i] - 1][cycle[i+1] - 1]
            if w == 100000:
                return False
            total_weight += w
        if total_weight < 0:
            return True
        return False
