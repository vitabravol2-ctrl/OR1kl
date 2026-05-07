from collections import deque
from typing import Iterable

import numpy as np

from btcusdt_sim.data.entities import Tick


class MarketBuffer:
    def __init__(self, maxlen: int = 5000) -> None:
        self._ticks: deque[Tick] = deque(maxlen=maxlen)

    def append(self, tick: Tick) -> None:
        self._ticks.append(tick)

    def __len__(self) -> int:
        return len(self._ticks)

    def latest(self) -> Tick | None:
        return self._ticks[-1] if self._ticks else None

    def tail(self, n: int) -> Iterable[Tick]:
        if n <= 0:
            return []
        return list(self._ticks)[-n:]

    def to_numpy_mid_prices(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.array([t.mid_price for t in sample], dtype=np.float64)

    def to_numpy_spreads(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.array([t.spread for t in sample], dtype=np.float64)

    def to_numpy_volumes(self, n: int = 200) -> np.ndarray:
        sample = self.tail(n)
        return np.array([t.volume for t in sample], dtype=np.float64)
