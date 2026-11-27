from pathlib import Path
from typing import Any, NoReturn


COMMENT: str = "#"
WHITESPACE: str = " \t\n\r"
DIGITS: str = "0123456789."

LITERALS: dict[str, Any] = {"true": True, "false": False, "null": None}


class JsonHandlerError(ValueError):
    """ Error raised when a JSON text cannot be read """

    def __init__(self, message: str,
                 text: str = "", position: int = 0) -> None:
        """ Init Method: add the line and the column to the message """
        self.line = text.count("\n", 0, position) + 1
        self.column = position - (text.rfind("\n", 0, position) + 1) + 1
        super().__init__(
            f"{message}: line {self.line} column {self.column}")


class JsonHandler():

    @staticmethod
    def load(path: Path | str) -> Any:
        """ Read a JSON file (comments allowed) """
        with open(path, "r", encoding="utf-8") as file:
            return JsonHandler.loads(file.read())

    @staticmethod
    def loads(text: str) -> Any:
        """ Read a JSON text (comments allowed) """
        parser = _Parser(text)
        value = parser.parse_value()
        parser.skip_blank()
        if not parser.at_end():
            parser.error("Extra data after the JSON value")
        return value

    @staticmethod
    def dump(data: Any, path: Path,  indent: int = 4) -> None:
        """ Write data to a JSON file """
        write = Writer
        with open(path, "w", encoding="utf-8") as file:
            file.write(write._write(data, indent, 0) + "\n")

    @staticmethod
    def dumps(data: Any, indent: int = 4) -> str:
        """ Data to a JSON text """
        write = Writer
        return write._write(data, indent, 0)


class _Parser():
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def error(self, message: str) -> NoReturn:
        raise JsonHandlerError(message, self.text, self.pos)

    def at_end(self) -> bool:
        return self.pos >= len(self.text)

    def expect(self, char: str) -> None:
        self.skip_blank()
        if self.peek() != char:
            self.error(f"Expecting '{char}'")
        self.pos += 1

    def peek(self) -> str:
        return "" if self.at_end() else self.text[self.pos]

    def parse_value(self) -> Any:
        """ Read any JSON value, depending on its first character """
        self.skip_blank()
        char = self.peek()
        if char == "{":
            return self.parse_obj()
        if char == "[":
            return self.parse_array()
        if char == '"':
            return self.parse_string()
        if char != "" and char in "-0123456789":
            return self.parse_number()
        for word, value in LITERALS.items():
            if self.text.startswith(word, self.pos):
                self.pos += len(word)
                return value
        self.error("Expecting a value")

    def parse_obj(self) -> dict[str, Any]:
        """parse dict value to format dict"""
        result: dict[str, Any] = {}
        self.pos += 1
        self.skip_blank()
        if self.peek() == "}":
            self.pos += 1
            return result
        while True:
            self.skip_blank()
            if self.peek() != '"':
                self.error("Expecting a property name in double quotes")
            key = self.parse_string()
            self.expect(":")
            result[key] = self.parse_value()
            self.skip_blank()
            if self.peek() == ",":
                self.pos += 1
                continue
            if self.peek() == "}":
                self.pos += 1
                return result
            self.error("Expecting ',' or '}'")

    def parse_array(self) -> list[Any]:
        """parse array value to format array"""
        result: list[Any] = []
        self.pos += 1
        self.skip_blank()
        if self.peek() == "]":
            self.pos += 1
            return result
        while True:
            result.append(self.parse_value())
            self.skip_blank()
            if self.peek() == ",":
                self.pos += 1
                continue
            if self.peek() == "]":
                self.pos += 1
                return result
            self.error("Expecting ',' or ']'")

    def parse_string(self) -> str:
        """parse string value to format string"""
        self.pos += 1
        start = self.pos
        while True:
            if self.at_end():
                self.error("Unterminated string")
            char = self.peek()
            if char == '"':
                self.pos += 1
                return self.text[start:self.pos - 1]
            if char == "\\":
                self.error("Escapes are not supported")
            if char == "\n":
                self.error("Unterminated string")
            self.pos += 1

    def parse_number(self) -> int | float:
        """parse number value to format number"""
        start = self.pos
        if self.peek() == "-":
            self.pos += 1
        while self.peek() != "" and self.peek() in DIGITS:
            self.pos += 1
        number = self.text[start:self.pos]
        try:
            return float(number) if "." in number else int(number)
        except ValueError:
            self.pos = start
            self.error(f"Invalid number '{number}'")

    def skip_blank(self) -> None:
        """ Skip the whitespace and the comments """
        while not self.at_end():
            char = self.text[self.pos]
            if char in WHITESPACE:
                self.pos += 1
            elif char == COMMENT:
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end == -1 else end
            else:
                return


class Writer:

    @staticmethod
    def _write_string(text: str) -> str:
        """ A Python string as a JSON string """
        if '"' in text or "\\" in text or "\n" in text:
            raise JsonHandlerError(f"Cannot write the string {text!r}")
        return f'"{text}"'

    @staticmethod
    def _write(data: Any, indent: int | None, level: int) -> str:
        """ Any supported value as JSON text, `level` = nesting depth """
        if data is None:
            return "null"
        if data is True:
            return "true"
        if data is False:
            return "false"
        if isinstance(data, (int, float)):
            return repr(data)
        if isinstance(data, str):
            return Writer._write_string(data)
        if isinstance(data, dict):
            items = [f"{Writer._write_string(str(key))}: "
                     f"{Writer._write(value, indent, level + 1)}"
                     for key, value in data.items()]
            return Writer._join(items, "{", "}", indent, level)
        if isinstance(data, (list, tuple)):
            items = [Writer._write(value, indent, level + 1) for value in data]
            return Writer._join(items, "[", "]", indent, level)
        raise JsonHandlerError(
            f"{type(data).__name__} cannot be written in JSON", )

    @staticmethod
    def _join(items: list[str], opening: str, closing: str,
              indent: int | None, level: int) -> str:
        """ Put the items between the brackets, on one line or indented """
        if not items:
            return opening + closing
        if indent is None:
            return opening + ", ".join(items) + closing
        inner = "\n" + " " * (indent * (level + 1))
        outer = "\n" + " " * (indent * level)
        return opening + inner + ("," + inner).join(items) + outer + closing
