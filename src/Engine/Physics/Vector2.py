from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Vector2:
    """Represent a two-dimensional point or vector.

    Attributes:
        x: The horizontal component.
        y: The vertical component.
    """

    x: float
    y: float

    def __add__(self, other: Vector2) -> Vector2:
        """Return the component-wise sum of two vectors.

        Args:
            other: The vector to add.

        Returns:
            A new vector containing the sum of both operands.
        """
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        """Return the component-wise difference of two vectors.

        Args:
            other: The vector to subtract.

        Returns:
            A new vector containing the difference of both operands.
        """
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        """Return this vector multiplied by a scalar.

        Args:
            scalar: The numeric factor applied to both components.

        Returns:
            A new scaled vector.
        """
        return Vector2(self.x * scalar, self.y * scalar)

    def length_squared(self) -> float:
        """Return the squared Euclidean length of this vector.

        Returns:
            The squared vector length.
        """
        return self.x * self.x + self.y * self.y

    def length(self) -> float:
        """Return the Euclidean length of this vector.

        Returns:
            The vector length.
        """
        return math.sqrt(self.length_squared())

    def normalized(self) -> Vector2:
        """Return a unit-length copy of this vector.

        Returns:
            A normalized vector.

        Raises:
            ValueError: If the vector has zero length.
        """
        length = self.length()
        if length == 0:
            raise ValueError("Cannot normalize a zero-length vector")
        return Vector2(self.x / length, self.y / length)
