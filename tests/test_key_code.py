from Engine.InputHandler import (
    KEY_CODES,
    KEY_A,
    KEY_DOWN,
    KEY_ENTER,
    KEY_ESCAPE,
    KEY_F1,
    KEY_F35,
    KEY_KP_0,
    KEY_LEFT,
    KEY_S,
    KEY_UPPER_A,
    KEY_Z,
)


def test_common_keysyms_match_mlx_values() -> None:
    assert KEY_A == 97
    assert KEY_Z == 122
    assert KEY_UPPER_A == 65
    assert KEY_LEFT == 0xFF51
    assert KEY_DOWN == 0xFF54
    assert KEY_ESCAPE == 0xFF1B
    assert KEY_KP_0 == 0xFFB0


def test_key_aliases_match_their_standard_symbols() -> None:
    assert KEY_ENTER == 0xFF0D
    assert KEY_S in KEY_CODES
    assert KEY_ENTER in KEY_CODES


def test_function_key_range_is_complete() -> None:
    function_keys = {
        KEY_F1 + offset for offset in range(KEY_F35 - KEY_F1 + 1)
    }
    assert function_keys <= KEY_CODES
