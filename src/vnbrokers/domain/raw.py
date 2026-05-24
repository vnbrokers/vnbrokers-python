from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawPayload:
    source: str
    data: Any
