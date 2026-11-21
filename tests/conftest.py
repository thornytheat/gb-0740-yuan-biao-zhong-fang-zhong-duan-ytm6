import pytest
from app.config import ROOT
from app.main import create_app
from app.modules.m7_release.service import compute


@pytest.fixture(scope="session")
def small():
    return (ROOT / "sample_data" / "clean.json").read_bytes()


@pytest.fixture(scope="session")
def night():
    return (ROOT / "sample_data" / "nightly.json").read_bytes()


@pytest.fixture(scope="session")
def clean(small):
    return compute(small)


@pytest.fixture(scope="session")
def nightly(night):
    return compute(night)


@pytest.fixture
def client(tmp_path):
    return create_app({"TESTING": True, "DB": tmp_path / "run.sqlite"}).test_client()
