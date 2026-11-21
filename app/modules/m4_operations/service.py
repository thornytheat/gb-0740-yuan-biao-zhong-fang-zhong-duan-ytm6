PUBLISH = {
    "independent": ("直发", "停发"),
    "compare": ("双发", "对照保留"),
    "blocked": ("停发", "维持"),
}
BACKFILL = {
    "independent": ("仅新键", "禁旧键补，防同一订单算进两个区域"),
    "compare": ("仅旧键+映射换算", "新旧不得同补"),
    "blocked": ("禁止", "先补证据再评估"),
}


def operations(verdicts, comparisons, retention_ok, deliveries, admission_id):
    switched = {sid: 0 for sid in verdicts}
    for key, record in deliveries.items():
        if record["key"] == "new":
            switched[key.split("@")[0]] += 1
    publish, recheck, backfill = [], [], []
    for sid in sorted(verdicts):
        state = verdicts[sid]["state"]
        kept = retention_ok[sid]
        anchor = comparisons[sid]["checksum"] if kept and sid in comparisons else "—"
        new_key, old_key = PUBLISH[state]
        kind, limit = BACKFILL[state]
        publish.append(
            {"来源": sid, "状态": _label(state), "新键": new_key, "旧键": old_key, "准入": admission_id}
        )
        if state == "independent":
            basis = "新键台账+对照快照"
        elif state == "compare":
            basis = "旧键对照快照"
        elif not kept and switched[sid] > 0:
            basis = "已切换区域无法复核"
        elif not kept:
            basis = "对照缺失，先补留快照"
        else:
            basis = "旧键台账"
        recheck.append(
            {"来源": sid, "状态": _label(state), "复核依据": basis, "证据锚": anchor, "准入": admission_id}
        )
        backfill.append(
            {"来源": sid, "状态": _label(state), "补数键制": kind, "约束": limit, "准入": admission_id}
        )
    return {"发布": publish, "回查": recheck, "补数": backfill}


def _label(state):
    return {"independent": "独立交付", "compare": "旧键对照", "blocked": "不可放行"}[state]
