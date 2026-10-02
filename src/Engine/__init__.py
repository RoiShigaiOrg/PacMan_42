from .Graphics import MlxScreen

__all__ = [
        "MlxScreen",
        "Engine",
        ]


def __getattr__(name: str):
    """Load the unfinished high-level engine only when it is requested."""
    if name == "Engine":
        from .Engine import Engine

        return Engine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
