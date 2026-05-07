#!/usr/bin/env python3
"""Validate harness-neutral eval suites for Agent Skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_ADAPTERS = {"codex", "cursor", "opencode", "pi", "claude-code", "generic"}
ALLOWED_ASSERTIONS = {
    "artifact_exists",
    "contains",
    "not_contains",
    "regex",
    "json_field",
    "schema_valid",
    "script_exit_zero",
    "rubric_score",
    "manual_review",
    "harness_event",
    "metric_available",
}
ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate evals/evals.json for harness-neutral skill tests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  uv run scripts/validate-eval-suite.py .\n"
            "  uv run scripts/validate-eval-suite.py ../my-skill --json\n\n"
            "Exit codes:\n"
            "  0  valid, possibly with warnings\n"
            "  1  validation errors found\n"
            "  2  invalid command-line arguments"
        ),
    )
    parser.add_argument("skill", help="Path to a skill directory or SKILL.md file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def resolve_skill_dir(raw: str) -> Path:
    path = Path(raw).expanduser().resolve()
    if path.is_file():
        return path.parent
    return path


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def add_warning(warnings: list[dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def path_exists(skill_dir: Path, eval_dir: Path, raw_path: str) -> bool:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.exists()
    return (eval_dir / path).exists() or (skill_dir / path).exists()


def validate_files(
    eval_case: dict[str, Any],
    skill_dir: Path,
    eval_dir: Path,
    eval_id: str,
    errors: list[dict[str, str]],
) -> None:
    files = eval_case.get("files", [])
    if files is None:
        return
    if not isinstance(files, list):
        add_error(errors, "files_not_list", f"{eval_id}: `files` must be a list of paths.")
        return
    for index, file_path in enumerate(files):
        if not is_non_empty_string(file_path):
            add_error(errors, "file_path_invalid", f"{eval_id}: files[{index}] must be a non-empty string.")
            continue
        if not path_exists(skill_dir, eval_dir, file_path):
            add_error(errors, "file_missing", f"{eval_id}: referenced file does not exist: {file_path}")


def validate_assertions(
    eval_case: dict[str, Any],
    eval_id: str,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    assertions = eval_case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        add_error(errors, "assertions_missing", f"{eval_id}: `assertions` must be a non-empty list.")
        return

    for index, assertion in enumerate(assertions):
        label = f"{eval_id}: assertions[{index}]"
        if not isinstance(assertion, dict):
            add_error(errors, "assertion_not_mapping", f"{label} must be an object.")
            continue

        assertion_type = assertion.get("type")
        if not is_non_empty_string(assertion_type):
            add_error(errors, "assertion_type_missing", f"{label} must have a non-empty `type`.")
            continue
        if assertion_type not in ALLOWED_ASSERTIONS:
            add_error(
                errors,
                "assertion_type_unknown",
                f"{label} has unsupported type {assertion_type!r}.",
            )

        evidence_keys = {"path", "target", "value", "pattern", "command", "schema", "metric", "field"}
        if not evidence_keys.intersection(assertion):
            add_warning(
                warnings,
                "assertion_weak",
                f"{label} has no concrete evidence key such as path, target, value, pattern, command, schema, metric, or field.",
            )


def validate_grading(
    eval_case: dict[str, Any],
    eval_id: str,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    grading = eval_case.get("grading")
    if grading is None:
        add_warning(warnings, "grading_missing", f"{eval_id}: `grading` is missing.")
        return
    if not isinstance(grading, dict):
        add_error(errors, "grading_not_mapping", f"{eval_id}: `grading` must be an object.")
        return

    method = grading.get("method")
    if method not in {"script", "rubric", "manual"}:
        add_error(errors, "grading_method_invalid", f"{eval_id}: grading.method must be script, rubric, or manual.")

    if method == "rubric":
        pass_score = grading.get("pass_score")
        if not isinstance(pass_score, (int, float)) or not 0 <= float(pass_score) <= 1:
            add_error(errors, "pass_score_invalid", f"{eval_id}: rubric grading needs pass_score from 0 to 1.")


def validate_eval_case(
    eval_case: Any,
    index: int,
    seen_ids: set[str],
    skill_dir: Path,
    eval_dir: Path,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    if not isinstance(eval_case, dict):
        add_error(errors, "eval_not_mapping", f"evals[{index}] must be an object.")
        return

    eval_id = eval_case.get("id")
    if not is_non_empty_string(eval_id):
        add_error(errors, "id_missing", f"evals[{index}] must have a non-empty `id`.")
        eval_id = f"evals[{index}]"
    else:
        if not ID_RE.fullmatch(eval_id):
            add_error(errors, "id_format", f"{eval_id}: `id` must use lowercase hyphen-case.")
        if eval_id in seen_ids:
            add_error(errors, "id_duplicate", f"{eval_id}: duplicate eval id.")
        seen_ids.add(eval_id)

    adapter = eval_case.get("harness_adapter")
    if adapter not in ALLOWED_ADAPTERS:
        add_error(
            errors,
            "adapter_invalid",
            f"{eval_id}: `harness_adapter` must be one of {', '.join(sorted(ALLOWED_ADAPTERS))}.",
        )
    if adapter == "generic" and not is_non_empty_string(eval_case.get("adapter_notes")):
        add_warning(warnings, "generic_adapter_notes_missing", f"{eval_id}: generic adapter should explain the runner.")

    for field in ("prompt", "expected_output"):
        if not is_non_empty_string(eval_case.get(field)):
            add_error(errors, f"{field}_missing", f"{eval_id}: `{field}` must be a non-empty string.")
        elif len(eval_case[field].strip()) < 20:
            add_warning(warnings, f"{field}_short", f"{eval_id}: `{field}` looks too short to be useful.")

    validate_files(eval_case, skill_dir, eval_dir, eval_id, errors)
    validate_assertions(eval_case, eval_id, errors, warnings)
    validate_grading(eval_case, eval_id, errors, warnings)


def validate(skill_arg: str) -> dict[str, Any]:
    skill_dir = resolve_skill_dir(skill_arg)
    eval_file = skill_dir / "evals" / "evals.json"
    eval_dir = eval_file.parent
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    info: dict[str, Any] = {
        "skill_dir": str(skill_dir),
        "eval_file": str(eval_file),
        "allowed_adapters": sorted(ALLOWED_ADAPTERS),
    }

    if not (skill_dir / "SKILL.md").exists():
        add_error(errors, "skill_missing", f"SKILL.md not found in {skill_dir}")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    if not eval_file.exists():
        add_error(errors, "eval_file_missing", f"File not found: {eval_file}")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    try:
        suite = json.loads(eval_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_error(errors, "json_parse_error", f"Could not parse evals.json: {exc}")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    if not isinstance(suite, dict):
        add_error(errors, "suite_not_mapping", "evals.json must contain a JSON object.")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    version = suite.get("version")
    if version != 1:
        add_error(errors, "version_invalid", "`version` must be 1.")

    evals = suite.get("evals")
    if not isinstance(evals, list) or not evals:
        add_error(errors, "evals_missing", "`evals` must be a non-empty list.")
        return {"ok": False, "errors": errors, "warnings": warnings, "info": info}

    seen_ids: set[str] = set()
    for index, eval_case in enumerate(evals):
        validate_eval_case(eval_case, index, seen_ids, skill_dir, eval_dir, errors, warnings)

    info["eval_count"] = len(evals)
    return {"ok": not errors, "errors": errors, "warnings": warnings, "info": info}


def print_text_report(result: dict[str, Any]) -> None:
    status = "OK" if result["ok"] else "FAIL"
    print(f"{status}: {result['info']['eval_file']}")
    if result["errors"]:
        print(f"ERRORS: {len(result['errors'])}")
    if result["warnings"]:
        print(f"WARNINGS: {len(result['warnings'])}")
    for error in result["errors"]:
        print(f"ERROR [{error['code']}]: {error['message']}")
    for warning in result["warnings"]:
        print(f"WARNING [{warning['code']}]: {warning['message']}")
    if "eval_count" in result["info"]:
        print(f"DETAILS: eval_count={result['info']['eval_count']}")


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
