from app.modules.m5_rollback.service import revert


def test_restoration_attests_snapshot(single):
    row = single["回退"]
    assert row["恢复一致"] and row["当前摘要"] != row["回退后摘要"]
    assert row["断链"] == [] and row["回退后新键残留"] == 0


def test_broken_anchor_listed(cutover):
    row = cutover["回退"]
    assert row["断链"] == ["northeast@2026-11-21"]
    assert row["恢复一致"] is False and row["回退后新键残留"] == 1


def test_unrelated_deliveries_not_modified(cutover, single):
    assert cutover["回退"]["影响外变动"] == []
    assert single["回退"]["影响外变动"] == []


def test_revert_restores_original_region():
    records = {"east@2026-11-21": {"key": "new", "version": "n-1", "anchor": "o-1"}}
    assert revert(records) == {"east@2026-11-21": {"key": "old", "version": "o-1"}}


def test_revert_keeps_old_and_broken():
    records = {
        "a@2026-11-21": {"key": "old", "version": "o-1", "anchor": None},
        "b@2026-11-21": {"key": "new", "version": "n-1", "anchor": None},
    }
    restored = revert(records)
    assert restored["a@2026-11-21"] == {"key": "old", "version": "o-1"}
    assert restored["b@2026-11-21"] == {"key": "new", "version": "n-1"}


def test_revert_idempotent(cutover, single):
    assert cutover["回退"]["回退幂等"] and single["回退"]["回退幂等"]
