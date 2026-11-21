from app.modules import VIEWS


def test_each_independent_module(client):
    result = client.post("/api/admissions", json={"sample": "cutover"}).json
    for route, (_, fields) in VIEWS.items():
        api = client.get(f"/api/{route}/{result['id']}")
        assert api.status_code == 200 and set(api.json) == set(fields)
        assert client.get(f"/console/{route}?plan={result['id']}").status_code == 200


def test_operations_endpoints_share_one_admission(client):
    key = client.post("/api/admissions", json={"sample": "cutover"}).json["id"]
    for route in ("publish", "recheck", "backfill"):
        api = client.get(f"/api/{route}/{key}")
        assert api.status_code == 200 and api.json["准入"] == key


def test_distinct_expected_results(client):
    single = client.post("/api/admissions", json={"sample": "single"}).json
    cutover = client.post("/api/admissions", json={"sample": "cutover"}).json
    assert single["coverage"]["独立交付"] == 1 and single["rollback"]["恢复一致"]
    assert cutover["coverage"]["不可放行"] == 3
    assert cutover["rollback"]["断链"] == ["northeast@2026-11-21"]


def test_unknown_plan_is_404(client):
    assert client.get("/console/admission?plan=missing").status_code == 404
    assert client.get("/api/admission/missing").status_code == 404
