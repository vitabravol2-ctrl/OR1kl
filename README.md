# BTCUSDT Research Market Intelligence Terminal v0.2.0

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (NOT a trading bot).

## v0.2.0 Game Theory Core
- Added **GameTheoryCore**:
  - player model synthesis for crowd + market maker behavior
  - payoff-matrix scoring across directional/fake/sweep/range scenarios
  - Nash-like decision selection (`best_scenario`, confidence, expected payoff)
- Added **PlayerModelEngine**:
  - tracks pressure, vulnerability, likely action, risk, payoff expectation for:
    - `LONG_CROWD`
    - `SHORT_CROWD`
    - `MARKET_MAKER`
    - `MOMENTUM_TRADERS`
    - `LIQUIDITY_PROVIDERS`
    - `OUR_SIMULATOR`
- Added **CrowdPainEngine**:
  - pain map above/below current price
  - trapped-side proxy and liquidation-pressure proxy
  - `PainScore = stop_density * liquidity_reward / distance_penalty` style logic
- Added **PayoffMatrixEngine**:
  - scenarios:
    - `MOVE_UP`, `MOVE_DOWN`
    - `FAKE_UP_THEN_DOWN`, `FAKE_DOWN_THEN_UP`
    - `COMPRESSION_WAIT`
    - `SWEEP_HIGH`, `SWEEP_LOW`
    - `RANGE_TRAP`
  - metrics: reward, cost, risk, liquidity gain, crowd pain, MM advantage, expected payoff
- Added **GameDecisionEngine**:
  - selects best + second scenario
  - confidence and scenario reason output

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
- GAME THEORY STATE
- PLAYER ADVANTAGE
- CROWD PAIN MAP
- PAYOFF MATRIX
- BEST SCENARIO
- MARKET MAKER INCENTIVE
- TRAPPED SIDE

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
- `btcusdt_sim/core/game_theory_engine.py`: game theory stack (player model, pain, payoff, decision)
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
