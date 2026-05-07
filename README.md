# BTCUSDT Research Market Intelligence Terminal v0.1.3

Professional realtime BTCUSDT intelligence cockpit for microstructure research (NOT a trading bot).

## v0.1.3 Cockpit Upgrade
- Live BTC price panel with realtime pulse coloring.
- Spread + activity panel with gauge and scrolling spread graph.
- Tick flow panel with ticks/sec and tick acceleration.
- Buy/Sell pressure bars + order flow delta.
- Volatility state panel: LOW / MID / HIGH / EXTREME.
- Market regime + severity + stability indicators.
- Probability gauge for P(up), P(down), confidence, directional bias.
- Event stream panel with severity tiers (LOW/HIGH/CRITICAL).
- System health cockpit with latency, reconnects, stale, queue pressure, replay queue, dropped frames/ticks, memory proxy, CPU usage.

## Flow Intelligence Engine
`btcusdt_sim/core/tick_flow_engine.py` computes lightweight realtime flow metrics:
- buy wave
- sell wave
- pressure shift
- tick acceleration
- momentum pulse
- buyer/seller dominance

These metrics are rendered directly in GUI graphs and pressure bars.

## Visualization System (Lightweight Qt Drawing)
The GUI uses custom Qt paint widgets (`SparklineWidget`) instead of heavy plotting libraries:
- Scrolling micro price graph
- Spread activity line
- Aggression histogram-style line
- Tick velocity graph

Rendering strategy:
- throttled UI pump via QTimer
- update only newest payload
- bounded repaint cycle
- no full-screen redraws

## Core Architecture
- `btcusdt_sim/core/market_state_engine.py`: spread, micro trend, volatility, aggression, tick velocity
- `btcusdt_sim/core/market_regime_engine.py`: market regime classification
- `btcusdt_sim/core/micro_event_detector.py`: micro-event detection
- `btcusdt_sim/core/probability_engine.py`: directional probability and confidence
- `btcusdt_sim/core/tick_flow_engine.py`: realtime flow intelligence
- `btcusdt_sim/infra/replay.py`: async replay storage (`jsonl.gz`)
- `btcusdt_sim/gui/main_window.py`: professional multi-panel cockpit UI

## Launch (Windows 10)
- Double click `run.bat`
- Or run `run.ps1` in PowerShell

## Update + launch (Windows 10)
- Double click `update_from_git.bat`
- Or run `update_from_git.ps1`

## Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
