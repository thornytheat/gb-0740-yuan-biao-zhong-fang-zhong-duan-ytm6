from collections import defaultdict

from app.keys import AdmissionError, day, identifier, nonnegative_count, partition, small_count

LABELS = {"sources": "来源", "mappings": "映射", "comparisons": "对照", "deliveries": "交付"}
CODES = {"sources": "SOURCE", "mappings": "MAPPING", "comparisons": "COMPARE", "deliveries": "DELIVERY"}


class RowError(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def window(raw):
    try:
        live = day(raw["live"])
        through = day(raw["through"])
        if through > live:
            raise ValueError("截止日晚于上线日")
    except (KeyError, TypeError, ValueError) as exc:
        raise AdmissionError("WINDOW", "切换窗口无效") from exc
    return {"live": live.isoformat(), "through": through.isoformat()}


def source_row(raw):
    sid = identifier(raw["id"])
    consumers = small_count(raw["consumers"])
    upgraded = small_count(raw["upgraded"])
    if upgraded > consumers:
        raise ValueError("已升级超过消费者总数")
    old_keys = raw["old_keys"]
    if not isinstance(old_keys, list) or not 1 <= len(old_keys) <= 40:
        raise ValueError("旧键清单无效")
    declared = [identifier(key) for key in old_keys]
    if len(set(declared)) != len(declared):
        raise ValueError("旧键重复")
    return sid, {
        "consumers": consumers,
        "upgraded": upgraded,
        "old_rows": nonnegative_count(raw["old_rows"]),
        "new_rows": nonnegative_count(raw["new_rows"]),
        "old_keys": declared,
    }


def mapping_row(raw, sources):
    if ("rows" in raw) == ("count" in raw):
        raise ValueError("行数新旧字段必须择一")
    sid = identifier(raw["source"])
    old = identifier(raw["old"])
    new = identifier(raw["new"])
    rows = nonnegative_count(raw.get("rows", raw.get("count")))
    checked = raw["checked"]
    if not isinstance(checked, bool):
        raise ValueError("核对标记须为布尔")
    if sid not in sources:
        raise RowError("UNKNOWN_SOURCE")
    if old not in sources[sid]["old_keys"]:
        raise RowError("UNKNOWN_KEY")
    return (sid, old), {"new": new, "rows": rows, "checked": checked}


def comparison_row(raw, sources):
    sid = identifier(raw["source"])
    snapshot = identifier(raw["snapshot"])
    checksum = raw.get("checksum")
    if checksum is not None and (not isinstance(checksum, str) or not 1 <= len(checksum) <= 128):
        raise ValueError("校验锚无效")
    keep_until = day(raw["keep_until"]).isoformat()
    retained = raw["retained"]
    if not isinstance(retained, bool):
        raise ValueError("保留标记须为布尔")
    if sid not in sources:
        raise RowError("UNKNOWN_SOURCE")
    return sid, {
        "snapshot": snapshot,
        "checksum": checksum,
        "keep_until": keep_until,
        "retained": retained,
    }


def delivery_row(raw, sources, through):
    sid = identifier(raw["source"])
    when = day(raw["day"])
    kind = raw["key"]
    if kind not in ("old", "new"):
        raise ValueError("键制须为 old 或 new")
    version = identifier(raw["version"])
    anchor = raw.get("anchor")
    if anchor is not None:
        anchor = identifier(anchor)
    if kind == "old" and anchor is not None:
        raise ValueError("旧键交付不应携带锚点")
    if sid not in sources:
        raise RowError("UNKNOWN_SOURCE")
    if when > through:
        raise RowError("DATE_LIMIT")
    return partition(sid, raw["day"]), {"key": kind, "version": version, "anchor": anchor}


def _rows(records, parse, category):
    accepted, isolated, duplicates = {}, [], []
    pairs = defaultdict(list)
    for line, entry in enumerate(records, 1):
        try:
            key, value = parse(entry)
        except RowError as exc:
            isolated.append({"类别": LABELS[category], "源行": line, "原因码": exc.code})
            continue
        except (ValueError, TypeError, KeyError, AttributeError):
            isolated.append(
                {"类别": LABELS[category], "源行": line, "原因码": f"INVALID_{CODES[category]}"}
            )
            continue
        pairs[key].append((line, value))
    for key, candidates in pairs.items():
        line, record = candidates[0]
        label = key if isinstance(key, str) else ":".join(key)
        if any(value != record for _, value in candidates[1:]):
            isolated.extend(
                {"类别": LABELS[category], "源行": index, "对象": label, "原因码": "CONFLICT"}
                for index, _ in candidates
            )
            continue
        accepted[key] = {**record, "line": line}
        duplicates.extend(
            {"类别": LABELS[category], "源行": index, "对象": label, "原因码": "DUPLICATE"}
            for index, _ in candidates[1:]
        )
    return accepted, isolated, duplicates


def intake(value):
    meta = window(value["switch"])
    through = day(meta["through"])
    sources, iso_s, dup_s = _rows(value["sources"], source_row, "sources")
    mappings, iso_m, dup_m = _rows(value["mappings"], lambda r: mapping_row(r, sources), "mappings")
    comparisons, iso_c, dup_c = _rows(
        value["comparisons"], lambda r: comparison_row(r, sources), "comparisons"
    )
    deliveries, iso_d, dup_d = _rows(
        value["deliveries"], lambda r: delivery_row(r, sources, through), "deliveries"
    )
    groups = [("sources", iso_s, dup_s, sources), ("mappings", iso_m, dup_m, mappings)]
    groups += [("comparisons", iso_c, dup_c, comparisons), ("deliveries", iso_d, dup_d, deliveries)]
    counts = {
        name: {
            "input": len(value[name]),
            "accepted": len(accepted),
            "isolated": len(isolated),
            "duplicate": len(duplicate),
        }
        for name, isolated, duplicate, accepted in groups
    }
    return {
        "meta": meta,
        "sources": sources,
        "mappings": mappings,
        "comparisons": comparisons,
        "deliveries": deliveries,
        "isolated": sorted(iso_s + iso_m + iso_c + iso_d, key=lambda r: (r["源行"], r["类别"])),
        "duplicates": dup_s + dup_m + dup_c + dup_d,
        "counts": counts,
    }
