def test_operations_read_same_admission(cutover):
    key = cutover["批次"]["编号"]
    for table in ("发布", "回查", "补数"):
        assert {row["准入"] for row in cutover[table]} == {key}


def test_independent_backfill_new_key_only(cutover):
    row = next(r for r in cutover["补数"] if r["来源"] == "east")
    assert row["补数键制"] == "仅新键" and "防同一订单" in row["约束"]


def test_compare_backfill_old_key_with_mapping(cutover):
    row = next(r for r in cutover["补数"] if r["来源"] == "south")
    assert row["补数键制"] == "仅旧键+映射换算" and row["约束"] == "新旧不得同补"


def test_blocked_backfill_forbidden(cutover):
    rows = {r["来源"]: r for r in cutover["补数"]}
    for sid in ("west", "central", "northeast"):
        assert rows[sid]["补数键制"] == "禁止"


def test_publish_old_key_lifecycle(cutover):
    rows = {r["来源"]: r for r in cutover["发布"]}
    assert (rows["east"]["新键"], rows["east"]["旧键"]) == ("直发", "停发")
    assert (rows["south"]["新键"], rows["south"]["旧键"]) == ("双发", "对照保留")
    assert (rows["west"]["新键"], rows["west"]["旧键"]) == ("停发", "维持")


def test_recheck_unauditable_when_comparison_lost(cutover):
    rows = {r["来源"]: r for r in cutover["回查"]}
    assert rows["central"]["复核依据"] == "已切换区域无法复核"
    assert rows["central"]["证据锚"] == "—"
    assert rows["east"]["复核依据"] == "新键台账+对照快照"
    assert rows["east"]["证据锚"] == "c9f2east"
