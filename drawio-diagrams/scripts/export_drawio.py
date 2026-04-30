#!/usr/bin/env python3
"""Экспортирует диаграммы draw.io через настольный CLI draw.io."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys


EMBED_FORMATS = {"png", "svg", "pdf"}
ALLOW_DESKTOP_EXPORT_ENV = "DRAWIO_ALLOW_DESKTOP_EXPORT"
LEGACY_ALLOW_UNSTABLE_MACOS_ENV = "DRAWIO_ALLOW_UNSTABLE_MACOS_EXPORT"


def is_wsl() -> bool:
    proc_version = Path("/proc/version")
    if not proc_version.exists():
        return False
    return "microsoft" in proc_version.read_text(encoding="utf-8", errors="ignore").lower()


def locate_drawio() -> tuple[str, str]:
    candidates: list[tuple[str, str]] = []

    env_path = os.environ.get("DRAWIO_CMD")
    if env_path:
        candidates.append((env_path, "env"))

    path_candidate = shutil.which("drawio")
    if path_candidate:
        candidates.append((path_candidate, "path"))

    system = platform.system()
    if is_wsl():
        win_user = os.environ.get("WIN_USER", "")
        platform_candidates = [
            "/mnt/c/Program Files/draw.io/draw.io.exe",
            f"/mnt/c/Users/{win_user}/AppData/Local/Programs/draw.io/draw.io.exe" if win_user else "",
        ]
        candidates.extend((candidate, "platform-default") for candidate in platform_candidates)
    elif system == "Darwin":
        platform_candidates = [
            "/Applications/draw.io.app/Contents/MacOS/draw.io",
            "/Applications/diagrams.net.app/Contents/MacOS/draw.io",
        ]
        candidates.extend((candidate, "platform-default") for candidate in platform_candidates)
    elif system == "Windows":
        candidates.append((r"C:\Program Files\draw.io\draw.io.exe", "platform-default"))

    for candidate, source in candidates:
        if candidate and Path(candidate).exists():
            return candidate, source

    raise FileNotFoundError("Не удалось найти настольный CLI draw.io.")


def resolve_command_path(command: str) -> Path:
    path = Path(command).expanduser()
    try:
        return path.resolve()
    except OSError:
        return path


def is_desktop_drawio_binary(command: str) -> bool:
    resolved = resolve_command_path(command)
    normalized = resolved.as_posix().lower()
    system = platform.system()

    if system == "Darwin":
        return normalized.endswith(".app/contents/macos/draw.io")
    if is_wsl() or system == "Windows":
        return normalized.endswith("/draw.io.exe") or normalized.endswith("/diagrams.net.exe")
    return resolved.name.lower() in {"drawio", "draw.io", "diagrams.net"}


def env_flag(name: str) -> bool:
    value = os.environ.get(name, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


def should_block_desktop_export(command: str, source: str, allow_override: bool) -> bool:
    if allow_override:
        return False
    return is_desktop_drawio_binary(command)


def maybe_postprocess(source: Path) -> None:
    npx = shutil.which("npx")
    if not npx:
        return

    commands = [
        [npx, "--yes", "@drawio/postprocess", str(source)],
        [npx, "@drawio/postprocess", str(source)],
    ]

    for command in commands:
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if completed.returncode == 0:
            return


def open_output(path: Path) -> None:
    try:
        if is_wsl():
            win_path = subprocess.run(
                ["wslpath", "-w", str(path)],
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip()
            subprocess.run(["cmd.exe", "/c", "start", "", win_path], check=False)
            return
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        elif system == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            opener = shutil.which("xdg-open")
            if opener:
                subprocess.run([opener, str(path)], check=False)
    except OSError:
        return


def build_output_path(source: Path, export_format: str, output: str | None) -> Path:
    if output:
        return Path(output)
    return source.with_suffix(f"{source.suffix}.{export_format}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser._positionals.title = "позиционные аргументы"
    parser._optionals.title = "необязательные аргументы"
    parser.add_argument("-h", "--help", action="help", help="показать это сообщение и выйти")
    parser.add_argument("source", help="Путь к исходному .drawio файлу.")
    parser.add_argument("--format", required=True, choices=["png", "svg", "pdf", "jpg"], help="Формат экспорта.")
    parser.add_argument("--output", help="Путь к экспортированному артефакту.")
    parser.add_argument("--page-index", type=int, help="Индекс страницы для экспорта, начиная с 1.")
    parser.add_argument("--all-pages", action="store_true", help="Экспортировать все страницы, в основном полезно для PDF.")
    parser.add_argument("--border", type=int, default=10, help="Размер рамки в пикселях.")
    parser.add_argument("--scale", type=float, help="Коэффициент масштаба, передаваемый draw.io.")
    parser.add_argument("--transparent", action="store_true", help="Прозрачный фон для экспорта PNG.")
    parser.add_argument("--postprocess", action="store_true", help="Попробовать необязательный @drawio/postprocess перед экспортом.")
    parser.add_argument("--open", action="store_true", help="Открыть экспортированный файл после создания, если возможно.")
    parser.add_argument(
        "--allow-desktop-export",
        "--allow-unstable-macos-export",
        dest="allow_desktop_export",
        action="store_true",
        help=(
            "Разрешить запуск настольного приложения draw.io из автоматизации, хотя "
            "настольные сборки могут падать, зависать, требовать дисплей или вызывать системные диалоги."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        print(f"Исходный файл не существует: {source}", file=sys.stderr)
        return 2

    output = build_output_path(source, args.format, args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.postprocess:
        maybe_postprocess(source)

    try:
        drawio_cmd, drawio_source = locate_drawio()
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    allow_desktop_export = (
        args.allow_desktop_export
        or env_flag(ALLOW_DESKTOP_EXPORT_ENV)
        or env_flag(LEGACY_ALLOW_UNSTABLE_MACOS_ENV)
    )
    if should_block_desktop_export(drawio_cmd, drawio_source, allow_desktop_export):
        print(
            "Настольный экспорт draw.io заблокирован в безопасном режиме: настольное приложение может падать, зависать, "
            "требовать GUI-сеанс или вызывать системные диалоги при запуске из автоматизации. "
            "Если есть более безопасная обертка или рендерер, укажи DRAWIO_CMD на нее "
            "вместо официального настольного бинарного файла. "
            "Если явно нужен риск настольного приложения, повтори запуск с "
            "--allow-desktop-export или задай "
            f"{ALLOW_DESKTOP_EXPORT_ENV}=1. "
            "На этом хосте macOS наблюдавшийся сбой — диалог "
            '“Application unexpectedly quit”.',
            file=sys.stderr,
        )
        return 4

    command = [drawio_cmd, "-x", "-f", args.format]
    if args.format in EMBED_FORMATS:
        command.append("-e")
    if args.border is not None:
        command.extend(["-b", str(args.border)])
    if args.scale is not None:
        command.extend(["-s", str(args.scale)])
    if args.transparent and args.format == "png":
        command.append("-t")
    if args.all_pages:
        command.append("-a")
    if args.page_index is not None:
        command.extend(["-p", str(args.page_index)])
    command.extend(["-o", str(output), str(source)])

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Экспорт draw.io завершился с кодом {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1

    print(output)
    if args.open:
        open_output(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
