from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque, Optional
from collections import deque
import math


# Max target = 2^256 - 1 (easiest difficulty)
MAX_TARGET = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


@dataclass
class DifficultyConfig:
    target_time: float = 15.0       # seconds (ideal time to mine a block)
    window_size: int = 5            # number of recent samples to average
    default_difficulty: int = MAX_TARGET  # Starting difficulty (target). Max = Easiest.


@dataclass
class DifficultyState:
    times: Deque[float] = field(default_factory=lambda: deque(maxlen=5))


class DifficultyService:
    """
    Static utility that tracks recent mining times and computes a recommended
    difficulty (target) based on the current window average.
    """

    cfg = DifficultyConfig()
    state = DifficultyState(times=deque(maxlen=cfg.window_size))
    current_difficulty = cfg.default_difficulty

    @classmethod
    def update_time_to_mine(cls, mining_time: float) -> None:
        if not (math.isfinite(mining_time) and mining_time > 0):
            return
        cls.state.times.append(mining_time)

        avg_time = cls._avg_time()
        if avg_time is None:
            return

        # Granular adjustment by ratio
        # new_target = old_target * (actual_time / expected_time)
        ratio = avg_time / cls.cfg.target_time

        # Clamp adjustment factor
        if ratio < 0.25:
            ratio = 0.25
        if ratio > 4.0:
            ratio = 4.0

        new_target = int(cls.current_difficulty * ratio)

        # Clamp to valid range
        if new_target > MAX_TARGET:
            new_target = MAX_TARGET
        if new_target < 1:
            new_target = 1

        cls.current_difficulty = new_target

    @classmethod
    def _avg_time(cls) -> Optional[float]:
        if not cls.state.times:
            return None
        return sum(cls.state.times) / len(cls.state.times)
