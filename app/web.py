from app.config import SAMPLES
from app.keys import ReplayError
from flask import abort, current_app


def repository():
    return current_app.extensions["plans"]


def record(key):
    value = repository().get(key)
    if not value:
        abort(404)
    return value


def fixture(slug):
    if not isinstance(slug, str) or slug not in SAMPLES:
        raise ReplayError("SAMPLE", "请选择已登记的清单")
    return (current_app.config["INPUTS"] / f"{slug}.json").read_bytes()
