from .ArcadeMode import ArcadeMode
from .GameState import GameMode, GameState
from .InfinityMode import InfinityMode
from Engine.Engine import Engine

GAME_STATES: dict[GameMode, type[GameState]] = {
    GameMode.NORMAL: ArcadeMode,
    GameMode.INFINITE: InfinityMode,
}


class GameStateFactory:
    """
        GameStateFactory Class Definition

        Create the GameState of the chosen mode and keep the current one.
            The scene where the mode is chosen calls start(mode).
            The other scenes read factory.state.
        A NORMAL game exists from the start, so state is never empty.
    """

    def __init__(
            self, engine: Engine,
            mode: GameMode = GameMode.NORMAL) -> None:
        """ Init Method of the GameStateFactory Class """
        self.__engine = engine
        self.__state: GameState = GAME_STATES[mode](engine)

    def start(self, mode: GameMode) -> GameState:
        """ Create a new game of this mode """
        self.__state = GAME_STATES[mode](self.__engine)
        return self.__state

    @property
    def state(self) -> GameState:
        """ The game in progress """
        return self.__state
