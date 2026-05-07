from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QGroupBox, QLabel, QMainWindow, QProgressBar, QTextEdit, QVBoxLayout, QWidget


class SparklineWidget(QFrame):
    def __init__(self, color: str = "#29f1a4") -> None:
        super().__init__()
        self._values: list[float] = []
        self._color = QColor(color)
        self.setMinimumHeight(56)

    def set_values(self, values: list[float]) -> None:
        self._values = values[-140:]
        self.update()

    def paintEvent(self, _) -> None:
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0b141f"))
        if len(self._values) < 2:
            return
        lo, hi = min(self._values), max(self._values)
        span = max(hi - lo, 1e-9)
        w, h = self.width(), self.height()
        step = w / max(len(self._values) - 1, 1)
        p.setPen(QPen(self._color, 1.5))
        last_x, last_y = 0.0, h - ((self._values[0] - lo) / span) * (h - 8) - 4
        for i, v in enumerate(self._values[1:], start=1):
            x = i * step
            y = h - ((v - lo) / span) * (h - 8) - 4
            p.drawLine(int(last_x), int(last_y), int(x), int(y))
            last_x, last_y = x, y


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Tactical Radar Cockpit v0.1.6")
        self.setMinimumSize(1680, 980)
        self._log_lines: deque[str] = deque(maxlen=260)
        root = QWidget(); grid = QGridLayout(root)

        self.price = self._mk_label("0.00"); self.price.setObjectName("priceLabel")
        self.ws_status = self._mk_label("WS: DISCONNECTED")
        self.tactical_state = self._mk_label("TACTICAL STATE: NEUTRAL_FLOW")
        self.priority = self._mk_label("PRIORITY: LOW")
        self.dominant_side = self._mk_label("Dominant side: NEUTRAL")
        self.pressure_dir = self._mk_label("Pressure direction: FLAT")
        self.stress = self._mk_label("Liquidity stress: 0.00")
        self.momentum_state = self._mk_label("Momentum state: STABLE")
        self.fake_pressure = self._mk_label("Fake pressure: 0.00")
        self.reaction_state = self._mk_label("Reaction state: WEAK_RESPONSE")
        self.absorption_status = self._mk_label("Absorption: INACTIVE")
        self.cont_strength = self._mk_label("Continuation strength: 0.00")

        self.danger_bar = QProgressBar(); self.danger_bar.setRange(0, 100)
        self.opp_bar = QProgressBar(); self.opp_bar.setRange(0, 100)
        self.stress_bar = QProgressBar(); self.stress_bar.setRange(0, 100)

        self.depth_graph = SparklineWidget("#29f1a4")
        self.flow_graph = SparklineWidget("#ffd166")
        self.memory_graph = SparklineWidget("#8ecae6")
        self.danger_graph = SparklineWidget("#ef476f")
        self.reaction_graph = SparklineWidget("#90e0ef")
        self.absorption_graph = SparklineWidget("#f4a261")

        self.events = QTextEdit(); self.events.setReadOnly(True)
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)

        panels = [
            self._panel("TACTICAL STATE", [self.price, self.ws_status, self.tactical_state, self.priority, self.dominant_side]),
            self._panel("TACTICAL RADAR", [self.pressure_dir, self.stress, self.momentum_state, self.fake_pressure, self.reaction_state, self.absorption_status, self.cont_strength, self._mk_label("Danger"), self.danger_bar, self._mk_label("Opportunity"), self.opp_bar, self.danger_graph]),
            self._panel("MARKET STRESS", [self._mk_label("Stress severity"), self.stress_bar, self._mk_label("Depth / pressure"), self.depth_graph]),
            self._panel("FLOW RHYTHM", [self._mk_label("Flow acceleration"), self.flow_graph]),
            self._panel("MEMORY HEAT", [self._mk_label("Persistent tactical memory"), self.memory_graph]),
            self._panel("LIQUIDITY WARFARE", [self._mk_label("Sweep / Exhaustion"), self.reaction_graph]),
            self._panel("ABSORPTION", [self._mk_label("Absorption strength"), self.absorption_graph]),
            self._panel("SIGNAL PRIORITY", [self.events]),
            self._panel("LOG STREAM", [self.log_window]),
        ]
        grid.addWidget(panels[0], 0, 0); grid.addWidget(panels[1], 0, 1); grid.addWidget(panels[2], 0, 2)
        grid.addWidget(panels[3], 1, 0); grid.addWidget(panels[4], 1, 1); grid.addWidget(panels[5], 1, 2)
        grid.addWidget(panels[6], 2, 0); grid.addWidget(panels[7], 2, 1); grid.addWidget(panels[8], 2, 2)
        grid.addWidget(panels[8], 3, 0, 1, 3)

        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        tactical = data.get("tactical", {})
        depth = data.get("depth", {})
        flow = data.get("flow", {})
        memory = data.get("memory", {})
        warfare = data.get("warfare", {})
        absorption = data.get("absorption", {})
        reaction = data.get("reaction", {})

        self.price.setText(f"{data['price']:.2f}")
        self.ws_status.setText(f"WS: {data['ws_state']}")
        self.tactical_state.setText(f"TACTICAL STATE: {tactical.get('state', 'NEUTRAL_FLOW')}")
        self.priority.setText(f"PRIORITY: {tactical.get('priority', 'LOW')}")
        self._set_priority_style(tactical.get("priority", "LOW"))

        self.dominant_side.setText(f"Dominant side: {tactical.get('dominant_side', 'NEUTRAL')}")
        self.pressure_dir.setText(f"Pressure direction: {tactical.get('pressure_direction', 'FLAT')}")
        self.stress.setText(f"Liquidity stress: {tactical.get('liquidity_stress', 0.0):.2f}")
        self.momentum_state.setText(f"Momentum state: {tactical.get('momentum_state', 'STABLE')}")
        self.fake_pressure.setText(f"Fake pressure: {tactical.get('fake_pressure_warning', 0.0):.2f}")
        self.reaction_state.setText(f"Reaction state: {reaction.get('state', 'WEAK_RESPONSE')}")
        self.absorption_status.setText(f"Absorption: {tactical.get('absorption_status', 'INACTIVE')}")
        self.cont_strength.setText(f"Continuation strength: {tactical.get('continuation_strength', 0.0):.2f}")

        self.danger_bar.setValue(int(tactical.get("tactical_danger", 0.0) * 100))
        self.opp_bar.setValue(int(tactical.get("tactical_opportunity", 0.0) * 100))
        self.stress_bar.setValue(int(tactical.get("liquidity_stress", 0.0) * 100))

        self.depth_graph.set_values(depth.get("pressure_series", []))
        self.flow_graph.set_values(flow.get("accel_series", []))
        self.memory_graph.set_values(memory.get("pressure_history", []))
        self.danger_graph.set_values(tactical.get("danger_series", []))
        self.reaction_graph.set_values(warfare.get("consumption_series", []) + warfare.get("exhaustion_series", []))
        self.absorption_graph.set_values(absorption.get("strength_series", []) + reaction.get("reaction_series", []))

        self.events.setText("\n".join(self._fmt_event(e) for e in data.get("events", [])))
        self._append_log(data.get("log", ""))

    def _set_priority_style(self, priority: str) -> None:
        color = "#6ee7ff"
        if priority == "MID": color = "#ffd166"
        if priority == "HIGH": color = "#ff9f1c"
        if priority == "CRITICAL": color = "#ff4d4d"
        self.priority.setStyleSheet(f"font-weight: 700; color: {color};")

    def _fmt_event(self, ev: dict) -> str:
        return f"[{ev.get('severity_level', 'LOW')}] {ev.get('name')}"

    def _mk_label(self, text: str) -> QLabel:
        w = QLabel(text); w.setAlignment(Qt.AlignLeft); return w

    def _panel(self, title: str, widgets: list[QWidget]) -> QGroupBox:
        box = QGroupBox(title); layout = QVBoxLayout(box)
        for w in widgets: layout.addWidget(w)
        return box

    def _append_log(self, message: str) -> None:
        if not message:
            return
        if self._log_lines and self._log_lines[0] == message:
            return
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app: return
        app.setStyleSheet("""
            QWidget { background-color: #060d16; color: #c8f7da; font-size: 12px; }
            QGroupBox { border: 1px solid #1f6f57; margin-top: 8px; font-weight: bold; }
            QLabel#priceLabel { font-size: 34px; font-weight: 800; }
            QTextEdit { background-color: #0a1522; color: #ffe084; border: 1px solid #2b4561; }
            QProgressBar { border: 1px solid #1e5d4b; text-align: center; }
            QProgressBar::chunk { background-color: #2fd08d; }
        """)
