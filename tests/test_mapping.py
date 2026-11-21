def test_west_evidence_incomplete(cutover):
    row = next(r for r in cutover["证据"] if r["来源"] == "west")
    assert row["证据"] == "不全" and row["冲突"] == "R-W1"
    assert row["未映射"] == "R-W1、R-W2"


def test_east_evidence_complete(cutover):
    row = next(r for r in cutover["证据"] if r["来源"] == "east")
    assert row["证据"] == "齐全" and row["已映射"] == 2


def test_accepted_mapping_rows(cutover):
    assert len(cutover["映射"]) == 6


def test_retention_states(cutover):
    states = {row["来源"]: row["状态"] for row in cutover["对照"]}
    assert states["central"] == "丢失" and states["east"] == "保留"


def test_retention_checksum_pinned(cutover):
    row = next(r for r in cutover["对照"] if r["来源"] == "east")
    assert row["校验锚"] == "c9f2east" and row["保留至"] == "2027-06-01"
