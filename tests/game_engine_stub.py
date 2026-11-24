from typing import Any

# Same values as .config.json, for the keys read by GameState.
# Old and new names are both given, whichever GameState reads.
GAME_CONFIG: dict[str, Any] = {
    "lives": 3,
    "pacgum_points": 10,
    "super_points": 50,
    "ghost_points": 200,
    "extra_life": 10000,
    "level_time": 120,
    "step_level": 3,
    "speed_increase": 0.1,
    "max_speed": 3.0,
    "power_duration": 10.0,
    "death_recovery_duration": 3.0,
    "max_level": 10,
    "pellet_points": 10,
    "power_pellet_points": 50,
    "extra_life_score": 10000,
    "speed_step_levels": 3,
    "max_ghost_combo": 3
}


class FakeGameEngine:
    """
        Engine stand-in for the tests that create a GameState.

        FakeGameEngine(lives=2) changes one value of GAME_CONFIG.
    """

    def __init__(self, **overrides: Any) -> None:
        self.config: dict[str, Any] = {**GAME_CONFIG, **overrides}

    def get_config_key(self, key: str) -> Any:
        if key not in self.config:
            raise KeyError(f"Unknown config key: {key}")
        return self.config[key]

    def set_config_key(self, key: str, value: Any) -> None:
        self.config[key] = value
