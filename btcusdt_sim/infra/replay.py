import gzip
import json
import threading
from dataclasses import asdict
from pathlib import Path
from queue import Empty, Queue

from btcusdt_sim.data.entities import ReplayFrame


class ReplayStorage:
    def __init__(self, path: str = "snapshots/replay.jsonl.gz") -> None:
        self._path = Path(path)
        self._queue: Queue[ReplayFrame] = Queue(maxsize=2048)
        self._stop = threading.Event()
        self._written = 0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(self, frame: ReplayFrame) -> bool:
        try:
            self._queue.put_nowait(frame)
            return True
        except Exception:
            return False

    def status(self) -> dict:
        return {"queued": self._queue.qsize(), "written": self._written}

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2.0)

    def _run(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(self._path, "at", encoding="utf-8") as f:
            while not self._stop.is_set():
                try:
                    frame = self._queue.get(timeout=0.2)
                except Empty:
                    continue
                f.write(json.dumps(asdict(frame), separators=(",", ":")) + "\n")
                self._written += 1
                if self._written % 50 == 0:
                    f.flush()


class ReplayReader:
    def __init__(self, path: str = "snapshots/replay.jsonl.gz") -> None:
        self._path = Path(path)

    def iter_frames(self):
        if not self._path.exists():
            return
        with gzip.open(self._path, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
