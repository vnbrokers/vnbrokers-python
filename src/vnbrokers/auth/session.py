from dataclasses import dataclass


@dataclass(frozen=True)
class AuthSession:
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: str | None = None
