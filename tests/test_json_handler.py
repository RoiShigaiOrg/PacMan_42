from pathlib import Path

import pytest

from Engine.FileManager.JsonHandler import JsonHandler, JsonHandlerError


def test_reads_every_json_type() -> None:
    text = '{"i": -3, "f": 0.1, "s": "a b", "l": [true, false, null], "o": {}}'
    assert JsonHandler.loads(text) == {
        "i": -3, "f": 0.1, "s": "a b", "l": [True, False, None], "o": {},
    }


def test_comments_are_ignored() -> None:
    text = (
        "# config of the game\n"
        "{\n"
        "    # whole line comment\n"
        '    "lives": 3,   # end of line comment\n'
        '    "dimension": [1920, 1080]\n'
        "}\n"
        "# last line"
    )
    assert JsonHandler.loads(text) == {"lives": 3, "dimension": [1920, 1080]}


def test_hash_inside_a_string_is_kept() -> None:
    assert JsonHandler.loads('{"color": "#FFC629"}') == {"color": "#FFC629"}


@pytest.mark.parametrize("text", [
    '{"a": 1,}', "[1, 2,]", "{a: 1}", '"open', "[1, 2", "[1] 2", "",
    "# only a comment", "-", "1.2.3", "tru", '"es\\"cape"',
])
def test_invalid_json_raises(text: str) -> None:
    with pytest.raises(JsonHandlerError):
        JsonHandler.loads(text)


def test_error_gives_the_line() -> None:
    with pytest.raises(JsonHandlerError, match="line 3"):
        JsonHandler.loads('{\n  "a": 1,\n  "b": ]\n}')


def test_writing_a_quote_is_refused() -> None:
    with pytest.raises(JsonHandlerError):
        JsonHandler.dumps({"login": 'le"o'})


def test_dumps_is_indented() -> None:
    data = {"login": "leo 42", "scores": [1, 2], "empty": {}}
    assert JsonHandler.dumps(data) == (
        '{\n'
        '    "login": "leo 42",\n'
        '    "scores": [\n'
        '        1,\n'
        '        2\n'
        '    ],\n'
        '    "empty": {}\n'
        '}'
    )


def test_file_round_trip(tmp_path: Path) -> None:
    data = {"scores": [{"login": "leo", "score": 1200, "time": 42},
                       {"login": None, "score": 0, "time": 0.5}]}
    path = tmp_path / "scores.json"
    JsonHandler.dump(data, path)
    assert JsonHandler.load(path) == data
