from dataclasses import dataclass


@dataclass(slots=True)
class MicroTickSetupResult:
    direction: str
    entry_candidate: float
    target_price: float
    invalidation_price: float
    timeout_ms: int
    signal_quality: str
    confidence: float
    ev_estimate: float
    reason: str


class MicroTickSetupEngine:
    def __init__(self, confidence_threshold: float = 0.55, tick_size: float = 0.1) -> None:
        self.confidence_threshold = confidence_threshold
        self.tick_size = tick_size

    def evaluate(self, price: float, tactical: dict, game: dict) -> MicroTickSetupResult:
        decision = game.get("decision", {})
        pressure = tactical.get("pressure_direction", "FLAT")
        opportunity = tactical.get("tactical_opportunity", 0.0)
        danger = tactical.get("tactical_danger", 0.0)
        confidence = float(decision.get("confidence", 0.0))
        trapped = game.get("trapped_side", "NONE")

        direction = "WAIT"
        reason = "conditions not aligned"
        if pressure == "UP" and opportunity > danger and confidence > self.confidence_threshold and trapped == "SHORTS":
            direction = "LONG"
            reason = "up pressure + shorts trapped + confidence gate"
        elif pressure == "DOWN" and opportunity > danger and confidence > self.confidence_threshold and trapped == "LONGS":
            direction = "SHORT"
            reason = "down pressure + longs trapped + confidence gate"

        if direction == "LONG":
            entry = price
            target = price + self.tick_size
            invalidation = price - self.tick_size
        elif direction == "SHORT":
            entry = price
            target = price - self.tick_size
            invalidation = price + self.tick_size
        else:
            entry = price
            target = price
            invalidation = price

        ev = max(min(opportunity - danger + (confidence - 0.5), 1.0), -1.0)
        if direction == "WAIT":
            quality = "WAIT"
        elif confidence >= 0.8 and ev > 0.35:
            quality = "A"
        elif confidence >= 0.68 and ev > 0.18:
            quality = "B"
        else:
            quality = "C"

        return MicroTickSetupResult(
            direction=direction,
            entry_candidate=entry,
            target_price=target,
            invalidation_price=invalidation,
            timeout_ms=1200,
            signal_quality=quality,
            confidence=confidence,
            ev_estimate=ev,
            reason=reason,
        )
