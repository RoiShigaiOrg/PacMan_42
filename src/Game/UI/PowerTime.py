import math

from Engine.Graphics.MlxDisplay import MlxDisplay

WHITE: int = 0xFFFFFFFF


class PowerTimer:
    """
        Show "POWER  5" while Pac-Man can eat the ghosts.
        Nothing is written when the time is 0: the next
        display.render() covers the old text.
    """

    def __init__(self, x: int, y: int, color: int = WHITE) -> None:
        """ Init Method of the PowerTimer Class """
        self.x = x
        self.y = y
        self.color = color
        self.__text: str = ""

    def set_time(self, seconds: float) -> None:
        """ Prepare the text, empty when the power mode is over """
        if seconds <= 0:
            self.__text = ""
        else:
            self.__text = f"POWER {math.ceil(seconds):>2}"

    def draw(self, display: MlxDisplay) -> None:
        """ Write the text (at every frame, after display.render()) """
        if self.__text:
            display.write_text(self.x, self.y, self.color, self.__text)
