import random
from collections import defaultdict

from .abs_generator import AbsGenerator

reduced_alpha = "abcdef"
reduced_alnum = "abcde123"


class GeneratorDsaWeek3A(AbsGenerator):
    def generate(self) -> str:
        n, m = random.randint(1, 20), random.randint(1, 20)
        s = set()
        alph = 'abcdefgxy'
        for i in range((n+m)*10):
            w = ""
            for _ in range(random.randint(1, 8)):
                w += random.choice(alph)
            while w in s:
                w = ""
                for _ in range(random.randint(1, 8)):
                    w += random.choice(alph)
            s.add(w)
        s = list(s)
        r = f"{n}\n"
        r += " ".join(random.choices(s, k=n)) + "\n"
        return r


class GeneratorDsaWeek3B(AbsGenerator):
    def generate(self) -> str:
        n, m = random.randint(1, 20), random.randint(1, 20)
        bb = 0
        s = set()
        alph = 'abcdefgxy'
        for i in range((n+m)*10 if not bb else (n+m)*2):
            w = ""
            for _ in range(random.randint(1, 8)):
                w += random.choice(alph)
            while w in s and not bb:
                w = ""
                for _ in range(random.randint(1, 8)):
                    w += random.choice(alph)
            s.add(w)
        s = list(s)
        r = f"{n}\n"
        r += " ".join(random.choices(s, k=n)) + "\n"
        r += f"{m}\n"
        r += " ".join(random.choices(s, k=m)) + "\n"
        return r


class GeneratorDsaWeek4A(AbsGenerator):
    @staticmethod
    def gen_name():
        n = random.randint(1, 10)
        s = ""
        for i in range(n):
            s += reduced_alpha[random.randint(0, len(reduced_alpha) - 1)]
        return s

    def generate(self) -> str:
        if random.random() < 0.9:
            n = random.randint(0, 50//2-1) * 2 + 1
        else:
            n = random.randint(0, 10 ** 3 // 2 - 1) * 2 + 1
        s = set()
        test = f"{n}\n"
        for i in range(n):
            r = random.randint(0, 10**6)
            while r in s:
                r = random.randint(0, 10 ** 6)
            s.add(r)
            test += f"{r} {GeneratorDsaWeek4A.gen_name()} {GeneratorDsaWeek4A.gen_name()}\n"
        return test


class GeneratorDsaWeek5A(AbsGenerator):
    @staticmethod
    def gen_word():
        len_ = random.randint(1, 16)
        s = ""
        for j in range(len_):
            s += random.choice(reduced_alpha)
        return s

    def generate(self) -> str:
        small = random.random() < 0.6
        n = random.randint(1, 10 if small else 1000)
        words = set()
        ml = -1
        for i in range(n):
            s = GeneratorDsaWeek5A.gen_word()
            while s in words:
                s = GeneratorDsaWeek5A.gen_word()
            words.add(s)
            ml = max(ml, len(s))
        words = list(words)
        k = random.randint(1, 50 if small else 10**5-1-ml)
        ck = 0
        t = ""
        while ck < k:
            w = random.choice(words)
            t += w
            ck += len(w)
        return f"{n} {len(t)}\n{' '.join(words)}\n{t}\n"


class GeneratorDsaWeek5B(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.6
        n = random.randint(1, 10 if small else 1000)
        k = random.randint(1, 50 if small else 10000)
        w, c = [], []
        for i in range(n):
            w.append(random.randint(1, 10 if small else 100))
            c.append(random.randint(1, 10 if small else 100))
        return f"{n} {k}\n{' '.join(map(str, w))}\n{' '.join(map(str, c))}\n"


class GeneratorDsaWeek6A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 1
        n = random.randint(1, 15 if small else 3000)
        cu, ma = [], []
        for i in range(n):
            cu.append(random.randint(0, 22 if small else 100))
            ma.append(random.randint(0, 22 if small else 100_000))
        r = f"{n}\n"
        for i in range(n):
            r += f"{cu[i]} {ma[i]}\n"
        return r


class GeneratorDsaWeek7A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.8
        n = random.randint(1, 12 if small else 1000)
        nums = list(range(1, n+1))
        random.shuffle(nums)
        return f"{n}\n{' '.join(map(str, nums))}\n"


class GeneratorDsaWeek8A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.9
        n = random.randint(1, 6 if small else 5000)
        res = f"{n}\n"
        for i in range(n):
            line = ' '.join(str(random.randint(-7, 7) if small else random.randint(-2**15, 2**15)) for _ in range(4))
            res += line + "\n"
        return res


class GeneratorDsaWeek11A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.9
        n = random.randint(1, 7 if small else 200)
        m = [[0] * n for _ in range(n)]
        r = f"{n}\n"
        for i in range(n):
            for j in range(i, n):
                m[i][j] = m[j][i] = random.randint(0, 1)
        for i in range(n):
            r += ' '.join(map(str, m[i])) + '\n'
        return r


class GeneratorDsaWeek12A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.7
        n = random.randint(1, 25 if small else 1000)
        e = random.randint(0, n*(n-1)//2)
        edges = [1]*e + [0]*(n*(n-1)//2 - e)
        random.shuffle(edges)

        r = f"{n} {e}\n"
        k = 0
        for i in range(n-1):
            for j in range(i+1, n):
                if edges[k]:
                    r += f"{i+1} {j+1} {random.randint(1, 30) * 5}\n"
                k += 1

        return r


class GeneratorDsaWeek13A(AbsGenerator):
    def generate(self) -> str:
        small = random.random() < 0.9
        n = random.randint(1, 10 if small else 100)

        r = f"{n}\n"
        for i in range(n):
            r += f"{' '.join(str(random.randint(-9, 15) if random.random() < 0.7 else 100000) for _ in range(n))}\n"

        return r


class GeneratorDsaWeek15A(AbsGenerator):
    NAMES: list[str] = ["max", "john doe", "ivan ivanovich", "Nickolay Kudasov", "Elon Musk", "elli"]
    book: dict[str, set[str]]

    def __init__(self):
        self.book = defaultdict(set)
        random.shuffle(self.NAMES)

    def generate(self) -> str:
        n = random.randint(1, 15 if random.random() < 0.9 else 125)
        r = f"{n}\n"
        for i in range(n):
            cmd = random.choices((1, 2, 3, 4), (3, 1, 0.5, 2))[0]
            match cmd:
                case 1:
                    if self.book:
                        name = self.get_name() if random.random() < 0.5 else self.gen_name()
                    else:
                        name = self.gen_name() if random.random() < 0.9 else 'arbuz'
                    number = self.gen_number() if random.random() < 0.8 else self.get_number(name)
                    r += f"ADD {name},{number}\n"
                    self.book[name].add(number)
                case 2:
                    name = self.get_name() if random.random() < 0.8 else "arbuz"
                    r += f"DELETE {name},{self.get_number(name) if random.random() < 0.8 else '+0'}\n"
                case 3:
                    r += f"DELETE {self.get_name() if random.random() < 0.8 else 'arbuz'}\n"
                case 4:
                    r += f"FIND {self.get_name() if random.random() < 0.7 else 'arbuz'}\n"
        return r

    def gen_name(self) -> str:
        for n in self.NAMES:
            if n not in self.book:
                return n
        while True:
            s = ''.join(random.choices("abcdefg", k=random.randint(1, 10)))
            if s not in self.book:
                return s

    @staticmethod
    def gen_number() -> str:
        n = "+"
        for i in range(random.randint(1, 6)):
            n += random.choice("0123456789")
        return n

    def get_name(self) -> str:
        if not self.book:
            return "arbuz"
        return random.choice(list(self.book.keys()))

    def get_number(self, name) -> str:
        if name not in self.book or not self.book[name]:
            return "+0"
        return random.choice(list(self.book[name]))


__all__ = [
    "GeneratorDsaWeek3A",
    "GeneratorDsaWeek3B",
    "GeneratorDsaWeek4A",
    "GeneratorDsaWeek5A",
    "GeneratorDsaWeek5B",
    "GeneratorDsaWeek6A",
    "GeneratorDsaWeek7A",
    "GeneratorDsaWeek8A",
    "GeneratorDsaWeek11A",
    "GeneratorDsaWeek12A",
    "GeneratorDsaWeek13A",
    "GeneratorDsaWeek15A",
]
