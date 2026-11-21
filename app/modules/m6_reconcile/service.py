from collections import Counter


def compare(tasks, change_count, accepted, isolated, duplicate):
    outcome = Counter(item["状态"] for item in tasks)
    rows_before = sum((item["当前"] or {}).get("rows", 0) for item in tasks)
    final_heads = [item["当前"] if item["状态"] == "blocked" else item["计划"] for item in tasks]
    rows_after = sum(head["rows"] for head in final_heads if head is not None)
    change = sum(
        item["计划"]["rows"] - (item["当前"] or {}).get("rows", 0)
        for item in tasks
        if item["状态"] == "write"
    )
    return {
        "受影响": len(tasks),
        "待写": outcome["write"],
        "复用": outcome["reuse"],
        "阻断": outcome["blocked"],
        "分区差": len(tasks) - sum(outcome[key] for key in ("write", "reuse", "blocked")),
        "变更输入": change_count,
        "变更采信": accepted,
        "隔离": isolated,
        "重复": duplicate,
        "变更差": change_count - accepted - isolated - duplicate,
        "原行数": str(rows_before),
        "模拟行数": str(rows_after),
        "行数变化": str(change),
        "行数差": str(rows_after - rows_before - change),
    }
