import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).parents[3]


def _load_common_module() -> ModuleType:
    path = ROOT / "examples" / "dnse" / "_common.py"
    spec = importlib.util.spec_from_file_location("dnse_examples_common", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_require_env_returns_configured_value(monkeypatch: pytest.MonkeyPatch) -> None:
    common = _load_common_module()

    monkeypatch.setenv("DNSE_ACCOUNT_NO", "0001179019")

    assert common.require_env("DNSE_ACCOUNT_NO") == "0001179019"


def test_require_env_rejects_missing_or_empty_value(monkeypatch: pytest.MonkeyPatch) -> None:
    common = _load_common_module()

    monkeypatch.delenv("DNSE_ACCOUNT_NO", raising=False)
    with pytest.raises(RuntimeError, match="DNSE_ACCOUNT_NO is required"):
        common.require_env("DNSE_ACCOUNT_NO")

    monkeypatch.setenv("DNSE_ACCOUNT_NO", "")
    with pytest.raises(RuntimeError, match="DNSE_ACCOUNT_NO is required"):
        common.require_env("DNSE_ACCOUNT_NO")


def test_get_positions_example_requires_account_no() -> None:
    source = (ROOT / "examples" / "dnse" / "get_positions.py").read_text(encoding="utf-8")

    assert 'require_env("DNSE_ACCOUNT_NO")' in source
    assert 'os.getenv("DNSE_ACCOUNT_NO", "")' not in source
    assert 'os.getenv("DNSE_ACCOUNT_ID", "")' not in source
