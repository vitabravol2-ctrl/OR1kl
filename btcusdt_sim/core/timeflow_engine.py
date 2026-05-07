from collections import deque


class TimeflowEngine:
    def __init__(self, window: int = 240) -> None:
        self._prev_ts: int | None = None
        self._speed: deque[float] = deque(maxlen=window)
        self._accel: deque[float] = deque(maxlen=window)
        self._pulse: deque[float] = deque(maxlen=window)

    def update(self, timestamp_ms: int, momentum_pulse: float) -> dict:
        dt_ms = 0.0
        if self._prev_ts is not None:
            dt_ms = max(float(timestamp_ms - self._prev_ts), 1.0)
        self._prev_ts = timestamp_ms

        arrival_speed = 1000.0 / dt_ms if dt_ms > 0 else 0.0
        self._speed.append(arrival_speed)

        accel = 0.0
        if len(self._speed) >= 2:
            accel = self._speed[-1] - self._speed[-2]
        self._accel.append(accel)

        pulse = momentum_pulse * (1.0 + min(abs(accel), 30.0) * 0.03)
        self._pulse.append(pulse)

        burst = arrival_speed > 8.0 or accel > 2.4
        dead_zone = arrival_speed < 1.2
        transition = "BURST" if burst else "DEAD" if dead_zone else "FLOW"
        continuity = max(0.0, 1.0 - min(abs(accel), 10.0) / 10.0)

        accel_spike = abs(accel) > 2.2
        flow_exhaustion = momentum_pulse > 3.2 and accel < -0.8
        flow_compression = abs(accel) < 0.2 and arrival_speed < 2.2
        pulse_rhythm = "RAPID" if arrival_speed > 7.5 else "SLOW" if arrival_speed < 1.6 else "STEADY"
        burst_transition = burst and (len(self._accel) > 2 and self._accel[-2] < 0)

        return {
            "arrival_speed": arrival_speed,
            "flow_acceleration": accel,
            "burst_activity": burst,
            "dead_zone": dead_zone,
            "pulse_transition": transition,
            "momentum_continuity": continuity,
            "acceleration_spike": accel_spike,
            "flow_exhaustion": flow_exhaustion,
            "flow_compression": flow_compression,
            "pulse_rhythm": pulse_rhythm,
            "burst_transition": burst_transition,
            "speed_series": list(self._speed),
            "accel_series": list(self._accel),
            "pulse_series": list(self._pulse),
        }
