# Office Design Builder — Design

## Goal

Build editable PowerPoint and Word artifacts from an existing Office template, a reference document, or an image while minimizing generated code and preserving design variety.

## Product principles

1. The model emits compact semantic specifications, never per-artifact Python.
2. Existing PPTX/DOCX templates are preserved rather than visually approximated when available.
3. Image references produce an explicit style fingerprint; they are not embedded as fake editable backgrounds unless requested.
4. Design families, tokens, motifs, and composable layouts provide variety without duplicated implementation.
5. OfficeCLI is the Office-native inspection/editing adapter; python-pptx/python-docx provide deterministic layout logic; LibreOffice is the fidelity renderer.
6. Every delivered artifact is structurally validated and visually renderable.

## Architecture

The initial product is a Python 3.12 CLI named `odb` with four boundaries:

- `inspect`: derive a normalized style fingerprint from PPTX or image input.
- `spec`: validate a semantic presentation specification.
- `build`: render an editable PPTX from the semantic spec plus fingerprint.
- `verify`: inspect the generated package and optionally render through LibreOffice.

The domain layer must not call subprocesses. OfficeCLI and LibreOffice integrations live behind adapters so they can be tested and replaced independently.

## MVP scope

The first vertical slice supports:

- PNG/JPEG reference inspection: dominant palette and canvas aspect ratio.
- PPTX reference inspection: slide size, theme-like font/color evidence, layout inventory, and reusable slide metadata.
- A versioned JSON presentation spec.
- Two composable layouts: `title` and `two_column`.
- Editable PPTX output via python-pptx.
- Deterministic style application from a fingerprint.
- Structural read-back test of the generated deck.

DOCX, Canva API access, advanced slide cloning, OfficeCLI mutations, OCR, animations, and pixel-level reconstruction remain post-MVP work.

## Data flow

```text
reference.pptx | reference.png
            ↓
       inspect adapter
            ↓
 style-fingerprint.v1.json
            +
 presentation-spec.v1.json
            ↓
       deterministic renderer
            ↓
        editable output.pptx
            ↓
 structural verification → optional LibreOffice render
```

## Design diversity

A style fingerprint stores palette, typography, geometry, density, and motif independently. Layouts consume semantic slots rather than absolute coordinates. The same content can therefore be rendered through different fingerprints, while the same fingerprint can produce multiple compositions.

No random variation is allowed by default. A future `variation_seed` may deterministically adjust approved ranges while preserving reproducibility.

## Error handling

CLI failures use stable codes and non-zero exits:

- `INPUT_NOT_FOUND`
- `UNSUPPORTED_REFERENCE`
- `INVALID_SPEC`
- `MISSING_ASSET`
- `BUILD_FAILED`
- `VERIFY_FAILED`
- `EXTERNAL_TOOL_FAILED`

Errors must identify the path and actionable correction without emitting secrets.

## Testing

- Unit tests for schema validation, palette extraction, and layout selection.
- Golden JSON fingerprints for deterministic inspection.
- Integration test that builds a PPTX and reads it back with python-pptx.
- Optional local acceptance test through LibreOffice when available.
- No network requirement for tests.
