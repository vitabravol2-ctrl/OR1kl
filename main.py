import asyncio
import logging
import os
import sys
import threading
import traceback
from dataclasses import asdict
from queue import Empty, Full, Queue
from time import perf_counter, process_time

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from btcusdt_sim.core.market_regime_engine import MarketRegimeEngine
from btcusdt_sim.core.market_memory_engine import MarketMemoryEngine
from btcusdt_sim.core.tactical_signal_engine import TacticalSignalEngine
from btcusdt_sim.core.liquidity_warfare_engine import LiquidityWarfareEngine
from btcusdt_sim.core.absorption_engine import AbsorptionEngine
from btcusdt_sim.core.reaction_engine import ReactionEngine
from btcusdt_sim.core.order_book_engine import OrderBookEngine
from btcusdt_sim.core.timeflow_engine import TimeflowEngine
from btcusdt_sim.core.market_state_engine import MarketStateEngine
from btcusdt_sim.core.micro_event_detector import MicroEventDetector
from btcusdt_sim.core.pattern_memory import PatternMemory
from btcusdt_sim.core.probability_engine import ProbabilityEngine
from btcusdt_sim.core.simulation_engine import SimulationEngine
from btcusdt_sim.core.game_theory_engine import GameTheoryCore
from btcusdt_sim.core.market_summary_engine import MarketSummaryEngine
from btcusdt_sim.core.micro_tick_setup_engine import MicroTickSetupEngine
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
        self.tactical_engine = TacticalSignalEngine()
        self.warfare_engine = LiquidityWarfareEngine()
        self.absorption_engine = AbsorptionEngine()
        self.reaction_engine = ReactionEngine()
        self.game_theory_core = GameTheoryCore()
        self.market_summary_engine = MarketSummaryEngine()
        self.micro_tick_setup_engine = MicroTickSetupEngine(
            confidence_threshold=CONFIG.micro_min_confidence,
            tick_size=CONFIG.micro_tick_size,
            target_ticks_1=CONFIG.micro_target_ticks_1,
            target_ticks_2=CONFIG.micro_target_ticks_2,
            risk_ticks=CONFIG.micro_risk_ticks,
            timeout_ms=CONFIG.micro_timeout_ms,
            min_ev=CONFIG.micro_min_ev,
            max_spread_ticks=CONFIG.micro_max_spread_ticks,
            fee_ticks=CONFIG.micro_fee_ticks,
            slippage_ticks=CONFIG.micro_slippage_ticks,
        )
        self.virtual_stats = {"wins": 0, "losses": 0, "timeouts": 0, "duration_total_ms": 0, "total": 0}
        self.virtual_position = "FLAT"
        self._last_log = ""
        self._last_game_scenario = ""
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
        memory = self.market_memory_engine.update(tick.mid_price, depth.get("liquidity_imbalance", 0.0), m["avg_spread"], m["short_volatility"], flow.get("momentum_pulse", 0.0))
        warfare = self.warfare_engine.update(depth, flow)
        absorption = self.absorption_engine.update(asdict(state), flow, depth)
        reaction = self.reaction_engine.update(flow, depth, absorption)
        events = self.event_detector.detect(state, tick.timestamp, flow, depth, warfare, absorption, reaction)
        tactical = self.tactical_engine.evaluate({"flow": flow, "depth": depth, "memory": memory, "market_state": asdict(state), "regime": regime.value, "events": [{"severity_level": e.severity_level} for e in events], "warfare": warfare, "absorption": absorption, "reaction": reaction})
        game = self.game_theory_core.evaluate(tick.mid_price, tactical, flow, depth, reaction)
        market_summary = self.market_summary_engine.summarize(tactical, game)
        ws_fresh = self.ws_diag.state.value not in {"STALE", "DISCONNECTED"}
        micro_setup = self.micro_tick_setup_engine.evaluate(tick.bid, tick.ask, tactical, game, ws_fresh=ws_fresh)
        sim_outcome = self._simulate_micro_tick_outcome(micro_setup.direction, reaction)

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
            "warfare": warfare,
            "absorption": absorption,
            "reaction": reaction,
            "tactical": tactical,
            "game": game,
            "market_summary": market_summary,
            "micro_tick_setup": asdict(micro_setup),
            "micro_tick_pipeline": ["DATA", "MICROSTRUCTURE", "GAME THEORY", "INTENT", "SETUP", "SIMULATION", "RESULT", "LEARNING"],
            "simulation_result": self._build_simulation_result(sim_outcome),
            "future_trading_gate": {"live_trading": "ENABLED" if CONFIG.live_trading_enabled else "DISABLED", "orders": "ENABLED" if CONFIG.order_execution_enabled else "DISABLED", "mode": "RESEARCH ONLY"},
            "cpu_usage": cpu_usage,
            "log": self._build_log(regime.value, events[-1].name if events else "none", sim_status, perf_counter()-started, game),
        }
        try:
            self.ui_queue.put_nowait(payload)
        except Full:
            self._dropped_ui += 1

    def _simulate_micro_tick_outcome(self, direction: str, reaction: dict) -> str:
        if direction == "WAIT":
            return "TIMEOUT"
        continuation = reaction.get("continuation_probability", 0.0)
        rejection = reaction.get("rejection_strength", 0.0)
        if continuation >= 0.58:
            return "WIN"
        if rejection >= 0.58:
            return "LOSS"
        return "TIMEOUT"

    def _build_simulation_result(self, outcome: str) -> dict:
        self.virtual_stats["total"] += 1
        self.virtual_stats["duration_total_ms"] += 1200
        if outcome == "WIN":
            self.virtual_stats["wins"] += 1
            self.virtual_position = "IN_VIRTUAL_LONG_SHORT"
        elif outcome == "LOSS":
            self.virtual_stats["losses"] += 1
            self.virtual_position = "STOPPED_VIRTUAL"
        else:
            self.virtual_stats["timeouts"] += 1
            self.virtual_position = "FLAT"
        total = max(self.virtual_stats["total"], 1)
        return {
            "virtual_wins": self.virtual_stats["wins"],
            "losses": self.virtual_stats["losses"],
            "timeouts": self.virtual_stats["timeouts"],
            "winrate": self.virtual_stats["wins"] / total,
            "avg_duration_ms": self.virtual_stats["duration_total_ms"] / total,
            "current_virtual_position": self.virtual_position,
            "last_outcome": outcome,
        }

    def _build_log(self, regime: str, event_name: str, sim_status: str, dt: float, game: dict) -> str:
        line = f"[TACTICAL] {regime} | event={event_name} | sim={sim_status} | dt={dt*1000:.2f}ms"
        decision = game.get("decision", {})
        conf = decision.get("confidence", 0.0)
        scenario = decision.get("best_scenario", "COMPRESSION_WAIT")
        game_line = ""
        if conf >= 0.55 and scenario != self._last_game_scenario:
            self._last_game_scenario = scenario
            game_line = (
                f"\n[GAME] scenario={scenario} payoff={decision.get('expected_payoff', 0.0):.2f} "
                f"confidence={conf:.2f} trapped={game.get('trapped_side', 'N/A')}"
            )
        full = line + game_line
        if full == self._last_log:
            return "[TACTICAL] grouped duplicate signal"
        self._last_log = full
        return full

    def shutdown(self) -> None:
        self.replay.stop()


def main() -> None:
    setup_logging()
    logger.info("[STARTUP] Python version: %s", sys.version.replace("\n", " "))
    logger.info("[STARTUP] Working directory: %s", os.getcwd())
    ui_queue: Queue = Queue(maxsize=256)

    try:
        app = QApplication([])
        window = MainWindow()
        window.show()
        logger.info("[STARTUP] GUI init OK")
    except Exception:
        logger.exception("[STARTUP] GUI initialization failed")
        raise

    orchestrator = AppOrchestrator(ui_queue)
    logger.info("[STARTUP] Requirements OK")

    def runner() -> None:
        try:
            logger.info("[STARTUP] WS thread starting")
            asyncio.run(orchestrator.run())
        except Exception:
            logger.error("[STARTUP] WS thread crashed:\n%s", traceback.format_exc())

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
    logger.info("[STARTUP] App ready")
    try:
        app.exec()
    finally:
        try:
            orchestrator.shutdown()
        except Exception:
            logger.error("Shutdown failed:\n%s", traceback.format_exc())


if __name__ == "__main__":
    main()
