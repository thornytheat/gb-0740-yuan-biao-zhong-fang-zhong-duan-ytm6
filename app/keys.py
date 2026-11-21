import hashlib
import json
import re
from datetime import date
from unicodedata import normalize


class AdmissionError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value):
        raise ValueError("标识无效")
    return value


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("日期需要 YYYY-MM-DD")
    return date.fromisoformat(value)


def partition(source, date_text):
    return f"{identifier(source)}@{day(date_text).isoformat()}"


def nonnegative_count(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("行数须为整数")
    token = normalize("NFKC", str(value)).strip()
    if not re.fullmatch(r"[0-9]{1,16}|[0-9]{1,3}(?:,[0-9]{3}){1,5}", token):
        raise ValueError("行数格式无效")
    number = int(token.replace(",", ""))
    if number > 9_007_199_254_740_991:
        raise ValueError("行数超过单分区限制")
    return number


def small_count(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 999:
        raise ValueError("消费者数须为 0-999 整数")
    return value


def fingerprint(value):
    serial = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(serial).hexdigest()
