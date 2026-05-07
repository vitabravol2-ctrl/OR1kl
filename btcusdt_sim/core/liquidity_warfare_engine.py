from collections import deque


class LiquidityWarfareEngine:
    def __init__(self, history: int = 180, min_state_duration: int = 4) -> None:
        self._prev_bid_walls: dict[float, float] = {}
        self._prev_ask_walls: dict[float, float] = {}
        self._consumption_hist: deque[float] = deque(maxlen=history)
        self._exhaustion_hist: deque[float] = deque(maxlen=history)
        self._state = "STABLE"
        self._state_age = 0
        self._min_state_duration = min_state_duration

    def update(self, depth: dict, flow: dict) -> dict:
        bid_walls = {round(p, 2): q for p, q in depth.get("bid_walls", [])}
        ask_walls = {round(p, 2): q for p, q in depth.get("ask_walls", [])}

        appeared = len([p for p in bid_walls if p not in self._prev_bid_walls]) + len([p for p in ask_walls if p not in self._prev_ask_walls])
        disappeared = len([p for p in self._prev_bid_walls if p not in bid_walls]) + len([p for p in self._prev_ask_walls if p not in ask_walls])

        aggressive = abs(float(flow.get("momentum_pulse", 0.0))) + abs(float(flow.get("flow_acceleration", 0.0)))
        consumption = min(1.0, (disappeared * 0.18) + aggressive * 0.09)
        spoof_risk = min(1.0, (disappeared * 0.22) + (appeared * 0.08) + max(0.0, 0.25 - abs(depth.get("liquidity_imbalance", 0.0))))
        sweeping = min(1.0, aggressive / 4.2 + consumption * 0.4)
        exhaustion = min(1.0, max(0.0, float(flow.get("momentum_continuity", 0.0)) - sweeping) + consumption * 0.35)

        self._consumption_hist.append(consumption)
        self._exhaustion_hist.append(exhaustion)

        proposed = "STABLE"
        if spoof_risk > 0.62:
            proposed = "FAKE_PRESSURE"
        elif sweeping > 0.72:
            proposed = "AGGRESSIVE_SWEEP"
        elif exhaustion > 0.65:
            proposed = "EXHAUSTED_FLOW"
        elif consumption > 0.48:
            proposed = "LIQUIDITY_CONSUMPTION"

        self._state_age += 1
        if proposed != self._state and self._state_age >= self._min_state_duration:
            self._state = proposed
            self._state_age = 0

        self._prev_bid_walls = bid_walls
        self._prev_ask_walls = ask_walls

        return {
            "state": self._state,
            "wall_appeared": appeared,
            "wall_disappeared": disappeared,
            "fake_liquidity_risk": spoof_risk,
            "sweep_risk": sweeping,
            "liquidity_consumption": consumption,
            "exhaustion_risk": exhaustion,
            "consumption_series": list(self._consumption_hist),
            "exhaustion_series": list(self._exhaustion_hist),
        }
