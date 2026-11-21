def _states(result):
    return {row["来源"]: row for row in result["准入"]}


def test_three_states(cutover):
    rows = _states(cutover)
    assert rows["east"]["状态"] == "独立交付"
    assert rows["south"]["状态"] == rows["north"]["状态"] == "旧键对照"
    assert {sid for sid, row in rows.items() if row["状态"] == "不可放行"} == {
        "west",
        "central",
        "northeast",
    }


def test_reason_codes(cutover):
    rows = _states(cutover)
    assert rows["west"]["原因码"] == ["MAPPING_GAP"]
    assert rows["central"]["原因码"] == ["COMPARE_LOST"]
    assert rows["northeast"]["原因码"] == ["ANCHOR_BROKEN"]
    assert rows["south"]["原因码"] == ["CONSUMERS_PENDING"]
    assert rows["north"]["原因码"] == ["NEWKEY_PARTIAL"]
    assert rows["east"]["原因码"] == []


def test_coverage_scope(cutover):
    scope = cutover["覆盖范围"]
    assert scope["登记来源"] == 6 and scope["在途交付"] == 7
    assert (scope["独立交付"], scope["旧键对照"], scope["不可放行"]) == (1, 2, 3)
    assert scope["未切换来源"] == 5 and scope["未切换分区"] == 3
    assert scope["上线日"] == "2026-12-01" and scope["数据截止"] == "2026-11-21"


def test_unswitched_scope(cutover):
    assert cutover["未切换"]["分区"] == [
        "north@2026-11-21",
        "south@2026-11-21",
        "west@2026-11-21",
    ]
    assert {row["来源"] for row in cutover["未切换"]["来源"]} == {
        "central",
        "north",
        "northeast",
        "south",
        "west",
    }


def test_single_source_independent(single):
    rows = _states(single)
    assert rows["east"]["状态"] == "独立交付" and rows["east"]["回退锚点"] == "完整"
    assert single["未切换"]["分区"] == []
