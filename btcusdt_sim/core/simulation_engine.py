from btcusdt_sim.data.entities import SimulationTrade


class SimulationEngine:
    def __init__(self, threshold: float = 0.6, tick_size: float = 0.1) -> None:
        self.threshold = threshold
        self.tick_size = tick_size

    def evaluate(self, price: float, p_up: float, p_down: float) -> tuple[str, SimulationTrade | None]:
        if p_up > self.threshold:
            trade = SimulationTrade(
                direction="LONG",
                entry_price=price,
                target_price=price + self.tick_size,
                stop_price=price - self.tick_size,
            )
            return "VIRTUAL LONG", trade

        if p_down > self.threshold:
            trade = SimulationTrade(
                direction="SHORT",
                entry_price=price,
                target_price=price - self.tick_size,
                stop_price=price + self.tick_size,
            )
            return "VIRTUAL SHORT", trade

        return "NO TRADE", None
