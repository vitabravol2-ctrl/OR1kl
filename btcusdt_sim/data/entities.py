from dataclasses import dataclass
from enum import Enum


class WSHealthState(str, Enum):
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    RECONNECTING = "RECONNECTING"
    DISCONNECTED = "DISCONNECTED"


class MarketRegime(str, Enum):
    CALM = "CALM"
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    COMPRESSION = "COMPRESSION"
    EXPANSION = "EXPANSION"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    CHAOTIC = "CHAOTIC"


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
    tick_velocity: float = 0.0


@dataclass(slots=True)
class MicroEvent:
    name: str
    timestamp: int
    severity: float


@dataclass(slots=True)
class ReplayFrame:
    timestamp: int
    price: float
    market_state: dict
    probabilities: dict
    regime: str


@dataclass(slots=True)
class ProbabilitySnapshot:
    p_up: float
    p_down: float
    confidence: float
    directional_bias: str


@dataclass(slots=True)
class WsDiagnostics:
    state: WSHealthState = WSHealthState.DISCONNECTED
    latency_ms: float = 0.0
    tick_rate: float = 0.0
    reconnect_count: int = 0
    stale_count: int = 0
    last_message_ts: float = 0.0


@dataclass(slots=True)
class SimulationTrade:
    direction: str
    entry_price: float
    target_price: float
    stop_price: float
    result: str = "OPEN"
