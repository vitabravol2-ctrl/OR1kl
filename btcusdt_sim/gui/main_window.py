from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTextEdit, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Game Theory Simulation Engine v0.1.0")
        self.setMinimumSize(900, 650)

        self._log_lines: deque[str] = deque(maxlen=200)

        root = QWidget()
        layout = QVBoxLayout(root)

        self.live_price = QLabel("LIVE PRICE: -")
        self.spread = QLabel("SPREAD: -")
        self.imbalance = QLabel("IMBALANCE: -")
        self.micro_trend = QLabel("MICRO TREND: -")
        self.volatility = QLabel("VOLATILITY: -")
        self.p_up = QLabel("P(up): -")
        self.p_down = QLabel("P(down): -")
        self.sim_status = QLabel("SIMULATION STATUS: -")
        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)

        for w in [
            self.live_price,
            self.spread,
            self.imbalance,
            self.micro_trend,
            self.volatility,
            self.p_up,
            self.p_down,
            self.sim_status,
        ]:
            w.setAlignment(Qt.AlignLeft)
            layout.addWidget(w)

        layout.addWidget(self.log_window)
        self.setCentralWidget(root)
        self._apply_dark_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        self.live_price.setText(f"LIVE PRICE: {data['price']:.2f}")
        self.spread.setText(f"SPREAD: {data['spread']:.2f}")
        self.imbalance.setText(f"IMBALANCE: {data['imbalance']:.5f}")
        self.micro_trend.setText(f"MICRO TREND: {data['micro_trend']:.5f}")
        self.volatility.setText(f"VOLATILITY: {data['volatility']:.5f}")
        self.p_up.setText(f"P(up): {data['p_up']:.3f}")
        self.p_down.setText(f"P(down): {data['p_down']:.3f}")
        self.sim_status.setText(f"SIMULATION STATUS: {data['sim_status']}")
        self._append_log(data['log'])

    def _append_log(self, message: str) -> None:
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_dark_theme(self, app: QApplication | None) -> None:
        if app is None:
            return
        app.setStyleSheet(
            """
            QWidget { background-color: #121212; color: #E0E0E0; font-size: 14px; }
            QTextEdit { background-color: #1E1E1E; border: 1px solid #333; }
            """
        )
