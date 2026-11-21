import hashlib
from datetime import datetime, timezone
from time import perf_counter

from app.config import VERSION
from app.keys import fingerprint
from app.modules.m1_intake.reader import read_bundle
from app.modules.m1_intake.service import intake
from app.modules.m2_mapping.service import accepted_rows, evidence, retention
from app.modules.m3_admission.service import adjudicate, admission_rows, scope
from app.modules.m4_operations.service import operations
from app.modules.m5_rollback.service import anchor_defects, rehearse
from app.modules.m6_reconcile.service import reconcile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw):
    return digest(VERSION.encode() + b":" + raw)[:26]


def safe_counts(value):
    if isinstance(value, dict):
        return {key: safe_counts(item) for key, item in value.items()}
    if isinstance(value, list):
        return [safe_counts(item) for item in value]
    if type(value) is int and abs(value) > 2**53 - 1:
        return str(value)
    return value


def compute(raw):
    began = perf_counter()
    value = read_bundle(raw)
    taken = intake(value)
    meta, sources = taken["meta"], taken["sources"]
    mapping_ok, evidence_rows = evidence(sources, taken["mappings"], taken["isolated"])
    retention_ok, retention_rows = retention(sources, taken["comparisons"], meta["live"])
    defects = anchor_defects(taken["deliveries"])
    verdicts = adjudicate(sources, mapping_ok, retention_ok, defects)
    coverage, unswitched = scope(meta, sources, verdicts, taken["deliveries"])
    key = identity(raw)
    ops = operations(verdicts, taken["comparisons"], retention_ok, taken["deliveries"], key)
    simulation = rehearse(taken["deliveries"])
    check = reconcile(taken["counts"], sources, verdicts, taken["deliveries"], retention_ok)
    summary = {
        "编号": key,
        "规则": VERSION,
        "文件摘要": digest(raw),
        "参数摘要": fingerprint({"live": meta["live"], "through": meta["through"]}),
        "时区": "UTC",
        "生成时间": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "上线日": meta["live"],
        "数据截止": meta["through"],
        "处理毫秒": round((perf_counter() - began) * 1000),
    }
    return safe_counts(
        {
            "批次": summary,
            "登记来源": [
                {
                    "来源": sid,
                    "消费者": record["consumers"],
                    "已升级": record["upgraded"],
                    "旧键在途": record["old_rows"],
                    "新键到达": record["new_rows"],
                    "旧键数": len(record["old_keys"]),
                }
                for sid, record in sorted(sources.items())
            ],
            "登记交付": [
                {
                    "分区": part,
                    "键制": "新键" if record["key"] == "new" else "旧键",
                    "版本": record["version"],
                    "锚点": record["anchor"],
                }
                for part, record in sorted(taken["deliveries"].items())
            ],
            "隔离": taken["isolated"],
            "重复": taken["duplicates"],
            "映射": accepted_rows(taken["mappings"]),
            "证据": evidence_rows,
            "对照": retention_rows,
            "准入": admission_rows(sources, verdicts, taken["comparisons"], defects),
            "覆盖范围": coverage,
            "未切换": unswitched,
            "发布": ops["发布"],
            "回查": ops["回查"],
            "补数": ops["补数"],
            "回退": simulation,
            "勾稽": check,
        }
    )


def execute(store, raw):
    key = identity(raw)
    previous = store.get(key)
    return (previous, True) if previous else store.save(key, compute(raw))
