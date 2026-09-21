# Editable Layout Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add seven strictly validated, deterministic, natively editable PowerPoint layouts to version 1.

**Architecture:** Extend the existing layout-specific validation maps and introduce focused renderer functions behind a deterministic dispatch map. Resolve local image assets from the specification directory through an explicit renderer `asset_root`; keep all other layouts independent of filesystem context.

**Tech Stack:** Python 3.12, dataclasses, pathlib, Pillow, python-pptx, pytest, LibreOffice, pdftoppm.

**Spec:** `docs/plans/layout-expansion-design.md`

## Global Constraints

- Preserve existing `title` and `two_column` behavior and JSON compatibility.
- Use strict RED → GREEN TDD for every behavior change.
- Reject overflow-prone content before rendering; never truncate or silently shrink text.
- Keep identical input output byte-identical.
- Use only native editable PowerPoint objects.
- Keep tests and builds offline.
- Implement and commit one layout at a time.
- Every layout requires structural, deterministic, geometry, LibreOffice-render, and visual acceptance evidence.

---

### Task 1: Approved design and reusable validation/rendering helpers

**Files:**
- Create: `docs/plans/layout-expansion-design.md`
- Modify: `src/office_design_builder/models.py`
- Modify: `src/office_design_builder/renderers/pptx.py`
- Test: `tests/test_models.py`
- Test: `tests/test_pptx_renderer.py`

**Interfaces:**
- Produces: bounded-string, bounded-list, finite-number, and exact-key validation helpers.
- Produces: shared title, bullet, geometry-bound, and renderer dispatch helpers.

- [ ] Add focused tests for over-limit strings/lists and exact nested-object keys; observe expected RED failures.
- [ ] Implement dependency-free validation helpers that include exact field paths.
- [ ] Add renderer helpers without changing existing `title` and `two_column` output bytes.
- [ ] Run existing deterministic regression tests and full local gates.
- [ ] Commit the approved design and helper foundation as `refactor: prepare layout expansion foundation`.

### Task 2: `section` layout

**Files:**
- Modify: `src/office_design_builder/models.py`
- Modify: `src/office_design_builder/renderers/pptx.py`
- Modify: `tests/test_models.py`
- Modify: `tests/test_pptx_renderer.py`

**Interfaces:**
- Consumes: shared bounded-string and title helpers.
- Produces: strict `section` validation and native editable rendering.

- [ ] Add RED model tests for missing title, unknown fields, over-limit title/subtitle, and malformed subtitle.
- [ ] Add RED renderer test asserting editable title/subtitle, named accents, slide bounds, and absence of pictures.
- [ ] Implement minimal validation and rendering.
- [ ] Add deterministic-byte regression coverage.
- [ ] Render a disposable section slide through LibreOffice and visually review it.
- [ ] Run full gates and commit as `feat: add editable section layout`.

### Task 3: `title_bullets` layout

**Files:** same model/renderer/test files as Task 2.

**Interfaces:**
- Produces: `title_bullets` with 1–6 level-zero native bullet paragraphs.

- [ ] Add RED model tests for empty, oversized, too-many, and non-string bullets.
- [ ] Add RED structural test proving one input item maps to one bullet paragraph.
- [ ] Implement strict validation and native bullet text-frame rendering.
- [ ] Verify bounds, deterministic bytes, LibreOffice output, and visual composition.
- [ ] Run full gates and commit as `feat: add editable title bullets layout`.

### Task 4: `image_text` layout and safe asset resolution

**Files:**
- Modify: `src/office_design_builder/models.py`
- Modify: `src/office_design_builder/renderers/pptx.py`
- Modify: `src/office_design_builder/cli.py`
- Modify: `tests/test_models.py`
- Modify: `tests/test_pptx_renderer.py`
- Modify: `tests/test_cli.py`

**Interfaces:**
- Changes: `build_presentation(..., *, asset_root: Path | None = None) -> Path`.
- CLI passes `arguments.spec.parent` as `asset_root`.
- Produces: embedded local PNG/JPEG plus editable title/body.

- [ ] Add RED contract tests for URLs, absolute/drive-qualified paths, traversal, unsupported suffixes, invalid position, and body limits.
- [ ] Add RED CLI tests proving relative paths resolve from the spec directory and invalid/missing images fail without partial output.
- [ ] Add RED structural test proving one picture is embedded, aspect ratio is preserved, and body paragraphs remain editable.
- [ ] Implement asset preflight, containment checks, Pillow decoding, explicit `asset_root`, and contain-fit geometry.
- [ ] Verify left/right positions, deterministic bytes, LibreOffice rendering, and both visual variants.
- [ ] Run full gates and commit as `feat: add editable image text layout`.

### Task 5: `comparison` layout

**Files:** same model/renderer/test files as Task 2.

**Interfaces:**
- Produces: two named native editable comparison panels with 1–4 bullets per side.

- [ ] Add RED tests for headings, list limits, unknown fields, and malformed items.
- [ ] Add RED structural test for two headings, two bullet frames, balanced panels, and slide bounds.
- [ ] Implement validation and rendering without changing `two_column` semantics.
- [ ] Verify deterministic bytes, LibreOffice rendering, and visual balance.
- [ ] Run full gates and commit as `feat: add editable comparison layout`.

### Task 6: `timeline` layout

**Files:** same model/renderer/test files as Task 2.

**Interfaces:**
- Produces: ordered 2–6 event timeline using editable lines, markers, labels, and descriptions.

- [ ] Add RED nested-object tests for event count, exact keys, and label/description limits.
- [ ] Add RED structural test proving input order, native shapes, and editable event text.
- [ ] Implement deterministic horizontal spacing and alternating description placement within bounds.
- [ ] Verify 2-event and 6-event boundary cases, deterministic bytes, LibreOffice rendering, and visual review.
- [ ] Run full gates and commit as `feat: add editable timeline layout`.

### Task 7: `table` layout

**Files:** same model/renderer/test files as Task 2.

**Interfaces:**
- Produces: one native PowerPoint table with 2–6 columns and 1–8 data rows.

- [ ] Add RED tests for column/row limits, non-array rows, mismatched row width, invalid cells, and unknown fields.
- [ ] Add RED structural read-back test for table shape, dimensions, header, and every cell value.
- [ ] Implement equal-width native table rendering with palette-derived header and body styling.
- [ ] Verify largest allowed table, bounds, deterministic bytes, LibreOffice rendering, and visual review.
- [ ] Run full gates and commit as `feat: add editable table layout`.

### Task 8: `chart` layout

**Files:** same model/renderer/test files as Task 2.

**Interfaces:**
- Produces: native editable clustered-column or line-with-markers chart and embedded workbook.

- [ ] Add RED tests for chart type, category limits, exact series keys, series count, finite numeric values, boolean rejection, and category/value length mismatch.
- [ ] Add RED structural read-back tests for column and line chart types, categories, series names, and values.
- [ ] Implement native chart rendering using `ChartData`, deterministic order, and palette-derived series colors.
- [ ] Verify both chart types, maximum data shape, bounds, deterministic bytes, LibreOffice rendering, and visual review.
- [ ] Run full gates and commit as `feat: add editable chart layout`.

### Task 9: Integrated example, documentation, and Task 5 acceptance

**Files:**
- Modify: `examples/presentation.json`
- Add: `examples/assets/` only if the image is original/disposable and license-safe.
- Modify: `README.md`
- Modify: `PROJECT_LOG.md`
- Modify: CLI and end-to-end tests as necessary.

**Interfaces:**
- Produces: documented examples for every supported layout and final Task 5 evidence.

- [ ] Add a compact example deck exercising all nine layouts.
- [ ] Validate, build, verify, rebuild, and prove byte identity.
- [ ] Render every example slide through LibreOffice and visually review each image.
- [ ] Document every JSON contract, path-resolution rule, and fail-closed limit.
- [ ] Run full pytest, offline build, `twine check`, CLI help, example validate/build/verify, and `git diff --check`.
- [ ] Update `PROJECT_LOG.md` with exact commits, tests, visual evidence, and open issues.
- [ ] Commit as `docs: document expanded editable layouts`.

## Self-review

- Spec coverage: all seven layouts, validation, asset safety, native object semantics, determinism, structural checks, and visual acceptance map to Tasks 2–9.
- Placeholder scan: no deferred implementation behavior or unspecified error handling remains.
- Type consistency: all tasks use `PresentationSpecV1`, `StyleFingerprintV1`, and the single keyword-only `asset_root` renderer extension.
