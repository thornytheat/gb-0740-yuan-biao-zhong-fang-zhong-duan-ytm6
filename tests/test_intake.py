import pytest
from app.keys import AdmissionError
from app.modules.m1_intake.reader import read_bundle
from app.modules.m1_intake.service import window


# TRAP-02
def test_bom(small):
    assert read_bundle(b"\xef\xbb\xbf" + small)["switch"]["live"] == "2026-12-01"


# TRAP-06
def test_fullwidth_grouping(cutover):
    row = next(row for row in cutover["登记来源"] if row["来源"] == "north")
    assert row["新键到达"] == 1200


# TRAP-07
def test_missing_value_isolated(cutover):
    assert {"类别": "来源", "源行": 7, "原因码": "INVALID_SOURCE"} in cutover["隔离"]


# TRAP-31
def test_upgraded_over_consumers_isolated(cutover):
    assert {"类别": "来源", "源行": 8, "原因码": "INVALID_SOURCE"} in cutover["隔离"]


# TRAP-14
def test_conflict_both_reviewed(cutover):
    rows = [r["源行"] for r in cutover["隔离"] if r["类别"] == "映射" and r["原因码"] == "CONFLICT"]
    assert rows == [6, 7]


# TRAP-16
def test_truncated_input_rejected(small):
    with pytest.raises(AdmissionError) as exc:
        read_bundle(small.rstrip()[:-1])
    assert exc.value.code == "JSON"


# TRAP-17
def test_legacy_count(cutover):
    row = next(r for r in cutover["映射"] if r["来源"] == "south")
    assert row["行数"] == 1500


def test_unknown_source_isolated(cutover):
    assert {"类别": "映射", "源行": 10, "原因码": "UNKNOWN_SOURCE"} in cutover["隔离"]


def test_unknown_key_isolated(cutover):
    assert {"类别": "映射", "源行": 11, "原因码": "UNKNOWN_KEY"} in cutover["隔离"]


# TRAP-23
def test_date_limit_isolated(cutover):
    assert {"类别": "交付", "源行": 3, "原因码": "DATE_LIMIT"} in cutover["隔离"]


def test_delivery_conflict_isolated(cutover):
    rows = [r["源行"] for r in cutover["隔离"] if r["类别"] == "交付" and r["原因码"] == "CONFLICT"]
    assert rows == [6, 7]


def test_duplicate_has_row_evidence(cutover):
    assert {"类别": "映射", "源行": 2, "对象": "east:R-E1", "原因码": "DUPLICATE"} in cutover["重复"]
    assert {"类别": "交付", "源行": 5, "对象": "south@2026-11-21", "原因码": "DUPLICATE"} in cutover["重复"]


def test_window_after_live_rejected():
    with pytest.raises(AdmissionError) as exc:
        window({"live": "2026-12-01", "through": "2026-12-02"})
    assert exc.value.code == "WINDOW"
