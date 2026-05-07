from dataclasses import dataclass


@dataclass(slots=True)
class Tick:
    timestamp: int
    bid: float
    ask: float
    spread: float
    mid_price: float
    volume: float


@dataclass(slots=True)
class MarketState:
    imbalance: float
    micro_trend: float
    volatility: float
    aggression: float
    spread: float


@dataclass(slots=True)
class SimulationTrade:
    direction: str
    entry_price: float
    target_price: float
    stop_price: float
    result: str = "OPEN"
