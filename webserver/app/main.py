import random
import time
from collections import defaultdict
from typing import Annotated

import uvicorn
from fastapi import (
    FastAPI,
    status,
    Request,
    Form,
    Body,
    Cookie,
    BackgroundTasks,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from .structures import Update, Result, Config
from .log import init_web

with open('config.json') as f:
    config = Config.model_validate_json(f.read())

LANGUAGES = {lang.id: lang for lang in config.languages}
TASKS = {t.id: t for t in config.tasks}
SECRET = config.secret.get_secret_value()
MAX_QUEUE = config.queue_size
MAX_REG = config.max_registrations
VERSION_ID = config.frontend_version

queue: list[str] = []
results: dict[str, Result] = {}
regs = defaultdict(int)
ban_list: list[str] = []

app = FastAPI()
app.mount('/static', StaticFiles(directory="static"), name="static")
# subapp for frontend middleware
api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_web(app)


def send_program(program_text: str, user: str, language: str, task: str):
    timestamp = int(time.time())
    f = open(f'/queue/{timestamp}_{user}_{task}_{language}.txt', 'w')
    f.write(program_text)
    f.close()


@api.middleware("http")
async def show_ip(request: Request, call_next):
    print(request.client.host if request.client is not None else 'No ip')
    return await call_next(request)


@api.middleware("http")
async def reg(request: Request, call_next):
    if request.url.path.startswith('/static/form.html'):
        return await call_next(request)

    if request.client and request.client.host in ban_list:
        return RedirectResponse(f"/static/form.html", status.HTTP_302_FOUND)

    user_id = request.cookies.get('user_id')
    if user_id is not None or request.url.path.startswith('/static/'):
        return await call_next(request)

    if user_id is None:
        # regs[request.client.host] += 1
        # if regs[request.client.host] >= MAX_REG and request.client.host not in ban_list:
        #     ban_list.append(request.client.host)
        #     return RedirectResponse("/static/form.html", status.HTTP_302_FOUND)
        # else:
        user_id = random.randbytes(32).hex()
        response = RedirectResponse(request.url)
        response.set_cookie('user_id', user_id)
        return response


@api.get("/")
async def redirect():
    return RedirectResponse(f"/static/form.html?v={VERSION_ID}")


"""
API
"""


@api.get('/task_list')
async def get_task_list():
    return [(task.id, task.name) for task in TASKS.values()]


@api.post('/submit')
async def form(background_tasks: BackgroundTasks,
               language: Annotated[str, Form()],
               task: Annotated[str, Form()],
               program: Annotated[str | None, Form()] = None,
               user_id: Annotated[str | None, Cookie()] = None):
    if program is None or program == "":
        raise HTTPException(400, "No input")
    if language not in LANGUAGES or task not in TASKS:
        raise HTTPException(400, "")
    if user_id is None:
        raise HTTPException(401, "Get a user_id cookie first")

    response = JSONResponse({'user_id': user_id})
    response.set_cookie('task', task)
    response.set_cookie('language', language)
    if user_id not in queue:
        if len(queue) >= MAX_QUEUE:
            raise HTTPException(503, "Busy")
        background_tasks.add_task(send_program, program, user_id, language, task)
        queue.append(user_id)
    return response


@api.get('/update', response_model_exclude_defaults=True)
def update(user_id: Annotated[str | None, Cookie()] = None):
    if user_id is None:
        raise HTTPException(400)
    if user_id in queue:
        return Update(code=1, position=queue.index(user_id) + 1)
    elif user_id in results:
        return Update(code=0)
    else:
        raise HTTPException(400)


@api.get('/result', response_model_exclude_defaults=True)
def result(user_id: Annotated[str | None, Cookie()] = None):
    if user_id is None:
        raise HTTPException(400)
    if user_id in results:
        return results.pop(user_id)
    raise HTTPException(400)


"""
Internal
"""


@app.get("/queue_size", response_class=PlainTextResponse)
async def get_queue_size():
    return str(len(queue))


@app.post("/ws_hello", response_class=PlainTextResponse)
async def ws_hello(token: Annotated[str, Body(embed=True)]) -> str:
    if token != SECRET:
        print("Bad token", flush=True)
        raise HTTPException(401, "Invalid token")
    return 'ok'


@app.post("/ws", response_class=PlainTextResponse)
async def internal(token: Annotated[str, Body()], data: dict) -> str:
    if token != SECRET:
        print("Bad token", flush=True)
        raise HTTPException(401, "Invalid token")
    user_id = data['user_id']
    if user_id in queue:
        queue.remove(user_id)
        data['task'] = TASKS[data['task']].name
        data['language'] = LANGUAGES[data['language']].name
        results[user_id] = Result(**data)
    return 'ok'


app.mount("/", api)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
