# Office Design Builder

Office Design Builder (`odb`) creates editable PowerPoint presentations from compact, versioned semantic JSON and style fingerprints. The MVP is local-first, deterministic, and uses native PowerPoint text shapes rather than flattened screenshots.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for reproducible environment setup
- LibreOffice is optional for visual rendering checks

## Setup

```bash
uv sync --python 3.12 --extra dev
```

All normal tests and builds work without network access after this one-time dependency installation.

## Commands

```bash
# Inspect a PNG, JPEG, or PPTX reference
uv run odb inspect reference.png --output fingerprint.json

# Validate a presentation specification
uv run odb validate presentation.json

# Build an editable PPTX
uv run odb build presentation.json \
  --fingerprint fingerprint.json \
  --output presentation.pptx

# Structurally verify the generated package
uv run odb verify presentation.pptx
```

Stable CLI failures include `INPUT_NOT_FOUND`, `INVALID_SPEC`, and `VERIFY_FAILED`.

## End-to-end example

```bash
uv run --offline odb validate examples/presentation.json
uv run --offline odb build examples/presentation.json \
  --fingerprint examples/style-fingerprint.json \
  --output /tmp/office-design-builder-example.pptx
uv run --offline odb verify /tmp/office-design-builder-example.pptx
```

The result contains editable text boxes using the `title` and `two_column` layouts. Identical inputs produce byte-identical PPTX output.

## Development gates

```bash
uv run --offline python -m pytest -q
PIP_NO_INDEX=1 uv run --offline python -m build --no-isolation
uv run --offline python -m office_design_builder.cli --help
git diff --check
```

## Current MVP boundaries

- Image inspection extracts canvas dimensions and a deterministic dominant palette. Raster references cannot reliably reveal font identity, so generic typography defaults are recorded.
- PPTX inspection extracts dimensions, layout names, and directly materialized text-run font/color evidence. Theme inheritance is not fully resolved yet.
- The renderer prioritizes semantic editability and deterministic output over pixel-perfect reconstruction.
- DOCX, Canva API access, OCR, animations, and advanced template-preserving cloning remain post-MVP work.
