from pathlib import Path

from arrowviz_2026.ast import Schematic, Shape, ShapeType
from arrowviz_2026.recognizers.shapes import recognize_schematic


def test_recognizes_regular_rounded_rectangle() -> None:
    fixture = Path("tests/data/00.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.ROUNDED,
            ),
        )
    )


def test_recognizes_wide_rounded_rectangle() -> None:
    fixture = Path("tests/data/01.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.ROUNDED,
            ),
        )
    )


def test_recognizes_regular_unrounded_rectangle() -> None:
    fixture = Path("tests/data/02.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.BOX,
            ),
        )
    )


def test_recognizes_wide_unrounded_rectangle() -> None:
    fixture = Path("tests/data/03.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.BOX,
            ),
        )
    )


def test_recognizes_circle_within_rounded_rectangle() -> None:
    fixture = Path("tests/data/05.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.ROUNDED,
                child=Shape(
                    id="shape-1",
                    shape_type=ShapeType.CIRCLE,
                ),
            ),
        )
    )


def test_recognizes_circle() -> None:
    fixture = Path("tests/data/04.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.CIRCLE,
            ),
        )
    )


def test_recognizes_dashed_rectangle() -> None:
    fixture = Path("tests/data/07.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.DASHED_BOX,
            ),
        )
    )


def test_recognizes_rounded_rectangle_within_circle() -> None:
    fixture = Path("tests/data/06.png")

    with fixture.open("rb") as image_file:
        result = recognize_schematic(image_file)

    assert result == Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=ShapeType.CIRCLE,
                child=Shape(
                    id="shape-1",
                    shape_type=ShapeType.ROUNDED,
                ),
            ),
        )
    )
