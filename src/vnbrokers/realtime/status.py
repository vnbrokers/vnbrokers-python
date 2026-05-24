from enum import Enum


class ConnectionStatus(str, Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATING = "authenticating"
    SUBSCRIBED = "subscribed"
    RECONNECTING = "reconnecting"
    CLOSING = "closing"
    CLOSED = "closed"
    FAILED = "failed"
