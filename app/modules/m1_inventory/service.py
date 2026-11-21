from collections import defaultdict

from app.keys import ReplayError, identifier, nonnegative_count, partition


def row(raw, source):
    if ("rows" in raw) == ("count" in raw):
        raise ValueError("行数新旧字段必须择一")
    key = partition(raw["dataset"], raw["day"])
    status = dict(
        version=identifier(raw["version"]), rows=nonnegative_count(raw.get("rows", raw.get("count")))
    )
    if source == "change":
        previous = raw["previous"]
        status["previous"] = identifier(previous) if previous is not None else None
    return key, status


def heads(records):
    result = {}
    for entry in records:
        try:
            key, value = row(entry, "head")
            if key in result:
                raise ValueError("分区指针重复")
        except (ValueError, TypeError, KeyError) as exc:
            raise ReplayError("INVALID_HEAD", "分区指针无效或重复") from exc
        result[key] = value
    return result


def changes(records):
    accepted, isolated, duplicates = {}, [], []
    pairs = defaultdict(list)
    for line, entry in enumerate(records, 1):
        try:
            key, values = row(entry, "change")
        except (ValueError, TypeError, KeyError):
            isolated.append({"源行": line, "原因码": "INVALID_CHANGE"})
            continue
        pairs[key].append((line, values))
    for key, candidates in pairs.items():
        line, record = candidates[0]
        if any(value != record for _, value in candidates[1:]):
            isolated.extend({"源行": index, "分区": key, "原因码": "CONFLICT"} for index, _ in candidates)
            continue
        accepted[key] = {**record, "line": line}
        duplicates.extend(
            {"源行": index, "分区": key, "原因码": "DUPLICATE"} for index, _ in candidates[1:]
        )
    return accepted, sorted(isolated, key=lambda r: r["源行"]), duplicates
