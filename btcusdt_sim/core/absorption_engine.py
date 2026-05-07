from collections import deque


class AbsorptionEngine:
    def __init__(self, history: int = 180) -> None:
        self._strength_hist: deque[float] = deque(maxlen=history)

    def update(self, market_state: dict, flow: dict, depth: dict) -> dict:
        aggression = float(market_state.get("aggression", 0.0))
        accel = float(flow.get("flow_acceleration", 0.0))
        imbalance = float(depth.get("liquidity_imbalance", 0.0))
        continuity = float(flow.get("momentum_continuity", 0.0))

        buy_abs = max(0.0, aggression * max(0.0, imbalance) * max(0.0, -accel + 0.4))
        sell_abs = max(0.0, aggression * max(0.0, -imbalance) * max(0.0, accel + 0.4))
        absorption_strength = min(1.0, buy_abs + sell_abs)
        stalled = absorption_strength > 0.22 and continuity < 0.58
        failed_push = absorption_strength > 0.32 and abs(accel) < 0.24
        trapped = stalled and abs(imbalance) > 0.22

        self._strength_hist.append(absorption_strength)

        return {
            "buy_absorbed": buy_abs,
            "sell_absorbed": sell_abs,
            "absorption_strength": absorption_strength,
            "trapped_continuation": trapped,
            "failed_push": failed_push,
            "stalled_momentum": stalled,
            "strength_series": list(self._strength_hist),
            "status": "ACTIVE" if absorption_strength > 0.24 else "LIGHT" if absorption_strength > 0.12 else "INACTIVE",
        }
