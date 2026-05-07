# BTCUSDT Research Market Intelligence Terminal v0.2.3

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (**NOT** a live trading bot).

## v0.2.3 Command Center Rebalance + Micro-Tick Lab

### 3-tab cockpit
1. **COMMAND CENTER**
2. **MICRO-TICK LAB**
3. **DIAGNOSTICS**

### Command Center layout (balanced, not overloaded)
- **Left panel:** BTC price, WS status, ticks/sec, latency, current regime, tactical state, priority feed.
- **Center panel (Market Decision Card):** market summary, intent, best scenario, trapped side, pressure direction, confidence, danger, opportunity, payoff score.
- **Right panel (Live Microstructure):** spread, bid/ask pressure, liquidity imbalance, absorption, reaction state, continuation strength, fake pressure warning, sweep risk.

### Micro-Tick Lab (UI + data wiring, research mode)
- **+1 Tick Setup:** virtual direction, entry candidate, +1 tick target, invalidation, timeout.
- **Signal Quality:** A/B/C/WAIT, reason, confidence, EV estimate.
- **Micro-Tick Chain:**
  - `DATA → MICROSTRUCTURE → GAME THEORY → INTENT → SETUP → SIMULATION → RESULT → LEARNING`
- **Simulation Result:** virtual wins, losses, timeouts, winrate, avg duration, current virtual position.
- **Future Trading Gate placeholder:**
  - `LIVE TRADING: DISABLED`
  - `ORDERS: DISABLED`
  - `MODE: RESEARCH ONLY`

### Algorithm pipeline (architectural readiness)
1. Tick ingestion
2. Market buffer
3. Market state
4. Tick flow
5. Depth/liquidity
6. Timeflow
7. Warfare/absorption/reaction
8. Tactical signal
9. Game theory scenario
10. Market intent
11. Micro-tick setup scoring
12. Virtual simulation
13. Result validation
14. Pattern memory update

### Safety rule
- Research-only pipeline.
- No real orders.
- No live trading execution.

## Core Architecture
- `main.py`: full orchestration pipeline + virtual micro-tick simulation result wiring.
- `btcusdt_sim/core/micro_tick_setup_engine.py`: `MicroTickSetupEngine` skeleton and setup output model.
- `btcusdt_sim/gui/main_window.py`: rebalanced Command Center + new Micro-Tick Lab + diagnostics separation.

## Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Windows Quick Start
1. `git pull`
2. Run `./run.ps1`
3. If PowerShell blocks script execution:
   - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
