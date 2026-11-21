import hashlib
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from app.modules.m7_release.service import execute
from app.modules.m7_release.store import Catalog


def test_identical_plan_idempotent(client):
    a = client.post("/api/plans", json={"sample": "clean"})
    b = client.post("/api/plans", json={"sample": "clean"})
    assert (a.status_code, b.status_code) == (201, 200)
    assert a.json["id"] == b.json["id"] and b.json["reused"]
    assert len(client.get("/api/plans").json) == 1


def test_bad_input_without_partial_plan(client):
    response = client.post("/api/plans", data={"bundle": (BytesIO(b"{"), "broken.json")})
    assert response.status_code == 422 and response.json["code"] == "JSON"
    assert client.get("/api/plans").json == []


def test_upload_is_attested(client, small):
    run = client.post("/api/plans", data={"bundle": (BytesIO(small), "source.json")}).json
    pack = client.get(f"/api/export/{run['id']}")
    assert "attachment" in pack.headers["Content-Disposition"]
    assert pack.json["批次"]["文件摘要"] == hashlib.sha256(small).hexdigest()


def test_parallel_convergence(tmp_path, small):
    store = Catalog(tmp_path / "archive.sqlite")
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: execute(store, small), range(4)))
    assert sum(not reused for _, reused in results) == 1
    assert len(store.latest()) == 1


def test_persistent_plan(tmp_path, small):
    path = tmp_path / "archive.sqlite"
    result, _ = execute(Catalog(path), small)
    assert Catalog(path).get(result["批次"]["编号"])["分区勾稽"]["模拟行数"] == "24"


def test_distinct_sources_distinct_batches(client):
    ids = [client.post("/api/plans", json={"sample": sample}).json["id"] for sample in ["clean", "nightly"]]
    assert len(set(ids)) == 2
