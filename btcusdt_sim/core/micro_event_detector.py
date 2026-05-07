from collections import deque

from btcusdt_sim.data.entities import MarketState, MicroEvent


class MicroEventDetector:
    def __init__(self, max_events: int = 200) -> None:
        self._events: deque[MicroEvent] = deque(maxlen=max_events)

    def detect(self, state: MarketState, ts: int) -> list[MicroEvent]:
        out: list[MicroEvent] = []
        if state.spread > 12:
            out.append(self._event("spread explosion", ts, min(1.0, state.spread / 30)))
        if abs(state.aggression) > 0.75:
            out.append(self._event("aggression spike", ts, abs(state.aggression)))
        if abs(state.imbalance) > 0.35:
            out.append(self._event("sudden imbalance shift", ts, min(1.0, abs(state.imbalance))))
        if state.volatility > 18:
            out.append(self._event("volatility burst", ts, min(1.0, state.volatility / 40)))
        if state.spread > 10 and abs(state.imbalance) > 0.2:
            out.append(self._event("liquidity sweep candidate", ts, 0.8))
        if abs(state.micro_trend) > 16 and state.tick_velocity > 10:
            out.append(self._event("momentum ignition", ts, 0.85))
        if state.volatility < 1.0 and state.tick_velocity < 1.5:
            out.append(self._event("dead market", ts, 0.6))
        return out

    def recent(self, n: int = 10) -> list[MicroEvent]:
        return list(self._events)[-n:]

    def _event(self, name: str, ts: int, severity: float) -> MicroEvent:
        ev = MicroEvent(name=name, timestamp=ts, severity=max(0.0, min(1.0, severity)))
        self._events.append(ev)
        return ev
