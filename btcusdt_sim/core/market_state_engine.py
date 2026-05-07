import numpy as np

from btcusdt_sim.data.entities import MarketState
from btcusdt_sim.data.market_buffer import MarketBuffer


class MarketStateEngine:
    def calculate(self, buffer: MarketBuffer) -> MarketState:
        latest = buffer.latest()
        if latest is None:
            return MarketState(0.0, 0.0, 0.0, 0.0, 0.0)

        prices = buffer.to_numpy_mid_prices(200)
        spreads = buffer.to_numpy_spreads(200)
        volumes = buffer.to_numpy_volumes(200)

        micro_trend = 0.0
        if prices.size >= 2:
            micro_trend = float(prices[-1] - prices[0])

        volatility = float(np.std(prices)) if prices.size > 1 else 0.0
        spread = float(np.mean(spreads)) if spreads.size > 0 else latest.spread

        imbalance = 0.0
        if latest.ask > 0:
            imbalance = (latest.bid - latest.ask) / (latest.bid + latest.ask)

        aggression = 0.0
        if volumes.size > 0:
            aggression = float(np.tanh(np.mean(volumes) / (np.std(volumes) + 1e-9)))

        tick_velocity = float(buffer.metrics().get("ticks_per_sec", 0.0))

        return MarketState(
            imbalance=imbalance,
            micro_trend=micro_trend,
            volatility=volatility,
            aggression=aggression,
            spread=spread,
            tick_velocity=tick_velocity,
        )
