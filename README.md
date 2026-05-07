# BTCUSDT Game Theory Simulation Engine v0.1.0

Research-first, self-learning simulation platform for BTCUSDT microstructure.

## Project Goal

This project is **not**:
- a trading bot
- a Binance order executor
- a high-frequency strategy runner

This project is:
- market microstructure research
- probabilistic +1 tick movement analysis
- virtual simulation of decisions
- groundwork for self-learning pattern memory

## Tech Stack

- Python 3.12
- PySide6
- asyncio
- websockets
- orjson
- numpy

## Implemented in v0.1.0

- Binance WebSocket connection (`bookTicker`, `aggTrade`)
- Real-time tick stream
- Rolling market buffer (5000 ticks)
- Market state engine
- Probability engine skeleton (mock probabilities)
- Simulation engine skeleton (virtual long/short decisions)
- Pattern memory skeleton
- Real-time dark GUI
- Safe reconnect with backoff + logging

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Architecture

- `btcusdt_sim/data`: entities and buffer
- `btcusdt_sim/core`: state, probability, simulation, learning
- `btcusdt_sim/infra`: Binance websocket client
- `btcusdt_sim/gui`: PySide6 dashboard
- `btcusdt_sim/utils`: config and logging

## Next Roadmap

- v0.2 richer market analysis
- v0.3 game theory/pain zones engine
- v0.4 full simulation lifecycle
- v0.5 self-learning ranking and scoring
