from random import randint

from .abs_generator import AbsGenerator


class ExampleGenerator(AbsGenerator):
    def generate(self) -> str:
        return str(randint(1, 2))