from app.keys import fingerprint


def anchor_defects(deliveries):
    defects = {}
    for key, record in sorted(deliveries.items()):
        if record["key"] == "new" and record["anchor"] is None:
            defects.setdefault(key.split("@")[0], []).append(key)
    return defects


def revert(records):
    """已交付结果回退到原区域：新键交付恢复为锚点登记的旧键版本。"""
    result = {}
    for key, record in records.items():
        if record["key"] == "new" and record.get("anchor") is not None:
            result[key] = {"key": "old", "version": record["anchor"]}
        else:
            result[key] = {"key": record["key"], "version": record["version"]}
    return result


def rehearse(deliveries):
    defects = anchor_defects(deliveries)
    broken = sorted(key for keys in defects.values() for key in keys)
    current = {
        key: {"key": record["key"], "version": record["version"]}
        for key, record in sorted(deliveries.items())
    }
    restored = revert(deliveries)
    residue = sorted(key for key, record in restored.items() if record["key"] != "old")
    outside = sorted(
        key
        for key in current
        if current[key] != restored[key] and current[key]["key"] != "new"
    )
    return {
        "交付指针": len(current),
        "新键交付": sum(1 for record in current.values() if record["key"] == "new"),
        "断链": broken,
        "当前摘要": fingerprint(current),
        "回退后摘要": fingerprint(restored),
        "回退后新键残留": len(residue),
        "影响外变动": outside,
        "回退幂等": revert(restored) == restored,
        "恢复一致": not broken and not residue and not outside,
    }
