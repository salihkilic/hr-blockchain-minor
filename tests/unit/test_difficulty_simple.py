from collections import deque

from src.Services.difficulty import Difficulty, DifficultyConfig, DifficultyState


def reset(cfg: DifficultyConfig | None = None) -> None:
    if cfg is None:
        cfg = DifficultyConfig()
    Difficulty.cfg = cfg
    Difficulty.state = DifficultyState(times=deque(maxlen=cfg.window_size))


def test_increase_when_fast_average():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    # All fast -> average below min_time -> increase by 1
    Difficulty.update(5.0)
    Difficulty.update(6.0)
    Difficulty.update(7.0)
    assert Difficulty.current_difficulty(prev_difficulty=2) == 3


def test_decrease_when_slow_average():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    Difficulty.update(25.0)
    Difficulty.update(22.0)
    Difficulty.update(21.0)
    assert Difficulty.current_difficulty(prev_difficulty=2) == 1


def test_keep_when_in_target_band():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    Difficulty.update(12.0)
    Difficulty.update(15.0)
    Difficulty.update(18.0)
    assert Difficulty.current_difficulty(prev_difficulty=2) == 2


def test_clamping_at_bounds():
    # Upper clamp
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3, min_difficulty=0, max_difficulty=3))
    Difficulty.update(5.0)
    Difficulty.update(6.0)
    Difficulty.update(7.0)
    assert Difficulty.current_difficulty(prev_difficulty=3) == 3  # cannot exceed max

    # Lower clamp
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3, min_difficulty=1, max_difficulty=5))
    Difficulty.update(25.0)
    Difficulty.update(25.0)
    Difficulty.update(25.0)
    assert Difficulty.current_difficulty(prev_difficulty=1) == 1  # cannot go below min


def test_window_averaging_uses_recent_samples():
    # Window size 3; feed fast then slow values; only last 3 should matter
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    # Older samples (will roll out)
    for _ in range(3):
        Difficulty.update(5.0)
    # Now newer samples: average ~19 -> within band => no change
    for _ in range(3):
        Difficulty.update(19.0)
    assert Difficulty.current_difficulty(prev_difficulty=2) == 2
