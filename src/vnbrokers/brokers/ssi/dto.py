from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SsiDTO:
    raw: Any
