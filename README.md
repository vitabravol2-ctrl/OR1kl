# BTCUSDT Research Market Intelligence Terminal v0.2.1

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (NOT a trading bot).

## v0.2.1 Adaptive Game Theory + Market Intent
- Added **MarketIntentEngine** with intent classification:
  - `BAIT_LONGS`, `BAIT_SHORTS`, `SWEEP_FOR_LIQUIDITY`
  - `ACCEPT_HIGHER`, `ACCEPT_LOWER`, `FAKE_BREAKOUT`
  - `RANGE_MANIPULATION`, `MOMENTUM_HUNT`, `EXHAUSTION_ROTATION`, `PANIC_EXTRACTION`
- Added **ScenarioEvolutionEngine**:
  - tracks scenario strengthening/collapse
  - transition flow output for cockpit scenario flow panel
  - failed scenario detection + persistence view
- Added **IntentRealityEngine**:
  - compares market intent vs actual reaction outcome
  - marks inversion behavior and weakness diagnostics
- Added **TrapAnalyzer**:
  - long/short trap probabilities
  - fake continuation + failed momentum severity
  - likely pain direction and trapped crowd severity
- Added **PayoffEvolutionEngine**:
  - payoff growth and collapse
  - scenario reinforcement/decay
  - smoothed payoff momentum for flow panel
- Added tactical stability controls in this layer:
  - intent persistence
  - confidence smoothing
  - scenario hysteresis-like transition gating
  - tactical instability score

## New Panels (v0.2.1)
- MARKET INTENT RADAR
- SCENARIO FLOW
- TRAP ANALYZER
- PAYOFF FLOW
- INTENT vs REALITY

## Existing Foundation (v0.2.0 and earlier)
- GameTheoryCore (player model, crowd pain, payoff matrix, decision engine)
- Tactical radar + liquidity warfare + absorption + reaction stack
- Event priority stream and lightweight sparkline-based cockpit rendering

## Performance Constraints
- Bounded memory via deque histories.
- Minimal redraw strategy with compact sparkline buffers.
- Async-safe queue handoff and non-blocking UI pump.
- Stable lightweight tactical repaint behavior.

## Core Architecture
- `btcusdt_sim/core/game_theory_engine.py`: adaptive game theory, intent, scenario evolution, trap and payoff flow logic
- `btcusdt_sim/gui/main_window.py`: cockpit UI v0.2.1, radar and flow panels
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
2. Run `.\run.ps1`
3. If PowerShell blocks script execution:
   - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
