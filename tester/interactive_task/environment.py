from abc import ABC, abstractmethod
from typing import Any


class AbsEnvironmentGenerator(ABC):
    @abstractmethod
    def generate(self) -> Any:
        pass


class AbsEnvironmentPresenter(ABC):
    @abstractmethod
    def to_string(self, env: Any) -> str:
        pass

