from Engine.Graphics.MlxDisplay import MlxDisplay

WHITE: int = 0xFFFFFFFF


class PlayTimer:
    """
        PlayTimer Class Definition

        Show the play time of the game: "TIME 3:42".
            It is the same value as the "time" saved in the leaderboard.
            The text is written with write_text over the image:
            it must be drawn at every frame, after display.render().
    """

    def __init__(
            self, x: int, y: int, label: str = "TIME",
            color: int = WHITE) -> None:
        """ Init Method of the PlayTimer Class """
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        self.__text: str = ""
        self.set_time(0.0)

    def set_time(self, seconds: float) -> None:
        """ Prepare the text from the seconds played """
        minutes, secs = divmod(max(0, int(seconds)), 60)
        self.__text = f"{self.label} {minutes}:{secs:02d}"

    def draw(self, display: MlxDisplay) -> None:
        """ Write the text (at every frame, after display.render()) """
        display.write_text(self.x, self.y, self.color, self.__text)
