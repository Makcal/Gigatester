from random import randint

from tester.generators import AbsGenerator


class ExampleGenerator(AbsGenerator):
    def generate(self) -> str:
        return str(randint(1, 2))