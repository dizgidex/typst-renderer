#!/usr/bin/env python3
"""Validate a versioned JSON document and compile it with Typst."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
REQUIRED_TYPST_PREFIX = "typst 0.14.2"


class InputError(ValueError):
    """Raised when an input document does not match schema version 1."""


def fail(path: str, message: str) -> None:
    raise InputError(f"{path}: {message}")


def require_object(value: Any, path: str, required: set[str], optional: set[str] = frozenset()) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(path, "must be an object")
    missing = required - value.keys()
    extra = value.keys() - required - optional
    if missing:
        fail(path, f"missing key(s): {', '.join(sorted(missing))}")
    if extra:
        fail(path, f"unknown key(s): {', '.join(sorted(extra))}")
    return value


def require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(path, "must be a non-empty string")
    return value


def require_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(path, "must be a number")
    if not math.isfinite(value) or value <= 0:
        fail(path, "must be finite and greater than zero")
    return float(value)


def validate_block(block: Any, path: str) -> None:
    if not isinstance(block, dict):
        fail(path, "must be an object")
    kind = block.get("type")
    if not isinstance(kind, str):
        fail(f"{path}.type", "must be a string")

    if kind == "heading":
        data = require_object(block, path, {"type", "level", "text"})
        if type(data["level"]) is not int or data["level"] not in (1, 2, 3):
            fail(f"{path}.level", "must be the integer 1, 2, or 3")
        require_text(data["text"], f"{path}.text")
    elif kind == "paragraph":
        data = require_object(block, path, {"type", "text"})
        require_text(data["text"], f"{path}.text")
    elif kind == "list":
        data = require_object(block, path, {"type", "ordered", "items"})
        if type(data["ordered"]) is not bool:
            fail(f"{path}.ordered", "must be true or false")
        items = data["items"]
        if not isinstance(items, list) or not items:
            fail(f"{path}.items", "must be a non-empty array")
        for index, item in enumerate(items):
            require_text(item, f"{path}.items[{index}]")
    elif kind == "callout":
        data = require_object(block, path, {"type", "tone", "title", "text"})
        if data["tone"] not in ("note", "tip", "caution"):
            fail(f"{path}.tone", "must be note, tip, or caution")
        require_text(data["title"], f"{path}.title")
        require_text(data["text"], f"{path}.text")
    elif kind == "fact_card":
        data = require_object(block, path, {"type", "label", "value"}, {"detail"})
        require_text(data["label"], f"{path}.label")
        require_text(data["value"], f"{path}.value")
        if "detail" in data:
            require_text(data["detail"], f"{path}.detail")
    elif kind == "relationship_diagram":
        data = require_object(block, path, {"type", "nodes", "relations"})
        nodes = data["nodes"]
        relations = data["relations"]
        if not isinstance(nodes, list) or not 2 <= len(nodes) <= 6:
            fail(f"{path}.nodes", "must contain between 2 and 6 labels")
        for index, node in enumerate(nodes):
            require_text(node, f"{path}.nodes[{index}]")
        if not isinstance(relations, list) or len(relations) != len(nodes) - 1:
            fail(f"{path}.relations", "must contain one label between each neighboring pair of nodes")
        for index, relation in enumerate(relations):
            require_text(relation, f"{path}.relations[{index}]")
    else:
        fail(f"{path}.type", f"unsupported block type {kind!r}")


def validate_book(book: Any) -> None:
    model = require_object(book, "$", {"schema_version", "document", "pages"})
    if type(model["schema_version"]) is not int or model["schema_version"] != 1:
        fail("$.schema_version", "must be the integer 1")

    document = require_object(model["document"], "$.document", {"title", "language", "page"})
    require_text(document["title"], "$.document.title")
    require_text(document["language"], "$.document.language")

    page_spec = require_object(
        document["page"],
        "$.document.page",
        {"width_mm", "height_mm", "margin_mm"},
    )
    width = require_number(page_spec["width_mm"], "$.document.page.width_mm")
    height = require_number(page_spec["height_mm"], "$.document.page.height_mm")
    margins = require_object(
        page_spec["margin_mm"],
        "$.document.page.margin_mm",
        {"top", "right", "bottom", "left"},
    )
    margin_values = {
        edge: require_number(margins[edge], f"$.document.page.margin_mm.{edge}")
        for edge in ("top", "right", "bottom", "left")
    }
    if width <= margin_values["left"] + margin_values["right"]:
        fail("$.document.page.margin_mm", "horizontal margins must leave a positive content area")
    if height <= margin_values["top"] + margin_values["bottom"]:
        fail("$.document.page.margin_mm", "vertical margins must leave a positive content area")

    pages = model["pages"]
    if not isinstance(pages, list) or not pages:
        fail("$.pages", "must be a non-empty array")
    seen_ids: set[str] = set()
    for index, page in enumerate(pages):
        path = f"$.pages[{index}]"
        page_data = require_object(page, path, {"id", "title", "blocks"}, {"section", "subtitle"})
        page_id = require_text(page_data["id"], f"{path}.id")
        if page_id in seen_ids:
            fail(f"{path}.id", f"duplicate page id {page_id!r}")
        seen_ids.add(page_id)
        if "section" in page_data:
            require_text(page_data["section"], f"{path}.section")
        require_text(page_data["title"], f"{path}.title")
        if "subtitle" in page_data:
            require_text(page_data["subtitle"], f"{path}.subtitle")
        blocks = page_data["blocks"]
        if not isinstance(blocks, list) or not blocks:
            fail(f"{path}.blocks", "must be a non-empty array")
        for block_index, block in enumerate(blocks):
            validate_block(block, f"{path}.blocks[{block_index}]")


def read_book(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        fail(f"{path}:{exc.lineno}:{exc.colno}", f"invalid JSON: {exc.msg}")
    except OSError as exc:
        fail(str(path), f"cannot read input: {exc}")


def compile_book(input_path: Path, output_path: Path) -> int:
    typst = shutil.which("typst")
    if typst is None:
        print("build: Typst CLI is required; install the documented version separately", file=sys.stderr)
        return 2
    version = subprocess.run([typst, "--version"], capture_output=True, text=True, check=False)
    if version.returncode != 0 or not version.stdout.startswith(REQUIRED_TYPST_PREFIX):
        print(f"build: expected {REQUIRED_TYPST_PREFIX}; found {version.stdout.strip() or 'unknown'}", file=sys.stderr)
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        typst,
        "compile",
        "--diagnostic-format",
        "short",
        "--input",
        f"book={input_path.relative_to(ROOT).as_posix()}",
        str(ROOT / "main.typ"),
        str(output_path),
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode == 0:
        print(f"PDF written: {output_path}")
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="version 1 JSON input")
    parser.add_argument("--output", required=True, type=Path, help="PDF output path")
    args = parser.parse_args(argv)

    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    try:
        input_path.relative_to(ROOT)
    except ValueError:
        print("build: input JSON must be inside the project directory", file=sys.stderr)
        return 2
    if input_path == output_path:
        print("build: input and output paths must differ", file=sys.stderr)
        return 2
    if output_path.suffix.lower() != ".pdf":
        print("build: output path must end in .pdf", file=sys.stderr)
        return 2

    try:
        validate_book(read_book(input_path))
    except InputError as exc:
        print(f"build: invalid input: {exc}", file=sys.stderr)
        return 2
    return compile_book(input_path, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
