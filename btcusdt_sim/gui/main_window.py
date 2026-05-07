from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMainWindow,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Cockpit v0.1.1")
        self.setMinimumSize(1200, 760)
        self._log_lines: deque[str] = deque(maxlen=250)

        root = QWidget()
        grid = QGridLayout(root)

        self.price = self._mk_label("BTC PRICE: -")
        self.ws_status = self._mk_label("WS STATUS: DISCONNECTED")
        self.tps = self._mk_label("TICKS/s: 0")
        self.latency = self._mk_label("LATENCY: 0 ms")
        self.spread = self._mk_label("SPREAD: -")
        self.micro = self._mk_label("MICRO TREND: -")
        self.vol = self._mk_label("VOLATILITY: -")
        self.aggro = self._mk_label("BUY/SELL AGGRESSION: -")
        self.p_up = self._mk_label("P(up): -")
        self.p_down = self._mk_label("P(down): -")
        self.sim = self._mk_label("SIM ENGINE: -")
        self.mem = self._mk_label("MEMORY: -")
        self.cpu = self._mk_label("CPU: -")
        self.diag = self._mk_label("DIAG: -")

        self.buffer_bar = QProgressBar()
        self.buffer_bar.setRange(0, 100)
        self.buffer_bar.setFormat("BUFFER FILL: %p%")

        left = self._mk_panel("COCKPIT CORE", [self.price, self.ws_status, self.tps, self.latency, self.sim])
        center = self._mk_panel("MARKET", [self.spread, self.micro, self.vol, self.aggro, self.p_up, self.p_down])
        right = self._mk_panel("DIAGNOSTICS", [self.mem, self.cpu, self.diag])
        right.layout().addWidget(self.buffer_bar)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)

        grid.addWidget(left, 0, 0)
        grid.addWidget(center, 0, 1)
        grid.addWidget(right, 0, 2)
        grid.addWidget(self.log_window, 1, 0, 1, 3)
        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        self.price.setText(f"BTC PRICE: {data['price']:.2f}")
        self.ws_status.setText(f"WS STATUS: {data['ws_state']}")
        self.tps.setText(f"TICKS/s: {data['ticks_per_sec']:.1f}")
        self.latency.setText(f"LATENCY: {data['latency_ms']:.1f} ms")
        self.spread.setText(f"AVG SPREAD: {data['spread']:.2f}")
        self.micro.setText(f"MICRO TREND: {data['micro_trend']:.5f}")
        self.vol.setText(f"VOL SCALE: {data['volatility']:.5f}")
        self.aggro.setText(f"BUY/SELL AGGRESSION: {data['aggression']:.5f}")
        self.p_up.setText(f"P(up): {data['p_up']:.3f}")
        self.p_down.setText(f"P(down): {data['p_down']:.3f}")
        self.sim.setText(f"SIM ENGINE: {data['sim_status']}")
        self.mem.setText(f"MEMORY: {data['mem_mb']:.1f} MB")
        self.cpu.setText(f"CPU: {data['cpu_pct']:.1f}%")
        self.diag.setText(data['diag'])
        self.buffer_bar.setValue(int(data['buffer_fill'] * 100))
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
            QWidget { background-color: #0A1018; color: #9fffb7; font-size: 13px; }
            QGroupBox { border: 1px solid #1c6b4f; margin-top: 8px; font-weight: bold; }
            QTextEdit { background-color: #0f1a25; color: #f1f191; border: 1px solid #2a4257; }
            QProgressBar { border: 1px solid #1c6b4f; text-align: center; }
            QProgressBar::chunk { background-color: #22d18f; }
        """)
