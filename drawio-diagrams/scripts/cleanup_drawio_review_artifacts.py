#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

TEMP_ROOT = Path('/tmp/drawio-review-gate')


def safe_stem(path: Path) -> str:
    chars = []
    for ch in path.stem:
        chars.append(ch if ch.isalnum() or ch in ('-', '_') else '-')
    stem = ''.join(chars).strip('-_')
    return stem or 'diagram'


def review_dir(drawio_path: Path) -> Path:
    return TEMP_ROOT / safe_stem(drawio_path)


def cleanup(drawio_path: Path) -> list[str]:
    drawio_path = drawio_path.resolve()
    removed: list[str] = []

    tmp_dir = review_dir(drawio_path)
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
        removed.append(str(tmp_dir))

    parent = drawio_path.parent
    stem = drawio_path.stem
    patterns = [
        f'{stem}.skill-test.drawio',
        f'{stem}.tmp.drawio',
        f'{stem}-skill-test.drawio',
        f'{stem}-tmp.drawio',
        f'{stem}*.review.jpg',
        f'{stem}*.review.jpeg',
        f'{stem}*.review.png',
        f'{stem}*.tmp.jpg',
        f'{stem}*.tmp.jpeg',
        f'{stem}*.tmp.png',
    ]

    seen: set[Path] = set()
    for pattern in patterns:
        for candidate in parent.glob(pattern):
            if candidate.resolve() == drawio_path or candidate in seen:
                continue
            seen.add(candidate)
            if candidate.is_dir():
                shutil.rmtree(candidate)
            elif candidate.exists():
                candidate.unlink()
            removed.append(str(candidate))

    return sorted(removed)


def prepare(drawio_path: Path) -> dict[str, str | list[str]]:
    drawio_path = drawio_path.resolve()
    removed = cleanup(drawio_path)
    tmp_dir = review_dir(drawio_path)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    stem = safe_stem(drawio_path)
    return {
        'drawio': str(drawio_path),
        'review_dir': str(tmp_dir),
        'png_pattern': str(tmp_dir / f'{stem}-page{{page}}.png'),
        'jpg_pattern': str(tmp_dir / f'{stem}-page{{page}}.jpg'),
        'removed': removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Prepare and clean temporary draw.io review artifacts.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    prepare_parser = subparsers.add_parser('prepare', help='Clean stale artifacts and create a fresh temp review directory.')
    prepare_parser.add_argument('drawio', type=Path)

    cleanup_parser = subparsers.add_parser('cleanup', help='Remove temp review artifacts for a .drawio file.')
    cleanup_parser.add_argument('drawio', type=Path)

    args = parser.parse_args()
    if args.command == 'prepare':
        print(json.dumps(prepare(args.drawio), ensure_ascii=False, indent=2))
        return 0
    if args.command == 'cleanup':
        print(json.dumps({'removed': cleanup(args.drawio.resolve())}, ensure_ascii=False, indent=2))
        return 0
    raise AssertionError('unreachable')


if __name__ == '__main__':
    raise SystemExit(main())
