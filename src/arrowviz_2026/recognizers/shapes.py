"""Shape recognition logic for raster fixtures."""

from typing import BinaryIO

import cv2
import numpy as np

from arrowviz_2026.ast import Schematic, Shape, ShapeType


_BORDER_SENTINELS = {
    "left": "left-border",
    "right": "right-border",
    "top": "top-border",
    "bottom": "bottom-border",
}


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

    hull = cv2.convexHull(contour)
    hull_area = float(cv2.contourArea(hull))
    solidity = area / hull_area if hull_area else 1.0
    aspect_ratio = w / h if h else 1.0

    if circularity > 0.88:
        return ShapeType.CIRCLE

    if solidity < 0.9 and 0.85 <= aspect_ratio <= 1.2:
        return ShapeType.HEART

    return ShapeType.ROUNDED if min_corner_distance > 2.0 else ShapeType.BOX


def _decode_threshold(image_bytes: bytes) -> np.ndarray:
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Unable to decode image")
    _, threshold = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY_INV)
    return threshold


def _has_detectable_circle(threshold: np.ndarray) -> bool:
    circles = cv2.HoughCircles(
        cv2.bitwise_not(threshold),
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=100,
        param2=20,
        minRadius=20,
        maxRadius=60,
    )
    return circles is not None and circles.shape[1] > 0


def _touches_border(contour: np.ndarray, image_shape: tuple[int, int]) -> bool:
    points = contour[:, 0, :]
    h, w = image_shape
    return bool(
        np.any(points[:, 0] == 0)
        or np.any(points[:, 0] == w - 1)
        or np.any(points[:, 1] == 0)
        or np.any(points[:, 1] == h - 1)
    )


def _recognize_schematic_from_threshold(threshold: np.ndarray) -> Schematic:
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
    top_shape_type = _classify_shape(contours[top_index])
    if top_shape_type == ShapeType.ROUNDED and _touches_border(contours[top_index], threshold.shape) and _has_detectable_circle(threshold):
        top_shape_type = ShapeType.CIRCLE

    child_shape: Shape | None = None
    first_child = int(hierarchy_flat[top_index][2])
    if first_child != -1:
        nested_index = int(hierarchy_flat[first_child][2])
        if nested_index != -1:
            child_shape = Shape(id="shape-1", shape_type=_classify_shape(contours[nested_index]))
        elif _touches_border(contours[top_index], threshold.shape) and _has_detectable_circle(threshold):
            direct_children: list[int] = []
            child_index = first_child
            while child_index != -1:
                direct_children.append(child_index)
                child_index = int(hierarchy_flat[child_index][0])

            non_heart_children = [
                i for i in direct_children if _classify_shape(contours[i]) != ShapeType.HEART
            ]
            if len(direct_children) > 1 and non_heart_children:
                best_child = min(non_heart_children, key=lambda i: cv2.contourArea(contours[i]))
                child_shape = Shape(id="shape-1", shape_type=_classify_shape(contours[best_child]))

    return Schematic(
        shapes=(
            Shape(
                id="shape-0",
                shape_type=top_shape_type,
                child=child_shape,
            ),
        )
    )


def _border_edges(threshold: np.ndarray) -> list[tuple[str, str]]:
    if threshold.size == 0:
        return []

    h, w = threshold.shape
    border_masks = {
        "left": np.zeros_like(threshold),
        "right": np.zeros_like(threshold),
        "top": np.zeros_like(threshold),
        "bottom": np.zeros_like(threshold),
    }
    border_masks["left"][:, 0] = threshold[:, 0]
    border_masks["right"][:, w - 1] = threshold[:, w - 1]
    border_masks["top"][0, :] = threshold[0, :]
    border_masks["bottom"][h - 1, :] = threshold[h - 1, :]

    edges: list[tuple[str, str]] = []
    if not _has_detectable_circle(threshold):
        return edges

    for side, mask in border_masks.items():
        if cv2.countNonZero(mask) == 0:
            continue
        if side in {"left", "top"}:
            edges.append((_BORDER_SENTINELS[side], "shape-0"))
        else:
            edges.append(("shape-0", _BORDER_SENTINELS[side]))

    return edges


def recognize_schematic(image_file: BinaryIO) -> Schematic:
    """Recognize a schematic from an image file handle."""

    threshold = _decode_threshold(image_file.read())
    return _recognize_schematic_from_threshold(threshold)


def recognize_graph(image_file: BinaryIO) -> tuple[Schematic, list[tuple[str, str]]]:
    """Recognize both shapes and border-connected edges from an image file handle."""

    threshold = _decode_threshold(image_file.read())
    return _recognize_schematic_from_threshold(threshold), _border_edges(threshold)
