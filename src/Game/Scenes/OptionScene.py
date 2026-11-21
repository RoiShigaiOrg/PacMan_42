from Engine.SceneManager import Scene
from Engine.Engine import Engine
from Engine.Graphics import MlxDisplay
from Engine.InputHandler import InputHandler
from Engine.InputHandler.KeyCode import KEY_ENTER, KEY_ESC

from ..UI.Component import Component
from ..UI.Selector import Selector
from ..UI.Clickable import Clickable
from ..UI.InputBar import InputBar
from typing import List

BLACK: int = 0xFF000000
OPTION_SIZE: tuple[float, float] = (0.3, 0.05)
OPTION_POSITIONS: tuple[tuple[float, float], ...] = (
    (0.35, 0.4),
    (0.35, 0.45),
    (0.35, 0.5),
)
INPUT_SIZE: tuple[float, float] = (0.58, 0.05)
INPUT_POSITION: tuple[float, float] = (0.21, 0.7)


class OptionScene(Scene):
    """
    Option Scene Class Definition

    The Option will be interface for the User to setup some
        configuration within the Game. Like screen resolution and
        keyBindings.
    """

    def __init__(
            self,
            engine: Engine,
            display: MlxDisplay) -> None:
        """ Init Method of the OptionScene. """
        super().__init__()
        self.__engine: Engine = engine
        self.__display: MlxDisplay = display
        self.__static_layer: bytes | None = None
        self.__config_option: List[Component] = [
            Selector(
                engine,
                0.3, 0.05,
                self.__engine.get_config_key("available_dimension"),
                str(self.__engine.get_config_key("dimension")[1])
            ),
            Selector(
                engine,
                0.3, 0.05,
                ["UP", "DOWN", "LEFT", "RIGHT"]
            ),
            Clickable(0.3, 0.05)
        ]
        self.__input: InputBar = InputBar(*INPUT_SIZE)
        self.__input_target: str | None = None
        self.__config_option[0].add_label("RESOLUTION")
        self.__config_option[1].add_label("MOVEMENT")
        self.__config_option[2].add_label("DEBUG MODE")
        self.__select_iter: int = 0
        self.__config_option[self.__select_iter].select()

    def update(self,
               delta_time: float,
               input_handler: InputHandler) -> None:
        """ Update the Screen using the current frame's input state. """
        if self.__input.key_capture_active:
            if input_handler.was_key_pressed(KEY_ESC):
                self.__input.end_key_capture()
                self.__input_target = None
                self.__mark_input_dirty()
                return
            keycode = self.__input.capture_key(input_handler)
            if keycode is not None and self.__input_target is not None:
                self.__engine.set_config_key(self.__input_target, keycode)
                self.__input.end_key_capture()
                self.__input_target = None
                self.__mark_input_dirty()
            return

        if input_handler.was_key_pressed(
                self.__engine.get_config_key("UP")):
            self.__process_up()
            return
        if input_handler.was_key_pressed(
                self.__engine.get_config_key("DOWN")):
            self.__process_down()
            return
        if input_handler.was_key_pressed(KEY_ENTER):
            self.__process_enter()
            return
        if input_handler.was_key_pressed(KEY_ESC):
            debug_option = self.__config_option[2]
            if isinstance(debug_option, Clickable):
                self.__engine.set_config_key(
                    "debug", debug_option.read_value()
                )
            self.__engine.scene_manager.last_scene()
            return
        self.__update_selected(input_handler)

    def render(self) -> None:
        """Restore and redraw only controls whose state has changed."""
        if not self.dirty_regions or self.__static_layer is None:
            return

        dirty_regions = self.restore_dirty_regions(
            self.__display, self.__static_layer
        )
        for index, (component, pos) in enumerate(zip(
                self.__config_option, self.__option_positions())):
            region = self.__option_region(index)
            if self.intersects_regions(region, dirty_regions):
                component.render(self.__display, pos)

        input_pos = self.__input_position()
        if (
                self.__input.key_capture_active
                and self.intersects_regions(
                    self.__input_region(), dirty_regions
                )
        ):
            self.__input.render(self.__display, input_pos)

        self.__display.render()
        for component, pos in zip(
                self.__config_option, self.__option_positions()):
            component.render_label(self.__display, pos)
        if self.__input.key_capture_active:
            self.__input.render_text(self.__display, input_pos)
        self.clear_dirty_regions()

    def render_on_change(self) -> None:
        """Build and snapshot the clean options layer on scene entry."""
        self.__display.clear_window()
        self.__display.clear(BLACK)
        for component, pos in zip(
                self.__config_option, self.__option_positions()):
            component.render(self.__display, pos)
        self.__static_layer = self.__display.snapshot()
        self.mark_full_screen_dirty(self.__display)

    def on_exit(self) -> None:
        """Apply the selected resolution when leaving the options menu."""
        self.__apply_resolution()

    def on_resolution_changed(self) -> None:
        """Discard size-dependent cached content before the menu is redrawn."""
        self.__static_layer = None
        self.clear_dirty_regions()

    def __update_selected(self, input_handler: InputHandler) -> None:
        """ Update the selected Component in the Option Scene."""
        component = self.__config_option[self.__select_iter]
        previous_value = (
            component.read_value()
            if isinstance(component, Selector)
            else None
        )
        component.update(input_handler)
        if (
                isinstance(component, Selector)
                and component.read_value() != previous_value
        ):
            self.__mark_option_dirty(self.__select_iter)

    def __process_up(self) -> None:
        """ Process the Up key for the Option Scene. """
        previous = self.__select_iter
        self.__config_option[self.__select_iter].unselect()
        self.__select_iter = self.__select_iter - 1
        if self.__select_iter < 0:
            self.__select_iter = len(self.__config_option) - 1
        self.__config_option[self.__select_iter].select()
        self.__mark_option_dirty(previous, self.__select_iter)

    def __process_down(self) -> None:
        """ Process the Down key for the Option Scene. """
        previous = self.__select_iter
        self.__config_option[self.__select_iter].unselect()
        self.__select_iter = (self.__select_iter + 1) % len(
                self.__config_option
            )
        self.__config_option[self.__select_iter].select()
        self.__mark_option_dirty(previous, self.__select_iter)

    def __process_enter(self) -> None:
        """ Process the Enter Key for the Option Scene """
        if self.__select_iter == 0:
            self.__apply_resolution()
            self.__mark_option_dirty(self.__select_iter)
        elif self.__select_iter == 1:
            movement_option = self.__config_option[1]
            if isinstance(movement_option, Selector):
                self.__input_target = str(movement_option.read_value())
                self.__input.begin_key_capture(
                    self.__input_target,
                    self.__engine.get_config_key(self.__input_target),
                )
                self.__mark_input_dirty()
        else:
            self.__config_option[self.__select_iter].callback()
            self.__mark_option_dirty(self.__select_iter)

    def __apply_resolution(self) -> None:
        """Apply the selected available resolution through the engine."""
        resolution_option = self.__config_option[0]
        if not isinstance(resolution_option, Selector):
            return
        available = self.__engine.get_config_key("available_dimension")
        key = str(resolution_option.read_value())
        size = available[key]
        self.__engine.apply_resolution((int(size[0]), int(size[1])))

    def __option_positions(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (
                self.__display.relative_width(x),
                self.__display.relative_height(y),
            )
            for x, y in OPTION_POSITIONS
        )

    def __option_region(self, index: int) -> tuple[int, int, int, int]:
        x, y = self.__option_positions()[index]
        return (
            x,
            y,
            max(1, self.__display.relative_width(OPTION_SIZE[0])),
            max(1, self.__display.relative_height(OPTION_SIZE[1])),
        )

    def __input_position(self) -> tuple[int, int]:
        return (
            self.__display.relative_width(INPUT_POSITION[0]),
            self.__display.relative_height(INPUT_POSITION[1]),
        )

    def __input_region(self) -> tuple[int, int, int, int]:
        x, y = self.__input_position()
        return (
            x,
            y,
            max(1, self.__display.relative_width(INPUT_SIZE[0])),
            max(1, self.__display.relative_height(INPUT_SIZE[1])),
        )

    def __mark_option_dirty(self, *indices: int) -> None:
        self.mark_dirty(*(self.__option_region(index) for index in indices))

    def __mark_input_dirty(self) -> None:
        self.mark_dirty(self.__input_region())
