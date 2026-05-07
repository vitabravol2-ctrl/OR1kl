# BTCUSDT Research Market Intelligence Terminal v0.2.2

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (NOT a trading bot).

## v0.2.2 Simplified GUI + Command Center Layout
- Introduced a **3-tab cockpit layout**:
  1. **COMMAND CENTER**
  2. **GAME THEORY**
  3. **DIAGNOSTICS**
- Main screen is now a decision-focused **Command Center** with larger typography and reduced panel noise.
- Added a central **MARKET DECISION CARD** showing:
  - Tactical state
  - Market intent
  - Best scenario
  - Pressure direction
  - Trap side
  - Confidence
  - Danger / Opportunity
- Added **MarketSummaryEngine** with one-line tactical narrative:
  - Example: "Market neutral flow, fake breakout intent, shorts vulnerable, compression wait scenario active, pressure up."
- Priority feed on Command Center now shows only **CRITICAL/HIGH** events.
- Engineering-heavy details (diagnostics/log stream) moved away from main decision screen.

## v0.2.1 Adaptive Game Theory + Market Intent
- Added **MarketIntentEngine** with intent classification.
- Added **ScenarioEvolutionEngine**, **IntentRealityEngine**, **TrapAnalyzer**, **PayoffEvolutionEngine**.
- Added tactical stability controls:
  - intent persistence
  - confidence smoothing
  - tactical instability score

## Core Architecture
- `btcusdt_sim/core/game_theory_engine.py`: adaptive game theory, intent, trap and payoff flow logic
- `btcusdt_sim/core/market_summary_engine.py`: concise market summary string for decision UI
- `btcusdt_sim/gui/main_window.py`: tabbed cockpit UI and command-center-focused layout
- `main.py`: orchestration and pipeline integration

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
