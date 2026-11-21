import pytest
from app.keys import ReplayError
from app.modules.m1_inventory.reader import read_bundle
from app.modules.m2_graph.registry import catalog
from app.modules.m2_graph.service import reverse_edges, topology


# TRAP-20
def test_cycle_path_from_sample(small):
    ds = read_bundle(small)["datasets"]
    ds[0]["inputs"].append({"dataset": "facts"})
    with pytest.raises(ReplayError) as exc:
        topology(catalog(ds))
    assert exc.value.code == "CYCLE" and str(exc.value) == "facts → orders → facts"


def test_unknown_dependency_is_clear():
    with pytest.raises(ReplayError) as exc:
        catalog([{"id": "facts", "revision": "r1", "inputs": [{"dataset": "raw"}]}])
    assert exc.value.code == "MISSING_DATASET"


def test_topological_dependencies_first(nightly):
    order = [d["数据集"] for d in nightly["依赖"]]
    assert order.index("orders") < order.index("facts") < order.index("day0") < order.index("ops")


def test_reverse_lag_for_distinct_children(night):
    assert reverse_edges(catalog(read_bundle(night)["datasets"]))["facts"] == [("day0", 0), ("day1", 1)]


def test_duplicate_edges_rejected(small):
    ds = read_bundle(small)["datasets"]
    ds[1]["inputs"] *= 2
    with pytest.raises(ReplayError) as exc:
        catalog(ds)
    assert exc.value.code == "DATASET"


def test_sorted_independent_of_registration_order(small):
    assert topology(catalog(list(reversed(read_bundle(small)["datasets"])))) == ["orders", "facts"]
