# Editable Layout Expansion Design

**Status:** Approved on 2026-09-21

## Goal

Extend `PresentationSpecV1` with seven native, editable PowerPoint layouts while preserving existing `title` and `two_column` behavior, deterministic output, offline operation, and stable `INVALID_SPEC` failures.

## Decisions

- Keep the existing `slides: list[dict[str, Any]]` public structure.
- Validate each layout with an explicit required/allowed field contract.
- Reject overflow-prone input before rendering; never truncate content or silently shrink it.
- Preserve all content as native PowerPoint objects: text boxes, shapes, pictures, tables, and charts.
- Support only local PNG/JPEG assets. Paths are relative to the specification file when invoked through the CLI.
- Support native editable column and line charts.
- Implement and accept one layout at a time.

## Alternatives rejected

### Per-layout dataclasses

They improve internal typing but require a broad serialization refactor and create unnecessary compatibility risk for the published v1 contract.

### Generic `slots` object

It is superficially extensible but weakens field-path errors and layout semantics. Explicit contracts are easier to validate, document, and render deterministically.

## Shared rules

Every slide:

- is a JSON object;
- has a supported `layout` string;
- contains exactly the fields allowed for that layout;
- uses non-empty strings after trimming;
- rejects boolean values where a number is expected;
- is validated fully before the output file is created.

Text limits count Python Unicode code points. Limits are contract boundaries, not renderer hints:

- slide title: 100 characters;
- section title: 80 characters;
- subtitle: 160 characters;
- bullet or body item: 160 characters;
- short label: 40 characters;
- descriptive text: 200 characters;
- image alt text: 160 characters;
- table cell: 80 characters;
- chart category: 30 characters;
- chart series name: 40 characters.

A value over its limit produces `InvalidSpecError(code="INVALID_SPEC")` with the exact field path. Renderers do not truncate or auto-fit.

## Layout contracts

### `section`

Purpose: introduce a new presentation section.

```json
{
  "layout": "section",
  "title": "Architecture",
  "subtitle": "How the pieces fit together"
}
```

Fields:

- required: `layout`, `title`;
- optional: `subtitle`;
- `title`: non-empty string, at most 80 characters;
- `subtitle`: non-empty string, at most 160 characters.

Rendering: large editable title, optional editable subtitle, palette-derived accent field and motif. No picture placeholder.

### `title_bullets`

Purpose: explain one topic with a concise list.

```json
{
  "layout": "title_bullets",
  "title": "Priorities",
  "bullets": ["Reliability", "Editability", "Determinism"]
}
```

Fields:

- required: `layout`, `title`, `bullets`;
- `title`: non-empty string, at most 100 characters;
- `bullets`: 1–6 non-empty strings, each at most 160 characters.

Rendering: editable title plus one editable text box containing real PowerPoint bullet paragraphs. Each input item maps to one level-zero paragraph.

### `image_text`

Purpose: combine one image with explanatory text.

```json
{
  "layout": "image_text",
  "title": "Product",
  "image": "assets/product.png",
  "image_alt": "Product dashboard",
  "body": ["Local-first workflow", "Editable output"],
  "image_position": "left"
}
```

Fields:

- required: `layout`, `title`, `image`, `image_alt`, `body`;
- optional: `image_position`;
- `title`: non-empty string, at most 100 characters;
- `image`: non-empty relative path ending in `.png`, `.jpg`, or `.jpeg`;
- `image_alt`: non-empty string, at most 160 characters;
- `body`: 1–5 non-empty strings, each at most 160 characters;
- `image_position`: `left` or `right`, default `left`.

Asset safety:

- reject absolute paths, URLs, drive-qualified paths, and `..` traversal;
- CLI resolution root is `spec_path.parent`;
- renderer receives an explicit `asset_root` and resolves the normalized path beneath it;
- missing, unreadable, corrupt, or wrong-format assets fail before saving output;
- image bytes are embedded in the PPTX; no external relationship remains.

Rendering: preserve source aspect ratio and contain the image within its image region without cropping. Body items remain editable bullet paragraphs. Set a deterministic picture name containing the alt text.

### `comparison`

Purpose: compare two named alternatives.

```json
{
  "layout": "comparison",
  "title": "Build or buy",
  "left_title": "Build",
  "left": ["Full control", "Higher effort"],
  "right_title": "Buy",
  "right": ["Fast adoption", "Vendor dependency"]
}
```

Fields:

- required: `layout`, `title`, `left_title`, `left`, `right_title`, `right`;
- `title`: at most 100 characters;
- `left_title`, `right_title`: at most 40 characters;
- `left`, `right`: each 1–4 non-empty strings, each at most 160 characters.

Rendering: two balanced editable panels with independent headings and bullet lists. This is semantically distinct from `two_column`, which has no column headings.

### `timeline`

Purpose: show an ordered sequence of milestones.

```json
{
  "layout": "timeline",
  "title": "Delivery plan",
  "events": [
    {"label": "Q1", "description": "Prototype"},
    {"label": "Q2", "description": "Pilot"}
  ]
}
```

Fields:

- required: `layout`, `title`, `events`;
- `title`: at most 100 characters;
- `events`: 2–6 objects;
- each event allows exactly `label` and `description`;
- `label`: non-empty string, at most 40 characters;
- `description`: non-empty string, at most 200 characters.

Rendering: native editable line, milestone markers, labels, and descriptions. Input order is presentation order. No automatic date parsing or sorting occurs.

### `table`

Purpose: present a compact matrix of text values.

```json
{
  "layout": "table",
  "title": "Plan comparison",
  "columns": ["Plan", "Price"],
  "rows": [["Basic", "$10"], ["Pro", "$25"]]
}
```

Fields:

- required: `layout`, `title`, `columns`, `rows`;
- `title`: at most 100 characters;
- `columns`: 2–6 non-empty strings, each at most 40 characters;
- `rows`: 1–8 arrays;
- every row length must equal the number of columns;
- every cell is a non-empty string of at most 80 characters.

Rendering: one native editable PowerPoint table. The first row is the styled header. Column widths are equal in v1; merged cells and per-cell styling are not supported.

### `chart`

Purpose: present one compact quantitative comparison or trend.

```json
{
  "layout": "chart",
  "title": "Revenue",
  "chart_type": "column",
  "categories": ["Q1", "Q2", "Q3"],
  "series": [
    {"name": "Actual", "values": [10, 12, 15]},
    {"name": "Target", "values": [9, 13, 16]}
  ]
}
```

Fields:

- required: `layout`, `title`, `chart_type`, `categories`, `series`;
- `title`: at most 100 characters;
- `chart_type`: `column` or `line`;
- `categories`: 2–8 non-empty strings, each at most 30 characters;
- `series`: 1–4 objects;
- each series allows exactly `name` and `values`;
- `name`: non-empty string, at most 40 characters;
- `values`: finite integers or floats, booleans rejected;
- each `values` length must equal `categories` length.

Rendering: native editable PowerPoint chart backed by its embedded workbook. `column` maps to clustered vertical columns; `line` maps to a line chart with markers. Series order and category order match the JSON input. No secondary axes, stacked mode, custom colors per point, or chart formulas are supported in v1.

## Renderer architecture

Keep `PresentationSpecV1` as the validation boundary. Move layout rendering out of the monolithic loop into focused private functions or a layout renderer map in `renderers/pptx.py`. Shared helpers own:

- title placement;
- editable bullet paragraphs;
- palette and typography tokens;
- slide-bound geometry;
- image path resolution and aspect-ratio fitting;
- deterministic chart/table styling.

`build_presentation` gains an optional keyword-only `asset_root: Path | None`. It is required when an `image_text` slide is present. CLI `build` passes `arguments.spec.parent`. Programmatic callers without image slides remain source compatible.

All assets are preflighted before `Presentation.save()`. A failed build must not leave a partial output or temporary package.

## Verification

Each layout is implemented as one vertical RED → GREEN slice and independently committed. Its acceptance requires:

1. malformed-slot model tests with exact field paths;
2. CLI `INVALID_SPEC` regression coverage;
3. structural PPTX read-back proving expected native object types and text/data;
4. byte-determinism test for identical input;
5. geometry assertions that every shape remains within slide bounds;
6. LibreOffice rendering of a disposable example;
7. visual review of the rendered slide;
8. full pytest, offline build, CLI help, example build/verify, and `git diff --check`.

The absence of LibreOffice must be reported as `NOT_RUN`, never as visual PASS. Current development environment has LibreOffice and `pdftoppm`, so all seven layouts require actual local rendering before acceptance.

## Compatibility

Existing `title` and `two_column` JSON remains valid and renders unchanged. Contract version stays `"1"` because this is an additive extension. Unknown fields and unsupported layouts remain errors. No new network dependency is introduced.
