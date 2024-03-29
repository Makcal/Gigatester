import pydantic


class Update(pydantic.BaseModel):
    code: int
    position: int | None = None


class Result(pydantic.BaseModel):
    code: int
    error: str | None = None
    time: float | None = None
    tests: int | None = None
    input: list[str] | None = None
    expected: list[str] | None = None
    output: list[str] | None = None
    language: str | None = None
    task: str | None = None
