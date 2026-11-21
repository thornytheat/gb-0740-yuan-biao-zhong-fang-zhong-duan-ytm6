import hashlib
import json


def fingerprint(value):
    serial = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(serial).hexdigest()


def destination(dataset, revision, date, inputs):
    values = {"数据集": dataset, "规则": revision, "分区日": date, "读源": inputs}
    # A version attests to its source snapshot and transformation revision.
    return {
        "version": "sha-" + fingerprint(values),
        "rows": sum(entry["rows"] for entry in inputs.values()),
    }


def source_state(current, change):
    expected = change["previous"]
    actual = current["version"] if current else None
    wanted = {k: change[k] for k in ("version", "rows")}
    if current == wanted:
        return "reuse", wanted, None
    if actual != expected or actual == wanted["version"]:
        return "blocked", None, "STALE_HEAD"
    return "write", wanted, None
