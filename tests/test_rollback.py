import pytest
from app.keys import ReplayError
from app.modules.m1_inventory.reader import read_bundle
from app.modules.m1_inventory.service import heads
from app.modules.m5_rollback.service import revert, stage_install


def test_restoration_attests_snapshot(clean):
    row = clean["回滚"]
    assert row["恢复一致"] and row["演练前摘要"] == row["回滚摘要"] != row["演练后摘要"]


def test_unrelated_partitions_not_modified(nightly):
    assert nightly["回滚"]["影响外变动"] == []


# TRAP-26
def test_stale_snapshot_atomic(clean, small):
    current = heads(read_bundle(small)["heads"])
    current["facts@2026-11-17"] = {"version": "foreign", "rows": 99}
    with pytest.raises(ReplayError) as exc:
        stage_install(current, clean["排程"])
    assert exc.value.code == "STALE_HEAD"
    assert current["orders@2026-11-17"]["version"] == "s1"


def test_new_part_is_deleted():
    new = {"version": "r3", "rows": 4}
    assert revert({"f@2026-11-17": new}, [("f@2026-11-17", None, new)]) == {}


def test_stale_revert_refuses_overwrite():
    with pytest.raises(ReplayError) as exc:
        revert({"k": {"version": "r3"}}, [("k", {"version": "r1"}, {"version": "r2"})])
    assert exc.value.code == "STALE_ROLLBACK"


def test_install_two_expected_versions(clean, small):
    after, changes = stage_install(heads(read_bundle(small)["heads"]), clean["排程"])
    assert len(changes) == 2 and [row["rows"] for row in after.values()] == [12, 12]
