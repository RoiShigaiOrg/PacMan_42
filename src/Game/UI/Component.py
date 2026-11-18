from abc import ABC, abstractmethod


class Component(ABC):
    """ Component Abstract Class Definition

    A Component is an Abstract Class that serve to create different
        UI experience obect within the Game. Component make sure that
        the abstract method are complete for easier implementation
        within the Program.
    """

    @abstractmethod
    def callback(self) -> None:
        """
        Run the method handled by the Component.
        """
        ...
