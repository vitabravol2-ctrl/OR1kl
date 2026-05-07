import asyncio
import logging
import threading
from queue import Empty, Queue

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from btcusdt_sim.core.market_state_engine import MarketStateEngine
from btcusdt_sim.core.pattern_memory import PatternMemory
from btcusdt_sim.core.probability_engine import ProbabilityEngine
from btcusdt_sim.core.simulation_engine import SimulationEngine
from btcusdt_sim.data.market_buffer import MarketBuffer
from btcusdt_sim.gui.main_window import MainWindow
from btcusdt_sim.infra.binance_ws_client import BinanceWsClient
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

    async def run(self) -> None:
        await self.ws_client.run(self.on_tick)

    async def on_tick(self, tick) -> None:
        self.buffer.append(tick)
        state = self.state_engine.calculate(self.buffer)
        p_up = self.prob_engine.calculate_up_probability(state)
        p_down = self.prob_engine.calculate_down_probability(state)
        sim_status, trade = self.sim_engine.evaluate(tick.mid_price, p_up, p_down)

        if trade is not None:
            self.pattern_memory.record(pattern_id="baseline_mock", result="TIMEOUT")

        self.ui_queue.put(
            {
                "price": tick.mid_price,
                "spread": state.spread,
                "imbalance": state.imbalance,
                "micro_trend": state.micro_trend,
                "volatility": state.volatility,
                "p_up": p_up,
                "p_down": p_down,
                "sim_status": sim_status,
                "log": f"t={tick.timestamp} {sim_status} p_up={p_up:.3f} p_down={p_down:.3f}",
            }
        )


def main() -> None:
    setup_logging()
    ui_queue: Queue = Queue(maxsize=1000)

    app = QApplication([])
    window = MainWindow()
    window.show()

    orchestrator = AppOrchestrator(ui_queue)

    def runner() -> None:
        asyncio.run(orchestrator.run())

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

    timer = QTimer()
    timer.setInterval(50)

    def pump_queue() -> None:
        while True:
            try:
                payload = ui_queue.get_nowait()
                window.update_dashboard(payload)
            except Empty:
                break
            except Exception as exc:
                logger.exception("UI update error: %s", exc)
                break

    timer.timeout.connect(pump_queue)
    timer.start()

    app.exec()


if __name__ == "__main__":
    main()
