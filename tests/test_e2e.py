from app.modules import VIEWS


def test_each_independent_module(client):
    result = client.post("/api/plans", json={"sample": "nightly"}).json
    for route, (_, fields) in VIEWS.items():
        api = client.get(f"/api/{route}/{result['id']}")
        assert api.status_code == 200 and set(api.json) == set(fields)
        assert client.get(f"/console/{route}?plan={result['id']}").status_code == 200


def test_distinct_expected_results(client):
    clean = client.post("/api/plans", json={"sample": "clean"}).json
    night = client.post("/api/plans", json={"sample": "nightly"}).json
    assert clean["summary"]["待写"] == clean["rollback"]["演练写入"] == 2
    assert night["summary"]["受影响"] > 10
    assert night["rollback"]["恢复一致"]
