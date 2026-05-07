# BTCUSDT Research Market Intelligence Terminal v0.1.6

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (NOT a trading bot).

## v0.1.6 Liquidity Warfare + Reaction Intelligence
- Added **LiquidityWarfareEngine**:
  - wall appearance/disappearance tracking
  - fake liquidity / spoof-candidate risk
  - sweep pressure and liquidity consumption
  - exhaustion and instability scoring
- Added **AbsorptionEngine**:
  - aggressive buy/sell absorption detection
  - trapped continuation and failed push logic
  - stalled momentum classification
- Added **ReactionEngine**:
  - response delay and reaction speed modeling
  - follow-through / failed follow-through analysis
  - continuation probability and rejection strength
  - reaction states:
    - FAST_ACCEPTANCE
    - WEAK_RESPONSE
    - FAILED_BREAK
    - AGGRESSIVE_ACCEPTANCE
    - STALLED_MOVE
    - REJECTION
    - PANIC_FLOW
    - EXHAUSTED_FLOW

## Tactical Persistence + Stability Controls
- Added hysteresis and minimum state duration in tactical + warfare logic.
- Added confidence smoothing to reduce state flip noise.
- Added cooldown-aware event emission in upgraded behavior analysis.

## Event System Upgrade
New behavior-analysis events:
- spoof candidate
- wall collapse
- liquidity consumed
- absorption detected
- failed breakout
- failed continuation
- panic flow
- pressure inversion

Severity ladder remains: `LOW` / `MID` / `HIGH` / `CRITICAL`.

## Cockpit Upgrade (Radar Combat Center)
Added/extended cockpit intelligence outputs:
- dominant tactical side
- fake pressure warning
- sweep / exhaustion risk
- continuation strength
- reaction strength/state
- absorption status

New/expanded panels:
- TACTICAL RADAR (upgraded)
- LIQUIDITY WARFARE
- ABSORPTION
- SIGNAL PRIORITY
- MARKET STRESS
- FLOW RHYTHM
- MEMORY HEAT

## Performance Constraints
- Bounded memory via deque histories.
- Minimal redraw strategy with compact sparkline buffers.
- Async-safe queue handoff and non-blocking UI pump.
- Stable lightweight tactical repaint behavior.

## Core Architecture
- `btcusdt_sim/core/liquidity_warfare_engine.py`: liquidity warfare + spoof behavior analysis
- `btcusdt_sim/core/absorption_engine.py`: absorption and failed push classification
- `btcusdt_sim/core/reaction_engine.py`: reaction delay/speed/follow-through modeling
- `btcusdt_sim/core/tactical_signal_engine.py`: tactical synthesis + persistence/hysteresis
- `btcusdt_sim/core/micro_event_detector.py`: upgraded event logic + cooldown
- `btcusdt_sim/gui/main_window.py`: tactical radar cockpit UI v0.1.6

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

## Troubleshooting
- **SyntaxError in `main.py`**
  - Run: `python -m py_compile main.py`
  - Ensure your local file is not corrupted and has normal line breaks.
- **requirements install failed**
  - Run: `python -m pip install --upgrade pip`
  - Then: `pip install -r requirements.txt`
- **PySide6 missing**
  - Activate `.venv`, then run `pip install -r requirements.txt`.
- **WebSocket disconnected**
  - The app reconnects automatically; check internet/firewall and Binance WS availability.
- **PowerShell execution policy**
  - Use: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
