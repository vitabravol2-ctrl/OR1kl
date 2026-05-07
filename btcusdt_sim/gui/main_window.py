from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGridLayout, QGroupBox, QLabel, QMainWindow, QProgressBar, QTextEdit, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Research Cockpit v0.1.2")
        self.setMinimumSize(1320, 820)
        self._log_lines: deque[str] = deque(maxlen=300)

        root = QWidget()
        grid = QGridLayout(root)

        self.price = self._mk_label("BTC PRICE: -")
        self.ws_status = self._mk_label("WS STATUS: DISCONNECTED")
        self.tps = self._mk_label("TICKS/s: 0")
        self.latency = self._mk_label("LATENCY: 0 ms")
        self.regime = self._mk_label("CURRENT MARKET REGIME: -")

        self.spread = self._mk_label("SPREAD: -")
        self.micro = self._mk_label("MICRO TREND: -")
        self.vol = self._mk_label("VOLATILITY: -")
        self.aggro = self._mk_label("AGGRESSION: -")

        self.p_up = self._mk_label("P(up): -")
        self.p_down = self._mk_label("P(down): -")
        self.bias = self._mk_label("DIRECTIONAL BIAS: -")
        self.conf = self._mk_label("CONFIDENCE: -")

        self.health = self._mk_label("SYSTEM HEALTH: -")
        self.replay = self._mk_label("REPLAY STATUS: -")
        self.diag = self._mk_label("DIAG: -")
        self.events = QTextEdit(); self.events.setReadOnly(True)
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)

        self.buffer_bar = QProgressBar(); self.buffer_bar.setRange(0, 100); self.buffer_bar.setFormat("BUFFER FILL: %p%")
        self.conf_bar = QProgressBar(); self.conf_bar.setRange(0, 100); self.conf_bar.setFormat("CONFIDENCE SCALE: %p%")

        core = self._mk_panel("COCKPIT CORE", [self.price, self.ws_status, self.tps, self.latency, self.regime])
        market = self._mk_panel("MARKET REGIME PANEL", [self.spread, self.micro, self.vol, self.aggro])
        prob = self._mk_panel("DIRECTIONAL BIAS PANEL", [self.p_up, self.p_down, self.bias, self.conf])
        prob.layout().addWidget(self.conf_bar)
        health = self._mk_panel("SYSTEM HEALTH PANEL", [self.health, self.replay, self.diag])
        health.layout().addWidget(self.buffer_bar)
        evpanel = QGroupBox("EVENT ALERT PANEL"); evlayout = QVBoxLayout(evpanel); evlayout.addWidget(self.events)

        grid.addWidget(core, 0, 0)
        grid.addWidget(market, 0, 1)
        grid.addWidget(prob, 0, 2)
        grid.addWidget(health, 1, 0)
        grid.addWidget(evpanel, 1, 1)
        grid.addWidget(self.log_window, 1, 2)
        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        self.price.setText(f"BTC PRICE: {data['price']:.2f}")
        self.ws_status.setText(f"WS STATUS: {data['ws_state']}")
        self.tps.setText(f"TICKS/s: {data['ticks_per_sec']:.1f}")
        self.latency.setText(f"LATENCY: {data['latency_ms']:.1f} ms")
        self.regime.setText(f"CURRENT MARKET REGIME: {data['regime']}")
        self.spread.setText(f"AVG SPREAD: {data['spread']:.2f}")
        self.micro.setText(f"MICRO TREND: {data['micro_trend']:.5f}")
        self.vol.setText(f"VOL SCALE: {data['volatility']:.5f}")
        self.aggro.setText(f"AGGRESSION: {data['aggression']:.5f}")
        self.p_up.setText(f"P(up): {data['p_up']:.3f}")
        self.p_down.setText(f"P(down): {data['p_down']:.3f}")
        self.bias.setText(f"DIRECTIONAL BIAS: {data['bias']}")
        self.conf.setText(f"CONFIDENCE: {data['confidence']:.3f}")
        self.health.setText(f"SYSTEM HEALTH: {data['health']}")
        self.replay.setText(f"REPLAY STATUS: {data['replay_status']}")
        self.diag.setText(data['diag'])
        self.buffer_bar.setValue(int(data['buffer_fill'] * 100))
        self.conf_bar.setValue(int(data['confidence'] * 100))
        self.events.setText("\n".join(data.get('events', [])))
        self._append_log(data['log'])

    def _mk_label(self, text: str) -> QLabel:
        w = QLabel(text)
        w.setAlignment(Qt.AlignLeft)
        return w

    def _mk_panel(self, title: str, labels: list[QLabel]) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        for l in labels:
            layout.addWidget(l)
        return box

    def _append_log(self, message: str) -> None:
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app:
            return
        app.setStyleSheet("""
            QWidget { background-color: #090f17; color: #9fffb7; font-size: 12px; }
            QGroupBox { border: 1px solid #1c6b4f; margin-top: 8px; font-weight: bold; }
            QTextEdit { background-color: #0f1a25; color: #f1f191; border: 1px solid #2a4257; }
            QProgressBar { border: 1px solid #1c6b4f; text-align: center; }
            QProgressBar::chunk { background-color: #22d18f; }
        """)
