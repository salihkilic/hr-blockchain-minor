from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Deque, Optional
from collections import deque
import math


# Max target = 2^256 - 1 (easiest difficulty)
MAX_TARGET = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF


@dataclass
class DifficultyConfig:
    target_time: float = 15       # seconds (ideal time to mine a block)
    window_size: int = 10            # number of recent samples to average
    # Starting difficulty (target). Max_Target = Easiest. Default is halfway.
    default_difficulty: int = 0xd3d3340d5bc9a0000000000000000000000000000000000000000000000

@dataclass
class DifficultyState:
    times: Deque[float] = field(default_factory=lambda: deque(maxlen=10))


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
        if ratio < 0.95:
            ratio = 0.95
        if ratio > 1.05:
            ratio = 1.05

        new_target = int(cls.current_difficulty * ratio)

        # Clamp to valid range
        if new_target > MAX_TARGET:
            new_target = MAX_TARGET
        if new_target < 1:
            new_target = 1

        logging.debug(f"Old Target: {cls.current_difficulty} | New target: {new_target} | Ratio: {ratio:.4f} | Avg Time: {avg_time:.2f}s")
        cls.current_difficulty = new_target

    @classmethod
    def _avg_time(cls) -> Optional[float]:
        if not cls.state.times:
            return None
        return sum(cls.state.times) / len(cls.state.times)

