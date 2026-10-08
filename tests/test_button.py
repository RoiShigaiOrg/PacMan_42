from Game.UI.Button import Button


class FakeInput:
    mouse_position = (20, 30)

    def was_mouse_button_pressed(self, button: int) -> bool:
        return button == 1


def test_button_contains_positions_on_left_and_top_edges() -> None:
    button = Button(20, 30, 100, 40)

    assert button.contains((20, 30))
    assert button.contains((119, 69))
    assert not button.contains((120, 30))
    assert not button.contains((20, 70))


def test_button_update_reports_click_and_hover_state() -> None:
    button = Button(20, 30, 100, 40)

    assert button.update(FakeInput())
    assert button.hovered


def test_button_rejects_non_positive_dimensions() -> None:
    try:
        Button(0, 0, 0, 20)
    except ValueError:
        return
    raise AssertionError("expected invalid button dimensions to fail")
