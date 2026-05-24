import json
from pathlib import Path
from typing import Any


def load_json_fixture(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
