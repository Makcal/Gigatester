from pydantic import BaseModel, SecretStr


class Language(BaseModel):
    id: str
    name: str


class Task(BaseModel):
    id: str
    name: str


class Config(BaseModel):
    languages: list[Language]
    tasks: list[Task]
    secret: SecretStr
    queue_size: int
    max_registrations: int
    frontend_version: int

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

