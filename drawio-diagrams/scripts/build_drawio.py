#!/usr/bin/env python3
"""Build an editable draw.io (.drawio) file from a JSON spec."""

from __future__ import annotations

import argparse
import copy
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


EXAMPLE_SPEC = {
    "meta": {
        "host": "app.diagrams.net",
        "agent": "Codex",
        "version": "24.7.17",
        "compressed": False,
    },
    "pages": [
        {
            "id": "overview",
            "name": "Overview",
            "pageWidth": 1600,
            "pageHeight": 900,
            "layout": {
                "direction": "horizontal",
                "start_x": 80,
                "start_y": 120,
                "gap_x": 120,
                "gap_y": 80,
                "columns": 3,
            },
            "nodes": [
                {"id": "client-app", "label": "Client App", "kind": "process"},
                {"id": "api-gateway", "label": "API Gateway", "kind": "process"},
                {"id": "orders-service", "label": "Orders Service", "kind": "process"},
                {
                    "id": "orders-db",
                    "label": "Orders DB",
                    "kind": "database",
                    "width": 170,
                    "height": 90,
                },
                {
                    "id": "payments",
                    "label": "Payment Provider",
                    "kind": "cloud",
                    "x": 1220,
                    "y": 120,
                },
                {
                    "id": "legend",
                    "label": "Blue = internal\\nPurple = external",
                    "kind": "note",
                    "x": 1220,
                    "y": 320,
                    "width": 220,
                    "height": 100,
                },
            ],
            "edges": [
                {
                    "id": "edge-client-api",
                    "source": "client-app",
                    "target": "api-gateway",
                    "label": "HTTPS",
                },
                {
                    "id": "edge-api-orders",
                    "source": "api-gateway",
                    "target": "orders-service",
                    "label": "REST",
                },
                {
                    "id": "edge-orders-db",
                    "source": "orders-service",
                    "target": "orders-db",
                    "label": "SQL",
                },
                {
                    "id": "edge-orders-payments",
                    "source": "orders-service",
                    "target": "payments",
                    "label": "Capture",
                    "dashed": True,
                },
            ],
        }
    ],
}


NODE_STYLES = {
    "process": OrderedDict(
        [
            ("rounded", "1"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("fillColor", "#dae8fc"),
            ("strokeColor", "#6c8ebf"),
        ]
    ),
    "decision": OrderedDict(
        [
            ("shape", "rhombus"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("fillColor", "#fff2cc"),
            ("strokeColor", "#d6b656"),
        ]
    ),
    "terminator": OrderedDict(
        [
            ("shape", "mxgraph.flowchart.terminator"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("fillColor", "#f8cecc"),
            ("strokeColor", "#b85450"),
        ]
    ),
    "database": OrderedDict(
        [
            ("shape", "cylinder3"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("boundedLbl", "1"),
            ("backgroundOutline", "1"),
            ("fillColor", "#d5e8d4"),
            ("strokeColor", "#82b366"),
        ]
    ),
    "note": OrderedDict(
        [
            ("shape", "note"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("backgroundOutline", "1"),
            ("fillColor", "#fff2cc"),
            ("strokeColor", "#d6b656"),
        ]
    ),
    "cloud": OrderedDict(
        [
            ("shape", "cloud"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("fillColor", "#e1d5e7"),
            ("strokeColor", "#9673a6"),
        ]
    ),
    "swimlane": OrderedDict(
        [
            ("shape", "swimlane"),
            ("whiteSpace", "wrap"),
            ("html", "1"),
            ("horizontal", "0"),
            ("startSize", "28"),
            ("fillColor", "#f5f5f5"),
            ("strokeColor", "#666666"),
        ]
    ),
}


EDGE_STYLE = OrderedDict(
    [
        ("edgeStyle", "orthogonalEdgeStyle"),
        ("rounded", "0"),
        ("orthogonalLoop", "1"),
        ("jettySize", "auto"),
        ("html", "1"),
        ("endArrow", "block"),
    ]
)

NODE_STYLE_KEYS = (
    "shape",
    "rounded",
    "whiteSpace",
    "html",
    "fillColor",
    "strokeColor",
    "fontColor",
    "fontStyle",
    "dashed",
    "horizontal",
    "startSize",
    "swimlaneFillColor",
    "container",
    "pointerEvents",
    "align",
    "verticalAlign",
    "overflow",
    "opacity",
    "perimeter",
    "size",
)

EDGE_STYLE_KEYS = (
    "edgeStyle",
    "rounded",
    "html",
    "endArrow",
    "startArrow",
    "curved",
    "strokeColor",
    "strokeWidth",
    "fontColor",
    "jettySize",
    "orthogonalLoop",
    "elbow",
    "entryX",
    "entryY",
    "entryDx",
    "entryDy",
    "exitX",
    "exitY",
    "exitDx",
    "exitDy",
    "startSize",
    "endSize",
    "dashed",
)


def prettify(element: ET.Element, level: int = 0) -> None:
    indent = "\n" + ("  " * level)
    child_indent = "\n" + ("  " * (level + 1))
    if len(element):
        if not element.text or not element.text.strip():
            element.text = child_indent
        for child in element:
            prettify(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = child_indent
        if element[-1].tail != indent:
            element[-1].tail = indent
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indent


def style_to_string(style: OrderedDict[str, str]) -> str:
    return "".join(f"{key}={value};" for key, value in style.items())


def normalize_value(value: object) -> str:
    text = str(value)
    return text.replace("\\n", "<br>").replace("\n", "<br>")


def build_node_style(node: dict) -> str:
    if "style" in node and node["style"]:
        return node["style"]
    kind = node.get("kind", "process")
    style = copy.deepcopy(NODE_STYLES.get(kind, NODE_STYLES["process"]))
    for key in NODE_STYLE_KEYS:
        if key in node:
            style[key] = str(int(node[key])) if isinstance(node[key], bool) else str(node[key])
    return style_to_string(style)


def build_edge_style(edge: dict) -> str:
    if "style" in edge and edge["style"]:
        return edge["style"]
    style = copy.deepcopy(EDGE_STYLE)
    if edge.get("dashed"):
        style["dashed"] = "1"
        style["endArrow"] = edge.get("endArrow", "open")
    for key in EDGE_STYLE_KEYS:
        if key in edge:
            style[key] = str(int(edge[key])) if isinstance(edge[key], bool) else str(edge[key])
    return style_to_string(style)


def assign_positions(page: dict) -> None:
    layout = page.get("layout", {})
    direction = layout.get("direction", "horizontal")
    start_x = int(layout.get("start_x", 80))
    start_y = int(layout.get("start_y", 80))
    gap_x = int(layout.get("gap_x", 80))
    gap_y = int(layout.get("gap_y", 60))
    columns = max(int(layout.get("columns", 3)), 1)

    next_index = 0
    for node in page.get("nodes", []):
        node.setdefault("width", 180)
        node.setdefault("height", 70)
        if "x" in node and "y" in node:
            continue
        row = next_index // columns
        col = next_index % columns
        if direction == "vertical":
            x = start_x + row * (int(node["width"]) + gap_x)
            y = start_y + col * (int(node["height"]) + gap_y)
        else:
            x = start_x + col * (int(node["width"]) + gap_x)
            y = start_y + row * (int(node["height"]) + gap_y)
        node["x"] = x
        node["y"] = y
        next_index += 1


def ensure_ids(page: dict) -> None:
    for index, node in enumerate(page.get("nodes", []), start=1):
        node.setdefault("id", f"node-{index}")
    for index, edge in enumerate(page.get("edges", []), start=1):
        edge.setdefault("id", f"edge-{index}")


def validate_page_spec(page: dict) -> None:
    reserved = {"0", "1"}
    node_ids = []
    edge_ids = []
    for node in page.get("nodes", []):
        node_id = str(node["id"])
        if node_id in reserved:
            raise ValueError(f"Node id '{node_id}' is reserved.")
        node_ids.append(node_id)
    for edge in page.get("edges", []):
        edge_id = str(edge["id"])
        if edge_id in reserved:
            raise ValueError(f"Edge id '{edge_id}' is reserved.")
        edge_ids.append(edge_id)

    all_ids = node_ids + edge_ids
    if len(set(all_ids)) != len(all_ids):
        duplicates = sorted({item for item in all_ids if all_ids.count(item) > 1})
        raise ValueError(f"Duplicate cell id(s) in page '{page.get('name', 'Unnamed')}': {', '.join(duplicates)}")

    node_id_set = set(node_ids)
    for edge in page.get("edges", []):
        source = str(edge["source"])
        target = str(edge["target"])
        if source not in node_id_set:
            raise ValueError(f"Edge '{edge['id']}' references unknown source '{source}'.")
        if target not in node_id_set:
            raise ValueError(f"Edge '{edge['id']}' references unknown target '{target}'.")


def make_graph_model(page: dict) -> ET.Element:
    page_width = str(page.get("pageWidth", 1600))
    page_height = str(page.get("pageHeight", 900))
    model = ET.Element(
        "mxGraphModel",
        {
            "dx": page_width,
            "dy": page_height,
            "grid": str(page.get("grid", 1)),
            "gridSize": str(page.get("gridSize", 10)),
            "guides": str(page.get("guides", 1)),
            "tooltips": str(page.get("tooltips", 1)),
            "connect": str(page.get("connect", 1)),
            "arrows": str(page.get("arrows", 1)),
            "fold": str(page.get("fold", 1)),
            "page": str(page.get("page", 1)),
            "pageScale": str(page.get("pageScale", 1)),
            "pageWidth": page_width,
            "pageHeight": page_height,
            "math": str(page.get("math", 0)),
            "shadow": str(page.get("shadow", 0)),
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    for node in page.get("nodes", []):
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": node["id"],
                "value": normalize_value(node.get("label", "")),
                "style": build_node_style(node),
                "vertex": "1",
                "parent": str(node.get("parent", "1")),
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(node["x"]),
                "y": str(node["y"]),
                "width": str(node.get("width", 180)),
                "height": str(node.get("height", 70)),
                "as": "geometry",
            },
        )

    for edge in page.get("edges", []):
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": edge["id"],
                "value": normalize_value(edge.get("label", "")),
                "style": build_edge_style(edge),
                "edge": "1",
                "parent": str(edge.get("parent", "1")),
                "source": str(edge["source"]),
                "target": str(edge["target"]),
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "relative": "1",
                "as": "geometry",
            },
        )
        geometry = cell.find("mxGeometry")
        points = edge.get("points", [])
        if points:
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for point in points:
                ET.SubElement(
                    array,
                    "mxPoint",
                    {
                        "x": str(point["x"]),
                        "y": str(point["y"]),
                    },
                )
    return model


def build_drawio(spec: dict) -> ET.ElementTree:
    meta = spec.get("meta", {})
    if meta.get("compressed"):
        raise ValueError("Compressed output is not supported by this helper. Omit meta.compressed or set it to false.")
    mxfile = ET.Element(
        "mxfile",
        {
            "host": str(meta.get("host", "app.diagrams.net")),
            "modified": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "agent": str(meta.get("agent", "Codex")),
            "version": str(meta.get("version", "24.7.17")),
            "compressed": "false",
        },
    )

    pages = spec.get("pages", [])
    if not pages:
        raise ValueError("Spec must contain at least one page.")

    for index, page in enumerate(pages, start=1):
        ensure_ids(page)
        assign_positions(page)
        validate_page_spec(page)
        diagram = ET.SubElement(
            mxfile,
            "diagram",
            {
                "id": str(page.get("id", f"page-{index}")),
                "name": str(page.get("name", f"Page {index}")),
            },
        )
        diagram.append(make_graph_model(page))

    tree = ET.ElementTree(mxfile)
    prettify(mxfile)
    return tree


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", help="Path to a JSON spec file.")
    parser.add_argument("output", nargs="?", help="Path to the output .drawio file.")
    parser.add_argument(
        "--example",
        action="store_true",
        help="Print an example JSON spec and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.example:
        print(json.dumps(EXAMPLE_SPEC, indent=2, ensure_ascii=True))
        return 0
    if not args.spec or not args.output:
        print("Provide SPEC and OUTPUT, or use --example.", file=sys.stderr)
        return 2

    spec_path = Path(args.spec)
    output_path = Path(args.output)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    tree = build_drawio(spec)
    output_path.write_text(
        ET.tostring(tree.getroot(), encoding="unicode"),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
