import random
from abc import ABC, abstractmethod

eng_alphabet = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"


class AbsGenerator(ABC):
    @staticmethod
    @abstractmethod
    def generate() -> str:
        pass


class GeneratorWeek3A(AbsGenerator):
    @staticmethod
    def generate() -> str:
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
    @staticmethod
    def generate() -> str:
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
    @staticmethod
    def gen_name():
        n = random.randint(1, 10)
        s = ""
        for i in range(n):
            s += eng_alphabet[random.randint(0, len(eng_alphabet)-1)]
        return s

    @staticmethod
    def generate() -> str:
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
            test += f"{r} {GeneratorWeek4A.gen_name()} {GeneratorWeek4A.gen_name()}\n"
        return test


class GeneratorWeek5A(AbsGenerator):
    @staticmethod
    def gen_word():
        len_ = random.randint(1, 16)
        s = ""
        for j in range(len_):
            s += random.choice(eng_alphabet)
        return s

    @staticmethod
    def generate() -> str:
        small = random.random() < 0.6
        n = random.randint(1, 10 if small else 1000)
        words = set()
        ml = -1
        for i in range(n):
            s = GeneratorWeek5A.gen_word()
            while s in words:
                s = GeneratorWeek5A.gen_word()
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


class GeneratorWeek5B(AbsGenerator):
    @staticmethod
    def generate() -> str:
        small = random.random() < 0.6
        n = random.randint(1, 10 if small else 1000)
        k = random.randint(1, 50 if small else 10000)
        w, c = [], []
        for i in range(n):
            w.append(random.randint(1, 10 if small else 100))
            c.append(random.randint(1, 10 if small else 100))
        return f"{n} {k}\n{' '.join(map(str, w))}\n{' '.join(map(str, c))}\n"
