from Game.GameState import DEAD, NORMAL, SUPER, GameState


def test_new_game() -> None:
    stats = GameState(lives=3)
    assert (stats.scores, stats.lives, stats.level) == (0, 3, 1)
    assert stats.state == NORMAL
    assert not stats.is_over()


def test_ghost_combo_doubles() -> None:
    stats = GameState()
    stats.eat_Fruit()
    assert stats.state == SUPER
    assert [stats.eat_ghost() for _ in range(5)] == [200, 400, 800, 1600, 1600]


def test_extra_life_given_once() -> None:
    stats = GameState(lives=3)
    stats.add_point(10000)
    stats.add_point(10000)
    assert stats.lives == 4


def test_losing_every_life_ends_the_game() -> None:
    stats = GameState(lives=2)
    stats.lose_life()
    assert stats.state == DEAD
    stats.lose_life()
    assert stats.is_over()


def test_cheat_and_infinite_modes() -> None:
    stats = GameState(lives=1)
    stats.cheat_mod(True)
    stats.lose_life()
    assert stats.lives == 1 and stats.state == NORMAL
    stats.cheat_mod(False)
    stats.game_mod(True)
    stats.lose_life()
    assert stats.lives == 1 and stats.state == DEAD


def test_reset_keeps_modes() -> None:
    stats = GameState()
    stats.cheat_mod(True)
    stats.add_point(500)
    stats.reset_stats()
    assert stats.scores == 0 and stats.cheat
