from btcusdt_sim.data.entities import MarketRegime, MarketState


class MarketRegimeEngine:
    def classify(self, state: MarketState) -> MarketRegime:
        abs_trend = abs(state.micro_trend)
        abs_imb = abs(state.imbalance)
        abs_agg = abs(state.aggression)

        if state.volatility > 35 and state.tick_velocity > 14:
            return MarketRegime.CHAOTIC
        if state.spread > 2.5 * max(state.volatility, 1e-6):
            return MarketRegime.LIQUIDITY_SWEEP
        if state.volatility > 20:
            return MarketRegime.HIGH_VOLATILITY
        if state.volatility < 2 and abs_trend < 4:
            return MarketRegime.CALM
        if state.volatility < 5 and abs_imb < 0.08:
            return MarketRegime.COMPRESSION
        if state.volatility > 10 and abs_agg > 0.4:
            return MarketRegime.EXPANSION
        if state.micro_trend > 0 and abs_trend > 8:
            return MarketRegime.TRENDING_UP
        if state.micro_trend < 0 and abs_trend > 8:
            return MarketRegime.TRENDING_DOWN
        return MarketRegime.CALM
