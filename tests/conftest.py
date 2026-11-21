import pytest
from app.config import ROOT
from app.main import create_app
from app.modules.m7_issue.service import compute


@pytest.fixture(scope="session")
def small():
    return (ROOT / "sample_data" / "single.json").read_bytes()


@pytest.fixture(scope="session")
def night():
    return (ROOT / "sample_data" / "cutover.json").read_bytes()


@pytest.fixture(scope="session")
def single(small):
    return compute(small)


@pytest.fixture(scope="session")
def cutover(night):
    return compute(night)


@pytest.fixture
def client(tmp_path):
    return create_app({"TESTING": True, "DB": tmp_path / "run.sqlite"}).test_client()
