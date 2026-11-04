from .Loader import Loader
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel
import json


class EngineConfig(BaseModel):
    dimension: List[int]
    available_dimension: Dict[str, List[int]]
    key_config: Dict[str, int]
    debug: bool


class ConfigLoader(Loader):
    """
        ConfigLoader Class definition

        This Loader is used to load the config file for the Engine and
            Project Initialization.
    """

    def __init__(self, config_file: Path, data: EngineConfig | None = None) -> None:
        """ Init Method of ConfigLoader """
        if config_file is None:
            raise ValueError("ConfigLoader: File is None")
        self.__file: Path = config_file
        self.__data: EngineConfig | None = data

    def load(self) -> EngineConfig:
        """ Load the config from the JSON config file """
        with open(self.__file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"data: {data}")
        return EngineConfig.model_validate(data)

    def store(self) -> None:
        """ Write the actual config into the JSON config file """
        if self.__data is None:
            raise ValueError("ConfigLoader: Data is None")
        json_str: str = self.__data.model_dump_json()
        with open(self.__file, "w+", encoding="utf-8") as f:
            f.write(json_str)
