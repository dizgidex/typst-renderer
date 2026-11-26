# Dependencies and fonts

## Runtime

| Dependency | Use | Version/status |
|---|---|---|
| Typst CLI | JSON-driven document compilation | 0.15.1 required by `build.py` |
| Python | JSON validation and command wrapper | 3.13.2 in pinned QA; runtime standard library only |
| PT Sans | Body and heading typography | External installed font; not bundled |
| PT Mono | Page-number typography | External installed font; not bundled |

## Development and test tools

The independent Draft 2020-12 schema test uses `jsonschema==4.26.0`. Its required packages are pinned in [requirements-dev.txt](requirements-dev.txt). The renderer build wrapper does not import `jsonschema`.

Poppler `pdfinfo` is used by the smoke test to verify page count. It is not used by the build wrapper and is not a Python dependency. The P06 GitHub Actions workflow pins its Ubuntu package version.

## Font license record

PT Sans and PT Mono are distributed under the SIL Open Font License 1.1. Neither font is included in this project. Review the upstream notices before redistributing font files or derivatives: [PT Sans metadata](https://github.com/google/fonts/blob/main/ofl/ptsans/METADATA.pb), [PT Mono metadata](https://github.com/google/fonts/blob/main/ofl/ptmono/METADATA.pb).

The font licenses do not apply to this renderer's source code. The renderer is released under the MIT License; see [LICENSE](LICENSE).

## Font fallback observation

Typst embeds `Libertinus Serif Bold` as a fallback font in the current synthetic PDF, in addition to PT Sans and PT Mono. The fallback likely covers a symbol such as the right arrow; `pdffonts` does not map embedded fonts to individual glyphs. This has been visually checked in the synthetic example, but arbitrary glyph coverage remains unverified.

## Dependency inventory

- No Python packages are required.
- No JavaScript packages are required.
- No remote service or credential is used.
- No font, image, or PDF fixture is bundled.
