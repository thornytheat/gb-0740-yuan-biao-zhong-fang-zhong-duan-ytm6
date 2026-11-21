import json

from app.modules.m7_issue.service import compute


def test_conservation_zero(cutover, single):
    for result in (cutover, single):
        check = result["勾稽"]
        assert check["来源差"] == check["映射差"] == check["对照差"] == check["交付差"] == 0


def test_delivery_conservation(cutover):
    check = cutover["勾稽"]
    assert check["交付输入"] == 11
    assert (check["交付采信"], check["交付隔离"], check["交付重复"]) == (7, 3, 1)
    assert check["新键交付"] == 4 and check["旧键交付"] == check["未切换分区"] == 3


def test_source_and_comparison_counts(cutover):
    check = cutover["勾稽"]
    assert check["登记来源"] == 6
    assert (check["独立交付"], check["旧键对照"], check["不可放行"]) == (1, 2, 3)
    assert check["对照齐备"] == 5 and check["对照缺失"] == 1


# TRAP-09
def test_aggregated_large_counts_are_exact_strings():
    big = 9_007_199_254_740_991
    bundle = {
        "switch": {"live": "2026-12-01", "through": "2026-11-21"},
        "sources": [
            {
                "id": sid,
                "consumers": 1,
                "upgraded": 1,
                "old_rows": big,
                "new_rows": big,
                "old_keys": [f"R-{sid.upper()}1"],
            }
            for sid in ("alpha", "beta")
        ],
        "mappings": [
            {"source": sid, "old": f"R-{sid.upper()}1", "new": f"R-{sid.upper()}2", "rows": big, "checked": True}
            for sid in ("alpha", "beta")
        ],
        "comparisons": [
            {
                "source": sid,
                "snapshot": f"cmp-{sid}",
                "checksum": f"sum-{sid}",
                "keep_until": "2027-06-01",
                "retained": True,
            }
            for sid in ("alpha", "beta")
        ],
        "deliveries": [],
    }
    result = compute(json.dumps(bundle).encode())
    assert result["勾稽"]["旧键在途行数"] == str(2 * big)
    assert result["勾稽"]["新键到达行数"] == str(2 * big)
    assert result["勾稽"]["独立交付"] == 2
