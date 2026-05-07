from collections import deque


class ReactionEngine:
    STATES = [
        "FAST_ACCEPTANCE",
        "WEAK_RESPONSE",
        "FAILED_BREAK",
        "AGGRESSIVE_ACCEPTANCE",
        "STALLED_MOVE",
        "REJECTION",
        "PANIC_FLOW",
        "EXHAUSTED_FLOW",
    ]

    def __init__(self, history: int = 200, alpha: float = 0.25) -> None:
        self._reaction_hist: deque[float] = deque(maxlen=history)
        self._delay_hist: deque[float] = deque(maxlen=history)
        self._last_impulse = 0.0
        self._smoothed_speed = 0.0
        self._alpha = alpha

    def update(self, flow: dict, depth: dict, absorption: dict) -> dict:
        accel = float(flow.get("flow_acceleration", 0.0))
        pulse = float(flow.get("momentum_pulse", 0.0))
        continuity = float(flow.get("momentum_continuity", 0.0))
        imbalance = float(depth.get("liquidity_imbalance", 0.0))

        impulse = abs(accel) + abs(pulse) * 0.45 + abs(imbalance) * 1.4
        reaction_delay = max(0.0, self._last_impulse - impulse)
        reaction_speed = min(1.0, impulse / 3.8)
        self._smoothed_speed = self._smoothed_speed * (1 - self._alpha) + reaction_speed * self._alpha
        follow = min(1.0, continuity * 0.65 + self._smoothed_speed * 0.35)
        failed_follow = follow < 0.38 and impulse > 0.5
        delayed_impulse = reaction_delay > 0.35 and impulse < 0.55
        rejection_strength = min(1.0, absorption.get("absorption_strength", 0.0) * 1.2 + max(0.0, -accel) * 0.24)
        continuation_prob = min(1.0, max(0.0, follow - rejection_strength * 0.45 + abs(imbalance) * 0.2))

        state = "WEAK_RESPONSE"
        if impulse > 2.8 and follow > 0.72:
            state = "AGGRESSIVE_ACCEPTANCE"
        elif reaction_speed > 0.74 and follow > 0.62:
            state = "FAST_ACCEPTANCE"
        elif failed_follow and rejection_strength > 0.5:
            state = "FAILED_BREAK"
        elif delayed_impulse:
            state = "STALLED_MOVE"
        elif rejection_strength > 0.64:
            state = "REJECTION"
        elif abs(accel) > 2.2 and follow < 0.45:
            state = "PANIC_FLOW"
        elif follow < 0.32 and impulse < 0.48:
            state = "EXHAUSTED_FLOW"

        self._reaction_hist.append(self._smoothed_speed)
        self._delay_hist.append(reaction_delay)
        self._last_impulse = impulse

        return {
            "state": state,
            "response_delay": reaction_delay,
            "reaction_speed": self._smoothed_speed,
            "follow_through": follow,
            "failed_follow_through": failed_follow,
            "delayed_impulse": delayed_impulse,
            "continuation_probability": continuation_prob,
            "rejection_strength": rejection_strength,
            "reaction_series": list(self._reaction_hist),
            "delay_series": list(self._delay_hist),
        }
