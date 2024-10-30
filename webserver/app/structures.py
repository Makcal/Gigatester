from pydantic import BaseModel


class Language(BaseModel):
    id: str
    name: str


class Task(BaseModel):
    id: str
    name: str


class Config(BaseModel):
    languages: list[Language]
    tasks: list[Task]


class Update(BaseModel):
    code: int
    position: int | None = None


class Result(BaseModel):
    code: int
    error: str | None = None
    time: float | None = None
    tests: int | None = None
    input: list[str] | None = None
    expected: list[str] | None = None
    output: list[str] | None = None
    language: str | None = None
    task: str | None = None
    interactive: bool | None = None

