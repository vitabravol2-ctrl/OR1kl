from dataclasses import dataclass, field


@dataclass(slots=True)
class MicroTickSetupResult:
    direction: str
    entry_candidate: float
    target_price: float
    target_price_2: float
    invalidation_price: float
    timeout_ms: int
    signal_quality: str
    confidence: float
    ev_estimate: float
    reason: str
    reason_list: list[str] = field(default_factory=list)


class MicroTickSetupEngine:
    LONG_SCENARIOS = {"SWEEP_LOW", "FAKE_DOWN_THEN_UP", "MOVE_UP", "ACCEPT_HIGHER"}
    SHORT_SCENARIOS = {"SWEEP_HIGH", "FAKE_UP_THEN_DOWN", "MOVE_DOWN", "ACCEPT_LOWER"}
    LONG_INTENTS = {"BAIT_SHORTS", "ACCEPT_HIGHER", "MOMENTUM_HUNT"}
    SHORT_INTENTS = {"BAIT_LONGS", "ACCEPT_LOWER", "MOMENTUM_HUNT"}

    def __init__(
        self,
        confidence_threshold: float = 0.58,
        tick_size: float = 0.1,
        target_ticks_1: int = 1,
        target_ticks_2: int = 2,
        risk_ticks: int = 2,
        timeout_ms: int = 1200,
        min_ev: float = 0.0,
        max_spread_ticks: float = 2.5,
        fee_ticks: float = 0.15,
        slippage_ticks: float = 0.10,
    ) -> None:
        self.confidence_threshold = confidence_threshold
        self.tick_size = tick_size
        self.target_ticks_1 = target_ticks_1
        self.target_ticks_2 = target_ticks_2
        self.risk_ticks = risk_ticks
        self.timeout_ms = timeout_ms
        self.min_ev = min_ev
        self.max_spread_ticks = max_spread_ticks
        self.fee_ticks = fee_ticks
        self.slippage_ticks = slippage_ticks

    def evaluate(self, bid: float, ask: float, tactical: dict, game: dict, ws_fresh: bool = True) -> MicroTickSetupResult:
        decision = game.get("decision", {})
        reaction = game.get("intent_reality", {})
        absorption = tactical.get("absorption_status", "INACTIVE")
        pressure = tactical.get("pressure_direction", "FLAT")
        opportunity = float(tactical.get("tactical_opportunity", 0.0))
        danger = float(tactical.get("tactical_danger", 0.0))
        confidence = float(decision.get("confidence", 0.0))
        trapped = game.get("trapped_side", "NONE")
        scenario = decision.get("best_scenario", "COMPRESSION_WAIT")
        intent = game.get("intent", {}).get("intent", "RANGE_MANIPULATION")
        volatility = float(tactical.get("liquidity_stress", 0.0))
        spread_ticks = max((ask - bid) / max(self.tick_size, 1e-9), 0.0)

        mid = (bid + ask) / 2.0
        long_entry = ask
        short_entry = bid

        timeout_penalty = 0.05 if tactical.get("state") == "DEAD_FLOW" else 0.0
        target_ticks = self.target_ticks_2 if confidence >= 0.70 else self.target_ticks_1
        p_win = max(min(opportunity * 0.65 + confidence * 0.35, 1.0), 0.0)
        p_loss = max(min(danger * 0.7 + (1.0 - confidence) * 0.3, 1.0), 0.0)
        ev = p_win * target_ticks - p_loss * self.risk_ticks - self.fee_ticks - self.slippage_ticks - timeout_penalty

        reasons: list[str] = []
        if spread_ticks > self.max_spread_ticks:
            reasons.append("spread too wide")
        if not ws_fresh:
            reasons.append("stale ws data")
        if volatility >= 0.95:
            reasons.append("extreme volatility")
        if opportunity <= danger:
            reasons.append("opportunity <= danger")
        if ev <= self.min_ev:
            reasons.append("ev below threshold")
        if confidence < self.confidence_threshold:
            reasons.append("confidence below threshold")

        long_ok = (
            pressure == "UP"
            and trapped == "SHORTS"
            and scenario in self.LONG_SCENARIOS
            and intent in self.LONG_INTENTS
            and reaction.get("reality", "WEAK_RESPONSE") != "FAST_REJECTION"
            and absorption != "SELL_ABSORPTION"
        )
        short_ok = (
            pressure == "DOWN"
            and trapped == "LONGS"
            and scenario in self.SHORT_SCENARIOS
            and intent in self.SHORT_INTENTS
            and reaction.get("reality", "WEAK_RESPONSE") != "FAST_REJECTION"
            and absorption != "BUY_ABSORPTION"
        )

        direction = "WAIT"
        if not reasons and long_ok:
            direction = "LONG"
            reasons = [
                "pressure UP",
                "shorts trapped",
                f"best scenario {scenario}",
                f"intent {intent}",
                f"opportunity {opportunity:.2f} > danger {danger:.2f}",
                f"EV {ev:+.2f} ticks",
            ]
        elif not reasons and short_ok:
            direction = "SHORT"
            reasons = [
                "pressure DOWN",
                "longs trapped",
                f"best scenario {scenario}",
                f"intent {intent}",
                f"opportunity {opportunity:.2f} > danger {danger:.2f}",
                f"EV {ev:+.2f} ticks",
            ]
        elif long_ok and short_ok:
            reasons.append("signal conflict")

        if direction == "LONG":
            entry = long_entry
            target = entry + self.tick_size * self.target_ticks_1
            target_2 = entry + self.tick_size * self.target_ticks_2
            invalidation = entry - self.tick_size * self.risk_ticks
        elif direction == "SHORT":
            entry = short_entry
            target = entry - self.tick_size * self.target_ticks_1
            target_2 = entry - self.tick_size * self.target_ticks_2
            invalidation = entry + self.tick_size * self.risk_ticks
        else:
            entry = mid
            target = mid
            target_2 = mid
            invalidation = mid

        if direction == "WAIT":
            quality = "WAIT"
        elif confidence >= 0.70 and ev > 0.20 and scenario in self.LONG_SCENARIOS.union(self.SHORT_SCENARIOS):
            quality = "A"
        elif confidence >= 0.58 and ev > 0:
            quality = "B"
        else:
            quality = "C"

        return MicroTickSetupResult(
            direction=direction,
            entry_candidate=entry,
            target_price=target,
            target_price_2=target_2,
            invalidation_price=invalidation,
            timeout_ms=self.timeout_ms,
            signal_quality=quality,
            confidence=confidence,
            ev_estimate=ev,
            reason="; ".join(reasons) if reasons else "conditions aligned",
            reason_list=reasons,
        )
