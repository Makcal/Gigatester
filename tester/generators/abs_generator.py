from abc import ABC, abstractmethod


class AbsGenerator(ABC):
    @staticmethod
    @abstractmethod
    def generate() -> str:
        pass
