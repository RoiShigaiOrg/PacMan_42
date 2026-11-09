from Engine.FileManager.Loader import EngineConfig, Loader
from pathlib import Path
from typing import cast
import json


class GameConfig(EngineConfig):
    """ GameConfig Class Declaration, loaded by ConfigLoader in Engine """
    pacgum_points: int
    super_points: int
    ghost_points: int
    lives: int
    level_time: int
    extra_life: int
    step_level: int
    speed_increase: float
    max_speed: float


class GameConfigLoader(Loader):
    """
    GameConfigLoader Class Definition

    This Class is meant to be use with the FileManager Interface
        to load the specified GameConfig File at program initialization
    """

    def __init__(self, file: Path, config: GameConfig | None = None) -> None:
        """ Init Method for the GameConfigLoader """
        if file is None:
            raise ValueError("GameConfigLoader: File is None")
        self.__file = file
        self.__config: GameConfig | None = config

    def load(self) -> GameConfig:
        """ load Method for the GameConfigLoader """
        with open(self.__file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cast(GameConfig, GameConfig.model_validate(data))

    def store(self) -> None:
        """ Store method for the GameConfigLoader """
        if self.__config is None:
            raise ValueError("GameConfigLoader: config is None")
        json_str: str = self.__config.model_dump_json()
        with open(self.__file, "w+", encoding="utf-8") as f:
            f.write(json_str)
