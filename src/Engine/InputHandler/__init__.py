from .InputHandler import InputHandler
from . import KeyCode as _key_code

_key_names = _key_code.__all__
globals().update({name: getattr(_key_code, name) for name in _key_names})

__all__ = [
        "InputHandler",
        *_key_names,
        ]
