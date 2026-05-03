import pytest

# Provide required env vars for all tests so Settings validation passes
@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
