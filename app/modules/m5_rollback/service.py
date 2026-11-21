from app.keys import ReplayError
from app.modules.m3_fingerprint.service import fingerprint


def stage_install(heads, tasks):
    for item in tasks:
        if item["状态"] == "write" and heads.get(item["分区"]) != item["当前"]:
            raise ReplayError("STALE_HEAD", f"指针已经变动 {item['分区']}")
    result = dict(heads)
    changed = []
    for item in tasks:
        if item["状态"] == "write":
            key = item["分区"]
            result[key] = item["计划"]
            changed.append((key, item["当前"], item["计划"]))
    return result, changed


def revert(new_heads, changes):
    for key, _, published in changes:
        if new_heads.get(key) != published:
            raise ReplayError("STALE_ROLLBACK", f"新版本已经替换 {key}")
    result = dict(new_heads)
    for key, old, _ in reversed(changes):
        if old is None:
            del result[key]
        else:
            result[key] = old
    return result


def rehearse(heads, tasks):
    after, changes = stage_install(heads, tasks)
    restored = revert(after, changes)
    covered = {item["分区"] for item in tasks if item["状态"] == "write"}
    return {
        "演练写入": len(changes),
        "演练前摘要": fingerprint(heads),
        "演练后摘要": fingerprint(after),
        "回滚摘要": fingerprint(restored),
        "恢复一致": heads == restored,
        "影响外变动": sorted(
            key
            for key in heads.keys() | after.keys()
            if heads.get(key) != after.get(key) and key not in covered
        ),
    }
