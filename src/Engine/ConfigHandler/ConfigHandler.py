from collections.abc import Mapping
from typing import Any, Generic, TypeVar
from pydantic import BaseModel


ConfigT = TypeVar("ConfigT", bound=BaseModel)


class ConfigHandler(Generic[ConfigT]):
    """
    ConfigHandler Class Declaration

    The ConfigHandler is the Engine Part that will
        manage the setting and getting of configuration value.
        It is derived from the EngineConfig BaseModel and cand values can
        be read and write using the attribute primitive method.
    """

    def __init__(self, config: ConfigT) -> None:
        """ Init Method of the ConfigHandler """
        if config is None:
            raise ValueError("ConfigHandler: config is None")
        self._config = config

    def get(self, key: str) -> Any:
        """ Get Method for the ConfigHandler """
        self._check_key(key)
        return getattr(self._config, key)

    def set(self, key: str, value: Any) -> None:
        """ Set Method for the ConfigHandler """
        self._check_key(key)
        setattr(self._config, key, value)

    def update(self, values: Mapping[str, Any]) -> None:
        """Set several known configuration values."""
        for key, value in values.items():
            self.set(key, value)

    def _check_key(self, key: str) -> None:
        """ Private Method to check if the key exist or not """
        if key not in type(self._config).model_fields:
            raise KeyError(f"Unknown config key: {key}")

    def __getitem__(self, key: str) -> Any:
        """ Get Item Attribute Method """
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """ Set Item Attribute method """
        self.set(key, value)
