import pytest
from app.keys import ReplayError
from app.modules.m1_inventory.reader import read_bundle
from app.modules.m1_inventory.service import heads


# TRAP-02
def test_bom(small):
    assert read_bundle(b"\xef\xbb\xbf" + small)["through"] == "2026-11-17"


# TRAP-06
def test_fullwidth_grouping(nightly):
    assert next(row["rows"] for row in nightly["登记"] if row["分区"] == "orders@2026-11-19") == 1202


# TRAP-07
def test_missing_value_isolated(nightly):
    assert {"源行": 7, "原因码": "INVALID_CHANGE"} in nightly["隔离"]


# TRAP-14
def test_conflict_both_reviewed(nightly):
    assert [r["源行"] for r in nightly["隔离"] if r["原因码"] == "CONFLICT"] == [5, 6]


# TRAP-16
def test_truncated_input_rejected(small):
    with pytest.raises(ReplayError) as exc:
        read_bundle(small.rstrip()[:-1])
    assert exc.value.code == "JSON"


# TRAP-17
def test_legacy_count(nightly):
    assert next(r["rows"] for r in nightly["登记"] if r["version"] == "legacy-16") == 119


def test_head_dup_is_fatal(small):
    values = read_bundle(small)["heads"]
    with pytest.raises(ReplayError) as exc:
        heads(values + values[:1])
    assert exc.value.code == "INVALID_HEAD"


def test_duplicate_has_row_evidence(nightly):
    assert nightly["重复"] == [{"源行": 2, "分区": "orders@2026-11-17", "原因码": "DUPLICATE"}]
