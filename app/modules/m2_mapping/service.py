from collections import defaultdict


def accepted_rows(mappings):
    return [
        {
            "来源": sid,
            "旧键": old,
            "新键": record["new"],
            "行数": record["rows"],
            "已核": "是" if record["checked"] else "否",
        }
        for (sid, old), record in sorted(mappings.items())
    ]


def evidence(sources, mappings, isolated):
    conflicts = defaultdict(set)
    for row in isolated:
        if row["类别"] == "映射" and row["原因码"] == "CONFLICT":
            sid, old = row["对象"].split(":", 1)
            conflicts[sid].add(old)
    status, rows = {}, []
    for sid in sorted(sources):
        accepted = {old: record for (src, old), record in mappings.items() if src == sid}
        declared = sources[sid]["old_keys"]
        unmapped = sorted(key for key in declared if key not in accepted)
        unchecked = sorted(old for old, record in accepted.items() if not record["checked"])
        merged = defaultdict(list)
        for old, record in accepted.items():
            merged[record["new"]].append(old)
        shared = sorted(old for olds in merged.values() if len(olds) > 1 for old in olds)
        clash = sorted(set(shared) | conflicts[sid])
        gaps = sorted(set(unmapped) | set(unchecked) | set(clash))
        status[sid] = not gaps
        rows.append(
            {
                "来源": sid,
                "旧键": len(declared),
                "已映射": len(accepted),
                "未映射": "、".join(unmapped) or "—",
                "未核": "、".join(unchecked) or "—",
                "冲突": "、".join(clash) or "—",
                "证据": "齐全" if not gaps else "不全",
            }
        )
    return status, rows


def retention(sources, comparisons, live):
    status, rows = {}, []
    for sid in sorted(sources):
        record = comparisons.get(sid)
        if record is None:
            state = "未登记"
        elif not record["retained"]:
            state = "丢失"
        elif not record["checksum"]:
            state = "无校验锚"
        elif record["keep_until"] < live:
            state = "保留不足"
        else:
            state = "保留"
        status[sid] = state == "保留"
        rows.append(
            {
                "来源": sid,
                "快照": record["snapshot"] if record else "—",
                "校验锚": record["checksum"] if record and record["checksum"] else "—",
                "保留至": record["keep_until"] if record else "—",
                "状态": state,
            }
        )
    return status, rows
