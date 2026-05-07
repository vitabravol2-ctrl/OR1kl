import asyncio
import logging
from time import perf_counter, time
from typing import Awaitable, Callable

import orjson
import websockets

from btcusdt_sim.data.entities import Tick, WSHealthState, WsDiagnostics
from btcusdt_sim.utils.config import AppConfig

logger = logging.getLogger(__name__)


class BinanceWsClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._latest_bid = 0.0
        self._latest_ask = 0.0
        self._diag = WsDiagnostics()
        self._latest_depth_bids: list[tuple[float, float]] = []
        self._latest_depth_asks: list[tuple[float, float]] = []

    async def run(
        self,
        on_tick: Callable[[Tick], Awaitable[None]],
        on_diag: Callable[[WsDiagnostics], None],
    ) -> None:
        delay = self._config.reconnect_base_delay_sec
        url = f"{self._config.ws_base_url}?streams={self._config.streams_query}"

        while True:
            self._set_state(WSHealthState.CONNECTING, on_diag)
            try:
                async with websockets.connect(url, ping_interval=15, ping_timeout=15, close_timeout=5) as ws:
                    delay = self._config.reconnect_base_delay_sec
                    self._set_state(WSHealthState.CONNECTED, on_diag)
                    while True:
                        started = perf_counter()
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=self._config.ws_stale_timeout_sec)
                        except asyncio.TimeoutError:
                            self._diag.stale_count += 1
                            self._set_state(WSHealthState.STALE, on_diag)
                            break

                        self._diag.last_message_ts = time()
                        self._diag.latency_ms = (perf_counter() - started) * 1000.0
                        payload = orjson.loads(msg)
                        tick = self._parse_tick(payload)
                        if tick is not None:
                            await on_tick(tick)
                            self._diag.tick_rate = max(self._diag.tick_rate * 0.85, 1.0)
                            state = WSHealthState.DEGRADED if self._diag.latency_ms > 350 else WSHealthState.CONNECTED
                            self._set_state(state, on_diag)
            except Exception as exc:
                logger.warning("[WS] error=%s reconnect_in=%.1fs", exc, delay)

            self._diag.reconnect_count += 1
            self._set_state(WSHealthState.RECONNECTING, on_diag)
            await asyncio.sleep(delay)
            delay = min(delay * 2.0, self._config.reconnect_max_delay_sec)

    def _set_state(self, state: WSHealthState, on_diag: Callable[[WsDiagnostics], None]) -> None:
        self._diag.state = state
        on_diag(self._diag)

    def _parse_tick(self, payload: dict) -> Tick | None:
        data = payload.get("data", {})
        stream = payload.get("stream", "")

        if stream.endswith("@bookTicker"):
            self._latest_bid = float(data.get("b", 0.0))
            self._latest_ask = float(data.get("a", 0.0))
            return None

        if "@depth" in stream:
            self._latest_depth_bids = [(float(p), float(q)) for p, q in data.get("b", [])[:10]]
            self._latest_depth_asks = [(float(p), float(q)) for p, q in data.get("a", [])[:10]]
            return None

        if stream.endswith("@aggTrade"):
            price = float(data.get("p", 0.0))
            quantity = float(data.get("q", 0.0))
            ts = int(data.get("T", 0))
            bid = self._latest_bid or price
            ask = self._latest_ask or price
            spread = max(ask - bid, 0.0)
            mid = (bid + ask) / 2.0
            return Tick(timestamp=ts, bid=bid, ask=ask, spread=spread, mid_price=mid, volume=quantity, bids=self._latest_depth_bids, asks=self._latest_depth_asks)
        return None
