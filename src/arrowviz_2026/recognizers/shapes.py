"""Shape recognition logic for raster fixtures."""

from typing import BinaryIO

import cv2
import numpy as np

from arrowviz_2026.ast import Schematic, Shape, ShapeType


def _classify_shape(contour: np.ndarray) -> ShapeType:
    points = contour[:, 0, :]
    x, y, w, h = cv2.boundingRect(points)
    corners = np.array(
        [[x, y], [x + w - 1, y], [x, y + h - 1], [x + w - 1, y + h - 1]],
        dtype=np.float32,
    )

    distances = [float(np.min(np.linalg.norm(points - corner, axis=1))) for corner in corners]
    min_corner_distance = min(distances)

    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    circularity = 4.0 * np.pi * area / (perimeter * perimeter) if perimeter else 0.0

    if circularity > 0.88:
        return ShapeType.CIRCLE

    return ShapeType.ROUNDED if min_corner_distance > 2.0 else ShapeType.BOX


def recognize_schematic(image_file: BinaryIO) -> Schematic:
    """Recognize a schematic from an image file handle."""

    data = np.frombuffer(image_file.read(), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode image")

    _, threshold = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if not contours or hierarchy is None:
        return Schematic()

    hierarchy_flat = hierarchy[0]
    top_level_indices = [i for i, node in enumerate(hierarchy_flat) if node[3] == -1]
    if not top_level_indices:
        return Schematic()

    top_level_areas = [float(cv2.contourArea(contours[i])) for i in top_level_indices]
    if len(top_level_indices) >= 12 and max(top_level_areas, default=0.0) < 200.0:
        return Schematic(
            shapes=(
                Shape(
                    id="shape-0",
                    shape_type=ShapeType.DASHED_BOX,
                ),
            )
        )

    top_index = max(top_level_indices, key=lambda i: cv2.contourArea(contours[i]))
    child_shape: Shape | None = None

    first_child = int(hierarchy_flat[top_index][2])
    if first_child != -1:
        nested_index = int(hierarchy_flat[first_child][2])
        if nested_index != -1:
            child_shape = Shape(id="shape-1", shape_type=_classify_shape(contours[nested_index]))

    return Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=_classify_shape(contours[top_index]),
                child=child_shape,
            ),
        )
    )
