# Subject-neutral Typst Renderer

An independent JSON-to-PDF renderer candidate. The package accepts a small, versioned JSON document model and renders headings, paragraphs, lists, callouts, fact cards, and simple relationship diagrams.

This is an experimental local implementation. It is not a production publishing system, a source-book converter, or a prepress/PDF-X tool.

## Requirements

- Python 3.13.2 for the pinned QA environment. The renderer build wrapper itself uses only the standard library.
- Typst CLI **0.15.1**. The build wrapper rejects other versions to keep the current smoke build reproducible.
- PT Sans and PT Mono installed on the system. Fonts are not bundled. See [DEPENDENCIES.md](DEPENDENCIES.md).
- Poppler `pdfinfo` for automated page-count verification in the smoke tests.

The renderer has no Python runtime packages. The independent JSON Schema test uses the exact development pins in `requirements-dev.txt`.

## Set up QA dependencies

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Build the invented example

From this directory:

```sh
python3 build.py --input examples/synthetic-book.json --output build/synthetic-book.pdf
pdfinfo build/synthetic-book.pdf
```

The wrapper validates the JSON before invoking Typst. Input JSON must be inside the project directory so Typst can resolve it within its project root. It writes only the output path supplied by the caller.

## Run smoke tests

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Tests validate the Draft 2020-12 schema and synthetic example with the independent `jsonschema` package, exercise invalid input and path rejection, and compile only invented content into temporary locations. The smoke test requires Typst and Poppler `pdfinfo`.

## Continuous integration

The [GitHub Actions workflow](.github/workflows/ci.yml) runs on pushes and pull requests. It pins its actions to full commit SHAs, uses pinned tool and package versions, grants the workflow token only `contents: read`, and runs schema validation, negative tests, smoke tests, and the synthetic PDF build.

## Input format

See [FUNCTIONAL-SPEC.md](FUNCTIONAL-SPEC.md) and [schema/renderer-v1.schema.json](schema/renderer-v1.schema.json) for schema and behavior. The included JSON example contains invented text and exercises every supported block type.

## Limitations

- Page content is expected to fit within the selected page. The renderer does not yet perform editorial overflow checks or automatic block splitting.
- The relationship diagram is a simple horizontal chain, not a general graph-layout engine.
- The project contains no image support, PDF box manipulation, OCR, source ingestion, external API calls, or bundled fonts.
- Passing the smoke tests demonstrates only that synthetic JSON compiles into a PDF with the requested page count. It does not establish visual, editorial, accessibility, or print-production quality.

## License

Released under the [MIT License](LICENSE). The example content is synthetic. See [PROVENANCE.md](PROVENANCE.md) for project and dependency notes.
