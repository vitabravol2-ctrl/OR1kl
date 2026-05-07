from collections import deque


class MarketMemoryEngine:
    def __init__(self, size: int = 180) -> None:
        self._liquidity_zones: deque[float] = deque(maxlen=size)
        self._sweeps: deque[float] = deque(maxlen=size)
        self._rejections: deque[float] = deque(maxlen=size)
        self._pressure_hist: deque[float] = deque(maxlen=size)

    def update(self, price: float, pressure: float, spread: float, volatility: float) -> dict:
        if abs(pressure) > 0.25:
            self._liquidity_zones.append(price)
        if spread > 8 or volatility > 10:
            self._sweeps.append(price)
        if len(self._liquidity_zones) > 2 and any(abs(price - p) < 1.5 for p in list(self._liquidity_zones)[-6:]):
            self._rejections.append(price)
        self._pressure_hist.append(pressure)

        return {
            "recent_liquidity_zones": list(self._liquidity_zones)[-8:],
            "recent_sweeps": list(self._sweeps)[-8:],
            "repeated_rejection_levels": list(self._rejections)[-8:],
            "pressure_history": list(self._pressure_hist),
        }
