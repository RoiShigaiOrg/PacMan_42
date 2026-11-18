from Engine.Engine import Engine
from typing import Callable, Any
from .Component import Component


class Selector(Component):
    """ Selector Class Definition

    The Selector is the Component UI Object serving to display
        multiple KEY within the same Object.
    """

    def __init__(
            self,
            engine: Engine,
            key: Any,
            callback: Callable | None = None) -> None:
        """ Init method of the Selector Component. """
        self.__engine: Engine = engine
        self.__key: Any = key
