from .Loader import Loader
from pathlib import Path
from typing import Any
import mlx


class SpriteLoader(Loader):
    """
        SpriteLoader Class Definition

        The Sprite Loader is a class specialized to load
            all the sprite used for the entitys and map textures.
    """

    def __init__(self, sprite_file: Path, mlx_session: Any) -> None:
        """ Init Method of the SpriteLoader Object """
        if sprite_file is None:
            raise ValueError("SpriteLoader: File is None")
        self.__file: Path = sprite_file

    def load(self, filename: Path = Path(".")) -> dict:
        """ Load Method of the SpriteLoader Class """
        raise NotImplementedError("SpriteLoader.load is not implemented")
