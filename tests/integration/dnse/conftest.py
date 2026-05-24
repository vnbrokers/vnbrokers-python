import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from vnbrokers.brokers.dnse import DnseBroker, DnseConfig
from vnbrokers.transport.http import HttpxTransport


FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "dnse"


@dataclass(frozen=True)
class RouteResponse:
    body: Any
    status_code: int = 200


@dataclass
class LocalDnseServer:
    base_url: str
    statuses: list[int]

    def assert_200_responses(self, expected_count: int) -> None:
        assert self.statuses == [200] * expected_count


def _fixture(name: str) -> Any:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _routes() -> dict[tuple[str, str], RouteResponse]:
    return {
        ("POST", "/registration/send-email-otp"): RouteResponse(
            _fixture("send_email_otp_200.json")
        ),
        ("POST", "/registration/trading-token"): RouteResponse(_fixture("trading_token_200.json")),
        ("GET", "/accounts"): RouteResponse(_fixture("get_accounts_200.json")),
        ("GET", "/accounts/0001179019/balances"): RouteResponse(_fixture("get_balances_200.json")),
        ("GET", "/accounts/0001179019/orders"): RouteResponse(_fixture("get_orders_200.json")),
        ("GET", "/accounts/0001179019/orders/history"): RouteResponse(
            _fixture("get_orders_history_200.json")
        ),
        ("GET", "/accounts/0001179019/executions/42"): RouteResponse(
            {"id": 42, "reports": [{"execId": "E1"}]}
        ),
        ("GET", "/accounts/0001179019/ppse"): RouteResponse(
            {"qmaxBuy": 1209, "qmaxSell": 700, "price": 23000}
        ),
        ("GET", "/accounts/0001179019/loan-packages"): RouteResponse(
            {"symbol": "ACB", "marketType": "STOCK", "loanPackages": [{"id": 1769}]}
        ),
        ("GET", "/accounts/0001179019/positions"): RouteResponse(
            _fixture("get_positions_200.json")
        ),
        ("GET", "/accounts/positions/177796763592657"): RouteResponse(
            _fixture("get_position_200.json")
        ),
        ("POST", "/accounts/positions/177796763592657/close"): RouteResponse(
            _fixture("close_position_200.json")
        ),
        ("POST", "/accounts/orders"): RouteResponse(_fixture("place_order_200.json")),
        ("GET", "/accounts/0001179019/orders/42"): RouteResponse(_fixture("get_order_200.json")),
        ("PUT", "/accounts/0001179019/orders/42"): RouteResponse(_fixture("update_order_200.json")),
        ("DELETE", "/accounts/0001179019/orders/42"): RouteResponse({}),
        ("GET", "/instruments"): RouteResponse(_fixture("get_instruments_200.json")),
        ("GET", "/price/HPG/secdef"): RouteResponse(_fixture("get_secdef_200.json")),
        ("GET", "/market/working-dates"): RouteResponse(_fixture("get_working_dates_200.json")),
        ("GET", "/price/ACB/trades/latest"): RouteResponse(
            _fixture("get_latest_price_trades_200.json")
        ),
        ("GET", "/price/ACB/trades"): RouteResponse(_fixture("get_price_trades_200.json")),
        ("GET", "/price/HPG/close"): RouteResponse(
            {
                "prices": [
                    {
                        "marketId": "STO",
                        "boardId": "G1",
                        "symbol": "HPG",
                        "closePrice": 26.8,
                        "time": "2026-04-08 02:14:59",
                    }
                ]
            }
        ),
        ("GET", "/price/ohlc"): RouteResponse(_fixture("get_ohlc_200.json")),
        ("GET", "/brokers/accounts/care-by"): RouteResponse(
            {"careBy": [{"accountNo": "0001179019", "fullName": "Nguyen Van A"}], "total": 1}
        ),
    }


@contextmanager
def _serve_dnse(routes: dict[tuple[str, str], RouteResponse]) -> Iterator[LocalDnseServer]:
    statuses: list[int] = []

    class Handler(BaseHTTPRequestHandler):
        def do_DELETE(self) -> None:
            self._handle()

        def do_GET(self) -> None:
            self._handle()

        def do_POST(self) -> None:
            self._handle()

        def do_PUT(self) -> None:
            self._handle()

        def log_message(self, format: str, *args: object) -> None:
            return None

        def _handle(self) -> None:
            if self.headers.get("Content-Length"):
                self.rfile.read(int(self.headers["Content-Length"]))

            path = urlsplit(self.path).path
            response = routes.get((self.command, path))
            if response is None:
                statuses.append(404)
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"message": f"No route for {self.path}"}).encode())
                return

            statuses.append(response.status_code)
            self.send_response(response.status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response.body).encode())

    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    except PermissionError as exc:
        pytest.skip(f"Local HTTP server is not permitted in this environment: {exc}")

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield LocalDnseServer(base_url=f"http://{host}:{port}", statuses=statuses)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def dnse_server() -> Iterator[LocalDnseServer]:
    with _serve_dnse(_routes()) as server:
        yield server


@pytest.fixture
def dnse_broker(dnse_server: LocalDnseServer) -> DnseBroker:
    return DnseBroker(
        DnseConfig(
            base_url=dnse_server.base_url,
            api_key="key",
            api_secret="secret",
            trading_token="trade-token",
            market_type="DERIVATIVE",
            positions_page_size=20,
        ),
        http_transport=HttpxTransport(),
    )
