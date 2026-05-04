#!/usr/bin/env python3
"""Эвристический QA компоновки для файлов draw.io (.drawio)."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import math
from pathlib import Path
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zlib


PEER_GAP_WARNING = 24.0
PAGE_EDGE_WARNING = 24.0
SWIMLANE_BORDER_WARNING = 32.0
EDGE_CLEARANCE_WARNING = 12.0
CORRIDOR_OFFSET_WARNING = 6.0
CORRIDOR_OVERLAP_WARNING = 30.0
TRIVIAL_EDGE_GAP = 120.0
RETURN_LOOP_THRESHOLD = 120.0
LONG_LOOP_SPAN_RATIO = 0.25


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class BBox:
    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def center(self) -> Point:
        return Point(self.left + (self.width / 2.0), self.top + (self.height / 2.0))

    def overlaps(self, other: "BBox") -> bool:
        return (
            self.left < other.right
            and self.right > other.left
            and self.top < other.bottom
            and self.bottom > other.top
        )

    def contains_point_strict(self, point: Point) -> bool:
        return self.left < point.x < self.right and self.top < point.y < self.bottom

    def contains_point(self, point: Point) -> bool:
        return self.left <= point.x <= self.right and self.top <= point.y <= self.bottom

    def gap_to(self, other: "BBox") -> float:
        dx = max(other.left - self.right, self.left - other.right, 0.0)
        dy = max(other.top - self.bottom, self.top - other.bottom, 0.0)
        return math.hypot(dx, dy)

    def union(self, other: "BBox") -> "BBox":
        return BBox(
            left=min(self.left, other.left),
            top=min(self.top, other.top),
            right=max(self.right, other.right),
            bottom=max(self.bottom, other.bottom),
        )


@dataclass(frozen=True)
class Vertex:
    cell_id: str
    page_name: str
    parent_id: str
    bbox: BBox
    style: dict[str, str]
    is_container: bool
    is_swimlane: bool


@dataclass(frozen=True)
class Edge:
    cell_id: str
    page_name: str
    source_id: str
    target_id: str
    parent_id: str
    style: dict[str, str]
    waypoints: tuple[Point, ...]
    source_point: Point | None
    target_point: Point | None


@dataclass(frozen=True)
class Segment:
    edge_id: str
    start: Point
    end: Point


@dataclass(frozen=True)
class Issue:
    level: str
    page_name: str
    code: str
    message: str


def parse_style(style: str | None) -> dict[str, str]:
    parsed: dict[str, str] = {}
    if not style:
        return parsed
    for token in style.split(";"):
        if not token:
            continue
        if "=" in token:
            key, value = token.split("=", 1)
            parsed[key] = value
        else:
            parsed[token] = "1"
    return parsed


def decode_diagram(diagram: ET.Element) -> ET.Element:
    graph_model = diagram.find("mxGraphModel")
    if graph_model is not None:
        return graph_model

    payload = (diagram.text or "").strip()
    if not payload:
        raise ValueError(f"Диаграмма '{diagram.get('name', 'Unnamed')}' не содержит данных mxGraphModel.")

    raw = base64.b64decode(payload)
    inflated = zlib.decompress(raw, -15)
    xml_text = unquote(inflated.decode("utf-8"))
    return ET.fromstring(xml_text)


def numeric(value: str | None, default: float) -> float:
    if value is None or value == "":
        return default
    return float(value)


def absolute_bbox(
    cell_id: str,
    cells: dict[str, ET.Element],
    cache: dict[str, BBox],
) -> BBox | None:
    if cell_id in cache:
        return cache[cell_id]
    cell = cells[cell_id]
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return None

    width = numeric(geometry.get("width"), 0.0)
    height = numeric(geometry.get("height"), 0.0)
    x = numeric(geometry.get("x"), 0.0)
    y = numeric(geometry.get("y"), 0.0)
    parent_id = cell.get("parent")
    if parent_id in cells and cells[parent_id].get("vertex") == "1":
        parent_bbox = absolute_bbox(parent_id, cells, cache)
        if parent_bbox is not None:
            x += parent_bbox.left
            y += parent_bbox.top
    bbox = BBox(left=x, top=y, right=x + width, bottom=y + height)
    cache[cell_id] = bbox
    return bbox


def is_container_style(style: dict[str, str]) -> tuple[bool, bool]:
    shape = style.get("shape", "")
    is_swimlane = shape == "swimlane" or "swimlaneFillColor" in style
    is_container = is_swimlane or style.get("container") == "1" or style.get("group") == "1"
    return is_container, is_swimlane


def point_distance_to_segment(point: Point, start: Point, end: Point) -> float:
    dx = end.x - start.x
    dy = end.y - start.y
    if dx == 0 and dy == 0:
        return math.hypot(point.x - start.x, point.y - start.y)
    t = ((point.x - start.x) * dx + (point.y - start.y) * dy) / ((dx * dx) + (dy * dy))
    t = max(0.0, min(1.0, t))
    closest = Point(start.x + (t * dx), start.y + (t * dy))
    return math.hypot(point.x - closest.x, point.y - closest.y)


def point_distance_to_bbox(point: Point, bbox: BBox) -> float:
    dx = max(bbox.left - point.x, 0.0, point.x - bbox.right)
    dy = max(bbox.top - point.y, 0.0, point.y - bbox.bottom)
    return math.hypot(dx, dy)


def segment_rect_distance(start: Point, end: Point, bbox: BBox) -> float:
    if segment_intersects_rect_interior(start, end, bbox):
        return 0.0
    distances = [
        point_distance_to_bbox(start, bbox),
        point_distance_to_bbox(end, bbox),
    ]
    corners = (
        Point(bbox.left, bbox.top),
        Point(bbox.right, bbox.top),
        Point(bbox.right, bbox.bottom),
        Point(bbox.left, bbox.bottom),
    )
    distances.extend(point_distance_to_segment(corner, start, end) for corner in corners)
    return min(distances)


def segment_intersects_rect_interior(start: Point, end: Point, bbox: BBox) -> bool:
    dx = end.x - start.x
    dy = end.y - start.y
    p = (-dx, dx, -dy, dy)
    q = (
        start.x - bbox.left,
        bbox.right - start.x,
        start.y - bbox.top,
        bbox.bottom - start.y,
    )
    t0 = 0.0
    t1 = 1.0
    for p_value, q_value in zip(p, q):
        if p_value == 0:
            if q_value <= 0:
                return False
            continue
        t = q_value / p_value
        if p_value < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t0 >= t1:
        return False
    midpoint = Point(start.x + ((t0 + t1) / 2.0) * dx, start.y + ((t0 + t1) / 2.0) * dy)
    return bbox.contains_point_strict(midpoint)


def boundary_point_toward(bbox: BBox, toward: Point) -> Point:
    center = bbox.center
    dx = toward.x - center.x
    dy = toward.y - center.y
    if dx == 0 and dy == 0:
        return center
    scales: list[float] = []
    if dx > 0:
        scales.append((bbox.right - center.x) / dx)
    elif dx < 0:
        scales.append((bbox.left - center.x) / dx)
    if dy > 0:
        scales.append((bbox.bottom - center.y) / dy)
    elif dy < 0:
        scales.append((bbox.top - center.y) / dy)
    positive = [scale for scale in scales if scale > 0]
    if not positive:
        return center
    scale = min(positive)
    return Point(center.x + dx * scale, center.y + dy * scale)


def anchored_point(
    bbox: BBox,
    x_fraction: float | None,
    y_fraction: float | None,
    toward: Point,
) -> Point:
    if x_fraction is not None or y_fraction is not None:
        x = bbox.left + bbox.width * (0.5 if x_fraction is None else x_fraction)
        y = bbox.top + bbox.height * (0.5 if y_fraction is None else y_fraction)
        return Point(x, y)
    return boundary_point_toward(bbox, toward)


def style_fraction(style: dict[str, str], key: str) -> float | None:
    value = style.get(key)
    return None if value is None else float(value)


def style_bool(style: dict[str, str], key: str) -> bool:
    value = style.get(key)
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def has_full_anchor_style(edge: Edge) -> bool:
    return all(key in edge.style for key in ("exitX", "exitY", "entryX", "entryY"))


def is_curved_edge(edge: Edge) -> bool:
    return style_bool(edge.style, "curved")


def is_manual_edge(edge: Edge) -> bool:
    return (
        edge.style.get("edgeStyle") == "none"
        or edge.style.get("routing") == "manual"
        or style_bool(edge.style, "manual")
    )


def build_polyline(edge: Edge, vertices: dict[str, Vertex]) -> list[Point] | None:
    source = vertices.get(edge.source_id)
    target = vertices.get(edge.target_id)
    if source is None or target is None:
        return None
    first_hint = edge.waypoints[0] if edge.waypoints else edge.target_point or target.bbox.center
    last_hint = edge.waypoints[-1] if edge.waypoints else edge.source_point or source.bbox.center
    source_anchor = edge.source_point or anchored_point(
        source.bbox,
        style_fraction(edge.style, "exitX"),
        style_fraction(edge.style, "exitY"),
        first_hint,
    )
    target_anchor = edge.target_point or anchored_point(
        target.bbox,
        style_fraction(edge.style, "entryX"),
        style_fraction(edge.style, "entryY"),
        last_hint,
    )
    return [source_anchor, *edge.waypoints, target_anchor]


def vertex_label(vertex: Vertex) -> str:
    return f"{vertex.cell_id}"


def edge_label(edge: Edge) -> str:
    return f"{edge.cell_id}"


def bbox_union(boxes: list[BBox]) -> BBox | None:
    if not boxes:
        return None
    union = boxes[0]
    for box in boxes[1:]:
        union = union.union(box)
    return union


def overlap_length(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def segment_orientation(segment: Segment) -> str:
    if abs(segment.start.x - segment.end.x) < 1e-6:
        return "vertical"
    if abs(segment.start.y - segment.end.y) < 1e-6:
        return "horizontal"
    return "other"


def proper_segment_intersection(a: Segment, b: Segment) -> Point | None:
    x1, y1 = a.start.x, a.start.y
    x2, y2 = a.end.x, a.end.y
    x3, y3 = b.start.x, b.start.y
    x4, y4 = b.end.x, b.end.y

    denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
    if abs(denominator) < 1e-6:
        return None

    t = (((x1 - x3) * (y3 - y4)) - ((y1 - y3) * (x3 - x4))) / denominator
    u = (((x1 - x3) * (y1 - y2)) - ((y1 - y3) * (x1 - x2))) / denominator
    if not (1e-6 < t < 1.0 - 1e-6 and 1e-6 < u < 1.0 - 1e-6):
        return None
    return Point(x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def is_trivial_adjacent_edge(edge: Edge, vertices: dict[str, Vertex]) -> bool:
    source = vertices.get(edge.source_id)
    target = vertices.get(edge.target_id)
    if source is None or target is None:
        return False
    if source.parent_id != target.parent_id:
        return False
    vertical_overlap = overlap_length(source.bbox.top, source.bbox.bottom, target.bbox.top, target.bbox.bottom)
    horizontal_overlap = overlap_length(source.bbox.left, source.bbox.right, target.bbox.left, target.bbox.right)
    if vertical_overlap > 0:
        gap = max(target.bbox.left - source.bbox.right, source.bbox.left - target.bbox.right, 0.0)
        if gap <= TRIVIAL_EDGE_GAP:
            return True
    if horizontal_overlap > 0:
        gap = max(target.bbox.top - source.bbox.bottom, source.bbox.top - target.bbox.bottom, 0.0)
        if gap <= TRIVIAL_EDGE_GAP:
            return True
    return False


def has_explicit_route(edge: Edge, vertices: dict[str, Vertex]) -> bool:
    if edge.waypoints:
        return True
    if edge.source_point is not None and edge.target_point is not None:
        return True
    if is_curved_edge(edge) or is_manual_edge(edge):
        return False
    return has_full_anchor_style(edge) and is_trivial_adjacent_edge(edge, vertices)


def route_requires_visual_qa(edge: Edge) -> bool:
    return is_curved_edge(edge) or is_manual_edge(edge)


def climb_parents(cell_id: str, cells: dict[str, ET.Element]) -> list[str]:
    lineage: list[str] = []
    current = cells.get(cell_id)
    seen: set[str] = set()
    while current is not None:
        parent_id = current.get("parent")
        if not parent_id or parent_id in seen:
            break
        seen.add(parent_id)
        lineage.append(parent_id)
        current = cells.get(parent_id)
    return lineage


def page_dominant_direction(vertices: list[Vertex]) -> str:
    boxes = [vertex.bbox for vertex in vertices if not vertex.is_container]
    union = bbox_union(boxes)
    if union is None:
        return "horizontal"
    return "horizontal" if union.width >= union.height else "vertical"


def is_long_return_loop(edge: Edge, vertices: dict[str, Vertex], direction: str, core_box: BBox | None) -> bool:
    source = vertices.get(edge.source_id)
    target = vertices.get(edge.target_id)
    if source is None or target is None:
        return False
    source_center = source.bbox.center
    target_center = target.bbox.center
    if direction == "horizontal":
        span = abs(target_center.x - source_center.x)
        limit = RETURN_LOOP_THRESHOLD
        extra = 0.0 if core_box is None else core_box.width * LONG_LOOP_SPAN_RATIO
        return target_center.x < source_center.x - limit and span > max(limit, extra)
    span = abs(target_center.y - source_center.y)
    limit = RETURN_LOOP_THRESHOLD
    extra = 0.0 if core_box is None else core_box.height * LONG_LOOP_SPAN_RATIO
    return target_center.y < source_center.y - limit and span > max(limit, extra)


def parse_page(diagram: ET.Element) -> tuple[dict[str, Vertex], dict[str, Edge], dict[str, ET.Element], BBox]:
    graph_model = decode_diagram(diagram)
    page_name = diagram.get("name", "Unnamed")
    page_width = numeric(graph_model.get("pageWidth"), numeric(graph_model.get("dx"), 1600.0))
    page_height = numeric(graph_model.get("pageHeight"), numeric(graph_model.get("dy"), 900.0))
    page_box = BBox(left=0.0, top=0.0, right=page_width, bottom=page_height)
    root = graph_model.find("root")
    if root is None:
        return {}, {}, {}, page_box

    cells = {
        cell.get("id"): cell
        for cell in root.findall("mxCell")
        if cell.get("id")
    }
    bbox_cache: dict[str, BBox] = {}
    vertices: dict[str, Vertex] = {}
    edges: dict[str, Edge] = {}

    for cell_id, cell in cells.items():
        if cell.get("vertex") == "1":
            style = parse_style(cell.get("style"))
            is_container, is_swimlane = is_container_style(style)
            bbox = absolute_bbox(cell_id, cells, bbox_cache)
            if bbox is None:
                continue
            vertices[cell_id] = Vertex(
                cell_id=cell_id,
                page_name=page_name,
                parent_id=cell.get("parent", "1"),
                bbox=bbox,
                style=style,
                is_container=is_container,
                is_swimlane=is_swimlane,
            )
        elif cell.get("edge") == "1":
            style = parse_style(cell.get("style"))
            geometry = cell.find("mxGeometry")
            waypoints: list[Point] = []
            source_point: Point | None = None
            target_point: Point | None = None
            if geometry is not None:
                for array in geometry.findall("Array"):
                    if array.get("as") != "points":
                        continue
                    for point in array.findall("mxPoint"):
                        waypoints.append(
                            Point(
                                x=numeric(point.get("x"), 0.0),
                                y=numeric(point.get("y"), 0.0),
                            )
                        )
                for point in geometry.findall("mxPoint"):
                    parsed_point = Point(
                        x=numeric(point.get("x"), 0.0),
                        y=numeric(point.get("y"), 0.0),
                    )
                    if point.get("as") == "sourcePoint":
                        source_point = parsed_point
                    elif point.get("as") == "targetPoint":
                        target_point = parsed_point
            edges[cell_id] = Edge(
                cell_id=cell_id,
                page_name=page_name,
                source_id=cell.get("source", ""),
                target_id=cell.get("target", ""),
                parent_id=cell.get("parent", "1"),
                style=style,
                waypoints=tuple(waypoints),
                source_point=source_point,
                target_point=target_point,
            )

    return vertices, edges, cells, page_box


def analyze_page(diagram: ET.Element) -> list[Issue]:
    vertices, edges, cells, page_box = parse_page(diagram)
    page_name = diagram.get("name", "Unnamed")
    issues: list[Issue] = []
    emitted: set[tuple[str, str, str]] = set()

    def emit(level: str, code: str, message: str) -> None:
        key = (level, code, message)
        if key in emitted:
            return
        emitted.add(key)
        issues.append(Issue(level=level, page_name=page_name, code=code, message=message))

    non_container_vertices = {
        cell_id: vertex
        for cell_id, vertex in vertices.items()
        if not vertex.is_container
    }
    swimlanes = {
        cell_id: vertex
        for cell_id, vertex in vertices.items()
        if vertex.is_swimlane
    }

    peer_vertices = list(non_container_vertices.values())
    for index, first in enumerate(peer_vertices):
        for second in peer_vertices[index + 1 :]:
            if first.parent_id != second.parent_id:
                continue
            if first.bbox.overlaps(second.bbox):
                emit(
                    "FAIL",
                    "peer-overlap",
                    f"равноправные узлы '{vertex_label(first)}' и '{vertex_label(second)}' пересекаются",
                )
                continue
            gap = first.bbox.gap_to(second.bbox)
            if gap < PEER_GAP_WARNING:
                emit(
                    "WARN",
                    "peer-gap",
                    (
                        f"равноправные узлы '{vertex_label(first)}' и '{vertex_label(second)}' "
                        f"стоят друг от друга всего в {gap:.1f}px"
                    ),
                )

    for vertex in non_container_vertices.values():
        margin = min(
            vertex.bbox.left,
            vertex.bbox.top,
            page_box.right - vertex.bbox.right,
            page_box.bottom - vertex.bbox.bottom,
        )
        if margin < PAGE_EDGE_WARNING:
            emit(
                "WARN",
                "page-edge-gap",
                f"узел '{vertex_label(vertex)}' находится всего в {margin:.1f}px от края страницы",
            )
        for ancestor_id in climb_parents(vertex.cell_id, cells):
            swimlane = swimlanes.get(ancestor_id)
            if swimlane is None:
                continue
            border_gap = min(
                vertex.bbox.left - swimlane.bbox.left,
                vertex.bbox.top - swimlane.bbox.top,
                swimlane.bbox.right - vertex.bbox.right,
                swimlane.bbox.bottom - vertex.bbox.bottom,
            )
            if border_gap < SWIMLANE_BORDER_WARNING:
                emit(
                    "WARN",
                    "swimlane-gap",
                    (
                        f"узел '{vertex_label(vertex)}' находится всего в {border_gap:.1f}px от "
                        f"swimlane '{vertex_label(swimlane)}'"
                    ),
                )

    polyline_segments: list[Segment] = []
    core_box = bbox_union([vertex.bbox for vertex in non_container_vertices.values()])
    direction = page_dominant_direction(list(non_container_vertices.values()))
    long_return_loops = 0

    for edge in edges.values():
        if not edge.source_id or not edge.target_id:
            emit(
                "WARN",
                "edge-skip",
                f"у связи '{edge_label(edge)}' отсутствует source или target; сначала запусти структурную проверку",
            )
            continue
        if not has_explicit_route(edge, vertices):
            emit(
                "FAIL",
                "auto-routing-forbidden",
                (
                    f"связь '{edge_label(edge)}' не имеет явного маршрута; "
                    "авторазводка draw.io запрещена в финальном файле"
                ),
            )
            continue
        if route_requires_visual_qa(edge):
            emit(
                "WARN",
                "visual-qa-required",
                (
                    f"связь '{edge_label(edge)}' использует кривую или ручную геометрию; "
                    "скрипт не доказывает реальный изгиб, нужен последний визуальный QA"
                ),
            )
            for waypoint in edge.waypoints:
                for vertex in non_container_vertices.values():
                    if vertex.cell_id in {edge.source_id, edge.target_id}:
                        continue
                    if vertex.bbox.contains_point_strict(waypoint):
                        emit(
                            "FAIL",
                            "waypoint-inside-node",
                            (
                                f"у связи '{edge_label(edge)}' промежуточная точка ({waypoint.x:.1f}, {waypoint.y:.1f}) "
                                f"находится внутри узла '{vertex_label(vertex)}'"
                            ),
                        )
            continue
        if (
            not edge.waypoints
            and edge.source_point is None
            and edge.target_point is None
            and not (has_full_anchor_style(edge) and is_trivial_adjacent_edge(edge, vertices))
        ):
            emit(
                "WARN",
                "missing-waypoints",
                (
                    f"у связи '{edge_label(edge)}' нет явных промежуточных точек, хотя "
                    "маршрут нетривиален"
                ),
            )
        polyline = build_polyline(edge, vertices)
        if polyline is None or len(polyline) < 2:
            emit(
                "WARN",
                "edge-skip",
                f"связь '{edge_label(edge)}' не удалось проанализировать, потому что отсутствует геометрия source или target",
            )
            continue
        if is_long_return_loop(edge, vertices, direction, core_box):
            long_return_loops += 1
        for waypoint in edge.waypoints:
            for vertex in non_container_vertices.values():
                if vertex.cell_id in {edge.source_id, edge.target_id}:
                    continue
                if vertex.bbox.contains_point_strict(waypoint):
                    emit(
                        "FAIL",
                        "waypoint-inside-node",
                        (
                            f"у связи '{edge_label(edge)}' промежуточная точка ({waypoint.x:.1f}, {waypoint.y:.1f}) "
                            f"находится внутри узла '{vertex_label(vertex)}'"
                        ),
                    )
        for start, end in zip(polyline, polyline[1:]):
            polyline_segments.append(Segment(edge_id=edge.cell_id, start=start, end=end))
            for vertex in non_container_vertices.values():
                if vertex.cell_id in {edge.source_id, edge.target_id}:
                    continue
                if segment_intersects_rect_interior(start, end, vertex.bbox):
                    emit(
                        "FAIL",
                        "edge-through-node",
                        (
                            f"связь '{edge_label(edge)}' пересекает чужой узел "
                            f"'{vertex_label(vertex)}'"
                        ),
                    )
                    continue
                clearance = segment_rect_distance(start, end, vertex.bbox)
                if clearance < EDGE_CLEARANCE_WARNING:
                    emit(
                        "WARN",
                        "edge-clearance",
                        (
                            f"связь '{edge_label(edge)}' проходит в {clearance:.1f}px от "
                            f"узла '{vertex_label(vertex)}'"
                        ),
                    )

    crossings = 0
    for index, first in enumerate(polyline_segments):
        for second in polyline_segments[index + 1 :]:
            if first.edge_id == second.edge_id:
                continue
            intersection = proper_segment_intersection(first, second)
            if intersection is not None and (core_box is None or core_box.contains_point(intersection)):
                crossings += 1
                emit(
                    "WARN",
                    "edge-crossing",
                    (
                        f"связи '{first.edge_id}' и '{second.edge_id}' пересекаются в основной области "
                        f"в точке ({intersection.x:.1f}, {intersection.y:.1f})"
                    ),
                )

            first_orientation = segment_orientation(first)
            second_orientation = segment_orientation(second)
            if first_orientation != second_orientation or first_orientation == "other":
                continue
            if first_orientation == "horizontal":
                same_line = abs(first.start.y - second.start.y) < CORRIDOR_OFFSET_WARNING
                overlap = overlap_length(
                    min(first.start.x, first.end.x),
                    max(first.start.x, first.end.x),
                    min(second.start.x, second.end.x),
                    max(second.start.x, second.end.x),
                )
            else:
                same_line = abs(first.start.x - second.start.x) < CORRIDOR_OFFSET_WARNING
                overlap = overlap_length(
                    min(first.start.y, first.end.y),
                    max(first.start.y, first.end.y),
                    min(second.start.y, second.end.y),
                    max(second.start.y, second.end.y),
                )
            if same_line and overlap > CORRIDOR_OVERLAP_WARNING:
                emit(
                    "WARN",
                    "corridor-stack",
                    (
                        f"связи '{first.edge_id}' и '{second.edge_id}' используют один коридор "
                        "без видимого смещения"
                    ),
                )

    if long_return_loops > 2 or crossings > 1:
        details: list[str] = []
        if long_return_loops > 2:
            details.append(f"длинных возвратных петель: {long_return_loops}")
        if crossings > 1:
            details.append(f"центральных пересечений: {crossings}")
        emit(
            "WARN",
            "split-needed",
            "странице, вероятно, нужно разделение на обзор и детали, потому что остаются " + " и ".join(details),
        )

    return issues


def analyze_drawio(path: Path) -> list[Issue]:
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != "mxfile":
        raise ValueError("Корневой элемент должен быть <mxfile>.")
    diagrams = root.findall("diagram")
    if not diagrams:
        raise ValueError("Файл не содержит страниц <diagram>.")
    issues: list[Issue] = []
    for diagram in diagrams:
        issues.extend(analyze_page(diagram))
    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser._positionals.title = "позиционные аргументы"
    parser._optionals.title = "необязательные аргументы"
    parser.add_argument("-h", "--help", action="help", help="показать это сообщение и выйти")
    parser.add_argument("path", help="Путь к .drawio файлу.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    try:
        issues = analyze_drawio(path)
    except (ET.ParseError, ValueError, zlib.error, base64.binascii.Error) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    fail_count = sum(1 for issue in issues if issue.level == "FAIL")
    warn_count = sum(1 for issue in issues if issue.level == "WARN")

    if fail_count == 0 and warn_count == 0:
        print(f"LAYOUT OK: {path}")
        print("Summary: 0 fails, 0 warnings")
        return 0

    status = "LAYOUT FAIL" if fail_count else "LAYOUT WARN"
    print(f"{status}: {path}")
    for issue in issues:
        print(f"{issue.level} [{issue.page_name}] {issue.code}: {issue.message}")
    print(f"Summary: {fail_count} fails, {warn_count} warnings")
    return 1 if fail_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
