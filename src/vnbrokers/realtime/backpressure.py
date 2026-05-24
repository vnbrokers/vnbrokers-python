from dataclasses import dataclass
from enum import Enum


class BackpressureMode(str, Enum):
    ERROR_ON_OVERFLOW = "error_on_overflow"
    DROP_OLDEST = "drop_oldest"


@dataclass(frozen=True)
class BackpressurePolicy:
    mode: BackpressureMode = BackpressureMode.ERROR_ON_OVERFLOW
    max_queue_size: int = 1024
