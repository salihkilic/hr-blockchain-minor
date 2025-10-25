from collections import deque

from services.difficulty import Difficulty, DifficultyConfig, DifficultyState


def reset(cfg: DifficultyConfig | None = None) -> None:
    if cfg is None:
        cfg = DifficultyConfig()
    Difficulty.cfg = cfg
    Difficulty.state = DifficultyState(times=deque(maxlen=cfg.window_size))
    Difficulty.current_difficulty = cfg.default_difficulty


def test_increase_when_fast_average():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    # All fast -> average below min_time -> increase by 1
    Difficulty.update_time_to_mine(5.0) # Becomes 3
    Difficulty.update_time_to_mine(6.0) # Becomes 4
    Difficulty.update_time_to_mine(7.0) # Becomes 5
    assert Difficulty.current_difficulty == 5


def test_decrease_when_slow_average():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    Difficulty.update_time_to_mine(25.0) # Becomes 1
    Difficulty.update_time_to_mine(22.0) # Becomes 0
    Difficulty.update_time_to_mine(21.0) # Stays at 0
    assert Difficulty.current_difficulty == 0


def test_keep_when_in_target_band():
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))
    Difficulty.update_time_to_mine(12.0) # Stays at 2
    Difficulty.update_time_to_mine(15.0) # Stays at 2
    Difficulty.update_time_to_mine(18.0) # Stays at 2
    assert Difficulty.current_difficulty == 2


def test_clamping_at_bounds():
    # Upper clamp
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3, min_difficulty=0, max_difficulty=3))
    Difficulty.update_time_to_mine(5.0) # Becomes 3
    Difficulty.update_time_to_mine(6.0) # Stays at 3
    Difficulty.update_time_to_mine(7.0) # Stays at 3
    assert Difficulty.current_difficulty == 3  # cannot exceed max

    # Lower clamp
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3, min_difficulty=1, max_difficulty=5))
    Difficulty.update_time_to_mine(25.0)
    Difficulty.update_time_to_mine(25.0)
    Difficulty.update_time_to_mine(25.0)
    assert Difficulty.current_difficulty == 1  # cannot go below min


def test_window_averaging_uses_recent_samples():
    # Window size 3; feed fast then slow values; only last 3 should matter
    reset(DifficultyConfig(min_time=10.0, max_time=20.0, window_size=3))

    # Older samples (will roll out)
    for _ in range(3):
        Difficulty.update_time_to_mine(5.0)

    assert Difficulty.current_difficulty == 5  # increased to 5

    # Newer samples: average ~19 -> within band => no change
    for _ in range(3):
        Difficulty.update_time_to_mine(19.0)
    assert Difficulty.current_difficulty == 6  # Increased to 6 on the first sample, then stays
