from pathlib import Path
from typing import Any, Literal

from ...Sprite.SpriteSheet import SpriteSheet
from .Loader import Loader


class SpriteLoader(Loader):
    """Load a PNG image into an MLX-independent SpriteSheet Class."""

    def __init__(
        self,
        sprite_file: Path,
        mlx_session: Any,
        mlx_ptr: Any,
    ) -> None:
        """Create a loader using the active MLX session and pointer."""
        if sprite_file is None:
            raise ValueError("SpriteLoader: File is None")
        if mlx_session is None or mlx_ptr is None:
            raise ValueError("SpriteLoader requires an active MLX session")

        self.__file = sprite_file
        self.__session = mlx_session
        self.__mlx_ptr = mlx_ptr

    def load(self) -> SpriteSheet:
        """Load the PNG and copy its pixels into a SpriteSheet Class."""
        image, sheet_width, sheet_height = (
            self.__session.mlx_png_file_to_image(
                self.__mlx_ptr,
                str(self.__file),
            )
        )
        if not image:
            raise RuntimeError(f"Could not load spritesheet: {self.__file}")

        try:
            pixels, bits_per_pixel, stride, image_format = (
                self.__session.mlx_get_data_addr(image)
            )
            if bits_per_pixel != 32:
                raise RuntimeError(
                    f"Expected 32-bit pixels, got: {bits_per_pixel}"
                )
            if sheet_width <= 0 or sheet_height <= 0:
                raise RuntimeError(
                    "MLX returned invalid spritesheet dimensions"
                )
            if image_format not in (0, 1):
                raise RuntimeError(
                    f"Unsupported MLX image format: {image_format}"
                )
            if stride < sheet_width * 4:
                raise RuntimeError(
                    "MLX image stride is smaller than its pixel row"
                )
            if len(pixels) < stride * sheet_height:
                raise RuntimeError(
                    "MLX image buffer is smaller than its dimensions"
                )

            byte_order: Literal["little", "big"] = (
                "little" if image_format == 0 else "big"
            )
            pixel_rows: list[list[int]] = []
            for y in range(sheet_height):
                row: list[int] = []
                for x in range(sheet_width):
                    offset = y * stride + x * 4
                    row.append(
                        int.from_bytes(
                            pixels[offset:offset + 4],
                            byte_order,
                        )
                    )
                pixel_rows.append(row)

            return SpriteSheet(pixel_rows)
        finally:
            self.__session.mlx_destroy_image(self.__mlx_ptr, image)

    def store(self) -> None:
        """SpriteLoader is read-only and cannot store spritesheets."""
        raise NotImplementedError("SpriteLoader does not support storing")
