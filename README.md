# BTCUSDT Research Market Intelligence Terminal v0.1.4

Professional realtime BTCUSDT intelligence cockpit for microstructure research (NOT a trading bot).

## v0.1.4 Depth + Timeflow + Microstructure Intelligence
- Order book awareness via Binance `depth10` stream integration.
- New **OrderBookEngine** for bid/ask liquidity, imbalance, wall detection, pressure zones, and liquidity concentration.
- New **TimeflowEngine** for tick-arrival speed, acceleration, burst/dead-zone transitions, and momentum continuity.
- New **MarketMemoryEngine** for recent liquidity zones, sweep traces, repeated rejections, and pressure history.
- Upgraded microstructure signal set:
  - absorption
  - fake breakout candidate
  - liquidity grab candidate
  - exhaustion
  - pressure collapse
  - momentum continuation
  - trapped side candidate
- Event stream now includes severity levels (`LOW`, `MID`, `HIGH`, `CRITICAL`) and lifespan states (`fading`, `active`).

## New Cockpit Panels
- DEPTH MAP
- LIQUIDITY PRESSURE
- TIMEFLOW
- MARKET MEMORY
- ACTIVE SIGNALS
- LOG STREAM

## Lightweight Visualization (no heavy libs)
- Scrolling order-flow style sparkline renderers.
- Liquidity pulse graph.
- Pressure balance graph.
- Momentum/acceleration wave graph.

## Core Architecture
- `btcusdt_sim/core/order_book_engine.py`: depth map intelligence
- `btcusdt_sim/core/timeflow_engine.py`: timeflow intelligence
- `btcusdt_sim/core/market_memory_engine.py`: market memory
- `btcusdt_sim/core/micro_event_detector.py`: signal intelligence (non-predictive)
- `btcusdt_sim/core/tick_flow_engine.py`: realtime flow metrics
- `btcusdt_sim/infra/binance_ws_client.py`: `bookTicker + aggTrade + depth10`
- `btcusdt_sim/gui/main_window.py`: upgraded radar-style cockpit UI

## Performance Constraints
- Async-safe websocket processing.
- Bounded UI queue + bounded in-memory history deques.
- Lightweight Qt painting.
- No blocking depth logic.
- Safe replay cleanup on shutdown.

## Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
