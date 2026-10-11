from .Loader import Loader
from pathlib import Path


class SpriteLoader(Loader):
    """
        SpriteLoader Class Definition

        The Sprite Loader is a class specialized to load
            all the sprite used for the entitys and map textures.
    """

    def load(self, filename: Path = Path(".")) -> dict:
        """ Load Method of the SpriteLoader Class """
        raise NotImplementedError("SpriteLoader.load is not implemented")
