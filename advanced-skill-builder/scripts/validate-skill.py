#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "PyYAML>=6.0.2,<7",
# ]
# ///
"""Validate an Agent Skills directory against the public SKILL.md spec."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Agent Skills frontmatter, naming, and size guidance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run scripts/validate-skill.py .\n"
            "  uv run scripts/validate-skill.py ../my-skill --json\n\n"
            "Exit codes:\n"
            "  0  valid, possibly with warnings\n"
            "  1  validation errors found\n"
            "  2  invalid command-line arguments"
        ),
    )
    parser.add_argument(
        "skill",
        help="Path to a skill directory or to a SKILL.md file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of the short text report.",
    )
    return parser.parse_args()


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def add_warning(warnings: list[dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def resolve_skill_path(raw: str) -> tuple[Path, Path]:
    path = Path(raw).expanduser().resolve()
    if path.is_dir():
        return path, path / "SKILL.md"
    return path.parent, path


def split_frontmatter(text: str) -> tuple[str | None, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            frontmatter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return frontmatter, body
    return None, text


def count_estimated_tokens(text: str) -> int:
    # A rough guardrail for the public 5000-token recommendation.
    return max(len(text) // 4, len(re.findall(r"\S+", text)))


def validate_field_types(
    data: Any,
    skill_dir: Path,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    info: dict[str, Any] = {}

    if not isinstance(data, dict):
        add_error(errors, "frontmatter_not_mapping", "YAML frontmatter must be a mapping.")
        return info

    name = data.get("name")
    if not isinstance(name, str):
        add_error(errors, "name_missing_or_not_string", "`name` must be a string.")
    else:
        info["name_length"] = len(name)
        if not 1 <= len(name) <= 64:
            add_error(errors, "name_length", "`name` must be 1-64 characters.")
        if not NAME_RE.fullmatch(name) or "--" in name:
            add_error(
                errors,
                "name_format",
                "`name` may contain only a-z, 0-9, and hyphen; it must not start, end, or contain consecutive hyphens.",
            )
        if name != skill_dir.name:
            add_error(
                errors,
                "name_directory_mismatch",
                f"`name` must match the parent directory name: expected {skill_dir.name!r}, got {name!r}.",
            )

    description = data.get("description")
    if not isinstance(description, str):
        add_error(errors, "description_missing_or_not_string", "`description` must be a string.")
    else:
        info["description_length"] = len(description)
        if not 1 <= len(description) <= 1024:
            add_error(errors, "description_length", "`description` must be 1-1024 characters.")
        if not description.strip():
            add_error(errors, "description_empty", "`description` must not be empty.")

    compatibility = data.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            add_error(errors, "compatibility_not_string", "`compatibility` must be a string.")
        else:
            info["compatibility_length"] = len(compatibility)
            if not 1 <= len(compatibility) <= 500:
                add_error(errors, "compatibility_length", "`compatibility` must be 1-500 characters.")

    license_value = data.get("license")
    if license_value is not None:
        if not isinstance(license_value, str) or not license_value.strip():
            add_error(errors, "license_not_string", "`license` must be a non-empty string if present.")

    metadata = data.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            add_error(errors, "metadata_not_mapping", "`metadata` must be a mapping.")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str):
                    add_error(errors, "metadata_key_not_string", "`metadata` keys must be strings.")
                if not isinstance(value, str):
                    add_error(
                        errors,
                        "metadata_value_not_string",
                        f"`metadata.{key}` must be a string value.",
                    )

    allowed_tools = data.get("allowed-tools")
    if allowed_tools is not None:
        if not isinstance(allowed_tools, str):
            add_error(errors, "allowed_tools_not_string", "`allowed-tools` must be a string.")
        else:
            add_warning(
                warnings,
                "allowed_tools_experimental",
                "`allowed-tools` is experimental; runtime support may vary.",
            )

    known_fields = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    unknown = sorted(str(key) for key in data.keys() if key not in known_fields)
    if unknown:
        add_warning(
            warnings,
            "unknown_frontmatter_fields",
            "Unknown frontmatter fields are allowed, but check client compatibility: " + ", ".join(unknown),
        )

    return info


def validate(skill_arg: str) -> dict[str, Any]:
    skill_dir, skill_file = resolve_skill_path(skill_arg)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    info: dict[str, Any] = {
        "skill_dir": str(skill_dir),
        "skill_file": str(skill_file),
    }

    if skill_file.name != "SKILL.md":
        add_error(errors, "skill_file_name", "Skill file must be named exactly SKILL.md.")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    if not skill_file.exists():
        add_error(errors, "skill_file_missing", f"File not found: {skill_file}")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    if frontmatter is None:
        add_error(errors, "frontmatter_missing", "SKILL.md must start with YAML frontmatter delimited by --- lines.")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        add_error(errors, "yaml_parse_error", f"Could not parse YAML frontmatter: {exc}")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    info.update(validate_field_types(data, skill_dir, errors, warnings))

    line_count = len(text.splitlines())
    estimated_tokens = count_estimated_tokens(text)
    info["line_count"] = line_count
    info["estimated_tokens"] = estimated_tokens

    if line_count > 500:
        add_warning(warnings, "skill_md_line_count", "SKILL.md is over the recommended 500-line limit.")
    if estimated_tokens > 5000:
        add_warning(warnings, "skill_md_token_estimate", "SKILL.md may exceed the recommended 5000-token limit.")
    if not body.strip():
        add_warning(warnings, "body_empty", "SKILL.md body is empty; the skill may not be useful after activation.")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "info": info}


def print_text_report(result: dict[str, Any]) -> None:
    status = "OK" if result["ok"] else "FAIL"
    warnings = result["warnings"]
    print(f"{status}: {result['info']['skill_file']}")
    if result["ok"] and warnings:
        print(f"WARNINGS: {len(warnings)}")
    for error in result["errors"]:
        print(f"ERROR [{error['code']}]: {error['message']}")
    for warning in warnings:
        print(f"WARNING [{warning['code']}]: {warning['message']}")
    info = result["info"]
    details = []
    for key in ("name_length", "description_length", "compatibility_length", "line_count", "estimated_tokens"):
        if key in info:
            details.append(f"{key}={info[key]}")
    if details:
        print("DETAILS: " + ", ".join(details))


def main() -> int:
    args = parse_args()
    result = validate(args.skill)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text_report(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
