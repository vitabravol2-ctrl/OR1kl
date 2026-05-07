from collections import deque


class OrderBookEngine:
    def __init__(self, history: int = 240) -> None:
        self._bid_liquidity = 0.0
        self._ask_liquidity = 0.0
        self._imbalance = 0.0
        self._pressure = "NEUTRAL"
        self._bid_walls: list[tuple[float, float]] = []
        self._ask_walls: list[tuple[float, float]] = []
        self._depth_heat: deque[float] = deque(maxlen=history)
        self._pressure_hist: deque[float] = deque(maxlen=history)

    def update(self, bids: list[tuple[float, float]], asks: list[tuple[float, float]]) -> dict:
        self._bid_liquidity = sum(q for _, q in bids)
        self._ask_liquidity = sum(q for _, q in asks)
        total = self._bid_liquidity + self._ask_liquidity + 1e-9
        self._imbalance = (self._bid_liquidity - self._ask_liquidity) / total

        bid_threshold = self._bid_liquidity / max(len(bids), 1) * 1.8
        ask_threshold = self._ask_liquidity / max(len(asks), 1) * 1.8
        self._bid_walls = [(p, q) for p, q in bids if q >= bid_threshold][:4]
        self._ask_walls = [(p, q) for p, q in asks if q >= ask_threshold][:4]

        self._pressure = "BID" if self._imbalance > 0.08 else "ASK" if self._imbalance < -0.08 else "NEUTRAL"
        concentration = max([q for _, q in bids + asks], default=0.0)
        self._depth_heat.append(concentration)
        self._pressure_hist.append(self._imbalance)

        return {
            "bid_liquidity": self._bid_liquidity,
            "ask_liquidity": self._ask_liquidity,
            "liquidity_imbalance": self._imbalance,
            "pressure_dominance": self._pressure,
            "bid_walls": self._bid_walls,
            "ask_walls": self._ask_walls,
            "liquidity_concentration": concentration,
            "pressure_series": list(self._pressure_hist),
            "depth_heat_series": list(self._depth_heat),
        }
