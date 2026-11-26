from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build.py"
EXAMPLE = ROOT / "examples/synthetic-book.json"
SCHEMA = ROOT / "schema/renderer-v1.schema.json"


@unittest.skipUnless(shutil.which("typst") and shutil.which("pdfinfo"), "requires Typst 0.15.1 and Poppler pdfinfo")
class RendererSmokeTests(unittest.TestCase):
    def run_build(self, source: Path, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(BUILD), "--input", str(source), "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_json_schema_descriptor_is_versioned(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)

    def assert_build_rejects(self, content: str | dict[str, object], expected_message: str) -> None:
        with tempfile.TemporaryDirectory(prefix="dizgidex-typst-invalid-", dir=ROOT / "tests") as temp_dir:
            temp = Path(temp_dir)
            invalid_input = temp / "invalid.json"
            invalid_output = temp / "must-not-exist.pdf"
            serialized = content if isinstance(content, str) else json.dumps(content)
            invalid_input.write_text(serialized, encoding="utf-8")

            result = self.run_build(invalid_input, invalid_output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(expected_message, result.stderr)
            self.assertFalse(invalid_output.exists())

    def test_malformed_json_is_rejected(self) -> None:
        self.assert_build_rejects('{"schema_version": 1,', "invalid JSON")

    def test_unsupported_block_is_rejected(self) -> None:
        book = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        book["pages"][0]["blocks"][0]["type"] = "executable_markup"
        self.assert_build_rejects(book, "unsupported block type")

    def test_missing_required_field_is_rejected(self) -> None:
        book = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        del book["document"]["title"]
        self.assert_build_rejects(book, "missing key(s): title")

    def test_unsafe_input_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dizgidex-typst-path-", dir=ROOT / "tests") as temp_dir:
            temp = Path(temp_dir)
            output = temp / "must-not-exist.pdf"
            outside_input = ROOT.parent / "synthetic-outside-project.json"
            result = self.run_build(ROOT / ".." / outside_input.name, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input JSON must be inside the project directory", result.stderr)
            self.assertFalse(output.exists())

            symlink = temp / "outside-link.json"
            symlink.symlink_to(outside_input)
            result = self.run_build(symlink, output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input JSON must be inside the project directory", result.stderr)
            self.assertFalse(output.exists())

    def test_synthetic_json_builds_two_page_pdf(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dizgidex-typst-smoke-", dir=ROOT / "tests") as temp_dir:
            output = Path(temp_dir) / "synthetic.pdf"
            result = self.run_build(EXAMPLE, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            diagnostics = f"{result.stdout}\n{result.stderr}".casefold()
            self.assertNotIn("unknown font family", diagnostics, diagnostics)
            self.assertNotIn("variable fonts are not currently supported", diagnostics, diagnostics)
            self.assertTrue(output.is_file())
            data = output.read_bytes()
            self.assertTrue(data.startswith(b"%PDF-"))
            self.assertGreater(len(data), 500)

            pdfinfo = shutil.which("pdfinfo") or "pdfinfo"
            info = subprocess.run(
                [pdfinfo, str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(info.returncode, 0, info.stderr)
            match = re.search(r"^Pages:\s+(\d+)\s*$", info.stdout, re.MULTILINE)
            self.assertIsNotNone(match, info.stdout)
            self.assertEqual(int(match.group(1)), 2)

    def test_invalid_synthetic_input_fails_before_pdf_creation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="dizgidex-typst-invalid-", dir=ROOT / "tests") as temp_dir:
            temp = Path(temp_dir)
            invalid_input = temp / "invalid.json"
            invalid_output = temp / "must-not-exist.pdf"
            book = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            book["schema_version"] = 99
            invalid_input.write_text(json.dumps(book), encoding="utf-8")

            result = self.run_build(invalid_input, invalid_output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("schema_version", result.stderr)
            self.assertFalse(invalid_output.exists())


class IndependentJsonSchemaTests(unittest.TestCase):
    def test_draft_2020_12_schema_and_synthetic_example_validate(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(example))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
