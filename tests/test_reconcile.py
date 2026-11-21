from app.modules.m6_reconcile.service import compare


def test_rows_increase_two_per_partition(clean):
    check = clean["分区勾稽"]
    assert (check["原行数"], check["模拟行数"], check["行数变化"], check["行数差"]) == (
        "20",
        "24",
        "4",
        "0",
    )


def test_plan_partition_conservation(nightly):
    check = nightly["分区勾稽"]
    assert check["受影响"] == check["待写"] + check["阻断"] + check["复用"]
    assert check["阻断"] > 0 and check["待写"] > 0


def test_change_line_conservation(nightly):
    check = nightly["分区勾稽"]
    assert (check["变更输入"], check["变更采信"], check["隔离"], check["重复"], check["变更差"]) == (
        10,
        4,
        5,
        1,
        0,
    )


def test_blocked_keeps_origin_rows():
    tasks = [{"当前": {"rows": 4}, "计划": None, "状态": "blocked"}]
    stats = compare(tasks, 0, 0, 0, 0)
    assert stats["原行数"] == stats["模拟行数"] == "4"


# TRAP-09
def test_aggregated_large_counts_are_exact_strings():
    tasks = [{"当前": {"rows": 2**53 - 1}, "计划": {"rows": 2**53 - 1}, "状态": "reuse"}] * 2
    assert compare(tasks, 0, 0, 0, 0)["模拟行数"] == str(2**54 - 2)


def test_missing_disposition_visible():
    assert compare([], 4, 1, 0, 0)["变更差"] == 3
