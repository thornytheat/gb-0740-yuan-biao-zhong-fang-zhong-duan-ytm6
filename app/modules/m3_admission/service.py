from collections import Counter

LABELS = {"independent": "独立交付", "compare": "旧键对照", "blocked": "不可放行"}
REASONS = {
    "MAPPING_GAP": "映射证据不全",
    "COMPARE_LOST": "对照缺失无法复核",
    "ANCHOR_BROKEN": "回退锚点断链",
    "CONSUMERS_PENDING": "消费者未全升级",
    "NEWKEY_PARTIAL": "新键未全覆盖",
}


def adjudicate(sources, mapping_ok, retention_ok, defects):
    verdicts = {}
    for sid in sorted(sources):
        record = sources[sid]
        blocked = []
        if not mapping_ok[sid]:
            blocked.append("MAPPING_GAP")
        if not retention_ok[sid]:
            blocked.append("COMPARE_LOST")
        if defects.get(sid):
            blocked.append("ANCHOR_BROKEN")
        if blocked:
            verdicts[sid] = {"state": "blocked", "reasons": blocked}
            continue
        pending = []
        if record["upgraded"] < record["consumers"]:
            pending.append("CONSUMERS_PENDING")
        if record["new_rows"] < record["old_rows"]:
            pending.append("NEWKEY_PARTIAL")
        verdicts[sid] = {"state": "compare" if pending else "independent", "reasons": pending}
    return verdicts


def admission_rows(sources, verdicts, comparisons, defects):
    rows = []
    for sid in sorted(verdicts):
        record, verdict = sources[sid], verdicts[sid]
        comparison = comparisons.get(sid)
        broken = defects.get(sid, [])
        rows.append(
            {
                "来源": sid,
                "状态": LABELS[verdict["state"]],
                "状态码": verdict["state"],
                "原因码": verdict["reasons"],
                "消费者": f"{record['upgraded']}/{record['consumers']} 已升级",
                "新键覆盖": f"{record['new_rows']}/{record['old_rows']}",
                "对照快照": comparison["snapshot"] if comparison else "缺失",
                "回退锚点": f"断链 {len(broken)}" if broken else "完整",
            }
        )
    return rows


def scope(meta, sources, verdicts, deliveries):
    counts = Counter(verdict["state"] for verdict in verdicts.values())
    pending_sources = [sid for sid in sorted(verdicts) if verdicts[sid]["state"] != "independent"]
    pending_parts = sorted(key for key, record in deliveries.items() if record["key"] == "old")
    coverage = {
        "上线日": meta["live"],
        "数据截止": meta["through"],
        "登记来源": len(sources),
        "在途交付": len(deliveries),
        "独立交付": counts["independent"],
        "旧键对照": counts["compare"],
        "不可放行": counts["blocked"],
        "未切换来源": len(pending_sources),
        "未切换分区": len(pending_parts),
        "说明": "准入覆盖登记来源在数据截止前的在途交付与已声明旧键；未登记来源与截止日后的交付不在范围内。",
    }
    unswitched = {
        "来源": [
            {"来源": sid, "状态": LABELS[verdicts[sid]["state"]], "原因码": verdicts[sid]["reasons"]}
            for sid in pending_sources
        ],
        "分区": pending_parts,
    }
    return coverage, unswitched
