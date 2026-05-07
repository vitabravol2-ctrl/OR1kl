import gzip
import json
import threading
from pathlib import Path
from queue import Empty, Queue

from btcusdt_sim.data.entities import Tick


class TickSnapshotWriter:
    def __init__(self, path: str = "snapshots/ticks.jsonl.gz", compress: bool = True) -> None:
        self._path = Path(path)
        self._compress = compress
        self._queue: Queue[list[Tick]] = Queue(maxsize=8)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(self, ticks: list[Tick]) -> None:
        try:
            self._queue.put_nowait(ticks)
        except Exception:
            pass

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)

    def _run(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        opener = gzip.open if self._compress else open
        mode = "at"
        with opener(self._path, mode, encoding="utf-8") as f:
            while not self._stop.is_set():
                try:
                    ticks = self._queue.get(timeout=0.2)
                except Empty:
                    continue
                for t in ticks:
                    f.write(json.dumps(t.__dict__) + "\n")
                f.flush()
