from app.modules.m3_fingerprint.service import destination, fingerprint, source_state


def test_canonical_keys_order():
    assert fingerprint({"a": 0, "b": 1}) == fingerprint({"b": 1, "a": 0})


def test_versions_contains_revision(clean):
    inputs = clean["排程"][1]["上游"]
    assert (
        destination("facts", "build-04", "2026-11-17", inputs)["version"]
        != destination("facts", "build-05", "2026-11-17", inputs)["version"]
    )


def test_partition_date_changes_hash(clean):
    inputs = clean["排程"][1]["上游"]
    assert (
        destination("facts", "build-04", "2026-11-17", inputs)["version"]
        != destination("facts", "build-04", "2026-11-18", inputs)["version"]
    )


def test_source_same_snapshot_can_be_replayed():
    assert (
        source_state({"version": "r1", "rows": 3}, {"version": "r1", "rows": 3, "previous": "r0"})[0]
        == "reuse"
    )


def test_same_version_different_content_blocks():
    assert source_state({"version": "r1", "rows": 3}, {"version": "r1", "rows": 6, "previous": "r1"}) == (
        "blocked",
        None,
        "STALE_HEAD",
    )


def test_plan_rows_from_sources(clean):
    assert clean["排程"][1]["计划"]["rows"] == 12


def test_large_nested_counts_serialize_losslessly():
    from app.modules.m7_release.service import safe_counts

    assert safe_counts({"rows": 2**53 + 1}) == {"rows": "9007199254740993"}
