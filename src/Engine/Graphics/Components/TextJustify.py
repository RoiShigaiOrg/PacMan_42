"""Text placement options shared by graphic components."""

TEXT_CENTER: int = 0
TEXT_END: int = 1
TEXT_START: int = 2

TEXT_CENTER_LOW: int = 3
TEXT_END_LOW: int = 4
TEXT_START_LOW: int = 5

TEXT_CENTER_HIGH: int = 6
TEXT_END_HIGH: int = 7
TEXT_START_HIGH: int = 8

VALID_TEXT_JUSTIFICATIONS = frozenset({
    TEXT_CENTER,
    TEXT_END,
    TEXT_START,
    TEXT_CENTER_LOW,
    TEXT_END_LOW,
    TEXT_START_LOW,
    TEXT_CENTER_HIGH,
    TEXT_END_HIGH,
    TEXT_START_HIGH,
})
