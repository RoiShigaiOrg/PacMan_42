from abc import ABC, abstractmethod
from typing import Any


class Loader(ABC):
    """
        Loader Abstract Class Definition

        The Loader Abstract Class is the template for all Loader
            Object used in the FileManager Class. The main method
            used in those Class is the load method.
    """

    @abstractmethod
    def load(self) -> Any:
        """ Load Method of the Loader Class """
        ...

    @abstractmethod
    def store(self) -> None:
        """ Store Method of the Loader Class """
        ...
