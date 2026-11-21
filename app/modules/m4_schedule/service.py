from datetime import timedelta

from app.keys import day
from app.modules.m3_fingerprint.service import destination, source_state


def assemble(datasets, order, heads, source, affected):
    index = {name: i for i, name in enumerate(order)}
    tasks = []
    resolved = {}
    for key in sorted(affected, key=lambda item: (index[item.split("@")[0]], item.split("@")[1])):
        name, date_text = key.split("@")
        existing = heads.get(key)
        inputs = {}
        if key in source:
            state, new, reason = source_state(existing, source[key])
        else:
            for parent, lag in datasets[name]["reads"]:
                date_in = day(date_text) - timedelta(days=lag)
                part = f"{parent}@{date_in.isoformat()}"
                inputs[part] = resolved.get(part, heads.get(part))
            missing = next((part for part, value in inputs.items() if value is None), None)
            if missing:
                state, new, reason = "blocked", None, "MISSING_INPUT"
            else:
                new = destination(name, datasets[name]["revision"], date_text, inputs)
                state, reason = ("reuse", None) if existing == new else ("write", None)
        resolved[key] = new
        tasks.append(
            {"分区": key, "状态": state, "原因码": reason, "当前": existing, "计划": new, "上游": inputs}
        )
    return tasks
