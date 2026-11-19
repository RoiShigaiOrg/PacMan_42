from Engine.Graphics.MlxDisplay import MlxDisplay
from .XpmAlphabet import XpmImage

HEART_FILE = "heart.xpm"
HEART_EMPTY_FILE: str | None = None


class Heart():
    """Show "HEART" at (x, y).
            The MLX the sprite is load of the xpm, drawn on the window,
            over the image:
            it must be written again at every frame."""
    def __init__(self, x: int, y: int, sprite: XpmImage,
                 empty_sprite: XpmImage | None = None, scale: int = 1) -> None:
        self.x = x
        self.y = y
        self.scale = scale
        self.__sprite = sprite
        self.full: bool = True
        self.__empty_sprite = empty_sprite

    @property
    def width(self) -> int:
        """ Width of the heart in pixels """
        return self.__sprite.width * self.scale

    @property
    def height(self) -> int:
        """ Height of the heart in pixels """
        return self.__sprite.height * self.scale

    def draw(self, display: MlxDisplay):
        """draw the heart, if it is to be drawn"""
        sprite = self.__sprite if self.full else self.__empty_sprite
        if sprite is not None:
            sprite.draw(display, self.x, self.y, self.scale, {})


class Lives():
    """Show bar of "HEART" at (x, y).
            add a heart or remove a heart,
            and display the correct number of hearts again."""
    def __init__(self, x: int, y: int, max_lives: int, scale: int = 1,
                 gap: int = 6,
                 heart_file: XpmImage = HEART_FILE,
                 empty_file: XpmImage | None = None) -> None:
        self.x = x
        self.y = y
        self.scale = scale
        self.gap = gap
        self.sprite = XpmImage(heart_file)
        self.empty = XpmImage(empty_file) if empty_file else None
        step = self.sprite.width * scale + gap
        self.hearts: list[Heart] = [
            Heart(x + index * step, y, self.sprite, self.empty, scale)
            for index in range(max_lives)
        ]
        self.__lives: int = max_lives
        self.__changed: bool = True

    @property
    def width(self) -> int:
        """ Width of the whole bar in pixels """
        if not self.hearts:
            return 0
        return (len(self.hearts) * (self.hearts[0].width + self.gap)
                - self.gap)

    @property
    def height(self) -> int:
        """ Height of the bar in pixels """
        return self.hearts[0].height if self.hearts else 0

    def set_lives(self, lives: int) -> None:
        """ Fill the first `lives` hearts, empty the others """
        lives = max(0, min(lives, len(self.hearts)))
        if lives == self.__lives:
            return
        self.__lives = lives
        for index, heart in enumerate(self.hearts):
            heart.full = index < lives
        self.__changed = True

    def redraw(self) -> None:
        """ Force the next draw (after a clear of the screen) """
        self.__changed = True

    def draw(self, display: MlxDisplay, background: int) -> bool:
        """
            Draw the bar if something changed.
            Return True if it was drawn (the caller can then render).
        """
        if not self.__changed:
            return False
        display.fill_rect(self.x, self.y, self.width, self.height,
                          background)
        for heart in self.hearts:
            heart.draw(display)
        self.__changed = False
        return True
