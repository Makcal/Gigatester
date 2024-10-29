from typing import Any, Callable
from tasks.task_base import TaskBase
from .abs_interactor import AbsCommunicator, AbsInteractor
from .environment import AbsEnvironmentGenerator, AbsEnvironmentPresenter
from testers import AbsTester


class InteractiveTask(TaskBase):
    def __init__(
            self,
            env_generator: "AbsEnvironmentGenerator",
            interactor_factory: Callable[["AbsCommunicator"], "AbsInteractor"],
            env_presenter: "AbsEnvironmentPresenter",
            reference: tuple[str, "AbsTester"],
            n_tests: int,
            one_timeout: int,
    ):
        super().__init__(reference, n_tests)
        self.env_generator = env_generator
        self.interactor_factory = interactor_factory
        self.env_presenter = env_presenter
        self.one_timeout = one_timeout

    def env_to_string(self, env: Any) -> str | None:
        return self.env_presenter.to_string(env) if self.env_presenter else None

