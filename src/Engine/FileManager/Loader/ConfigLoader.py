from .Loader import Loader
from pathlib import Path
import json


class ConfigLoader(Loader):
    """
        ConfigLoader Class definition

        This Loader is used to load the config file for the Engine and
            Project Initialization.
    """

    def load(self, filename: Path = Path(".config.json")) -> dict:
        """ Load the config from the JSON config file """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def store(
            self,
            filename: Path = Path(".config.json"),
            config: dict) -> None:
        """ Write the actual config into the JSON config file """
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(json.dump(config, indent=4))
