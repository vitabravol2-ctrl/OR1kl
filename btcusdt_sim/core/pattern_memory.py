from dataclasses import dataclass


@dataclass
class PatternStats:
    pattern_id: str
    wins: int = 0
    losses: int = 0
    timeouts: int = 0

    @property
    def winrate(self) -> float:
        total = self.wins + self.losses + self.timeouts
        return (self.wins / total) if total else 0.0


class PatternMemory:
    def __init__(self) -> None:
        self._patterns: dict[str, PatternStats] = {}

    def get_or_create(self, pattern_id: str) -> PatternStats:
        if pattern_id not in self._patterns:
            self._patterns[pattern_id] = PatternStats(pattern_id=pattern_id)
        return self._patterns[pattern_id]

    def record(self, pattern_id: str, result: str) -> PatternStats:
        stats = self.get_or_create(pattern_id)
        if result == "WIN":
            stats.wins += 1
        elif result == "LOSS":
            stats.losses += 1
        else:
            stats.timeouts += 1
        return stats
