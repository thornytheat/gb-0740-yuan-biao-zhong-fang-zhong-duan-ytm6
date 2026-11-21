from collections import Counter

GROUPS = [("来源", "sources"), ("映射", "mappings"), ("对照", "comparisons"), ("交付", "deliveries")]


def reconcile(counts, sources, verdicts, deliveries, retention_ok):
    states = Counter(verdict["state"] for verdict in verdicts.values())
    old_key = sum(1 for record in deliveries.values() if record["key"] == "old")
    result = {
        "登记来源": len(sources),
        "独立交付": states["independent"],
        "旧键对照": states["compare"],
        "不可放行": states["blocked"],
        "来源差": len(sources) - sum(states.values()),
        "新键交付": len(deliveries) - old_key,
        "旧键交付": old_key,
        "未切换分区": old_key,
        "对照齐备": sum(1 for ok in retention_ok.values() if ok),
        "对照缺失": sum(1 for ok in retention_ok.values() if not ok),
    }
    for label, name in GROUPS:
        group = counts[name]
        result[f"{label}输入"] = group["input"]
        result[f"{label}采信"] = group["accepted"]
        result[f"{label}隔离"] = group["isolated"]
        result[f"{label}重复"] = group["duplicate"]
        result[f"{label}差"] = group["input"] - group["accepted"] - group["isolated"] - group["duplicate"]
    result["旧键在途行数"] = str(sum(record["old_rows"] for record in sources.values()))
    result["新键到达行数"] = str(sum(record["new_rows"] for record in sources.values()))
    return result
