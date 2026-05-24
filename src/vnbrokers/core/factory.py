from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

from vnbrokers.core.broker import Broker
from vnbrokers.core.config import BrokerConfig

ConfigT = TypeVar("ConfigT", bound=BrokerConfig)
BrokerT = TypeVar("BrokerT", bound=Broker)


@dataclass(frozen=True)
class BrokerRegistration(Generic[ConfigT, BrokerT]):
    name: str
    broker_type: type[BrokerT]
    config_type: type[ConfigT]

    def create(self, config: ConfigT | None = None, **config_kwargs: Any) -> BrokerT:
        if config is not None and config_kwargs:
            raise TypeError("Pass either config or config keyword arguments, not both")
        if config is None:
            config = self.config_type(**config_kwargs)
        return self.broker_type(config)  # type: ignore[call-arg]


class BrokerFactory:
    def __init__(self, registrations: list[BrokerRegistration[Any, Broker]] | None = None) -> None:
        self._registrations: dict[str, BrokerRegistration[Any, Broker]] = {}
        for registration in registrations or []:
            self.register(registration)

    def register(self, registration: BrokerRegistration[Any, Broker]) -> None:
        self._registrations[_normalize_name(registration.name)] = registration

    def list_brokers(self) -> tuple[str, ...]:
        return tuple(sorted(self._registrations))

    def get_registration(self, name: str) -> BrokerRegistration[Any, Broker]:
        normalized = _normalize_name(name)
        try:
            return self._registrations[normalized]
        except KeyError as exc:
            raise ValueError(f"Unsupported broker: {normalized}") from exc

    def create_broker(
        self,
        name: str,
        config: BrokerConfig | None = None,
        **config_kwargs: Any,
    ) -> Broker:
        registration = self.get_registration(name)
        return registration.create(cast(Any, config), **config_kwargs)


def _normalize_name(name: str) -> str:
    return name.strip().lower()
