import asyncio
import logging
import threading
from dataclasses import asdict
from queue import Empty, Full, Queue
from time import perf_counter, process_time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from btcusdt_sim.core.market_regime_engine import MarketRegimeEngine
from btcusdt_sim.core.market_memory_engine import MarketMemoryEngine
from btcusdt_sim.core.order_book_engine import OrderBookEngine
from btcusdt_sim.core.timeflow_engine import TimeflowEngine
from btcusdt_sim.core.market_state_engine import MarketStateEngine
from btcusdt_sim.core.micro_event_detector import MicroEventDetector
from btcusdt_sim.core.pattern_memory import PatternMemory
from btcusdt_sim.core.probability_engine import ProbabilityEngine
from btcusdt_sim.core.simulation_engine import SimulationEngine
from btcusdt_sim.core.tick_flow_engine import TickFlowEngine
from btcusdt_sim.data.entities import ReplayFrame, WSHealthState, WsDiagnostics
from btcusdt_sim.data.market_buffer import MarketBuffer
from btcusdt_sim.gui.main_window import MainWindow
from btcusdt_sim.infra.binance_ws_client import BinanceWsClient
from btcusdt_sim.infra.replay import ReplayStorage
from btcusdt_sim.utils.config import CONFIG
from btcusdt_sim.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


class AppOrchestrator:
    def __init__(self, ui_queue: Queue) -> None:
        self.ui_queue = ui_queue
        self.buffer = MarketBuffer(maxlen=CONFIG.buffer_size)
        self.state_engine = MarketStateEngine()
        self.regime_engine = MarketRegimeEngine()
        self.event_detector = MicroEventDetector()
        self.prob_engine = ProbabilityEngine()
        self.sim_engine = SimulationEngine(threshold=CONFIG.simulation_threshold)
        self.pattern_memory = PatternMemory()
        self.flow_engine = TickFlowEngine()
        self.order_book_engine = OrderBookEngine()
        self.timeflow_engine = TimeflowEngine()
        self.market_memory_engine = MarketMemoryEngine()
        self._cpu_time_last = process_time()
        self._wall_time_last = perf_counter()
        self.ws_client = BinanceWsClient(CONFIG)
        self.ws_diag = WsDiagnostics(state=WSHealthState.CONNECTING)
        self.replay = ReplayStorage()
        self._dropped_ui = 0

    async def run(self) -> None:
        await self.ws_client.run(self.on_tick, self.on_diag)

    def on_diag(self, diag: WsDiagnostics) -> None:
        self.ws_diag = WsDiagnostics(**asdict(diag))

    async def on_tick(self, tick) -> None:
        started = perf_counter()
        self.buffer.append(tick)
        state = self.state_engine.calculate(self.buffer)
        regime = self.regime_engine.classify(state)
        probs = self.prob_engine.calculate(state)
        sim_status, _ = self.sim_engine.evaluate(tick.mid_price, probs.p_up, probs.p_down)
        m = self.buffer.metrics()
        flow = self.flow_engine.update(tick, m["ticks_per_sec"], state.aggression)
        depth = self.order_book_engine.update(tick.bids or [], tick.asks or [])
        timeflow = self.timeflow_engine.update(tick.timestamp, flow.get("momentum_pulse", 0.0))
        flow.update(timeflow)
        memory = self.market_memory_engine.update(tick.mid_price, depth.get("liquidity_imbalance", 0.0), m["avg_spread"], m["short_volatility"])
        events = self.event_detector.detect(state, tick.timestamp, flow, depth)

        self.replay.submit(
            ReplayFrame(
                timestamp=tick.timestamp,
                price=tick.mid_price,
                market_state=asdict(state),
                probabilities={"p_up": probs.p_up, "p_down": probs.p_down, "confidence": probs.confidence},
                regime=regime.value,
            )
        )
        replay_status = self.replay.status()

        now_wall = perf_counter()
        now_cpu = process_time()
        wall_delta = max(now_wall - self._wall_time_last, 1e-6)
        cpu_delta = max(now_cpu - self._cpu_time_last, 0.0)
        cpu_usage = min(max((cpu_delta / wall_delta) * 100.0, 0.0), 100.0)
        self._wall_time_last = now_wall
        self._cpu_time_last = now_cpu

        payload = {
            "price": tick.mid_price,
            "spread": m["avg_spread"],
            "micro_trend": state.micro_trend,
            "volatility": m["short_volatility"],
            "aggression": state.aggression,
            "p_up": probs.p_up,
            "p_down": probs.p_down,
            "confidence": probs.confidence,
            "bias": probs.directional_bias,
            "regime": regime.value,
            "events": [{"timestamp": e.timestamp, "name": e.name, "severity": e.severity, "severity_level": e.severity_level, "lifespan": e.lifespan} for e in events][-18:],
            "sim_status": sim_status,
            "ws_state": self.ws_diag.state.value,
            "ticks_per_sec": m["ticks_per_sec"],
            "latency_ms": self.ws_diag.latency_ms,
            "buffer_fill": self.buffer.fill_ratio(),
            "health": f"queue={self.ui_queue.qsize()} dropped={self._dropped_ui} replay_q={replay_status['queued']} replay_w={replay_status['written']} mem_mb={self.buffer.fill_ratio()*CONFIG.buffer_size*0.00035:.1f}",
            "replay_status": f"queued={replay_status['queued']} written={replay_status['written']}",
            "diag": f"reconnects={self.ws_diag.reconnect_count} stale={self.ws_diag.stale_count} dropped_frames={self.buffer.dropped_ticks()}",
            "flow": flow,
            "depth": depth,
            "memory": memory,
            "cpu_usage": cpu_usage,
            "log": f"[STATE] regime={regime.value} [EVENT] {events[-1].name if events else 'none'} [SIM] {sim_status} dt={(perf_counter()-started)*1000:.2f}ms",
        }
        try:
            self.ui_queue.put_nowait(payload)
        except Full:
            self._dropped_ui += 1

    def shutdown(self) -> None:
        self.replay.stop()


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
    orchestrator.shutdown()


if __name__ == "__main__":
    main()
