import random

from .abs_generator import AbsGenerator


class GeneratorAgla2Task5(AbsGenerator):
    @staticmethod
    def generate() -> str:
        fl = random.randint(0, 1)
        n = random.randint(1, 4)
        r = f"{n}\n"
        for i in range(n):
            for j in range(n):
                r += f"{round(random.random() * 10 - 5, 2) if fl else random.randint(-5, 5)} "
            r += '\n'
        return r
