from collections import deque
from services.difficulty_service import DifficultyService, DifficultyConfig, DifficultyState, MAX_TARGET

def reset(cfg: DifficultyConfig | None = None) -> None:
    if cfg is None:
        cfg = DifficultyConfig()
    DifficultyService.cfg = cfg
    DifficultyService.state = DifficultyState(times=deque(maxlen=cfg.window_size))
    DifficultyService.current_difficulty = cfg.default_difficulty

def test_increase_difficulty_when_fast():
    # If mining is fast, we want to make it HARDER (lower target).
    # Start with a middle target so we can see it decrease.
    start_target = MAX_TARGET // 2
    cfg = DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target)
    reset(cfg)

    # Mine in 5 seconds (fast, half of target time)
    # Ratio = 5/10 = 0.5
    # New target should be start_target * 0.5
    DifficultyService.update_time_to_mine(5.0)

    expected = int(start_target * 0.5)
    assert DifficultyService.current_difficulty == expected

def test_decrease_difficulty_when_slow():
    # If mining is slow, we want to make it EASIER (higher target).
    start_target = MAX_TARGET // 4
    cfg = DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target)
    reset(cfg)

    # Mine in 20 seconds (slow, double target time)
    # Ratio = 20/10 = 2.0
    # New target should be start_target * 2.0
    DifficultyService.update_time_to_mine(20.0)

    expected = int(start_target * 2.0)
    assert DifficultyService.current_difficulty == expected

def test_clamp_ratio_adjustments():
    # Test lower clamp (0.25)
    start_target = MAX_TARGET // 2
    cfg = DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target)
    reset(cfg)

    # Mine in 1 second (very fast)
    # Ratio = 1/10 = 0.1. Should clamp to 0.25.
    DifficultyService.update_time_to_mine(1.0)

    expected = int(start_target * 0.25)
    assert DifficultyService.current_difficulty == expected

    # Test upper clamp (4.0)
    start_target = MAX_TARGET // 16
    reset(DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target))

    # Mine in 100 seconds (very slow)
    # Ratio = 100/10 = 10. Should clamp to 4.0.
    DifficultyService.update_time_to_mine(100.0)

    expected = int(start_target * 4.0)
    assert DifficultyService.current_difficulty == expected

def test_target_max_bound():
    # Cannot exceed MAX_TARGET
    start_target = MAX_TARGET - 100
    cfg = DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target)
    reset(cfg)

    # Mine slow -> easier -> increase target
    DifficultyService.update_time_to_mine(20.0) # Ratio 2.0

    # Should clamp to MAX_TARGET
    assert DifficultyService.current_difficulty == MAX_TARGET

def test_target_min_bound():
    # Cannot go below 1 (though 1 is impossible practically, but technically the min)
    start_target = 10
    cfg = DifficultyConfig(target_time=10.0, window_size=1, default_difficulty=start_target)
    reset(cfg)

    # Mine very fast -> harder -> decrease target
    DifficultyService.update_time_to_mine(0.1) # Ratio clamped to 0.25
    # 10 * 0.25 = 2.5 -> 2
    # Do it again to get to < 1 intent?

    DifficultyService.current_difficulty = 2
    DifficultyService.update_time_to_mine(0.1) # Ratio 0.25 -> 2*0.25 = 0.5 -> int(0) -> clamped to 1?

    # Logic: if new_target < 1: new_target = 1

    assert DifficultyService.current_difficulty == 1

def test_window_average():
    # Verify it uses average of window
    start_target = MAX_TARGET // 2
    cfg = DifficultyConfig(target_time=10.0, window_size=2, default_difficulty=start_target)
    reset(cfg)

    # First sample - average is just sample
    # Mine 5s. Avg = 5. Ratio=0.5. Target -> half.
    DifficultyService.update_time_to_mine(5.0)
    assert DifficultyService.current_difficulty == int(start_target * 0.5)

    # Reset target for clarity or continue?
    # Current target is now T1.
    T1 = DifficultyService.current_difficulty

    # Second sample: 15s.
    # Window: [5, 15]. Avg = 10.
    # Ratio = 10/10 = 1.0. Target should stay same (T1).
    DifficultyService.update_time_to_mine(15.0)
    assert DifficultyService.current_difficulty == T1

