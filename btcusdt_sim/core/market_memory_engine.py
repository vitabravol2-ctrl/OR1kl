from collections import deque


class MarketMemoryEngine:
    def __init__(self, size: int = 180) -> None:
        self._liquidity_zones: deque[float] = deque(maxlen=size)
        self._sweeps: deque[float] = deque(maxlen=size)
        self._rejections: deque[float] = deque(maxlen=size)
        self._pressure_hist: deque[float] = deque(maxlen=size)
        self._momentum_memory: deque[float] = deque(maxlen=size)

    def update(self, price: float, pressure: float, spread: float, volatility: float, momentum: float = 0.0) -> dict:
        if abs(pressure) > 0.25:
            self._liquidity_zones.append(price)
        if spread > 8 or volatility > 10:
            self._sweeps.append(price)
        if len(self._liquidity_zones) > 2 and any(abs(price - p) < 1.5 for p in list(self._liquidity_zones)[-6:]):
            self._rejections.append(price)
        self._pressure_hist.append(pressure)
        self._momentum_memory.append(momentum)

        repeated_sweep_zones = [p for p in self._sweeps if abs(price - p) < 2.0]
        persistent_pressure = [p for p in self._liquidity_zones if abs(price - p) < 1.2]
        imbalance_clusters = [p for p in self._liquidity_zones if abs(price - p) < 2.8]

        return {
            "recent_liquidity_zones": list(self._liquidity_zones)[-8:],
            "recent_sweeps": list(self._sweeps)[-8:],
            "repeated_rejection_levels": list(self._rejections)[-8:],
            "pressure_history": list(self._pressure_hist),
            "repeated_sweep_zones": repeated_sweep_zones[-8:],
            "persistent_pressure_zones": persistent_pressure[-8:],
            "historical_imbalance_clusters": imbalance_clusters[-8:],
            "momentum_memory": list(self._momentum_memory)[-20:],
        }
