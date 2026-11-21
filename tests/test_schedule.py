import json

from app.modules.m1_inventory.reader import read_bundle
from app.modules.m7_release.service import compute


def test_lag_propagates_next_day(nightly):
    assert "day1@2026-11-18" in {r["分区"] for r in nightly["排程"]}
    assert "day1@2026-11-17" not in {r["分区"] for r in nightly["排程"]}


def test_immediate_child_reads_staged_version(clean):
    assert clean["排程"][1]["上游"]["orders@2026-11-17"] == {"version": "s2", "rows": 12}


# TRAP-23
def test_cutoff_included_but_lagged_next_day_excluded(night):
    data = read_bundle(night)
    data["through"] = "2026-11-17"
    result = compute(json.dumps(data).encode())
    keys = {r["分区"] for r in result["排程"]}
    assert "facts@2026-11-17" in keys and "day1@2026-11-18" not in keys


def test_stale_child_blocked(nightly):
    row = next(r for r in nightly["排程"] if r["分区"] == "facts@2026-11-18")
    assert row["上游"] == {"orders@2026-11-18": None} and row["原因码"] == "MISSING_INPUT"


def test_missing_unaffected_input_explained(nightly):
    row = next(r for r in nightly["排程"] if r["分区"] == "day0@2026-11-19")
    assert row["上游"]["buyers@2026-11-19"] is None


def test_direct_change_to_output_blocked(nightly):
    assert any(r.get("分区") == "facts@2026-11-21" and r["原因码"] == "NOT_SOURCE" for r in nightly["隔离"])


def test_invalid_override_cannot_replace_affected_descendant(small):
    data = read_bundle(small)
    data["changes"].append(
        {"dataset": "facts", "day": "2026-11-17", "version": "manual", "previous": "f1", "rows": 456}
    )
    result = compute(json.dumps(data).encode())
    assert result["排程"][1]["计划"]["rows"] == 12
    assert result["隔离"][0]["原因码"] == "NOT_SOURCE"
    assert result["分区勾稽"]["变更差"] == 0
