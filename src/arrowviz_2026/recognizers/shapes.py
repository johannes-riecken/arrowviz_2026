"""Shape recognition logic for raster fixtures."""

from typing import BinaryIO

import cv2
import numpy as np

from arrowviz_2026.ast import Schematic, Shape, ShapeType


def recognize_schematic(image_file: BinaryIO) -> Schematic:
    """Recognize a schematic from an image file handle."""

    data = np.frombuffer(image_file.read(), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode image")

    _, threshold = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return Schematic()

    contour = max(contours, key=cv2.contourArea)[:, 0, :]
    x, y, w, h = cv2.boundingRect(contour)
    corners = np.array(
        [[x, y], [x + w - 1, y], [x, y + h - 1], [x + w - 1, y + h - 1]],
        dtype=np.float32,
    )

    distances = [float(np.min(np.linalg.norm(contour - corner, axis=1))) for corner in corners]
    min_corner_distance = min(distances)

    area = float(cv2.contourArea(contour.reshape(-1, 1, 2)))
    perimeter = float(cv2.arcLength(contour.reshape(-1, 1, 2), True))
    circularity = 4.0 * np.pi * area / (perimeter * perimeter) if perimeter else 0.0

    if circularity > 0.88:
        shape_type = ShapeType.CIRCLE
    else:
        shape_type = ShapeType.ROUNDED if min_corner_distance > 2.0 else ShapeType.BOX

    return Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=shape_type,
            ),
        )
    )
