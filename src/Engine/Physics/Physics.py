from .Collision import Collision
from .CollisionDetection import detect_collision
from .Collider import Collider


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
