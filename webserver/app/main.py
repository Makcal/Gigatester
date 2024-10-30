import os
import random
import time
from collections import defaultdict
from typing import Annotated, Literal

import uvicorn
from fastapi import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

from .structures import Update, Result
from .log import init_web

LANGUAGES = Literal['java', 'cpp17', 'cpp20', 'cs', 'py']
LANGUAGE_NAMES = {
    'java': 'Java 23',
    'cpp17': 'GCC C++ 17',
    'cpp20': 'GCC C++ 20',
    'cs': 'C# 10',
    'py': 'Python 3.13'
}
TASKS = Literal[
    'example',
    'example_int',
]
TASK_NAMES = {
    'example': 'Example',
    'example_int': 'Example interactive',
}

VERSION_ID = "2"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_web(app)

queue: list[str] = []
results: dict[str, Result] = {}
regs = defaultdict(int)
ban_list: list[str] = []

SECRET = os.environ['SECRET']
MAX_QUEUE = int(os.environ['MAX_QUEUE'])
MAX_REG = int(os.environ['MAX_REG'])

app.mount('/static', StaticFiles(directory="static"), name="static")


def send_program(program_text: str, user: str, language: LANGUAGES, task: TASKS):
    timestamp = int(time.time())
    f = open(f'/queue/{timestamp}_{user}_{task}_{language}.txt', 'w')
    f.write(program_text)
    f.close()


@app.middleware("http")
async def show_ip(request: Request, call_next):
    print(request.client.host)
    return await call_next(request)


@app.middleware("http")
async def reg(request: Request, call_next):
    if request.url.path.startswith('/static/form.html'):
        return await call_next(request)

    if request.client.host in ban_list:
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


@app.get("/")
async def redirect():
    return RedirectResponse(f"/static/form.html?v={VERSION_ID}")


"""
API
"""


@app.get('/task_list')
async def get_task_list():
    return [(id_, name) for id_, name in TASK_NAMES.items()]


@app.post('/submit')
async def form(background_tasks: BackgroundTasks,
               language: Annotated[LANGUAGES, Form()],
               task: Annotated[TASKS, Form()],
               program: Annotated[str, Form()] = None,
               user_id: Annotated[str, Cookie()] = None):
    if program is None or program == "":
        raise HTTPException(400, "No input")

    response = JSONResponse({'user_id': user_id})
    response.set_cookie('task', task)
    response.set_cookie('language', language)
    if user_id not in queue:
        if len(queue) >= MAX_QUEUE:
            raise HTTPException(503, "Busy")
        background_tasks.add_task(send_program, program, user_id, language, task)
        queue.append(user_id)
    return response


@app.get('/update', response_model_exclude_defaults=True)
def update(user_id: Annotated[str, Cookie()] = None):
    if user_id is None:
        raise HTTPException(400)
    if user_id in queue:
        return Update(code=1, position=queue.index(user_id) + 1)
    elif user_id in results:
        return Update(code=0)
    else:
        raise HTTPException(400)


@app.get('/result', response_model_exclude_defaults=True)
def result(user_id: Annotated[str, Cookie()] = None):
    if user_id is None:
        raise HTTPException(400)
    if user_id in results:
        return results.pop(user_id)
    raise HTTPException(400)


@app.websocket("/ws")
async def internal(ws: WebSocket):
    try:
        await ws.accept()
        token = await ws.receive_text()
        if token != SECRET:
            print("Bad token", flush=True)
            await ws.close()
        await ws.send_text("ok")
        print("WS connected", flush=True)
        while True:
            data = await ws.receive_json()
            user_id = data['user_id']
            if user_id in queue:
                queue.remove(user_id)
                data['task'] = TASK_NAMES[data['task']]
                data['language'] = LANGUAGE_NAMES[data['language']]
                results[user_id] = Result(**data)
    except WebSocketDisconnect as e:
        print(e)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
