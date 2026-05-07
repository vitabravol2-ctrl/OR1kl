from btcusdt_sim.data.entities import MarketState, ProbabilitySnapshot


class ProbabilityEngine:
    def _normalize(self, up: float, down: float) -> tuple[float, float]:
        total = max(up + down, 1e-9)
        return up / total, down / total

    def calculate(self, market_state: MarketState) -> ProbabilitySnapshot:
        imbalance_score = market_state.imbalance
        aggression_score = market_state.aggression * 0.8
        trend_score = market_state.micro_trend / (abs(market_state.micro_trend) + 10)
        volatility_score = market_state.volatility / (market_state.volatility + 20)

        score_up = 1.0 + imbalance_score + aggression_score + trend_score + volatility_score * 0.2
        score_down = 1.0 - imbalance_score - aggression_score - trend_score + volatility_score * 0.2
        p_up, p_down = self._normalize(max(0.01, score_up), max(0.01, score_down))
        confidence = abs(p_up - p_down)
        directional_bias = "UP" if p_up > p_down else "DOWN" if p_down > p_up else "NEUTRAL"
        return ProbabilitySnapshot(
            p_up=max(0.0, min(1.0, p_up)),
            p_down=max(0.0, min(1.0, p_down)),
            confidence=confidence,
            directional_bias=directional_bias,
        )
