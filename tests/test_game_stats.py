from Game.GameState import GameState, PacManState


def test_new_game() -> None:
    stats = GameState(lives=3)
    assert (stats.scores, stats.lives, stats.level) == (0, 3, 1)
    assert stats.state == PacManState.NORMAL
    assert not stats.is_over()


def test_ghost_combo_doubles() -> None:
    stats = GameState()
    stats.eat_Fruit()
    assert stats.state == PacManState.SUPER
    assert [stats.eat_ghost() for _ in range(5)] == [200, 400, 800, 1600, 1600]


def test_extra_life_given_once() -> None:
    stats = GameState(lives=3)
    stats.add_point(10000)
    stats.add_point(10000)
    assert stats.lives == 4


def test_losing_every_life_ends_the_game() -> None:
    stats = GameState(lives=2)
    stats.lose_life()
    assert stats.state == PacManState.DEAD
    stats.lose_life()
    assert stats.is_over()


def test_death_state_expires_after_shared_recovery_duration() -> None:
    stats = GameState()
    stats.lose_life()

    assert stats.state is PacManState.DEAD
    assert stats.death_recovery_remaining == 3.0

    stats.update_death_recovery(2.5)

    assert stats.state is PacManState.DEAD
    assert stats.death_recovery_remaining == 0.5

    stats.update_death_recovery(0.5)

    assert stats.state is PacManState.NORMAL
    assert stats.death_recovery_remaining == 0.0


def test_reset_keeps_modes() -> None:
    stats = GameState()
    stats.cheat_mod(True)
    stats.add_point(500)
    stats.reset_stats()
    assert stats.scores == 0 and stats.cheat
