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

    @property
    def streams_query(self) -> str:
        return f"{self.symbol}@bookTicker/{self.symbol}@aggTrade"


CONFIG = AppConfig()
