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
        self.setWindowTitle("BTCUSDT Realtime Intelligence Cockpit v0.1.4")
        self.setMinimumSize(1680, 980)
        self._log_lines: deque[str] = deque(maxlen=300)
        root = QWidget(); grid = QGridLayout(root)

        self.price = self._mk_label("0.00"); self.price.setObjectName("priceLabel")
        self.ws_status = self._mk_label("WS: DISCONNECTED")
        self.tps = self._mk_label("Ticks/s: 0.0")
        self.tick_accel = self._mk_label("Tick accel: 0.00")
        self.depth_bias = self._mk_label("Depth pressure: NEUTRAL")
        self.bid_liq = self._mk_label("Bid liquidity: 0")
        self.ask_liq = self._mk_label("Ask liquidity: 0")
        self.liq_imb = self._mk_label("Liquidity imbalance: 0.000")
        self.memory = self._mk_label("Memory zones: 0")

        self.buy_pressure = QProgressBar(); self.buy_pressure.setRange(0, 100)
        self.sell_pressure = QProgressBar(); self.sell_pressure.setRange(0, 100)
        self.pressure_graph = SparklineWidget("#8ecae6")
        self.pulse_graph = SparklineWidget("#ef476f")
        self.flow_graph = SparklineWidget("#ffd166")
        self.depth_graph = SparklineWidget("#29f1a4")

        self.events = QTextEdit(); self.events.setReadOnly(True)
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)

        panels = [
            self._panel("LIVE BTC PRICE", [self.price, self.ws_status, self.tps, self.tick_accel]),
            self._panel("DEPTH MAP", [self.depth_bias, self.bid_liq, self.ask_liq, self.liq_imb, self.depth_graph]),
            self._panel("LIQUIDITY PRESSURE", [self._mk_label("Bid pressure"), self.buy_pressure, self._mk_label("Ask pressure"), self.sell_pressure, self.pressure_graph]),
            self._panel("TIMEFLOW", [self._mk_label("Liquidity pulse"), self.pulse_graph, self._mk_label("Flow acceleration"), self.flow_graph]),
            self._panel("MARKET MEMORY", [self.memory]),
            self._panel("ACTIVE SIGNALS", [self.events]),
            self._panel("LOG STREAM", [self.log_window]),
        ]
        grid.addWidget(panels[0], 0, 0); grid.addWidget(panels[1], 0, 1); grid.addWidget(panels[2], 0, 2)
        grid.addWidget(panels[3], 1, 0); grid.addWidget(panels[4], 1, 1); grid.addWidget(panels[5], 1, 2)
        grid.addWidget(panels[6], 2, 0, 1, 3)

        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        flow = data.get("flow", {}); depth = data.get("depth", {}); memory = data.get("memory", {})
        self.price.setText(f"{data['price']:.2f}")
        self.ws_status.setText(f"WS: {data['ws_state']}")
        self.tps.setText(f"Ticks/s: {data['ticks_per_sec']:.1f}")
        self.tick_accel.setText(f"Tick accel: {flow.get('tick_acceleration', 0.0):.2f}")

        self.depth_bias.setText(f"Depth pressure: {depth.get('pressure_dominance', 'NEUTRAL')}")
        self.bid_liq.setText(f"Bid liquidity: {depth.get('bid_liquidity', 0.0):.2f}")
        self.ask_liq.setText(f"Ask liquidity: {depth.get('ask_liquidity', 0.0):.2f}")
        self.liq_imb.setText(f"Liquidity imbalance: {depth.get('liquidity_imbalance', 0.0):.3f}")

        buy = int((depth.get("liquidity_imbalance", 0.0) + 1) * 50); buy = max(0, min(100, buy))
        self.buy_pressure.setValue(buy); self.sell_pressure.setValue(100 - buy)

        self.depth_graph.set_values(depth.get("depth_heat_series", []))
        self.pressure_graph.set_values(depth.get("pressure_series", []))
        self.pulse_graph.set_values(flow.get("pulse_series", []))
        self.flow_graph.set_values(flow.get("accel_series", []))

        self.memory.setText(f"Memory zones: {len(memory.get('recent_liquidity_zones', []))} | sweeps: {len(memory.get('recent_sweeps', []))}")
        self.events.setText("\n".join(self._fmt_event(e) for e in data.get("events", [])))
        self._append_log(data["log"])

    def _fmt_event(self, ev: dict) -> str:
        return f"[{ev.get('severity_level', 'LOW')}/{ev.get('lifespan', 'active')}] {ev.get('timestamp')} | {ev.get('name')} | sev={ev.get('severity', 0.0):.2f}"

    def _mk_label(self, text: str) -> QLabel:
        w = QLabel(text); w.setAlignment(Qt.AlignLeft); return w

    def _panel(self, title: str, widgets: list[QWidget]) -> QGroupBox:
        box = QGroupBox(title); layout = QVBoxLayout(box)
        for w in widgets: layout.addWidget(w)
        return box

    def _append_log(self, message: str) -> None:
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app: return
        app.setStyleSheet("""
            QWidget { background-color: #060d16; color: #c8f7da; font-size: 12px; }
            QGroupBox { border: 1px solid #1f6f57; margin-top: 8px; font-weight: bold; }
            QLabel#priceLabel { font-size: 36px; font-weight: 800; }
            QTextEdit { background-color: #0a1522; color: #ffe084; border: 1px solid #2b4561; }
            QProgressBar { border: 1px solid #1e5d4b; text-align: center; }
            QProgressBar::chunk { background-color: #2fd08d; }
        """)
