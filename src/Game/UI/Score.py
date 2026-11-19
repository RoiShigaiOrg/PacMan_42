from Engine.Graphics.MlxDisplay import MlxDisplay


class Score():
    """"""
    def __init__(self, x: int, y: int,
                 color: int, label: str = "SCORE",
                 digits: int = 6) -> None:
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        self.digits = digits
        self.__text: str = ""
        self.set_score(0)

    def set_score(self, score: int) -> int:
        """  """
        self.__text = f"{self.label}  {score:>{self.digits}}"

    def draw(self, display: MlxDisplay):
        """"""
        display.write_text(self.x,
                           self.y, self.color, self.__text)
