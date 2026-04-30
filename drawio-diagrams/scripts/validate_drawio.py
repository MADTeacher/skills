#!/usr/bin/env python3
"""Проверяет файлы draw.io (.drawio) и печатает короткую структурную сводку."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from pathlib import Path
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zlib


@dataclass
class PageSummary:
    name: str
    vertices: int
    edges: int


def ensure_no_comments(path: Path) -> None:
    comment_count = 0
    with path.open("rb") as handle:
        for _event, _element in ET.iterparse(handle, events=("comment",)):
            comment_count += 1
    if comment_count:
        raise ValueError(f"Файл содержит XML-комментарии: {comment_count}. Удали XML-комментарии из файлов draw.io.")


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


def validate_page(diagram: ET.Element) -> PageSummary:
    graph_model = decode_diagram(diagram)
    root = graph_model.find("root")
    if root is None:
        raise ValueError(f"В диаграмме '{diagram.get('name', 'Unnamed')}' отсутствует <root>.")

    cells = root.findall("mxCell")
    ids = {}
    vertices = 0
    edges = 0
    for cell in cells:
        cell_id = cell.get("id")
        if not cell_id:
            raise ValueError(f"В диаграмме '{diagram.get('name', 'Unnamed')}' есть ячейка без id.")
        if cell_id in ids:
            raise ValueError(f"В диаграмме '{diagram.get('name', 'Unnamed')}' есть повторяющийся id '{cell_id}'.")
        ids[cell_id] = cell
        if cell.get("vertex") == "1":
            vertices += 1
        if cell.get("edge") == "1":
            edges += 1

    if "0" not in ids or "1" not in ids:
        raise ValueError(f"В диаграмме '{diagram.get('name', 'Unnamed')}' отсутствуют обязательные корневые ячейки 0 и 1.")

    for cell in cells:
        if cell.get("edge") != "1":
            continue
        source = cell.get("source")
        target = cell.get("target")
        if not source or source not in ids:
            raise ValueError(
                f"В диаграмме '{diagram.get('name', 'Unnamed')}' связь '{cell.get('id')}' имеет невалидный source '{source}'."
            )
        if not target or target not in ids:
            raise ValueError(
                f"В диаграмме '{diagram.get('name', 'Unnamed')}' связь '{cell.get('id')}' имеет невалидный target '{target}'."
            )
        if cell.find("mxGeometry") is None:
            raise ValueError(
                f"В диаграмме '{diagram.get('name', 'Unnamed')}' у связи '{cell.get('id')}' отсутствует дочерний mxGeometry."
            )

    return PageSummary(diagram.get("name", "Unnamed"), vertices, edges)


def validate_drawio(path: Path) -> list[PageSummary]:
    ensure_no_comments(path)
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != "mxfile":
        raise ValueError("Корневой элемент должен быть <mxfile>.")

    diagrams = root.findall("diagram")
    if not diagrams:
        raise ValueError("Файл не содержит страниц <diagram>.")

    return [validate_page(diagram) for diagram in diagrams]


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
        summaries = validate_drawio(path)
    except (ET.ParseError, ValueError, zlib.error, base64.binascii.Error) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    print(f"VALID: {path}")
    for summary in summaries:
        print(f"- {summary.name}: вершин: {summary.vertices}, связей: {summary.edges}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
