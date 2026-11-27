from Engine.FileManager.JsonHandler import JsonHandler
from pathlib import Path
from typing import Any, Literal, cast

from ...Sprite.SpriteMetadata import AsepriteMetadata
from ...Sprite.SpriteSheet import SpriteSheet
from .Loader import Loader


class SpriteLoader(Loader):
    """
    Load a PNG image into an MLX-independent SpriteSheet Class.
    The Sprite Loader take one sprite_file Path, which is a SpriteSheet
        containing the differents sprite and a sprite_json Path,
        containing the different coordonates, size and metadata of
        the spritesheet.
    """

    def __init__(
        self,
        sprite_file: Path,
        mlx_session: Any,
        mlx_ptr: Any,
        sprite_json: Path | None = None,
    ) -> None:
        """Create a loader using the active MLX session and pointer."""
        if sprite_file is None:
            raise ValueError("SpriteLoader: File is None")
        if mlx_session is None or mlx_ptr is None:
            raise ValueError("SpriteLoader requires an active MLX session")

        self.__file: Path = sprite_file
        self.__json: Path | None = sprite_json
        self.__session = mlx_session
        self.__mlx_ptr = mlx_ptr

    def load(self) -> SpriteSheet:
        """Load the PNG and copy its pixels into a SpriteSheet Class."""
        pixels = self.__extract_pixel()
        metadata: AsepriteMetadata | None = None

        if self.__json is not None:
            metadata = self.__extract_metadata()
            if Path(metadata.meta.image).name != self.__file.name:
                raise ValueError(
                    "spritesheet image path does not match metadata image: "
                    f"{metadata.meta.image!r}"
                )

        return SpriteSheet(pixels, metadata)

    def __extract_metadata(self) -> AsepriteMetadata:
        """
        Extract the metadata from the json file associated with
            this spritesheet.
        """
        if self.__json is None:
            raise RuntimeError("No metadata JSON file was provided")
        data = JsonHandler.load(self.__json)
        return cast(AsepriteMetadata, AsepriteMetadata.model_validate(data))

    def __extract_pixel(self) -> list[list[int]]:
        """
        Extract the pixel from an Image and return a Matrix of
            the corresponding pixels value
        """
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
            return pixel_rows
        finally:
            self.__session.mlx_destroy_image(self.__mlx_ptr, image)

    def store(self) -> None:
        """SpriteLoader is read-only and cannot store spritesheets."""
        raise NotImplementedError("SpriteLoader does not support storing")
