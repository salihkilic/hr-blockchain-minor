from __future__ import annotations

from dataclasses import dataclass, field
from typing import Deque, Optional
from collections import deque
import math


@dataclass
class DifficultyConfig:
    min_time: float = 10.0       # seconds (lower threshold)
    max_time: float = 20.0       # seconds (upper threshold)
    min_difficulty: int = 0
    max_difficulty: int = 1
    window_size: int = 5         # number of recent samples to average
    step_limit: int = 1          # Max step change per update (usually 1)
    default_difficulty: int = 1  # Starting difficulty aligned with tests


@dataclass
class DifficultyState:
    times: Deque[float] = field(default_factory=lambda: deque(maxlen=5))


class DifficultyService:
    """
    Static utility that tracks recent mining times and computes a recommended
    difficulty based on the current window average. It does NOT persist an internal
    difficulty; you must pass your previous difficulty to current_difficulty(prev).
    """

    cfg = DifficultyConfig()
    state = DifficultyState(times=deque(maxlen=cfg.window_size))
    current_difficulty = cfg.default_difficulty

    @classmethod
    def update_time_to_mine(cls, mining_time: float) -> None:
        if not (math.isfinite(mining_time) and mining_time > 0):
            return
        cls.state.times.append(mining_time)
        new_difficulty = cls._calculate_difficulty()
        # Apply at most 1 step per update toward target
        if new_difficulty > cls.current_difficulty:
            cls.current_difficulty = min(cls.current_difficulty + cls.cfg.step_limit, cls.cfg.max_difficulty)
        elif new_difficulty < cls.current_difficulty:
            cls.current_difficulty = max(cls.current_difficulty - cls.cfg.step_limit, cls.cfg.min_difficulty)
        # else keep as is

    @classmethod
    def _calculate_difficulty(cls) -> int:
        avg = cls._avg_time()
        if avg is None:
            return cls.current_difficulty
        # If average below min_time -> target one step up; if above max_time -> one step down; else keep
        if avg < cls.cfg.min_time:
            return min(cls.cfg.max_difficulty, cls.current_difficulty + 1)
        if avg > cls.cfg.max_time:
            return max(cls.cfg.min_difficulty, cls.current_difficulty - 1)
        return cls.current_difficulty

    @classmethod
    def _avg_time(cls) -> Optional[float]:
        if not cls.state.times:
            return None
        return sum(cls.state.times) / len(cls.state.times)
