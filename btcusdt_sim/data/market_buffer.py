from collections import deque
from time import perf_counter

import numpy as np

from btcusdt_sim.data.entities import Tick


class MarketBuffer:
    def __init__(self, maxlen: int = 5000) -> None:
        self._maxlen = maxlen
        self._ticks: deque[Tick] = deque(maxlen=maxlen)
        self._tick_times: deque[float] = deque(maxlen=2048)
        self._dropped_ticks = 0

    def append(self, tick: Tick) -> None:
        if len(self._ticks) == self._maxlen:
            self._dropped_ticks += 1
        self._ticks.append(tick)
        self._tick_times.append(perf_counter())

    def __len__(self) -> int:
        return len(self._ticks)

    def capacity(self) -> int:
        return self._maxlen

    def fill_ratio(self) -> float:
        return len(self._ticks) / self._maxlen if self._maxlen else 0.0

    def dropped_ticks(self) -> int:
        return self._dropped_ticks

    def latest(self) -> Tick | None:
        return self._ticks[-1] if self._ticks else None

    def tail(self, n: int) -> list[Tick]:
        if n <= 0:
            return []
        return list(self._ticks)[-n:]

    def to_numpy_mid_prices(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.fromiter((t.mid_price for t in sample), dtype=np.float64, count=len(sample))

    def to_numpy_spreads(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.fromiter((t.spread for t in sample), dtype=np.float64, count=len(sample))

    def to_numpy_volumes(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.fromiter((t.volume for t in sample), dtype=np.float64, count=len(sample))

    def metrics(self, n: int = 300) -> dict:
        sample = self.tail(n)
        if not sample:
            return {"avg_spread": 0.0, "short_volatility": 0.0, "tick_pressure": 0.0, "ticks_per_sec": 0.0}
        spreads = np.fromiter((t.spread for t in sample), dtype=np.float64, count=len(sample))
        mids = np.fromiter((t.mid_price for t in sample), dtype=np.float64, count=len(sample))
        volumes = np.fromiter((t.volume for t in sample), dtype=np.float64, count=len(sample))

        avg_spread = float(np.mean(spreads)) if spreads.size else 0.0
        short_volatility = float(np.std(mids)) if mids.size > 1 else 0.0
        tick_pressure = float(np.tanh(np.mean(volumes) / (np.std(volumes) + 1e-9))) if volumes.size else 0.0

        now = perf_counter()
        ticks_per_sec = 0.0
        if self._tick_times:
            window = 1.0
            recent = sum(1 for ts in self._tick_times if now - ts <= window)
            ticks_per_sec = float(recent) / window

        return {
            "avg_spread": avg_spread,
            "short_volatility": short_volatility,
            "tick_pressure": tick_pressure,
            "ticks_per_sec": ticks_per_sec,
        }
