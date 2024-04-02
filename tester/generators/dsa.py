import random

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
]
