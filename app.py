import os
import re
from typing import Any, Iterator

from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def try_args(name_param: str, req: Any) -> str:
    try:
        param = req.args[name_param]
    except KeyError:
        param = '0'
    return param


@app.post("/perform_query")
def perform_query() -> Response:

    cmd1 = try_args('cmd1', request)  # можно было получить имя переменной, но это лишнее, так лучше
    value1 = try_args('value1', request)
    cmd2 = try_args('cmd2', request)
    value2 = try_args('value2', request)

    try:
        file_name = request.args['file_name']
    except KeyError:
        raise BadRequest(description="File's name is required")

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        raise BadRequest(description=f'{file_name} was not found')

    with open(file_path) as f:
        result = build_query(f, cmd1, value1, cmd2, value2)
        content = '\n'.join(result)
    return app.response_class(content, content_type="text/plain")


def build_query(f: Iterator, cmd1: str, value1: str, cmd2: str, value2: str) -> Iterator:
    f = map(lambda v: v.strip(), f)
    if cmd1 == '0' and cmd2 == '0':
        raise BaseException("Incorrect query")
    if cmd1 != '0':
        result = process_query(f, cmd1, value1)
        if cmd2 != '0':
            result = process_query(result, cmd2, value2)
    else:
        result = process_query(f, cmd2, value2)
    return result


def process_query(f: Iterator, cmd: str, value: str) -> Iterator:
    if cmd == "filter":
        return filter(lambda v: value in v, f)
    if cmd == "limit":
        idx = int(value)
        return iter(list(f)[:idx])
    if cmd == "map":
        idx = int(value)
        return map(lambda v: v.split(" ")[idx], f)
    if cmd == "unique":
        return iter(set(f))
    if cmd == 'sort':
        if value == 'desc':
            reverse = True
        else:
            reverse = False
        return iter(sorted(f, reverse=reverse))
    if cmd == 'regex':
        regex = re.compile(value)
        return filter(lambda v: regex.search(v), f)
    return f




