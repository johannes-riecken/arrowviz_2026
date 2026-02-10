from pathlib import Path

from arrowviz_2026.ast import Schematic, Shape, ShapeType
from arrowviz_2026.recognizers.shapes import recognize_schematic


def test_recognizes_regular_rounded_rectangle() -> None:
    fixture = Path("tests/data/00.png")

    result = recognize_schematic(fixture)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.ROUNDED,
            ),
        )
    )
