from abc import ABC, abstractmethod


class AbsGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass
