from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QProgressBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Game Theory Simulation Engine v0.2.2")
        self.setMinimumSize(1540, 920)
        self._log_lines: deque[str] = deque(maxlen=260)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        self.tabs = QTabWidget()
        root_layout.addWidget(self.tabs)

        self._build_command_center_tab()
        self._build_game_theory_tab()
        self._build_diagnostics_tab()

        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def _build_command_center_tab(self) -> None:
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setHorizontalSpacing(20)
        layout.setVerticalSpacing(16)

        self.price = self._mk_label("0.00", "priceLabel")
        self.ws_status = self._mk_label("WS: DISCONNECTED", "bigLabel")
        self.tactical_state = self._mk_label("STATE: NEUTRAL_FLOW", "bigLabel")
        self.intent_state = self._mk_label("INTENT: RANGE_MANIPULATION", "bigLabel")
        self.game_state = self._mk_label("BEST SCENARIO: COMPRESSION_WAIT", "bigLabel")
        self.pressure_dir = self._mk_label("PRESSURE: FLAT", "bigLabel")
        self.trapped_side = self._mk_label("TRAPPED: NONE", "bigLabel")
        self.game_conf = self._mk_label("CONFIDENCE: 0%", "bigLabel")
        self.market_summary = self._mk_label("MARKET SUMMARY: n/a", "summaryLabel")

        self.danger_bar = QProgressBar(); self.danger_bar.setRange(0, 100)
        self.opp_bar = QProgressBar(); self.opp_bar.setRange(0, 100)
        self.danger_value = self._mk_label("DANGER: 0%")
        self.opp_value = self._mk_label("OPPORTUNITY: 0%")

        decision_card = self._panel(
            "MARKET DECISION CARD",
            [
                self.tactical_state,
                self.intent_state,
                self.game_state,
                self.pressure_dir,
                self.trapped_side,
                self.game_conf,
                self.danger_value,
                self.danger_bar,
                self.opp_value,
                self.opp_bar,
                self.market_summary,
            ],
        )

        top = self._panel("COMMAND CENTER", [self.price, self.ws_status])
        layout.addWidget(top, 0, 0)
        layout.addWidget(decision_card, 0, 1, 2, 2)
        self.events = QTextEdit(); self.events.setReadOnly(True)
        layout.addWidget(self._panel("PRIORITY FEED (CRITICAL/HIGH)", [self.events]), 1, 0)
        self.tabs.addTab(tab, "COMMAND CENTER")

    def _build_game_theory_tab(self) -> None:
        tab = QWidget(); layout = QGridLayout(tab)
        self.pain_map = self._mk_label("Pain above/below: 0.00 / 0.00")
        self.player_advantage = self._mk_label("Player advantage: NEUTRAL")
        self.mm_incentive = self._mk_label("Market maker incentive: 0.00")
        self.payoff_summary = self._mk_label("Payoff score: 0.00")
        self.game_reason = self._mk_label("Reason: n/a")
        self.trap_prob = self._mk_label("Trap probability L/S: 0.00 / 0.00")
        self.pain_side = self._mk_label("Likely pain side: NONE")
        self.scenario_flow_label = self._mk_label("Scenario flow: COMPRESSION_WAIT -> COMPRESSION_WAIT")
        self.intent_reality = self._mk_label("Intent vs reality: n/a")
        self.payoff_momentum = self._mk_label("Payoff momentum: 0.00")

        layout.addWidget(self._panel("CROWD PAIN MAP", [self.pain_map]), 0, 0)
        layout.addWidget(self._panel("PAYOFF MATRIX", [self.payoff_summary, self.game_reason]), 0, 1)
        layout.addWidget(self._panel("PLAYER ADVANTAGE", [self.player_advantage, self.mm_incentive]), 1, 0)
        layout.addWidget(self._panel("TRAP ANALYZER", [self.trap_prob, self.pain_side]), 1, 1)
        layout.addWidget(self._panel("SCENARIO FLOW", [self.scenario_flow_label]), 2, 0)
        layout.addWidget(self._panel("INTENT vs REALITY", [self.intent_reality]), 2, 1)
        layout.addWidget(self._panel("PAYOFF FLOW", [self.payoff_momentum]), 3, 0, 1, 2)
        self.tabs.addTab(tab, "GAME THEORY")

    def _build_diagnostics_tab(self) -> None:
        tab = QWidget(); layout = QGridLayout(tab)
        self.diag_ws = self._mk_label("WS diagnostics: n/a")
        self.diag_latency = self._mk_label("latency: 0 ms")
        self.diag_queue = self._mk_label("queue pressure: n/a")
        self.diag_replay = self._mk_label("replay queue: n/a")
        self.diag_perf = self._mk_label("CPU/memory: n/a")
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)

        layout.addWidget(self._panel("WS DIAGNOSTICS", [self.diag_ws, self.diag_latency, self.diag_queue, self.diag_replay, self.diag_perf]), 0, 0)
        layout.addWidget(self._panel("LOGS / RAW EVENT STREAM", [self.log_window]), 1, 0)
        self.tabs.addTab(tab, "DIAGNOSTICS")

    def update_dashboard(self, data: dict) -> None:
        tactical = data.get("tactical", {})
        reaction = data.get("reaction", {})
        game = data.get("game", {})
        decision = game.get("decision", {})
        pain = game.get("pain", {})
        players = game.get("players", {})
        trap = game.get("trap", {})
        scenario_flow = game.get("scenario_flow", {})
        payoff_flow = game.get("payoff_flow", {})
        intent_reality = game.get("intent_vs_reality", {})
        intent = game.get("intent", {})

        self.price.setText(f"{data['price']:.2f}")
        self.ws_status.setText(f"WS: {data['ws_state']}")
        self.tactical_state.setText(f"STATE: {tactical.get('state', 'NEUTRAL_FLOW')}")
        self.intent_state.setText(f"INTENT: {intent.get('intent', 'RANGE_MANIPULATION')}")
        self.game_state.setText(f"BEST SCENARIO: {decision.get('best_scenario', 'COMPRESSION_WAIT')}")
        self.pressure_dir.setText(f"PRESSURE: {tactical.get('pressure_direction', 'FLAT')}")
        self.trapped_side.setText(f"TRAPPED: {game.get('trapped_side', 'NONE')}")
        self.game_conf.setText(f"CONFIDENCE: {int(decision.get('confidence', 0.0) * 100)}%")
        self.market_summary.setText(f"MARKET SUMMARY: {data.get('market_summary', 'n/a')}")

        danger = int(tactical.get("tactical_danger", 0.0) * 100)
        opp = int(tactical.get("tactical_opportunity", 0.0) * 100)
        self.danger_value.setText(f"DANGER: {danger}%")
        self.opp_value.setText(f"OPPORTUNITY: {opp}%")
        self.danger_bar.setValue(danger)
        self.opp_bar.setValue(opp)

        self.pain_map.setText(f"Pain above/below: {pain.get('pain_above', 0.0):.2f} / {pain.get('pain_below', 0.0):.2f}")
        long_v = players.get("LONG_CROWD", {}).get("vulnerability", 0.0)
        short_v = players.get("SHORT_CROWD", {}).get("vulnerability", 0.0)
        self.player_advantage.setText(f"Player advantage: {'SHORT_SIDE' if long_v > short_v else 'LONG_SIDE'}")
        self.mm_incentive.setText(f"Market maker incentive: {game.get('market_maker_incentive', 0.0):.2f}")
        self.payoff_summary.setText(f"Payoff score: {decision.get('expected_payoff', 0.0):.2f}")
        self.game_reason.setText(f"Reason: {decision.get('reason', 'n/a')}")
        self.trap_prob.setText(f"Trap probability L/S: {trap.get('long_trap_probability', 0.0):.2f} / {trap.get('short_trap_probability', 0.0):.2f}")
        self.pain_side.setText(f"Likely pain side: {trap.get('likely_pain_direction', 'NONE')}")
        self.scenario_flow_label.setText(f"Scenario flow: {scenario_flow.get('transition', 'COMPRESSION_WAIT -> COMPRESSION_WAIT')}")
        self.intent_reality.setText(f"Intent vs reality: {intent_reality.get('intent', 'N/A')} -> {intent_reality.get('reality', 'N/A')} ({intent_reality.get('verdict', 'n/a')})")
        self.payoff_momentum.setText(f"Payoff momentum: {payoff_flow.get('payoff_momentum', 0.0):.2f}")

        filtered_events = [self._fmt_event(e) for e in data.get("events", []) if e.get("severity_level") in {"CRITICAL", "HIGH"}]
        self.events.setText("\n".join(filtered_events) if filtered_events else "No CRITICAL/HIGH events")

        self.diag_ws.setText(f"WS diagnostics: {data.get('diag', 'n/a')}")
        self.diag_latency.setText(f"latency: {data.get('latency_ms', 0)} ms")
        self.diag_queue.setText(f"queue pressure: {data.get('health', 'n/a')}")
        self.diag_replay.setText(f"replay queue: {data.get('replay_status', 'n/a')}")
        self.diag_perf.setText(f"CPU/memory: cpu={data.get('cpu_usage', 0.0):.1f}%")
        self._append_log(data.get("log", ""))

    def _fmt_event(self, ev: dict) -> str:
        return f"[{ev.get('severity_level', 'LOW')}] {ev.get('name')}"

    def _mk_label(self, text: str, object_name: str | None = None) -> QLabel:
        w = QLabel(text)
        w.setAlignment(Qt.AlignLeft)
        if object_name:
            w.setObjectName(object_name)
        return w

    def _panel(self, title: str, widgets: list[QWidget]) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        for w in widgets:
            layout.addWidget(w)
        return box

    def _append_log(self, message: str) -> None:
        if not message:
            return
        if self._log_lines and self._log_lines[0] == message:
            return
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app:
            return
        app.setStyleSheet("""
            QWidget { background-color: #060d16; color: #d5fbe6; font-size: 14px; }
            QGroupBox { border: 1px solid #1f6f57; margin-top: 10px; font-weight: bold; padding-top: 12px; }
            QLabel#priceLabel { font-size: 52px; font-weight: 900; }
            QLabel#bigLabel { font-size: 20px; font-weight: 700; }
            QLabel#summaryLabel { font-size: 17px; color: #9cefc8; padding-top: 8px; }
            QTextEdit { background-color: #0a1522; color: #ffe084; border: 1px solid #2b4561; }
            QProgressBar { border: 1px solid #1e5d4b; text-align: center; min-height: 20px; }
            QProgressBar::chunk { background-color: #2fd08d; }
            QTabWidget::pane { border: 1px solid #1f6f57; }
        """)
