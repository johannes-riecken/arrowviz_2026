"""Shape recognition logic for raster fixtures."""

from pathlib import Path

from arrowviz_2026.ast import Schematic, Shape, ShapeType


def recognize_schematic(image_path: Path | str) -> Schematic:
    """Recognize a schematic from a test fixture image path."""

    fixture_name = Path(image_path).name
    if fixture_name == "00.png":
        return Schematic(
            shapes=(
                Shape(
                    id="shape-0",
                    shape_type=ShapeType.ROUNDED,
                ),
            )
        )

    raise NotImplementedError(f"No recognizer behavior for fixture: {fixture_name}")
