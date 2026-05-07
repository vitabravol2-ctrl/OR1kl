from collections import deque

from btcusdt_sim.data.entities import MarketState, MicroEvent


class MicroEventDetector:
    def __init__(self, max_events: int = 300, cooldown_ms: int = 1600) -> None:
        self._events: deque[MicroEvent] = deque(maxlen=max_events)
        self._last_emit: dict[str, int] = {}
        self._cooldown_ms = cooldown_ms

    def detect(self, state: MarketState, ts: int, flow: dict | None = None, order_book: dict | None = None) -> list[MicroEvent]:
        flow = flow or {}
        ob = order_book or {}
        candidates: list[tuple[str, float]] = []

        imbalance = abs(ob.get("liquidity_imbalance", 0.0))
        if imbalance > 0.32 and state.volatility < 8:
            candidates.append(("absorption", 0.72))
        if state.micro_trend > 12 and ob.get("pressure_dominance") == "ASK":
            candidates.append(("fake breakout candidate", 0.78))
        if state.spread > 10 and imbalance > 0.2:
            candidates.append(("liquidity grab candidate", 0.83))
        if flow.get("momentum_pulse", 0.0) > 3.5 and flow.get("tick_acceleration", 0.0) < -1.0:
            candidates.append(("exhaustion", 0.65))
        if abs(ob.get("liquidity_imbalance", 0.0)) < 0.05 and flow.get("flow_acceleration", 0.0) < -1.8:
            candidates.append(("pressure collapse", 0.7))
        if flow.get("momentum_continuity", 0.0) > 0.7 and flow.get("burst_activity", False):
            candidates.append(("momentum continuation", 0.74))
        if state.micro_trend < -10 and ob.get("pressure_dominance") == "BID":
            candidates.append(("trapped side candidate", 0.7))

        grouped: dict[str, float] = {}
        for name, sev in candidates:
            grouped[name] = max(grouped.get(name, 0.0), sev)

        out: list[MicroEvent] = []
        for name, sev in grouped.items():
            last = self._last_emit.get(name, 0)
            if ts - last < self._cooldown_ms:
                continue
            ev = self._event(name, ts, sev)
            out.append(ev)
            self._last_emit[name] = ts

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
