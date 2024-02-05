import os
import random
import time
from collections import defaultdict
from typing import Annotated

import uvicorn
from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import pydantic


class Update(pydantic.BaseModel):
    code: int
    position: int | None = None


class Result(pydantic.BaseModel):
    code: int
    error: str | None = None
    time: float | None = None
    tests: int | None = None
    input: str | None = None
    expected: str | None = None
    output: str | None = None


app = FastAPI()
queue: list[str] = []
results: dict[str, Result] = {}
regs = defaultdict(int)
banlist: list[str] = []

SECRET = os.environ['SECRET']
MAX_QUEUE = int(os.environ['MAX_QUEUE'])
MAX_REG = int(os.environ['MAX_REG'])

app.mount('/static', StaticFiles(directory="static"), name="static")


def send_program(code: str, user: str):
    tsmp = int(time.time()) - 170067800
    f = open(f'/queue/{tsmp}_{user}.txt', 'w')
    f.write(code)
    f.close()


@app.middleware("http")
async def show_ip(request: Request, call_next):
    print(request.client.host)
    return await call_next(request)


@app.middleware("http")
async def reg(request: Request, call_next):
    if request.url.path.startswith('/static/form.html'):
        return await call_next(request)

    if request.client.host in banlist:
        return RedirectResponse("/static/form.html", status.HTTP_302_FOUND)

    user_id = request.cookies.get('user_id')
    if user_id is not None or request.url.path.startswith('/static/'):
        return await call_next(request)

    if user_id is None:
        regs[request.client.host] += 1
        if regs[request.client.host] >= MAX_REG and request.client.host not in banlist:
            banlist.append(request.client.host)
            return RedirectResponse("/static/form.html", status.HTTP_302_FOUND)
        else:
            user_id = random.randbytes(32).hex()
            response = RedirectResponse(request.url)
            response.set_cookie('user_id', user_id)
            return response


@app.post('/submit')
async def form(background_tasks: BackgroundTasks, user_id: Annotated[str, Cookie()] = None,
               program: Annotated[str, Form()] = None):
    if program is None or program == "":
        raise HTTPException(400, "No input")

    response = RedirectResponse("/static/wait.html", status.HTTP_302_FOUND)
    if user_id not in queue:
        if len(queue) >= MAX_QUEUE:
            raise HTTPException(503, "Busy")
        background_tasks.add_task(send_program, program, user_id)
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
            code = data['code']
            user_id = data['user_id']
            if user_id in queue:
                queue.remove(user_id)
                if code == 0 or code == 1:
                    results[user_id] = Result(**data)
                else:
                    results[user_id] = Result(code=-1, error=data['error'])
    except WebSocketDisconnect as e:
        print(e)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
