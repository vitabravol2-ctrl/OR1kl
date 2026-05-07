# BTCUSDT Research Market Intelligence Terminal v0.1.5

Professional realtime BTCUSDT tactical intelligence cockpit for microstructure research (NOT a trading bot).

## v0.1.5 Tactical Market Radar
- New **TacticalSignalEngine** combining:
  - OrderBookEngine
  - TimeflowEngine
  - TickFlowEngine
  - MarketRegimeEngine
  - MarketMemoryEngine
  - ProbabilityEngine context
- Tactical state model with:
  - PRESSURE_BUILDUP
  - LIQUIDITY_TRAP
  - SWEEP_RISK
  - MOMENTUM_SURGE
  - ABSORPTION
  - DEAD_FLOW
  - CHAOTIC_FLOW
  - TREND_CONTINUATION
  - REVERSAL_RISK
  - NEUTRAL_FLOW
- Signal priority weighting: `LOW`, `MID`, `HIGH`, `CRITICAL`.

## Smart Tactical Visualization
- New cockpit center: **TACTICAL RADAR**.
- Added panels:
  - TACTICAL STATE
  - FLOW RHYTHM
  - MEMORY HEAT
  - SIGNAL PRIORITY
  - MARKET STRESS
- Lightweight radar-style widgets:
  - danger/opportunity gauges
  - tactical stress bars
  - directional tactical labels
  - dynamic priority coloring

## Event + Log Stream Upgrades
- Event deduplication and cooldown in `MicroEventDetector`.
- Severity-first tactical grouping for signal output.
- Log stream de-duplication and grouped duplicate collapse.

## Depth + Memory + Timeflow Upgrades
- Timeflow now computes acceleration spikes, flow exhaustion/compression, pulse rhythm, and burst transitions.
- Market memory now tracks repeated sweep zones, persistent pressure zones, historical imbalance clusters, momentum memory, and rejection traces.

## Performance Constraints
- Bounded rendering with small-history sparkline widgets.
- Minimal allocations via deques and capped UI log/event buffers.
- Non-blocking queue pump and lightweight Qt painting.

## Core Architecture
- `btcusdt_sim/core/tactical_signal_engine.py`: tactical state synthesis engine
- `btcusdt_sim/core/order_book_engine.py`: depth map intelligence
- `btcusdt_sim/core/timeflow_engine.py`: flow rhythm intelligence
- `btcusdt_sim/core/market_memory_engine.py`: memory heat intelligence
- `btcusdt_sim/core/micro_event_detector.py`: deduped tactical events
- `btcusdt_sim/gui/main_window.py`: tactical radar cockpit UI

## Linux/macOS
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
