from typing import Any


class InputHandler:
    """
        InputHandler Class Definition

        The InputHandler class is the service running by the
            Engine to register all the input registered on the
            MlxWindow
    """

    def __init__(
            self,
            session: Any,
            mlx_ptr: Any,
            window_ptr: Any) -> None:
        """ Init method for the InputHandler Class """
        self.__session = session
        self.__mlx_ptr = mlx_ptr
        self.__window = window_ptr
        self.__keys_down: set[int] = set()
        self.__keys_pressed: set[int] = set()
        self.__keys_released: set[int] = set()
        self.__mouse_position = (0, 0)
        self.__mouse_buttons_down: set[int] = set()
        self.__mouse_buttons_pressed: set[int] = set()
        self.__mouse_buttons_released: set[int] = set()

    def register_hooks(self) -> None:
        """Register all input events on the owned MLX window."""
        self.__session.mlx_hook(
            self.__window, 2, 1, self.__on_key_press, None
        )
        self.__session.mlx_hook(
            self.__window, 3, 2, self.__on_key_release, None
        )
        self.__session.mlx_hook(
            self.__window, 4, 4, self.__on_mouse_press, None
        )
        self.__session.mlx_hook(
            self.__window, 5, 8, self.__on_mouse_release, None
        )
        self.__session.mlx_hook(
            self.__window, 6, 64, self.__on_mouse_move, None
        )
        self.__session.mlx_hook(
            self.__window, 33, 0, self.__on_close, None
        )

    def __on_key_press(self, key: int, _: object) -> None:
        self.__keys_down.add(key)
        self.__keys_pressed.add(key)

    def __on_key_release(self, key: int, _: object) -> None:
        self.__keys_down.discard(key)
        self.__keys_released.add(key)

    def __on_mouse_press(
            self, button: int, x: int, y: int, _: object
    ) -> None:
        self.__mouse_position = (x, y)
        self.__mouse_buttons_down.add(button)
        self.__mouse_buttons_pressed.add(button)

    def __on_mouse_release(
            self, button: int, x: int, y: int, _: object
    ) -> None:
        self.__mouse_position = (x, y)
        self.__mouse_buttons_down.discard(button)
        self.__mouse_buttons_released.add(button)

    def __on_mouse_move(self, x: int, y: int, _: object) -> None:
        self.__mouse_position = (x, y)

    def __on_close(self, _: object) -> None:
        self.__session.mlx_loop_exit(self.__mlx_ptr)

    def is_key_down(self, key: int) -> bool:
        """Return whether a key is currently held."""
        return key in self.__keys_down

    def was_key_pressed(self, key: int) -> bool:
        """Return whether a key was pressed during the current frame."""
        return key in self.__keys_pressed

    def was_key_released(self, key: int) -> bool:
        """Return whether a key was released during the current frame."""
        return key in self.__keys_released

    @property
    def mouse_position(self) -> tuple[int, int]:
        """Return the latest cursor position in window coordinates."""
        return self.__mouse_position

    def is_mouse_button_down(self, button: int) -> bool:
        """Return whether a mouse button is currently held."""
        return button in self.__mouse_buttons_down

    def was_mouse_button_pressed(self, button: int) -> bool:
        """Return whether a mouse button was pressed during this frame."""
        return button in self.__mouse_buttons_pressed

    def was_mouse_button_released(self, button: int) -> bool:
        """Return whether a mouse button was released during this frame."""
        return button in self.__mouse_buttons_released

    def end_frame(self) -> None:
        """Clear input events that are only meaningful for one frame."""
        self.__keys_pressed.clear()
        self.__keys_released.clear()
        self.__mouse_buttons_pressed.clear()
        self.__mouse_buttons_released.clear()

    def debug_inputs(self) -> None:
        """ Debug method to display the state of the Input Handler """
        print(f"key_down: {self.__keys_down} - key_release: {self.__keys_released}")
