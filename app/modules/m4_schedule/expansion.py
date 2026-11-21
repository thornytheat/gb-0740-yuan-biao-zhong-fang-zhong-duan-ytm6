from collections import deque
from datetime import timedelta

from app.keys import ReplayError, day
from app.modules.m2_graph.service import reverse_edges


def impact(datasets, source, heads, through):
    try:
        limit = day(through)
    except ValueError as exc:
        raise ReplayError("THROUGH", "截止日期无效") from exc
    for key in heads:
        if key.split("@")[0] not in datasets:
            raise ReplayError("UNKNOWN_HEAD", "现行指针有未登记数据集")
    edges = reverse_edges(datasets)
    unknown = []
    source_keys = set()
    queue = deque()
    for key in sorted(source):
        node, date_text = key.split("@")
        when = day(date_text)
        if node not in datasets or datasets[node]["reads"] or when > limit or (limit - when).days > 31:
            code = "NOT_SOURCE" if node not in datasets or datasets[node]["reads"] else "DATE_LIMIT"
            unknown.append({"源行": source[key]["line"], "分区": key, "原因码": code})
            continue
        source_keys.add(key)
        queue.append((node, when))
    result = set()
    while queue:
        node, when = queue.popleft()
        key = f"{node}@{when.isoformat()}"
        if key in result:
            continue
        result.add(key)
        if len(result) > 1200:
            raise ReplayError("PLAN_LIMIT", "受影响分区超过 1200 个")
        for child, offset in edges[node]:
            next_day = when + timedelta(days=offset)
            if next_day <= limit:
                queue.append((child, next_day))
    return result, source_keys, unknown
