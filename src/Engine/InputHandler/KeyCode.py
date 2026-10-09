"""Standard X11 KeySym values returned by MLX key events.

MLX resolves an X11 key event to a KeySym before invoking the Python
callback.  These values are therefore symbols (for example ``z == 122``),
not physical X11 keycodes.
"""

# Printable ASCII keysyms.  Letter constants represent the unshifted keys;
# the corresponding uppercase symbols are available as KEY_UPPER_*.
KEY_SPACE = 0x20
KEY_EXCLAM = 0x21
KEY_QUOTE = 0x22
KEY_HASH = 0x23
KEY_DOLLAR = 0x24
KEY_PERCENT = 0x25
KEY_AMPERSAND = 0x26
KEY_APOSTROPHE = 0x27
KEY_LEFT_PAREN = 0x28
KEY_RIGHT_PAREN = 0x29
KEY_ASTERISK = 0x2A
KEY_PLUS = 0x2B
KEY_COMMA = 0x2C
KEY_MINUS = 0x2D
KEY_PERIOD = 0x2E
KEY_SLASH = 0x2F

KEY_0 = 0x30
KEY_1 = 0x31
KEY_2 = 0x32
KEY_3 = 0x33
KEY_4 = 0x34
KEY_5 = 0x35
KEY_6 = 0x36
KEY_7 = 0x37
KEY_8 = 0x38
KEY_9 = 0x39

KEY_COLON = 0x3A
KEY_SEMICOLON = 0x3B
KEY_LESS = 0x3C
KEY_EQUAL = 0x3D
KEY_GREATER = 0x3E
KEY_QUESTION = 0x3F
KEY_AT = 0x40

KEY_A = ord("a")
KEY_B = ord("b")
KEY_C = ord("c")
KEY_D = ord("d")
KEY_E = ord("e")
KEY_F = ord("f")
KEY_G = ord("g")
KEY_H = ord("h")
KEY_I = ord("i")
KEY_J = ord("j")
KEY_K = ord("k")
KEY_L = ord("l")
KEY_M = ord("m")
KEY_N = ord("n")
KEY_O = ord("o")
KEY_P = ord("p")
KEY_Q = ord("q")
KEY_R = ord("r")
KEY_S = ord("s")
KEY_T = ord("t")
KEY_U = ord("u")
KEY_V = ord("v")
KEY_W = ord("w")
KEY_X = ord("x")
KEY_Y = ord("y")
KEY_Z = ord("z")

KEY_UPPER_A = ord("A")
KEY_UPPER_B = ord("B")
KEY_UPPER_C = ord("C")
KEY_UPPER_D = ord("D")
KEY_UPPER_E = ord("E")
KEY_UPPER_F = ord("F")
KEY_UPPER_G = ord("G")
KEY_UPPER_H = ord("H")
KEY_UPPER_I = ord("I")
KEY_UPPER_J = ord("J")
KEY_UPPER_K = ord("K")
KEY_UPPER_L = ord("L")
KEY_UPPER_M = ord("M")
KEY_UPPER_N = ord("N")
KEY_UPPER_O = ord("O")
KEY_UPPER_P = ord("P")
KEY_UPPER_Q = ord("Q")
KEY_UPPER_R = ord("R")
KEY_UPPER_S = ord("S")
KEY_UPPER_T = ord("T")
KEY_UPPER_U = ord("U")
KEY_UPPER_V = ord("V")
KEY_UPPER_W = ord("W")
KEY_UPPER_X = ord("X")
KEY_UPPER_Y = ord("Y")
KEY_UPPER_Z = ord("Z")

KEY_LEFT_BRACKET = 0x5B
KEY_BACKSLASH = 0x5C
KEY_RIGHT_BRACKET = 0x5D
KEY_CARET = 0x5E
KEY_UNDERSCORE = 0x5F
KEY_GRAVE = 0x60
KEY_LEFT_BRACE = 0x7B
KEY_BAR = 0x7C
KEY_RIGHT_BRACE = 0x7D
KEY_TILDE = 0x7E

# Control, navigation, editing, and system keysyms.
KEY_BACKSPACE = 0xFF08
KEY_TAB = 0xFF09
KEY_LINEFEED = 0xFF0A
KEY_CLEAR = 0xFF0B
KEY_RETURN = 0xFF0D
KEY_PAUSE = 0xFF13
KEY_SCROLL_LOCK = 0xFF14
KEY_SYS_REQ = 0xFF15
KEY_ESCAPE = 0xFF1B
KEY_DELETE = 0xFFFF
KEY_HOME = 0xFF50
KEY_LEFT = 0xFF51
KEY_UP = 0xFF52
KEY_RIGHT = 0xFF53
KEY_DOWN = 0xFF54
KEY_PAGE_UP = 0xFF55
KEY_PAGE_DOWN = 0xFF56
KEY_END = 0xFF57
KEY_BEGIN = 0xFF58
KEY_SELECT = 0xFF60
KEY_PRINT = 0xFF61
KEY_EXECUTE = 0xFF62
KEY_INSERT = 0xFF63
KEY_UNDO = 0xFF65
KEY_REDO = 0xFF66
KEY_MENU = 0xFF67
KEY_FIND = 0xFF68
KEY_CANCEL = 0xFF69
KEY_HELP = 0xFF6A
KEY_BREAK = 0xFF6B
KEY_MODE_SWITCH = 0xFF7E
KEY_NUM_LOCK = 0xFF7F

# Function keys.
KEY_F1 = 0xFFBE
KEY_F2 = 0xFFBF
KEY_F3 = 0xFFC0
KEY_F4 = 0xFFC1
KEY_F5 = 0xFFC2
KEY_F6 = 0xFFC3
KEY_F7 = 0xFFC4
KEY_F8 = 0xFFC5
KEY_F9 = 0xFFC6
KEY_F10 = 0xFFC7
KEY_F11 = 0xFFC8
KEY_F12 = 0xFFC9
KEY_F13 = 0xFFCA
KEY_F14 = 0xFFCB
KEY_F15 = 0xFFCC
KEY_F16 = 0xFFCD
KEY_F17 = 0xFFCE
KEY_F18 = 0xFFCF
KEY_F19 = 0xFFD0
KEY_F20 = 0xFFD1
KEY_F21 = 0xFFD2
KEY_F22 = 0xFFD3
KEY_F23 = 0xFFD4
KEY_F24 = 0xFFD5
KEY_F25 = 0xFFD6
KEY_F26 = 0xFFD7
KEY_F27 = 0xFFD8
KEY_F28 = 0xFFD9
KEY_F29 = 0xFFDA
KEY_F30 = 0xFFDB
KEY_F31 = 0xFFDC
KEY_F32 = 0xFFDD
KEY_F33 = 0xFFDE
KEY_F34 = 0xFFDF
KEY_F35 = 0xFFE0

# Modifier keysyms.
KEY_SHIFT_LEFT = 0xFFE1
KEY_SHIFT_RIGHT = 0xFFE2
KEY_CONTROL_LEFT = 0xFFE3
KEY_CONTROL_RIGHT = 0xFFE4
KEY_CAPS_LOCK = 0xFFE5
KEY_SHIFT_LOCK = 0xFFE6
KEY_META_LEFT = 0xFFE7
KEY_META_RIGHT = 0xFFE8
KEY_ALT_LEFT = 0xFFE9
KEY_ALT_RIGHT = 0xFFEA
KEY_SUPER_LEFT = 0xFFEB
KEY_SUPER_RIGHT = 0xFFEC
KEY_HYPER_LEFT = 0xFFED
KEY_HYPER_RIGHT = 0xFFEE

# Keypad keysyms.
KEY_KP_SPACE = 0xFF80
KEY_KP_TAB = 0xFF89
KEY_KP_ENTER = 0xFF8D
KEY_KP_F1 = 0xFF91
KEY_KP_F2 = 0xFF92
KEY_KP_F3 = 0xFF93
KEY_KP_F4 = 0xFF94
KEY_KP_HOME = 0xFF95
KEY_KP_LEFT = 0xFF96
KEY_KP_UP = 0xFF97
KEY_KP_RIGHT = 0xFF98
KEY_KP_DOWN = 0xFF99
KEY_KP_PAGE_UP = 0xFF9A
KEY_KP_PAGE_DOWN = 0xFF9B
KEY_KP_END = 0xFF9C
KEY_KP_BEGIN = 0xFF9D
KEY_KP_INSERT = 0xFF9E
KEY_KP_DELETE = 0xFF9F
KEY_KP_EQUAL = 0xFFBD
KEY_KP_MULTIPLY = 0xFFAA
KEY_KP_ADD = 0xFFAB
KEY_KP_SEPARATOR = 0xFFAC
KEY_KP_SUBTRACT = 0xFFAD
KEY_KP_DECIMAL = 0xFFAE
KEY_KP_DIVIDE = 0xFFAF
KEY_KP_0 = 0xFFB0
KEY_KP_1 = 0xFFB1
KEY_KP_2 = 0xFFB2
KEY_KP_3 = 0xFFB3
KEY_KP_4 = 0xFFB4
KEY_KP_5 = 0xFFB5
KEY_KP_6 = 0xFFB6
KEY_KP_7 = 0xFFB7
KEY_KP_8 = 0xFFB8
KEY_KP_9 = 0xFFB9

# Common aliases used by applications.
KEY_ESC = KEY_ESCAPE
KEY_ENTER = KEY_RETURN
KEY_PAGEUP = KEY_PAGE_UP
KEY_PAGEDOWN = KEY_PAGE_DOWN
KEY_SHIFT = KEY_SHIFT_LEFT
KEY_CTRL = KEY_CONTROL_LEFT
KEY_ALT = KEY_ALT_LEFT


# Includes aliases intentionally: membership is useful for validating any
# named key constant accepted by InputHandler.
KEY_CODES = frozenset(
    value for name, value in globals().items()
    if (
        name.startswith("KEY_")
        and name != "KEY_CODES"
        and isinstance(value, int)
    )
)

__all__ = [
    name for name in globals()
    if name.startswith("KEY_")
]
