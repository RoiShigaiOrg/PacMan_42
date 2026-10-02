from .Loader import Loader
from pathlib import Path


class ConfigLoader(Loader):
    """
        ConfigLoader Class definition

        This Loader is used to load the config file for the Engine and
            Project Initialization.
    """

    def load(self, filename: Path) -> dict:
        ...
