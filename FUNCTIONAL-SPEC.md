# Subject-neutral Typst Renderer — Functional Specification

**Specification version:** 0.1  
**Prepared:** 2026-10-26  
**Implementation basis:** the requirements in the P04 authorization and this specification only.

## Purpose

Render a versioned JSON document into a paginated PDF using Typst. The input model describes common document structure without assuming a subject, publisher, curriculum, source-book format, or brand.

## Input model

The input is UTF-8 JSON with this top-level structure:

```json
{
  "schema_version": 1,
  "document": {
    "title": "Invented document",
    "language": "en",
    "page": {
      "width_mm": 210,
      "height_mm": 297,
      "margin_mm": {"top": 18, "right": 18, "bottom": 18, "left": 18}
    }
  },
  "pages": []
}
```

Requirements:

- `schema_version` is the integer `1`.
- `document.title` and `document.language` are non-empty strings.
- Page dimensions and all margins are positive numbers. Margins must leave a positive content area.
- `pages` is a non-empty array. Each page has a unique non-empty `id`, an optional `section`, a non-empty `title`, an optional `subtitle`, and a non-empty `blocks` array.
- All user-visible strings are data. The renderer supplies no subject-specific instructional text.
- Unknown schema versions and unknown block types fail validation with a concise error.

## Supported blocks

Each block has a `type` discriminator.

| Type | Required fields | Behavior |
|---|---|---|
| `heading` | `level` (1–3), `text` | Render a heading at the selected hierarchy level. |
| `paragraph` | `text` | Render a body paragraph. |
| `list` | `ordered` (boolean), `items` (non-empty string array) | Render an ordered or unordered list. |
| `callout` | `tone` (`note`, `tip`, or `caution`), `title`, `text` | Render a labeled, visually distinct text block. |
| `fact_card` | `label`, `value`; optional `detail` | Render a compact label/value card. |
| `relationship_diagram` | `nodes` (2–6 strings), `relations` (one fewer string than nodes) | Render a left-to-right chain of labeled vector nodes connected by arrows. |

Text is treated as plain content. The renderer does not evaluate input as Typst source.

## Layout and visual system

- One JSON page produces one PDF page; page numbering is derived from the actual page array length.
- Page dimensions and margins come from the input document object.
- Use a newly defined neutral visual system with named tokens for ink, muted text, paper, rules, panels, and one accent color. Token values are original to this implementation.
- Use externally installed, openly licensed sans-serif and monospace families; do not bundle font files. This implementation uses PT Sans and PT Mono.
- Use open spacing and restrained rules; avoid fixed subject-specific illustrations or fixed editorial copy.
- The first release supports vector output only. It does not load external images or perform PDF prepress processing.

## Build interface

The command-line build accepts an input JSON path inside the project directory and an output PDF path. It validates the complete JSON model before invoking Typst. The Typst compiler version is pinned in setup documentation. Build output is written only to the requested path.

## Validation and failure behavior

The Python standard-library wrapper validates required keys, types, page dimensions, unique IDs, supported block types, list contents, and diagram cardinality. Development tests independently validate the schema and synthetic example with a Draft 2020-12 JSON Schema implementation. Invalid input exits non-zero before Typst runs and identifies the failing JSON location. Typst compilation failures are returned as non-zero exits with compiler diagnostics.

## Acceptance criteria

1. A synthetic JSON example exercises all six block types.
2. A clean build produces a non-empty PDF whose page count equals the input page count.
3. An invalid synthetic input is rejected before PDF generation.
4. Automated tests use temporary output locations and leave no PDF artifacts in the source tree.
5. The repository contains no real book text, publisher assets, bundled fonts, production PDFs, credentials, or generated content.
6. Documentation records project provenance, runtime tools, font licensing, and the renderer's software license.

## Out of scope

PDF ingestion, OCR, curriculum modeling, publisher-specific layouts, image generation, remote services, multi-format export, print-box assignment, and claims of production or prepress readiness.
