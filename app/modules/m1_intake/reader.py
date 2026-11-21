import json

from app.config import MAX_BYTES
from app.keys import AdmissionError

FIELDS = {"switch", "sources", "mappings", "comparisons", "deliveries"}


def read_bundle(raw):
    if len(raw) > MAX_BYTES:
        raise AdmissionError("SIZE", "文件超过 300 KiB")
    try:
        value = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique)
    except (ValueError, RecursionError) as exc:
        raise AdmissionError("JSON", "文件须为完整 UTF-8 JSON") from exc
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise AdmissionError("FIELDS", "清单字段不完整")
    if not isinstance(value["switch"], dict):
        raise AdmissionError("WINDOW", "切换窗口须为对象")
    for key in FIELDS - {"switch"}:
        if not isinstance(value[key], list) or len(value[key]) > 300:
            raise AdmissionError("LIMIT", "单组清单最多 300 行")
    return value


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("字段重复")
        result[key] = value
    return result
