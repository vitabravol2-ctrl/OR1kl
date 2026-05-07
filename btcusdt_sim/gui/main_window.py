from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QProgressBar, QTextEdit, QVBoxLayout, QWidget


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
        pen = QPen(self._color, 1.5)
        p.setPen(pen)
        last_x, last_y = 0.0, h - ((self._values[0] - lo) / span) * (h - 8) - 4
        for i, v in enumerate(self._values[1:], start=1):
            x = i * step
            y = h - ((v - lo) / span) * (h - 8) - 4
            p.drawLine(int(last_x), int(last_y), int(x), int(y))
            last_x, last_y = x, y


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BTCUSDT Realtime Intelligence Cockpit v0.1.3")
        self.setMinimumSize(1460, 900)
        self._log_lines: deque[str] = deque(maxlen=300)

        root = QWidget()
        grid = QGridLayout(root)

        self.price = QLabel("0.00")
        self.price.setObjectName("priceLabel")
        self.price_delta = self._mk_label("Δ 0.00")
        self.ws_status = self._mk_label("WS: DISCONNECTED")
        self.tps = self._mk_label("Ticks/s: 0.0")
        self.tick_accel = self._mk_label("Tick accel: 0.00")

        self.spread = self._mk_label("Spread: 0.0000")
        self.spread_activity = QProgressBar(); self.spread_activity.setRange(0, 100)
        self.buy_pressure = QProgressBar(); self.buy_pressure.setRange(0, 100)
        self.sell_pressure = QProgressBar(); self.sell_pressure.setRange(0, 100)
        self.order_delta = self._mk_label("Order delta: 0.0000")

        self.vol_state = self._mk_label("VOL: LOW")
        self.regime = self._mk_label("Regime: -")
        self.severity = self._mk_label("Severity: 0.00")
        self.stability = self._mk_label("Stability: 0.00")

        self.p_up = self._mk_label("P(up): 0.000")
        self.p_down = self._mk_label("P(down): 0.000")
        self.bias = self._mk_label("Bias: NEUTRAL")
        self.conf = self._mk_label("Confidence: 0.000")
        self.conf_bar = QProgressBar(); self.conf_bar.setRange(0, 100)

        self.ws_latency = self._mk_label("WS latency: 0.0 ms")
        self.reconnects = self._mk_label("Reconnects: 0")
        self.stale = self._mk_label("Stale timer: 0")
        self.queue = self._mk_label("Queue pressure: 0")
        self.replay = self._mk_label("Replay queue: 0")
        self.dropped = self._mk_label("Dropped frames/ticks: 0/0")
        self.mem = self._mk_label("Memory MB: 0")
        self.cpu = self._mk_label("CPU %: 0")

        self.price_graph = SparklineWidget("#18f790")
        self.spread_graph = SparklineWidget("#ffd166")
        self.aggr_graph = SparklineWidget("#ef476f")
        self.velocity_graph = SparklineWidget("#8ecae6")

        self.events = QTextEdit(); self.events.setReadOnly(True)
        self.log_window = QTextEdit(); self.log_window.setReadOnly(True)

        live = self._panel("LIVE BTC PRICE", [self.price, self.price_delta, self.ws_status, self.tps, self.tick_accel, self.price_graph])
        spread = self._panel("SPREAD + TICK FLOW", [self.spread, self._mk_label("Spread gauge"), self.spread_activity, self.spread_graph, self.velocity_graph])
        pressure = self._panel("BUY/SELL PRESSURE", [self._mk_label("Buy aggression"), self.buy_pressure, self._mk_label("Sell aggression"), self.sell_pressure, self.order_delta, self.aggr_graph])
        regime = self._panel("VOLATILITY + REGIME", [self.vol_state, self.regime, self.severity, self.stability])
        probability = self._panel("PROBABILITY GAUGE", [self.p_up, self.p_down, self.bias, self.conf, self.conf_bar])
        health = self._panel("SYSTEM HEALTH COCKPIT", [self.ws_latency, self.reconnects, self.stale, self.queue, self.replay, self.dropped, self.mem, self.cpu])
        evpanel = self._panel("EVENT STREAM", [self.events])

        grid.addWidget(live, 0, 0)
        grid.addWidget(spread, 0, 1)
        grid.addWidget(pressure, 0, 2)
        grid.addWidget(regime, 1, 0)
        grid.addWidget(probability, 1, 1)
        grid.addWidget(health, 1, 2)
        grid.addWidget(evpanel, 2, 0, 1, 2)
        grid.addWidget(self.log_window, 2, 2)

        self.setCentralWidget(root)
        self._apply_theme(QApplication.instance())

    def update_dashboard(self, data: dict) -> None:
        price = data["price"]
        flow = data.get("flow", {})
        delta = flow.get("pressure_shift", 0.0)
        self.price.setText(f"{price:.2f}")
        self.price.setStyleSheet(f"color: {'#53f07c' if delta >= 0 else '#ff5f6d'};")
        self.price_delta.setText(f"Momentum pulse: {flow.get('momentum_pulse', 0.0):.5f}")

        self.ws_status.setText(f"WS: {data['ws_state']}")
        self.tps.setText(f"Ticks/s: {data['ticks_per_sec']:.1f}")
        self.tick_accel.setText(f"Tick accel: {flow.get('tick_acceleration', 0.0):.2f}")

        spread_v = max(data["spread"], 0.0)
        self.spread.setText(f"Spread: {spread_v:.4f}")
        self.spread_activity.setValue(min(int(spread_v * 10000), 100))

        buy = int(flow.get("buyer_dominance", 0.5) * 100)
        sell = int(flow.get("seller_dominance", 0.5) * 100)
        self.buy_pressure.setValue(buy)
        self.sell_pressure.setValue(sell)
        self.order_delta.setText(f"Order delta: {delta:.5f}")

        vol = data["volatility"]
        vol_state = "LOW" if vol < 2 else "MID" if vol < 6 else "HIGH" if vol < 12 else "EXTREME"
        self.vol_state.setText(f"VOL: {vol_state} ({vol:.4f})")
        self.regime.setText(f"Regime: {data['regime']}")
        self.severity.setText(f"Severity: {abs(delta)*1000:.2f}")
        self.stability.setText(f"Stability: {max(0.0, 1.0-abs(flow.get('tick_acceleration',0.0))/20):.2f}")

        self.p_up.setText(f"P(up): {data['p_up']:.3f}")
        self.p_down.setText(f"P(down): {data['p_down']:.3f}")
        self.bias.setText(f"Bias: {data['bias']}")
        self.conf.setText(f"Confidence: {data['confidence']:.3f}")
        self.conf_bar.setValue(int(data["confidence"] * 100))

        diag = data["diag"]
        self.ws_latency.setText(f"WS latency: {data['latency_ms']:.1f} ms")
        self.reconnects.setText(f"Reconnects: {diag.split()[0].split('=')[1]}")
        self.stale.setText(f"Stale timer: {diag.split()[1].split('=')[1]}")
        dropped_ticks = diag.split()[2].split('=')[1]
        self.dropped.setText(f"Dropped frames/ticks: {self._extract_drop(data['health'])}/{dropped_ticks}")
        self.queue.setText(f"Queue pressure: {self._extract_health(data['health'], 'queue')}")
        self.replay.setText(f"Replay queue: {self._extract_health(data['health'], 'replay_q')}")
        self.mem.setText(f"Memory MB: {self._extract_health(data['health'], 'mem_mb')}")
        self.cpu.setText(f"CPU %: {data.get('cpu_usage', 0.0):.1f}")

        self.price_graph.set_values(flow.get("price_series", []))
        self.spread_graph.set_values(flow.get("spread_series", []))
        self.aggr_graph.set_values(flow.get("aggression_series", []))
        self.velocity_graph.set_values(flow.get("velocity_series", []))

        self.events.setText("\n".join(self._fmt_event(e) for e in data.get("events", [])))
        self._append_log(data["log"])

    def _fmt_event(self, ev: dict) -> str:
        sev = ev.get("severity", 0.0)
        level = "CRITICAL" if sev > 0.85 else "HIGH" if sev > 0.55 else "LOW"
        return f"[{level}] {ev.get('timestamp')} | {ev.get('name')} | sev={sev:.2f}"

    def _extract_drop(self, health: str) -> str:
        return self._extract_health(health, "dropped")

    def _extract_health(self, health: str, key: str) -> str:
        for chunk in health.split():
            if chunk.startswith(f"{key}="):
                return chunk.split("=", maxsplit=1)[1]
        return "0"

    def _mk_label(self, text: str) -> QLabel:
        w = QLabel(text)
        w.setAlignment(Qt.AlignLeft)
        return w

    def _panel(self, title: str, widgets: list[QWidget]) -> QGroupBox:
        box = QGroupBox(title)
        layout = QVBoxLayout(box)
        for w in widgets:
            layout.addWidget(w)
        return box

    def _append_log(self, message: str) -> None:
        self._log_lines.appendleft(message)
        self.log_window.setText("\n".join(self._log_lines))

    def _apply_theme(self, app: QApplication | None) -> None:
        if not app:
            return
        app.setStyleSheet("""
            QWidget { background-color: #060d16; color: #c8f7da; font-size: 12px; }
            QGroupBox { border: 1px solid #1f6f57; margin-top: 8px; font-weight: bold; }
            QLabel#priceLabel { font-size: 36px; font-weight: 800; }
            QTextEdit { background-color: #0a1522; color: #ffe084; border: 1px solid #2b4561; }
            QProgressBar { border: 1px solid #1e5d4b; text-align: center; }
            QProgressBar::chunk { background-color: #2fd08d; }
        """)
