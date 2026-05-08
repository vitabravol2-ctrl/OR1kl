from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    symbol: str = "btcusdt"
    ws_base_url: str = "wss://stream.binance.com:9443/stream"
    buffer_size: int = 5000
    simulation_threshold: float = 0.6
    reconnect_base_delay_sec: float = 1.0
    reconnect_max_delay_sec: float = 30.0
    ws_stale_timeout_sec: float = 4.0
    snapshot_every_n_ticks: int = 500
    micro_tick_size: float = 0.1
    micro_target_ticks_1: int = 1
    micro_target_ticks_2: int = 2
    micro_risk_ticks: int = 2
    micro_timeout_ms: int = 1200
    micro_min_confidence: float = 0.58
    micro_min_ev: float = 0.0
    micro_max_spread_ticks: float = 2.5
    micro_fee_ticks: float = 0.15
    micro_slippage_ticks: float = 0.10
    live_trading_enabled: bool = False
    order_execution_enabled: bool = False

    @property
    def streams_query(self) -> str:
        return f"{self.symbol}@bookTicker/{self.symbol}@aggTrade/{self.symbol}@depth10@100ms"


CONFIG = AppConfig()
