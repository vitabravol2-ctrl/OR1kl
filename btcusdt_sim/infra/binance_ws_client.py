import asyncio
import logging
from typing import Awaitable, Callable

import orjson
import websockets

from btcusdt_sim.data.entities import Tick
from btcusdt_sim.utils.config import AppConfig

logger = logging.getLogger(__name__)


class BinanceWsClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._latest_bid = 0.0
        self._latest_ask = 0.0

    async def run(self, on_tick: Callable[[Tick], Awaitable[None]]) -> None:
        delay = self._config.reconnect_base_delay_sec
        url = f"{self._config.ws_base_url}?streams={self._config.streams_query}"

        while True:
            try:
                logger.info("Connecting to Binance WS: %s", url)
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    logger.info("Connected to Binance WS")
                    delay = self._config.reconnect_base_delay_sec
                    async for message in ws:
                        payload = orjson.loads(message)
                        tick = self._parse_tick(payload)
                        if tick:
                            await on_tick(tick)
            except Exception as exc:  # reconnect safety
                logger.warning("WS error: %s. Reconnect in %.1fs", exc, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._config.reconnect_max_delay_sec)

    def _parse_tick(self, payload: dict) -> Tick | None:
        data = payload.get("data", {})
        stream = payload.get("stream", "")

        if stream.endswith("@bookTicker"):
            self._latest_bid = float(data.get("b", 0.0))
            self._latest_ask = float(data.get("a", 0.0))
            return None

        if stream.endswith("@aggTrade"):
            price = float(data.get("p", 0.0))
            quantity = float(data.get("q", 0.0))
            ts = int(data.get("T", 0))
            bid = self._latest_bid or price
            ask = self._latest_ask or price
            spread = max(ask - bid, 0.0)
            mid = (bid + ask) / 2.0
            return Tick(timestamp=ts, bid=bid, ask=ask, spread=spread, mid_price=mid, volume=quantity)

        return None
