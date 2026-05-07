from collections import deque

from btcusdt_sim.data.entities import Tick


class TickFlowEngine:
    def __init__(self, window: int = 160) -> None:
        self._price_delta: deque[float] = deque(maxlen=window)
        self._spread_values: deque[float] = deque(maxlen=window)
        self._aggression_values: deque[float] = deque(maxlen=window)
        self._velocity_values: deque[float] = deque(maxlen=window)
        self._last_tick_ts: int | None = None

    def update(self, tick: Tick, ticks_per_sec: float, aggression: float) -> dict:
        prev_mid = self._price_delta[-1] if self._price_delta else tick.mid_price
        delta = tick.mid_price - prev_mid
        self._price_delta.append(tick.mid_price)
        self._spread_values.append(tick.spread)
        self._aggression_values.append(aggression)
        self._velocity_values.append(ticks_per_sec)

        buy_wave = max(delta, 0.0)
        sell_wave = max(-delta, 0.0)
        pressure_shift = buy_wave - sell_wave

        tick_acceleration = 0.0
        if len(self._velocity_values) >= 2:
            tick_acceleration = self._velocity_values[-1] - self._velocity_values[-2]

        momentum_pulse = abs(delta) * (1.0 + abs(tick_acceleration) * 0.02)
        buyer_dom = min(max(0.5 + pressure_shift * 25.0, 0.0), 1.0)
        seller_dom = 1.0 - buyer_dom

        return {
            "buy_wave": buy_wave,
            "sell_wave": sell_wave,
            "pressure_shift": pressure_shift,
            "tick_acceleration": tick_acceleration,
            "momentum_pulse": momentum_pulse,
            "buyer_dominance": buyer_dom,
            "seller_dominance": seller_dom,
            "price_series": list(self._price_delta),
            "spread_series": list(self._spread_values),
            "aggression_series": list(self._aggression_values),
            "velocity_series": list(self._velocity_values),
        }
