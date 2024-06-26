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

LANGUAGES = Literal['java', 'cpp17', 'cpp20', 'cs']
LANGUAGE_NAMES = {
    'java': 'Java 23',
    'cpp17': 'GCC C++ 17',
    'cpp20': 'GCC C++ 20',
    'cs': 'C# 10',
}
TASKS = Literal[
    'DSA_week3A',
    'DSA_week3B',
    'DSA_week4A',
    'DSA_week5A',
    'DSA_week5B',
    'DSA_week6A',
    'DSA_week7A',
    'DSA_week8A',
    'DSA_week11A',
    'DSA_week12A',
    'DSA_week13A',
    'DSA_week15A',
    'AGLA2_task1',
    'AGLA2_task2',
    'AGLA2_task3',
    'AGLA2_task4',
    'AGLA2_task5',
    'AGLA2_task6',
    'AGLA2_task7',
    'AGLA2_task8',
    'AGLA2_task9',
    'AGLA2_task10',
    'SSAD_task2',
    'SSAD_task3',
    'SSAD_task4',
]
TASK_NAMES = {
    'DSA_week3A': 'DSA week 3. Task A.',
    'DSA_week3B': 'DSA week 3. Task B.',
    'DSA_week4A': 'DSA week 4. Task A.',
    'DSA_week5A': 'DSA week 5. Task A.',
    'DSA_week5B': 'DSA week 5. Task B.',
    'DSA_week6A': 'DSA week 6. Task A.',
    'DSA_week7A': 'DSA week 7. Task A.',
    'DSA_week8A': 'DSA week 8. Task A.',
    'DSA_week11A': 'DSA week 11. Task A.',
    'DSA_week12A': 'DSA week 12. Task A.',
    'DSA_week13A': 'DSA week 13. Task A.',
    'DSA_week15A': 'DSA week 15. Task A.',
    'AGLA2_task1': 'AGLA II. Task 1.',
    'AGLA2_task2': 'AGLA II. Task 2.',
    'AGLA2_task3': 'AGLA II. Task 3.',
    'AGLA2_task4': 'AGLA II. Task 4.',
    'AGLA2_task5': 'AGLA II. Task 5.',
    'AGLA2_task6': 'AGLA II. Task 6.',
    'AGLA2_task7': 'AGLA II. Task 7.',
    'AGLA2_task8': 'AGLA II. Task 8.',
    'AGLA2_task9': 'AGLA II. Task 9.',
    'AGLA2_task10': 'AGLA II. Task 10.',
    'SSAD_task2': 'SSAD. Assignment 2.',
    'SSAD_task3': 'SSAD. Assignment 3.',
    'SSAD_task4': 'SSAD. Assignment 4.',
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


@app.post('/submit')
async def form(background_tasks: BackgroundTasks,
               language: Annotated[LANGUAGES, Form()], task: Annotated[TASKS, Form()],
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
