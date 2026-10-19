from .Collision import Collision
from .CollisionDetection import detect_collision
from .Collider import Collider
from .Vector2 import Vector2


class PhysicsEngine:
    """
        Physic Engine Class Definition

        The PhysicsEngine is the part of the Engine that will
            compute all the mouvement velocity and checks for the
            Collision between multiple objects.
    """

    def handle_collision(
            self, first: Collider, second: Collider
    ) -> Collision | None:
        """Detect overlap between two physics colliders.

        Args:
            first: The first collider participating in the query.
            second: The second collider participating in the query.

        Returns:
            A collision manifold when the colliders overlap, or ``None``
            when they do not. This method detects collisions only; it does
            not change either collider's position or velocity.
        """
        return detect_collision(first, second)

    def can_move(
            self, collider: Collider, delta: Vector2, *others: Collider
    ) -> bool:
        """Check whether a collider could move by a delta without colliding.

        The collider is temporarily placed at the candidate position to run
        the collision test against every other collider, then its position
        is restored. This method never leaves the collider moved; the caller
        applies the movement when the answer is ``True``.

        Args:
            collider: The collider that wants to move.
            delta: The candidate displacement from its current position.
            others: Colliders the movement must not overlap.

        Returns:
            ``True`` when the displacement causes no collision with any of
            the other colliders, ``False`` otherwise.
        """
        original = collider.position
        collider.position = original + delta
        blocked = any(
            detect_collision(collider, other) is not None for other in others
        )
        collider.position = original
        return not blocked
