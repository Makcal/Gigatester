__all__ = ['TASK_DICT']

import typing
from .example import (
    example_interactive_task,
    example_task,
)

if typing.TYPE_CHECKING:
    from simple_task import SimpleTask
    from interactive_task import InteractiveTask


# Old tasks, generators, and checkers can be found in older commits.
# B23 first year: check commits <= 63e4ef836053d09d1256db2af1abb5a5084e66c7


TASK_DICT: dict[str, "SimpleTask | InteractiveTask"] = {
    'example': example_task,
    'example_int': example_interactive_task,
}

