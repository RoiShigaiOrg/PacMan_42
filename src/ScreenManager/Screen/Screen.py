from abc import ABC, abstractmethod


class Screen(ABC):
    """
        Screen Abstract Class Definition

        This class is used to create different screen with their own behaviour
            and to be managed by the ScreenManager
        The main method of the Screen Class is the run method
            to start their own loop.
    """

    @abstractmethod
    def run(self) -> None:
        """ Abstract method to run the screen """
        ...
