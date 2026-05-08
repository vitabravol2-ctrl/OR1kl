# BTCUSDT Research Market Intelligence Terminal v0.2.4

Research-only BTCUSDT microstructure and game-theory simulator (**NOT** live trading).

## v0.2.4 Full algorithm audit + micro-tick decision chain

### Full decision chain
1. Binance WS streams: `bookTicker`, `aggTrade`, `depth`.
2. Tick/depth normalization: bid, ask, spread, mid, volume, aggression, depth liquidity.
3. Buffer/state engines: MarketBuffer → MarketState → TickFlow → OrderBook → Timeflow.
4. Tactical/game layer: LiquidityWarfare → Absorption → Reaction → TacticalSignal → GameTheoryCore → MarketIntent.
5. Setup/simulation/learning: MicroTickSetup → Simulation outcome → PatternMemory.

### Entry/exit logic
- **LONG** only when spread/ws freshness/volatility/pressure/opportunity/trap/scenario/intent/reaction/absorption/EV/confidence are aligned.
- **SHORT** mirrors LONG conditions.
- Otherwise **WAIT**.
- Targets: `+1 tick`, `+2 ticks`; invalidation by risk ticks; timeout and signal-flip cancellation supported in simulation payload.

### EV formula
`EV = P(win)*target_ticks - P(loss)*risk_ticks - fee_ticks - slippage_ticks - timeout_penalty`

Configurable in research mode:
- `MICRO_TICK_SIZE`
- `MICRO_TARGET_TICKS_1`, `MICRO_TARGET_TICKS_2`
- `MICRO_RISK_TICKS`
- `MICRO_TIMEOUT_MS`
- `MICRO_MIN_CONFIDENCE`, `MICRO_MIN_EV`
- `MICRO_MAX_SPREAD_TICKS`
- `MICRO_FEE_TICKS`, `MICRO_SLIPPAGE_TICKS`

### Signal quality
- **A**: confidence >= 0.70, EV clearly positive, scenario+intent+tactical alignment.
- **B**: confidence >= 0.58, EV positive.
- **C**: weak edge.
- **WAIT**: no edge/conflict/stale/poor spread/extreme volatility.

### Audit checklist
- Data continuity from WS to GUI payload.
- No mock constants in decision chain.
- Output field consistency and null/None safety gates.
- Stale WS guards in setup decisions.
- Mirror consistency for LONG/SHORT filters.

### Safety guards (research-only)
- `LIVE_TRADING_ENABLED = False`
- `ORDER_EXECUTION_ENABLED = False`
- GUI always displays:
  - `LIVE TRADING: DISABLED`
  - `ORDERS: DISABLED`
  - `MODE: RESEARCH ONLY`

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
