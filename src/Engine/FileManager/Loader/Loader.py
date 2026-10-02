from abc import ABC, abstractmethod
from Pathlib import Path


class Loader(ABC):
    """
        Loader Abstract Class Definition

        The Loader Abstract Class is the template for all Loader
            Object used in the FileManager Class. The main method
            used in those Class is the load method.
    """

    @abstractmethod
    def load(self, filename: Path) -> dict:
        """ Load Method of the Loader Class """
        ...
