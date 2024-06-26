# TrainYourBrain © 2024 by Daniil Gazizullin is licensed under CC BY-ND 4.0.
# To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/
import json
import logging
import os
import sys
import time

import structlog
from fastapi import FastAPI
from pydantic import parse_obj_as
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from structlog.types import EventDict, Processor
from uvicorn.protocols.utils import get_path_with_query_string


# Taken from https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e


# https://github.com/hynek/structlog/issues/35#issuecomment-591321744
def rename_event_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Log entries keep the text message in the `event` field, but Datadog
    uses the `message` field. This processor moves the value from one field to
    the other.
    See https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`, but we don't
    need it. This processor drops the key from the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging(json_logs: bool = False, log_level: str = "INFO"):
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if json_logs:
        # We rename the `event` key to `message` only in JSON logs, as Datadog looks
        #  for the `message` key but the pretty ConsoleRenderer looks for `event`
        shared_processors.append(rename_event_key)
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if json_logs:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer()

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Use OUR `ProcessorFormatter` to format all `logging` entries.
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    for _log in ["uvicorn", "uvicorn.error"]:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    # Since we re-create the access logs ourselves, to add all information
    # in the structured log (see the `logging_middleware` in main.py), we clear
    # the handlers and prevent the logs to propagate to a logger higher up in the
    # hierarchy (effectively rendering them silent).
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Log any uncaught exception instead of letting it be printed by Python
        (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
        See https://stackoverflow.com/a/16993115/3641865
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception


def init():
    LOG_JSON_FORMAT = parse_obj_as(bool, os.getenv("LOG_JSON_FORMAT", False))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    setup_logging(json_logs=LOG_JSON_FORMAT, log_level=LOG_LEVEL)


def init_web(app: FastAPI):
    init()

    access_logger = structlog.stdlib.get_logger("api.access")

    @app.middleware("http")
    async def _(request: Request, call_next) -> Response:
        structlog.contextvars.clear_contextvars()
        # These context vars will be added to all log entries emitted during the request
        request_id = request.headers.get("x-request-id")
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter_ns()
        # If the call_next raises an error, we still want to return our own
        # 500 response, so we can add headers to it (process time, request ID...)
        response = Response(status_code=500)
        statistics = {'success_result': False}
        try:
            response = await call_next(request)
            # collect statistics
            try:
                if request.url.path == "/result" and response.status_code == 200:
                    # copy body
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    response = Response(content=response_body, status_code=response.status_code,
                                        headers=dict(response.headers), media_type=response.media_type,
                                        background=response.background)

                    statistics['success_result'] = True
                    result: dict = json.loads(response_body)
                    result.pop("input", None)
                    result.pop("output", None)
                    result.pop("expected", None)
                    statistics['result'] = result
                    statistics['user_id'] = request.cookies.get('user_id')
            except Exception as e:
                response = Response(status_code=500)
                access_logger.error(f"LOGGER ERROR: {type(e)}: {e}")
        except Exception:
            await structlog.stdlib.get_logger("api.error").exception(
                "Uncaught exception"
            )
            raise
        finally:
            process_time = time.perf_counter_ns() - start_time
            status_code = response.status_code
            url = get_path_with_query_string(request.scope)  # type: ignore
            client_host = request.client.host  # type: ignore
            client_port = request.client.port  # type: ignore
            proxy = request.headers.get("x-forwarded-for", "")
            proxy = f" ({proxy})" if proxy else ""
            http_method = request.method
            http_version = request.scope["http_version"]
            url = (
                str(request.url).split("?")[0]
                if "g_recaptcha_response" in str(request.url)
                else str(request.url)
            )

            if str(request.url) != "http://0.0.0.0:8000/ping":
                # Recreate the Uvicorn access log format, but add all parameters
                # as structured information
                await access_logger.info(
                    (
                        f'{client_host}:{client_port}{proxy} - "{http_method} '
                        f'{url} HTTP/{http_version}" {status_code}'
                    ),
                    http={
                        "url": url,
                        "status_code": status_code,
                        "method": http_method,
                        "request_id": request_id,
                        "version": http_version,
                    },
                    statistics=statistics,
                    duration=process_time,
                )
            response.headers["X-Process-Time"] = str(process_time / 10**9)
            return response

