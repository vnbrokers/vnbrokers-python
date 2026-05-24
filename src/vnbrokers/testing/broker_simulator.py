from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrokerSimulator:
    responses: dict[str, Any] = field(default_factory=dict)

    def add_response(self, key: str, response: Any) -> None:
        self.responses[key] = response

    def response_for(self, key: str) -> Any:
        return self.responses[key]
