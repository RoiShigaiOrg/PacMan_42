from Engine.Animation import Animation, AnimationHandler
from Engine.InputHandler.KeyCode import KEY_D, KEY_Q, KEY_S, KEY_Z
from Engine.Physics import PhysicsEngine
from Engine.Sprite import Sprite, SpriteFrame
from Game.MapGeneration.Cell import Cell
from Game.MapGeneration.MapGeneration import Map
from Game.Player.Player import Player
from Game.Scenes.MapScene import MapScene


class FakeDisplay:
    pass


class PixelDisplay:
    def __init__(self) -> None:
        self.pixels: set[tuple[int, int]] = set()

    def draw_pixel(self, x: int, y: int, _color: int) -> None:
        self.pixels.add((x, y))


class FakeInput:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self.pressed = pressed or set()

    def was_key_pressed(self, key: int) -> bool:
        return key in self.pressed

    def is_key_down(self, _key: int) -> bool:
        return False


def make_map(blocked: set[tuple[int, int]] | None = None) -> Map:
    blocked = blocked or set()
    actual_map = Map.__new__(Map)
    actual_map.width = 5
    actual_map.height = 5
    actual_map.grid = [
        [
            Cell((column, row), (column, row) not in blocked)
            for column in range(actual_map.width)
        ]
        for row in range(actual_map.height)
    ]
    actual_map.set_colliders(10, 10, 50, 50)
    return actual_map


def make_animation_handler() -> AnimationHandler:
    colors = {
        "right": 0xFFFF0000,
        "left": 0xFF00FF00,
        "up": 0xFF0000FF,
        "down": 0xFFFFFF00,
    }
    animations = {
        direction: Animation((
            SpriteFrame(Sprite((1, 1), [[color]]), 100),
            SpriteFrame(Sprite((1, 1), [[color ^ 0x00000001]]), 100),
        ))
        for direction, color in colors.items()
    }
    return AnimationHandler(animations)


def make_player(
        blocked: set[tuple[int, int]] | None = None,
) -> tuple[Player, Map]:
    player = Player(
        movement_speed=120.0,
        animation_handler=make_animation_handler(),
    )
    actual_map = make_map(blocked)
    player.InitPlayer(FakeDisplay(), actual_map)
    return player, actual_map


def test_player_starts_with_right_animation_when_stationary() -> None:
    player, _actual_map = make_player()

    assert player.direction.length_squared() == 0
    assert player.visual_state == ("right", 0)


def test_player_switches_animation_when_actual_direction_changes() -> None:
    key_to_animation = (
        (KEY_D, "right"),
        (KEY_Q, "left"),
        (KEY_Z, "up"),
        (KEY_S, "down"),
    )

    for key, expected_animation in key_to_animation:
        player, actual_map = make_player()
        player.update_direction(
            FakeInput({key}), actual_map, PhysicsEngine(), 0.01
        )
        assert player.visual_state == (expected_animation, 0)


def test_player_keeps_animation_until_buffered_turn_is_reached() -> None:
    player, actual_map = make_player()
    physics = PhysicsEngine()

    player.update_direction(
        FakeInput({KEY_D}), actual_map, physics, 0.025
    )
    player.update_direction(
        FakeInput({KEY_Z}), actual_map, physics, 0.025
    )
    visual_state = player.visual_state
    assert visual_state is not None and visual_state[0] == "right"

    player.update_direction(FakeInput(), actual_map, physics, 0.1)

    assert player.direction.y < 0
    visual_state = player.visual_state
    assert visual_state is not None and visual_state[0] == "up"


def test_blocked_direction_falls_back_to_right_animation() -> None:
    # The Player starts in cell (2, 2), so (1, 2) blocks a left turn.
    player, actual_map = make_player({(1, 2)})

    player.update_direction(
        FakeInput({KEY_Q}), actual_map, PhysicsEngine(), 0.01
    )

    assert player.direction.length_squared() == 0
    assert player.visual_state == ("right", 0)


def test_player_sprite_is_scaled_to_square_cell_display_pixels() -> None:
    player, _actual_map = make_player()
    display = PixelDisplay()

    player.draw(display)

    assert len(display.pixels) == 100
    assert min(x for x, _y in display.pixels) == 30
    assert max(x for x, _y in display.pixels) == 39
    assert min(y for _x, y in display.pixels) == 30
    assert max(y for _x, y in display.pixels) == 39


def test_idle_animation_frame_change_invalidates_player_region() -> None:
    player, actual_map = make_player()
    scene = MapScene.__new__(MapScene)
    scene.map = actual_map
    scene._MapScene__player = player
    scene._MapScene__physics = PhysicsEngine()
    scene._MapScene__dirty_region = None

    scene._MapScene__update_player(FakeInput(), 0.1)

    assert player.position == (30, 30)
    assert player.visual_state == ("right", 1)
    assert scene._MapScene__dirty_region == (30, 30, 10, 10)
