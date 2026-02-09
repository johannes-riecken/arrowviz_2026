"""AST models for parsed schematics."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Sequence


class ShapeType(str, Enum):
    """Supported schematic shape types."""

    BOX = "box"
    ROUNDED = "rounded"
    CIRCLE = "circle"
    DASHED_BOX = "dashed_box"


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Shape:
    """A drawable shape in a schematic."""

    id: str
    shape_type: ShapeType
    label: str | None = None
    child: Shape | None = None


@dataclass(frozen=True)
class Connection:
    """A directed connection between shapes."""

    source_id: str
    target_id: str
    label: str | None = None
    waypoints: Sequence[Point] = field(default_factory=tuple)


@dataclass(frozen=True)
class Schematic:
    """Root node for a parsed schematic."""

    shapes: Sequence[Shape] = field(default_factory=tuple)
    connections: Sequence[Connection] = field(default_factory=tuple)

    def shape_ids(self) -> Iterable[str]:
        return (shape.id for shape in self.shapes)


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned bounding box for CST nodes."""

    top_left: Point
    bottom_right: Point


@dataclass(frozen=True)
class CstShape:
    """Concrete syntax shape including layout metadata."""

    id: str
    shape_type: ShapeType
    bounds: BoundingBox
    label: str | None = None
    child: CstShape | None = None


@dataclass(frozen=True)
class CstSchematic:
    """Concrete syntax tree for a schematic."""

    shapes: Sequence[CstShape] = field(default_factory=tuple)
    connections: Sequence[Connection] = field(default_factory=tuple)
