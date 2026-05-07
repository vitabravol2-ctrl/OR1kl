from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QGroupBox, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Game Theory Simulation Engine v0.2.3")
        self.setMinimumSize(1540, 920)
        self._log_lines: deque[str] = deque(maxlen=260)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        from PySide6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs)

        self._build_command_center_tab()
        self._build_micro_tick_lab_tab()
        self._build_diagnostics_tab()
        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def _build_command_center_tab(self) -> None:
        tab = QWidget(); layout = QGridLayout(tab)
        self.price = self._mk_label("BTC: 0.00", "priceLabel")
        self.ws_status = self._mk_label("WS: DISCONNECTED", "bigLabel")
        self.tps = self._mk_label("ticks/sec: 0")
        self.latency = self._mk_label("latency: 0 ms")
        self.regime = self._mk_label("regime: n/a")
        self.tactical_state = self._mk_label("tactical state: n/a")
        self.priority_feed = QTextEdit(); self.priority_feed.setReadOnly(True)

        self.market_summary = self._mk_label("market summary: n/a")
        self.intent = self._mk_label("intent: n/a")
        self.best_scenario = self._mk_label("best scenario: n/a")
        self.trapped_side = self._mk_label("trapped side: n/a")
        self.pressure = self._mk_label("pressure direction: FLAT")
        self.conf = self._mk_label("confidence: 0%")
        self.danger = self._mk_label("danger: 0%")
        self.opp = self._mk_label("opportunity: 0%")
        self.payoff = self._mk_label("payoff score: 0.00")

        self.spread = self._mk_label("spread: 0.00")
        self.bid_ask = self._mk_label("bid/ask pressure: 0.00 / 0.00")
        self.liq_imb = self._mk_label("liquidity imbalance: 0.00")
        self.absorption = self._mk_label("absorption: 0.00")
        self.reaction_state = self._mk_label("reaction state: n/a")
        self.continuation = self._mk_label("continuation strength: 0.00")
        self.fake_warn = self._mk_label("fake pressure warning: 0.00")
        self.sweep_risk = self._mk_label("sweep risk: 0.00")

        layout.addWidget(self._panel("LEFT PANEL", [self.price, self.ws_status, self.tps, self.latency, self.regime, self.tactical_state, self._mk_label("priority feed:"), self.priority_feed]), 0, 0)
        layout.addWidget(self._panel("MARKET DECISION CARD", [self.market_summary, self.intent, self.best_scenario, self.trapped_side, self.pressure, self.conf, self.danger, self.opp, self.payoff]), 0, 1)
        layout.addWidget(self._panel("LIVE MICROSTRUCTURE", [self.spread, self.bid_ask, self.liq_imb, self.absorption, self.reaction_state, self.continuation, self.fake_warn, self.sweep_risk]), 0, 2)
        self.tabs.addTab(tab, "COMMAND CENTER")

    def _build_micro_tick_lab_tab(self) -> None:
        tab = QWidget(); layout = QGridLayout(tab)
        self.setup_direction = self._mk_label("virtual direction: WAIT")
        self.setup_entry = self._mk_label("entry candidate: 0.00")
        self.setup_target = self._mk_label("target +1 tick: 0.00")
        self.setup_invalidation = self._mk_label("invalidation: 0.00")
        self.setup_timeout = self._mk_label("timeout: 0 ms")

        self.signal_grade = self._mk_label("quality: WAIT")
        self.signal_reason = self._mk_label("reason: n/a")
        self.signal_conf = self._mk_label("confidence: 0%")
        self.signal_ev = self._mk_label("EV estimate: 0.00")
        self.chain = self._mk_label("DATA → MICROSTRUCTURE → GAME THEORY → INTENT → SETUP → SIMULATION → RESULT → LEARNING")

        self.sim_wins = self._mk_label("virtual wins: 0")
        self.sim_losses = self._mk_label("losses: 0")
        self.sim_timeouts = self._mk_label("timeouts: 0")
        self.sim_winrate = self._mk_label("winrate: 0%")
        self.sim_duration = self._mk_label("avg duration: 0 ms")
        self.sim_position = self._mk_label("current virtual position: FLAT")

        self.gate = self._mk_label("LIVE TRADING: DISABLED\nORDERS: DISABLED\nMODE: RESEARCH ONLY")

        layout.addWidget(self._panel("+1 TICK SETUP", [self.setup_direction, self.setup_entry, self.setup_target, self.setup_invalidation, self.setup_timeout]), 0, 0)
        layout.addWidget(self._panel("SIGNAL QUALITY", [self.signal_grade, self.signal_reason, self.signal_conf, self.signal_ev]), 0, 1)
        layout.addWidget(self._panel("MICRO-TICK CHAIN", [self.chain]), 1, 0, 1, 2)
        layout.addWidget(self._panel("SIMULATION RESULT", [self.sim_wins, self.sim_losses, self.sim_timeouts, self.sim_winrate, self.sim_duration, self.sim_position]), 2, 0)
        layout.addWidget(self._panel("FUTURE TRADING GATE", [self.gate]), 2, 1)
        self.tabs.addTab(tab, "MICRO-TICK LAB")

    def _build_diagnostics_tab(self) -> None:
        tab = QWidget(); layout = QGridLayout(tab)
        self.diag = self._mk_label("diag: n/a")
        self.health = self._mk_label("health: n/a")
        self.replay = self._mk_label("replay: n/a")
        self.cpu = self._mk_label("cpu: 0%")
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)
        layout.addWidget(self._panel("ENGINE DIAGNOSTICS", [self.diag, self.health, self.replay, self.cpu]), 0, 0)
        layout.addWidget(self._panel("LOG STREAM", [self.log_window]), 1, 0)
        self.tabs.addTab(tab, "DIAGNOSTICS")

    def update_dashboard(self, data: dict) -> None:
        tactical = data.get("tactical", {}); game = data.get("game", {}); decision = game.get("decision", {})
        depth = data.get("depth", {}); reaction = data.get("reaction", {}); absorption = data.get("absorption", {})
        setup = data.get("micro_tick_setup", {}); sim = data.get("simulation_result", {}); gate = data.get("future_trading_gate", {})

        self.price.setText(f"BTC: {data.get('price', 0.0):.2f}")
        self.ws_status.setText(f"WS: {data.get('ws_state', 'n/a')}")
        self.tps.setText(f"ticks/sec: {data.get('ticks_per_sec', 0)}")
        self.latency.setText(f"latency: {data.get('latency_ms', 0)} ms")
        self.regime.setText(f"regime: {data.get('regime', 'n/a')}")
        self.tactical_state.setText(f"tactical state: {tactical.get('state', 'n/a')}")
        self.market_summary.setText(f"market summary: {data.get('market_summary', 'n/a')}")
        self.intent.setText(f"intent: {game.get('intent', {}).get('intent', 'n/a')}")
        self.best_scenario.setText(f"best scenario: {decision.get('best_scenario', 'n/a')}")
        self.trapped_side.setText(f"trapped side: {game.get('trapped_side', 'n/a')}")
        self.pressure.setText(f"pressure direction: {tactical.get('pressure_direction', 'FLAT')}")
        self.conf.setText(f"confidence: {int(decision.get('confidence', 0.0)*100)}%")
        self.danger.setText(f"danger: {int(tactical.get('tactical_danger', 0.0)*100)}%")
        self.opp.setText(f"opportunity: {int(tactical.get('tactical_opportunity', 0.0)*100)}%")
        self.payoff.setText(f"payoff score: {decision.get('expected_payoff', 0.0):.2f}")

        self.spread.setText(f"spread: {data.get('spread', 0.0):.2f}")
        self.bid_ask.setText(f"bid/ask pressure: {depth.get('bid_pressure', 0.0):.2f} / {depth.get('ask_pressure', 0.0):.2f}")
        self.liq_imb.setText(f"liquidity imbalance: {depth.get('liquidity_imbalance', 0.0):.2f}")
        self.absorption.setText(f"absorption: {absorption.get('absorption_score', 0.0):.2f}")
        self.reaction_state.setText(f"reaction state: {reaction.get('state', 'n/a')}")
        self.continuation.setText(f"continuation strength: {tactical.get('continuation_strength', 0.0):.2f}")
        self.fake_warn.setText(f"fake pressure warning: {tactical.get('fake_pressure_warning', 0.0):.2f}")
        self.sweep_risk.setText(f"sweep risk: {game.get('trap', {}).get('trapped_crowd_severity', 0.0):.2f}")

        self.priority_feed.setText("\n".join([self._fmt_event(e) for e in data.get('events', []) if e.get('severity_level') in {'CRITICAL', 'HIGH'}]) or "No CRITICAL/HIGH events")

        self.setup_direction.setText(f"virtual direction: {setup.get('direction', 'WAIT')}")
        self.setup_entry.setText(f"entry candidate: {setup.get('entry_candidate', 0.0):.2f}")
        self.setup_target.setText(f"target +1 tick: {setup.get('target_price', 0.0):.2f}")
        self.setup_invalidation.setText(f"invalidation: {setup.get('invalidation_price', 0.0):.2f}")
        self.setup_timeout.setText(f"timeout: {setup.get('timeout_ms', 0)} ms")
        self.signal_grade.setText(f"quality: {setup.get('signal_quality', 'WAIT')}")
        self.signal_reason.setText(f"reason: {setup.get('reason', 'n/a')}")
        self.signal_conf.setText(f"confidence: {int(setup.get('confidence', 0.0)*100)}%")
        self.signal_ev.setText(f"EV estimate: {setup.get('ev_estimate', 0.0):.2f}")
        self.chain.setText(" → ".join(data.get("micro_tick_pipeline", [])))

        self.sim_wins.setText(f"virtual wins: {sim.get('virtual_wins', 0)}")
        self.sim_losses.setText(f"losses: {sim.get('losses', 0)}")
        self.sim_timeouts.setText(f"timeouts: {sim.get('timeouts', 0)}")
        self.sim_winrate.setText(f"winrate: {int(sim.get('winrate', 0.0)*100)}%")
        self.sim_duration.setText(f"avg duration: {sim.get('avg_duration_ms', 0.0):.0f} ms")
        self.sim_position.setText(f"current virtual position: {sim.get('current_virtual_position', 'FLAT')}")
        self.gate.setText(f"LIVE TRADING: {gate.get('live_trading', 'DISABLED')}\nORDERS: {gate.get('orders', 'DISABLED')}\nMODE: {gate.get('mode', 'RESEARCH ONLY')}")

        self.diag.setText(f"diag: {data.get('diag', 'n/a')}")
        self.health.setText(f"health: {data.get('health', 'n/a')}")
        self.replay.setText(f"replay: {data.get('replay_status', 'n/a')}")
        self.cpu.setText(f"cpu: {data.get('cpu_usage', 0.0):.1f}%")
        self._append_log(data.get("log", ""))

    def _fmt_event(self, ev: dict) -> str:
        return f"[{ev.get('severity_level', 'LOW')}] {ev.get('name')}"

    def _mk_label(self, text: str, object_name: str | None = None) -> QLabel:
        w = QLabel(text); w.setAlignment(Qt.AlignLeft)
        if object_name: w.setObjectName(object_name)
        return w

    def _panel(self, title: str, widgets: list[QWidget]) -> QGroupBox:
        box = QGroupBox(title); layout = QVBoxLayout(box)
        for w in widgets: layout.addWidget(w)
        return box

    def _append_log(self, message: str) -> None:
        if not message: return
        if self._log_lines and self._log_lines[0] == message: return
        self._log_lines.appendleft(message); self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app: return
        app.setStyleSheet("""
            QWidget { background-color: #060d16; color: #d5fbe6; font-size: 14px; }
            QGroupBox { border: 1px solid #1f6f57; margin-top: 10px; font-weight: bold; padding-top: 12px; }
            QLabel#priceLabel { font-size: 40px; font-weight: 900; }
            QLabel#bigLabel { font-size: 18px; font-weight: 700; }
            QTextEdit { background-color: #0a1522; color: #ffe084; border: 1px solid #2b4561; min-height: 130px; }
        """)
