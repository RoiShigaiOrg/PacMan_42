from Engine.Graphics.MlxDisplay import MlxDisplay
import os
import re

Lines = tuple[int, int, int, int]
ColorMap = dict[int, int]

FILL: int = 0xFFFFC629
OUTLINE: int = 0xFFEB2A23
SHADOW: int = 0xFF0000FF


class XpmImage:
    """An XPM image, divided into horizontal strips of the same color."""

    def __init__(self, path: str) -> None:
        with open(path, encoding="ascii") as f:
            chains = re.findall(r'"(.*?)"', f.read())
        width, height, nb_colors, cpp = map(int, chains[0].split()[:4])

        colors: dict[str, int | None] = {}
        for ligne in chains[1:1 + nb_colors]:
            code, valeur = ligne[:cpp], ligne[cpp:].split()[-1]
            colors[code] = (
                None if valeur.lower() == "none"
                else 0xFF000000 | int(valeur.lstrip("#"), 16))

        self.width = width
        self.height = height
        self.lines: list[Lines] = []
        for y, line in enumerate(chains[1 + nb_colors:][:height]):
            codes = [line[i:i + cpp] for i in range(0, width * cpp, cpp)]
            x = 0
            while x < width:
                couleur = colors[codes[x]]
                n = 1
                while x + n < width and codes[x + n] == codes[x]:
                    n += 1
                if couleur is not None:
                    self.lines.append((x, y, n, couleur))
                x += n

    def draw(
            self, display: MlxDisplay, x: int, y: int,
            scale: int = 1, colors: ColorMap | None = None) -> None:
        """
                Draw the image, top-left corner at (x, y).

            colors replaces some colors of the file by others:
                {RED: 0xFFFFFF00} draws in yellow what is red in the file.
            A color that is not in the dict keeps its original value.
        """
        replace = colors or {}
        for dx, dy, n, color in self.lines:
            display.fill_rect(
                x + dx * scale, y + dy * scale,
                n * scale, scale, replace.get(color, color))


class XpmAlphabet():
    """All characters from one or more folders (e.g., 97.xpm for "a").

    If a character exists in multiple folders, the last one takes precedence.
    """

    def __init__(self, *files: str) -> None:
        self.letters: dict[str, XpmImage] = {}
        for file in files:
            for name in os.listdir(file):
                if name.endswith(".xpm"):
                    c = chr(int(name[:-4]))
                    self.letters[c] = XpmImage(os.path.join(file, name))
        self.height = max(i.height for i in self.letters.values())
        self.space = self.height // 3
        self.__colors: ColorMap = {}

    def set_colors(self, colors: ColorMap) -> None:
        """
            Change the default colors of this alphabet.

            Example: set_colors({RED: 0xFFFFFF00, BLUE: 0xFF000000})
            Colors that are not given keep their original value.
        """
        self.__colors = dict(colors)

    def reset_colors(self) -> None:
        """ Back to the original colors of the XPM files """
        self.__colors = {}

    def _image(self, c: str) -> XpmImage | None:
        """The character image, regardless of file case."""
        return (self.letters.get(c) or self.letters.get(c.lower())
                or self.letters.get(c.upper()))

    def length_texte(
            self, text: str, scale: int = 1,
            spacing: int = 0) -> int:
        total = 0
        for c in text.lower():
            image = self._image(c)
            total += (image.height if image else self.space) + spacing
        return max(0, total - spacing) * scale

    def write(
            self, display: MlxDisplay, x: int, y: int, text: str,
            scale: int = 1, spacing: int = 0,
            colors: ColorMap | None = None) -> None:
        """Writes the text, with the top-left corner at (x, y).

        Uppercase letters are displayed as lowercase. Negative spacing
        causes the letters to overlap, as in a logo.
        """
        palette = self.__colors if colors is None else colors
        for c in text.lower():
            image = self._image(c)
            if image is None:
                x += (self.space + spacing) * scale
                continue
            image.draw(display, x, y, scale, palette)
            x += (image.height + spacing) * scale
