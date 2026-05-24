from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TcbsDTO:
    raw: Any
