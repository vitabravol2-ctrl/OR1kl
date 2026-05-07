from collections import deque

from btcusdt_sim.data.entities import MarketState, MicroEvent


class MicroEventDetector:
    def __init__(self, max_events: int = 300) -> None:
        self._events: deque[MicroEvent] = deque(maxlen=max_events)

    def detect(self, state: MarketState, ts: int, flow: dict | None = None, order_book: dict | None = None) -> list[MicroEvent]:
        flow = flow or {}
        ob = order_book or {}
        out: list[MicroEvent] = []

        imbalance = abs(ob.get("liquidity_imbalance", 0.0))
        if imbalance > 0.32 and state.volatility < 8:
            out.append(self._event("absorption", ts, 0.72))
        if state.micro_trend > 12 and ob.get("pressure_dominance") == "ASK":
            out.append(self._event("fake breakout candidate", ts, 0.78))
        if state.spread > 10 and imbalance > 0.2:
            out.append(self._event("liquidity grab candidate", ts, 0.83))
        if flow.get("momentum_pulse", 0.0) > 3.5 and flow.get("tick_acceleration", 0.0) < -1.0:
            out.append(self._event("exhaustion", ts, 0.65))
        if abs(ob.get("liquidity_imbalance", 0.0)) < 0.05 and flow.get("flow_acceleration", 0.0) < -1.8:
            out.append(self._event("pressure collapse", ts, 0.7))
        if flow.get("momentum_continuity", 0.0) > 0.7 and flow.get("burst_activity", False):
            out.append(self._event("momentum continuation", ts, 0.74))
        if state.micro_trend < -10 and ob.get("pressure_dominance") == "BID":
            out.append(self._event("trapped side candidate", ts, 0.7))

        return out

    def recent(self, n: int = 16) -> list[MicroEvent]:
        return list(self._events)[-n:]

    def _event(self, name: str, ts: int, severity: float) -> MicroEvent:
        sev = max(0.0, min(1.0, severity))
        level = "LOW" if sev < 0.45 else "MID" if sev < 0.7 else "HIGH" if sev < 0.88 else "CRITICAL"
        lifespan = "active" if sev > 0.6 else "fading"
        ev = MicroEvent(name=name, timestamp=ts, severity=sev, severity_level=level, lifespan=lifespan)
        self._events.append(ev)
        return ev
