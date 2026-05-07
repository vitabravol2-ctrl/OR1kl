import asyncio
import logging
import threading
from queue import Empty, Full, Queue

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from btcusdt_sim.core.market_state_engine import MarketStateEngine
from btcusdt_sim.core.pattern_memory import PatternMemory
from btcusdt_sim.core.probability_engine import ProbabilityEngine
from btcusdt_sim.core.simulation_engine import SimulationEngine
from btcusdt_sim.data.entities import WSHealthState, WsDiagnostics
from btcusdt_sim.data.market_buffer import MarketBuffer
from btcusdt_sim.gui.main_window import MainWindow
from btcusdt_sim.infra.binance_ws_client import BinanceWsClient
from btcusdt_sim.infra.tick_snapshot_writer import TickSnapshotWriter
from btcusdt_sim.utils.config import CONFIG
from btcusdt_sim.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


class AppOrchestrator:
    def __init__(self, ui_queue: Queue) -> None:
        self.ui_queue = ui_queue
        self.buffer = MarketBuffer(maxlen=CONFIG.buffer_size)
        self.state_engine = MarketStateEngine()
        self.prob_engine = ProbabilityEngine()
        self.sim_engine = SimulationEngine(threshold=CONFIG.simulation_threshold)
        self.pattern_memory = PatternMemory()
        self.ws_client = BinanceWsClient(CONFIG)
        self.ws_diag = WsDiagnostics(state=WSHealthState.CONNECTING)
        self.snapshot_writer = TickSnapshotWriter()
        self._save_counter = 0

    async def run(self) -> None:
        await self.ws_client.run(self.on_tick, self.on_diag)

    def on_diag(self, diag: WsDiagnostics) -> None:
        self.ws_diag = WsDiagnostics(**diag.__dict__)

    async def on_tick(self, tick) -> None:
        self.buffer.append(tick)
        state = self.state_engine.calculate(self.buffer)
        p_up = self.prob_engine.calculate_up_probability(state)
        p_down = self.prob_engine.calculate_down_probability(state)
        sim_status, _ = self.sim_engine.evaluate(tick.mid_price, p_up, p_down)
        m = self.buffer.metrics()

        self._save_counter += 1
        if self._save_counter >= CONFIG.snapshot_every_n_ticks:
            self._save_counter = 0
            self.snapshot_writer.submit(self.buffer.tail(200))

        payload = {
            "price": tick.mid_price,
            "spread": m["avg_spread"],
            "imbalance": state.imbalance,
            "micro_trend": state.micro_trend,
            "volatility": m["short_volatility"],
            "aggression": m["tick_pressure"],
            "p_up": p_up,
            "p_down": p_down,
            "sim_status": sim_status,
            "ws_state": self.ws_diag.state.value,
            "ticks_per_sec": m["ticks_per_sec"],
            "latency_ms": self.ws_diag.latency_ms,
            "buffer_fill": self.buffer.fill_ratio(),
            "mem_mb": 0.0,
            "cpu_pct": 0.0,
            "diag": f"reconnects={self.ws_diag.reconnect_count} stale={self.ws_diag.stale_count} dropped={self.buffer.dropped_ticks()}",
            "log": f"[WS:{self.ws_diag.state.value}] t={tick.timestamp} p_up={p_up:.3f} p_down={p_down:.3f}",
        }
        try:
            self.ui_queue.put_nowait(payload)
        except Full:
            pass


def main() -> None:
    setup_logging()
    ui_queue: Queue = Queue(maxsize=256)

    app = QApplication([])
    window = MainWindow()
    window.show()

    orchestrator = AppOrchestrator(ui_queue)

    def runner() -> None:
        asyncio.run(orchestrator.run())

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

    timer = QTimer()
    timer.setInterval(80)

    def pump_queue() -> None:
        latest = None
        while True:
            try:
                latest = ui_queue.get_nowait()
            except Empty:
                break
        if latest is not None:
            window.update_dashboard(latest)

    timer.timeout.connect(pump_queue)
    timer.start()
    app.exec()


if __name__ == "__main__":
    main()
