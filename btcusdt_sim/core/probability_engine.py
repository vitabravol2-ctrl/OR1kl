from btcusdt_sim.data.entities import MarketState


class ProbabilityEngine:
    def calculate_up_probability(self, market_state: MarketState) -> float:
        bias = 0.5 + 0.1 * market_state.micro_trend / (abs(market_state.micro_trend) + 1.0)
        return max(0.0, min(1.0, bias))

    def calculate_down_probability(self, market_state: MarketState) -> float:
        return 1.0 - self.calculate_up_probability(market_state)
