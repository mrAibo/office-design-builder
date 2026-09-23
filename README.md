# Office Design Builder

Office Design Builder (`odb`) creates editable PowerPoint presentations and Word documents from JSON specifications and visual references. Generated slides and document content use native editable Office elements rather than full-page screenshots.

Current release: [v0.2.0 on PyPI](https://pypi.org/project/office-design-builder/0.2.0/) (editable PPTX and DOCX).

## What it does

- Inspects PNG, JPEG, and PPTX references.
- Extracts slide or image dimensions, a color palette, and available typography evidence.
- Validates versioned JSON presentation specifications.
- Builds editable `.pptx` and `.docx` files with deterministic output.
- Verifies that generated Office packages can be opened and contain editable content.

The renderer supports nine layouts: `title`, `two_column`, `section`, `title_bullets`, `image_text`, `comparison`, `timeline`, `table`, and `chart`.

## Requirements

- Python 3.12 or newer
- PowerPoint or LibreOffice Impress to edit the generated presentation
- LibreOffice only if you want to render slides to PDF or images outside `odb`

`uv` is recommended for installation, but a standard Python virtual environment also works.

## Install the released package

Install the exact release from PyPI in a virtual environment.

With `uv`:

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python office-design-builder==0.2.0
```

On Windows PowerShell, use the virtual environment's Windows Python path:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe office-design-builder==0.2.0
```

On Linux or macOS, run the installed command as:

```bash
.venv/bin/odb --help
```

On Windows:

```powershell
.venv\Scripts\odb.exe --help
```

## Quick start

The repository contains working examples in [`examples/`](examples/). From a cloned repository with the development environment installed:

```bash
uv run --offline odb validate examples/presentation.json

uv run --offline odb build examples/presentation.json \
  --fingerprint examples/style-fingerprint.json \
  --output presentation.pptx

uv run --offline odb verify presentation.pptx
```

With the current nine-slide source example, a successful verification prints:

```json
{"editable_text_shapes": 27, "slide_count": 9}
```

The released v0.2.0 package supports this nine-slide example.

Open `presentation.pptx` in PowerPoint or LibreOffice Impress. Text and decorative shapes remain editable.

## DOCX example

The DOCX MVP uses a separate `DocumentSpecV1` JSON contract, not a slide specification. From a source checkout:

```bash
uv run --offline odb validate examples/document.json
uv run --offline odb build examples/document.json \
  --fingerprint examples/style-fingerprint.json \
  --output document.docx
uv run --offline odb verify document.docx
```

The top level requires `version`, `title`, and a nonempty `blocks` array. Each ordered block is a one-key object: `{"heading": {"text": "...", "level": 1}}` (level 1–3), `{"paragraph": {"text": "..."}}`, `{"bullets": {"items": ["..."]}}`, `{"table": {"columns": ["...", "..."], "rows": [["...", "..."]]}}`, or `{"image": {"path": "assets/example.png", "alt": "..."}}`. Image paths are local PNG/JPEG files relative to the JSON specification; no URLs, absolute paths, or traversal. Fonts and colors come from the same style fingerprint used for PPTX, while its slide canvas is not a Word page size. Text, lists, and tables remain native editable Word elements; images are embedded. `verify` checks structure rather than visual quality.

## Typical workflow

### 1. Create a style fingerprint

Use an existing PNG, JPEG, or PPTX as a visual reference:

```bash
odb inspect reference.png --output fingerprint.json
```

For images, `odb` records pixel dimensions, aspect ratio, and up to five dominant colors. Raster images do not provide reliable font information, so the generated fingerprint uses generic sans-serif font names.

For PPTX references, `odb` records slide dimensions, layout names, slide count, and directly assigned text-run fonts and RGB colors. Theme-inherited values may not appear in the result.

Review the generated fingerprint before building. You can replace colors and fonts with values available on the target computer.

### 2. Write a presentation specification

Create a JSON file that describes the slides and their editable content:

```json
{
  "version": "1",
  "title": "Quarterly review",
  "slides": [
    {
      "layout": "title",
      "title": "Quarterly review",
      "subtitle": "Q3 results"
    },
    {
      "layout": "two_column",
      "title": "Results",
      "left": [
        "Revenue increased",
        "Customer retention improved"
      ],
      "right": [
        "Operating costs decreased",
        "Support response time improved"
      ]
    }
  ]
}
```

Validate it before building:

```bash
odb validate presentation.json
```

The command exits with status `0` and prints nothing when the specification is valid.

### 3. Build the presentation

```bash
odb build presentation.json \
  --fingerprint fingerprint.json \
  --output presentation.pptx
```

Use a `.pptx` filename for the output. Identical specifications and fingerprints produce byte-identical PPTX files.

### 4. Verify the result

```bash
odb verify presentation.pptx
```

Verification opens the package and reports the number of slides and non-empty editable text shapes. It checks structure, not visual quality. Open or render the presentation before delivering it to confirm font availability, line wrapping, and layout.

## JSON contracts

Both contracts use `"version": "1"`. Other versions are rejected.

### Presentation specification

Top-level fields:

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `version` | string | yes | Contract version; currently `"1"` |
| `title` | string | yes | Presentation title stored in the semantic specification |
| `slides` | array | yes | Ordered slide definitions |

`title` must be a non-empty string, and `slides` must contain at least one slide object. Unknown fields are rejected inside slide objects.

Supported slide layouts:

| Layout | Required fields | Optional fields |
| --- | --- | --- |
| `title` | `layout`, `title` | `subtitle` |
| `two_column` | `layout`, `title`, `left`, `right` | none |
| `section` | `layout`, `title` | `subtitle` |
| `title_bullets` | `layout`, `title`, `bullets` | none |
| `image_text` | `layout`, `title`, `image`, `image_alt`, `body` | `image_position` |
| `comparison` | `layout`, `title`, `left_title`, `left`, `right_title`, `right` | none |
| `timeline` | `layout`, `title`, `events` | none |
| `table` | `layout`, `title`, `columns`, `rows` | none |
| `chart` | `layout`, `title`, `chart_type`, `categories`, `series` | none |

All layouts are fail-closed: oversized collections, overlong text, malformed rows/events/series, and unknown fields are rejected with `INVALID_SPEC` rather than truncated or silently resized. Tables and column/line charts are native editable PowerPoint objects.

`image_text` accepts only local PNG/JPEG paths relative to the presentation specification. URL, absolute, drive-qualified, and parent-traversal paths are rejected. Images are embedded in the PPTX; `image_position` is `left` by default and may be `right`.

The versioned [`examples/presentation.json`](examples/presentation.json) exercises all nine layouts. Build it from the repository root so its image path resolves correctly:

```bash
odb build examples/presentation.json \
  --fingerprint examples/style-fingerprint.json \
  --output presentation.pptx
```

### Style fingerprint

Required fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `version` | string | Contract version; currently `"1"` |
| `canvas` | object | `width`, `height`, and `aspect_ratio` |
| `palette` | array of strings | Hex RGB colors such as `"#17324D"` |
| `typography` | object | `heading_font` and `body_font` |
| `geometry` | object | Reference-specific structural evidence |
| `density` | string | Density label carried by the contract |
| `motif` | string | Motif label carried by the contract |

`canvas.width`, `canvas.height`, and `canvas.aspect_ratio` must be finite positive numbers. `palette` must contain at least one `#RRGGBB` color. Both typography values, `density`, and `motif` must be non-empty strings, and `geometry` must be an object.

For manually written fingerprints, `canvas.width` and `canvas.height` are PowerPoint dimensions in inches. Image inspection initially reports those values in pixels, so review or replace them before using an image fingerprint to build a presentation.

The renderer requires at least one palette color. It uses the first color for text and accents. When a second color is present, the renderer uses a light tint of it for decorative panels; otherwise it derives the panels from the first color. `typography` must contain both `heading_font` and `body_font`.

Example:

```json
{
  "version": "1",
  "canvas": {
    "width": 13.333,
    "height": 7.5,
    "aspect_ratio": 1.7777333333
  },
  "palette": ["#17324D", "#E7EEF5"],
  "typography": {
    "heading_font": "Aptos Display",
    "body_font": "Aptos"
  },
  "geometry": {},
  "density": "balanced",
  "motif": "offset_blocks"
}
```

## Command reference

```text
odb inspect REFERENCE --output FINGERPRINT.json
odb validate PRESENTATION-or-DOCUMENT.json
odb build PRESENTATION-or-DOCUMENT.json --fingerprint FINGERPRINT.json --output OUTPUT.pptx-or-.docx
odb verify OUTPUT.pptx-or-.docx
```

Use command-specific help for the accepted arguments:

```bash
odb inspect --help
odb validate --help
odb build --help
odb verify --help
```

## Errors and exit codes

Successful commands return exit code `0`. Handled input and validation errors return exit code `2` and start with a stable identifier:

- `INPUT_NOT_FOUND`: a required local input path does not exist.
- `INVALID_REFERENCE`: an image or PPTX reference is corrupt, unsupported, unreadable, or contains no slides.
- `INVALID_SPEC`: JSON is malformed or does not satisfy the version 1 contract.
- `OUTPUT_WRITE_FAILED`: the requested fingerprint or presentation output cannot be written.
- `VERIFY_FAILED`: the PPTX cannot be read, has no slides, or has no editable text shapes.

Example:

```text
INVALID_SPEC: presentation.json: slides[0] missing required fields: title
```

`odb inspect` accepts only `.png`, `.jpg`, `.jpeg`, and `.pptx` references. Create the output parent directory and ensure it is writable before running `inspect` or `build`.

## Troubleshooting

### A generated deck uses the wrong font

The requested font must be installed on the computer opening or rendering the presentation. Replace `heading_font` and `body_font` in the fingerprint with installed font names, then rebuild.

### An image fingerprint creates an incorrectly sized slide

Image inspection records pixel dimensions. Replace `canvas.width` and `canvas.height` with the intended PowerPoint size in inches. For a standard widescreen presentation, use approximately `13.333` by `7.5`.

### A PPTX fingerprint has an empty palette

The inspector records directly assigned RGB text colors. Colors inherited from a theme or master may not be materialized in individual text runs. Add the required hex colors to `palette` manually.

### Verification passes, but the slide looks wrong

`odb verify` checks package structure and editable text. It does not detect missing fonts, text overflow, or poor composition. Review the presentation in PowerPoint or LibreOffice Impress.

### The command is not found

Run the executable from the active virtual environment, or activate the environment first:

```bash
source .venv/bin/activate
odb --help
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
odb --help
```

## Current limitations

- Output supports editable PPTX and DOCX; neither format is a pixel-perfect reproduction of a visual reference.
- PPTX theme inheritance is only partially inspected.
- Raster references do not reveal font identity or semantic layout.
- OCR, animations, speaker notes, and template-preserving cloning are not implemented.
- Charts support clustered columns and lines with markers only; advanced axes, stacking, formulas, and per-point formatting are not supported.
- Tables use equal-width columns and do not support merged cells or per-cell input styling.
- `verify` performs structural checks, not visual checks.
- PyPI releases use tag-gated Trusted Publishing; see [the publishing guide](docs/publishing.md).

## Development setup

Clone the repository and install the locked development environment:

```bash
git clone https://github.com/mrAibo/office-design-builder.git
cd office-design-builder
uv sync --python 3.12 --extra dev
```

Run the project gates:

```bash
uv run --offline python -m pytest -q
PIP_NO_INDEX=1 uv run --offline python -m build --no-isolation
uv run --offline python -m office_design_builder.cli --help
git diff --check
```

GitHub Actions runs the locked test, package-build, and CLI-help gates on Python 3.12 for both Ubuntu and Windows. LibreOffice rendering is not part of the Windows job; the cross-platform suite verifies structure and deterministic package behavior.

The separate `Publish` workflow builds and checks distribution artifacts on pull requests. Matching version tags may publish only through the protected `pypi` environment and PyPI Trusted Publishing; repository setup and the first upload remain explicit human gates.

Generated build directories and user documents are intentionally not tracked.

## License

[MIT](LICENSE)
