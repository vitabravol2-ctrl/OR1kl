from collections import Counter, deque


class TacticalSignalEngine:
    STATES = [
        "PRESSURE_BUILDUP",
        "LIQUIDITY_TRAP",
        "SWEEP_RISK",
        "MOMENTUM_SURGE",
        "ABSORPTION",
        "DEAD_FLOW",
        "CHAOTIC_FLOW",
        "TREND_CONTINUATION",
        "REVERSAL_RISK",
        "NEUTRAL_FLOW",
    ]

    def __init__(self, history: int = 220) -> None:
        self._state_hist: deque[str] = deque(maxlen=history)
        self._danger_hist: deque[float] = deque(maxlen=history)
        self._opp_hist: deque[float] = deque(maxlen=history)

    def evaluate(self, state: dict) -> dict:
        flow = state.get("flow", {})
        depth = state.get("depth", {})
        memory = state.get("memory", {})
        market_state = state.get("market_state", {})
        regime = state.get("regime", "CALM")
        events = state.get("events", [])

        imbalance = float(depth.get("liquidity_imbalance", 0.0))
        accel = float(flow.get("flow_acceleration", 0.0))
        pulse = float(flow.get("momentum_pulse", 0.0))
        continuity = float(flow.get("momentum_continuity", 0.0))
        volatility = float(market_state.get("volatility", 0.0))
        aggression = float(market_state.get("aggression", 0.0))
        event_density = len(events)

        if flow.get("dead_zone", False) and abs(imbalance) < 0.08:
            tactical_state = "DEAD_FLOW"
        elif regime == "CHAOTIC" or volatility > 15:
            tactical_state = "CHAOTIC_FLOW"
        elif abs(imbalance) > 0.38 and continuity > 0.65:
            tactical_state = "PRESSURE_BUILDUP"
        elif pulse > 3.8 and accel > 1.4:
            tactical_state = "MOMENTUM_SURGE"
        elif abs(imbalance) > 0.28 and abs(accel) < 0.35 and aggression < 0.35:
            tactical_state = "ABSORPTION"
        elif len(memory.get("repeated_sweep_zones", [])) >= 3 and abs(imbalance) > 0.2:
            tactical_state = "SWEEP_RISK"
        elif len(memory.get("historical_imbalance_clusters", [])) >= 3 and continuity < 0.5:
            tactical_state = "LIQUIDITY_TRAP"
        elif continuity > 0.72 and abs(imbalance) > 0.22:
            tactical_state = "TREND_CONTINUATION"
        elif continuity < 0.45 and abs(imbalance) > 0.2 and event_density > 3:
            tactical_state = "REVERSAL_RISK"
        else:
            tactical_state = "NEUTRAL_FLOW"

        danger = min(1.0, 0.36 * abs(imbalance) + 0.28 * max(0.0, -accel) + 0.2 * min(event_density / 8.0, 1.0) + 0.16 * min(volatility / 20.0, 1.0))
        opportunity = min(1.0, 0.36 * max(0.0, accel / 3.0) + 0.24 * min(pulse / 5.0, 1.0) + 0.22 * continuity + 0.18 * abs(imbalance))

        self._state_hist.append(tactical_state)
        self._danger_hist.append(danger)
        self._opp_hist.append(opportunity)

        dominant_side = "BUY" if imbalance > 0.08 else "SELL" if imbalance < -0.08 else "NEUTRAL"
        pressure_direction = "UP" if accel > 0.35 else "DOWN" if accel < -0.35 else "FLAT"
        stress = min(1.0, abs(imbalance) * 1.6 + volatility / 24.0)

        severity = max(danger, abs(imbalance), min(event_density / 8.0, 1.0))
        priority = "LOW" if severity < 0.32 else "MID" if severity < 0.56 else "HIGH" if severity < 0.78 else "CRITICAL"

        counts = Counter(e.get("severity_level", "LOW") for e in events)

        return {
            "state": tactical_state,
            "priority": priority,
            "dominant_side": dominant_side,
            "pressure_direction": pressure_direction,
            "liquidity_stress": stress,
            "momentum_state": "SURGE" if pulse > 3.2 else "EXHAUSTION" if accel < -1.1 else "STABLE",
            "tactical_danger": danger,
            "tactical_opportunity": opportunity,
            "signal_density": event_density,
            "severity_counts": dict(counts),
            "state_history": list(self._state_hist),
            "danger_series": list(self._danger_hist),
            "opportunity_series": list(self._opp_hist),
        }
