from .Loader import Loader
from pathlib import Path
from typing import Any, cast
import json


class ConfigLoader(Loader):
    """
        ConfigLoader Class definition

        This Loader is used to load the config file for the Engine and
            Project Initialization.
    """

    def load(
            self, filename: Path = Path(".config.json")
    ) -> dict[str, Any]:
        """ Load the config from the JSON config file """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cast(dict[str, Any], data)

    def store(
            self,
            config: dict,
            filename: Path = Path(".config.json")) -> None:
        """ Write the actual config into the JSON config file """
        with open(filename, "w+", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
