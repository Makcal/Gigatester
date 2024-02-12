import random
from abc import ABC, abstractmethod


class AbsGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass


class GeneratorWeek3A(AbsGenerator):
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


class GeneratorWeek3B(AbsGenerator):
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


class GeneratorWeek4A(AbsGenerator):
    def gen_name(self):
        alphabet = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        n = random.randint(1, 10)
        s = ""
        for i in range(n):
            s += alphabet[random.randint(0, len(alphabet)-1)]
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
            test += f"{r} {self.gen_name()} {self.gen_name()}\n"
        return test
