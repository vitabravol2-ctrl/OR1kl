# BTCUSDT Research Market Intelligence Terminal v0.1.2

Professional realtime cockpit for BTCUSDT microstructure research (NOT a trading bot).

## Focus
- Realtime market state understanding
- Market regime classification
- Micro-event detection
- Replay pipeline foundation
- Self-learning-ready architecture

## Architecture
- `btcusdt_sim/core/market_state_engine.py`: computes spread, micro trend, volatility, aggression, tick velocity
- `btcusdt_sim/core/market_regime_engine.py`: classifies CALM / TRENDING_UP / TRENDING_DOWN / HIGH_VOLATILITY / COMPRESSION / EXPANSION / LIQUIDITY_SWEEP / CHAOTIC
- `btcusdt_sim/core/micro_event_detector.py`: detects spread explosion, aggression spike, imbalance shift, volatility burst, liquidity sweep candidate, momentum ignition, dead market
- `btcusdt_sim/core/probability_engine.py`: weighted scoring, normalization, confidence, directional bias
- `btcusdt_sim/infra/replay.py`: async-only replay storage (`jsonl.gz`) + replay reader skeleton
- `btcusdt_sim/gui/main_window.py`: cockpit panels for regime/events/bias/confidence/health/replay

## Replay foundation
- Snapshot format: compressed `jsonl.gz`
- Type: `ReplayFrame`
- Writer: bounded queue + background thread
- Reader: skeleton iterator for future replay engine

## Cockpit GUI panels
- MARKET REGIME PANEL
- EVENT ALERT PANEL
- DIRECTIONAL BIAS PANEL
- CONFIDENCE SCALE
- SYSTEM HEALTH PANEL
- REPLAY STATUS PANEL

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
