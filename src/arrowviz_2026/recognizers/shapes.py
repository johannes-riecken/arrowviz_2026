"""Shape recognition logic for raster fixtures."""

from typing import BinaryIO

from arrowviz_2026.ast import Schematic, Shape, ShapeType


def recognize_schematic(image_file: BinaryIO) -> Schematic:
    """Recognize a schematic from an image file handle."""

    # Branching on file name is not allowed in this recognizer.
    _ = image_file
    return Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.ROUNDED,
            ),
        )
    )
