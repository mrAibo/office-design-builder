# Office Design Builder MVP Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Deliver a tested CLI that derives a style fingerprint from an image or PPTX reference and builds an editable PPTX from a compact semantic JSON specification.

**Architecture:** A small Python package separates domain schemas, reference inspection, rendering, verification, and CLI concerns. External tools are optional adapters; the MVP remains offline and deterministic.

**Tech Stack:** Python 3.12, python-pptx, Pillow, pytest, stdlib argparse/json/dataclasses.

---

### Task 1: Bootstrap project and contracts

**Objective:** Establish package layout, commands, project rules, and versioned schema models.

**Files:**
- Create: `pyproject.toml`
- Create: `src/office_design_builder/__init__.py`
- Create: `src/office_design_builder/errors.py`
- Create: `src/office_design_builder/models.py`
- Create: `tests/test_models.py`

**Steps:**
1. Write failing tests for valid/invalid fingerprints and presentation specs.
2. Run focused tests and observe expected failures.
3. Implement minimal dataclass parsing and validation.
4. Run focused and full tests.
5. Commit.

### Task 2: Inspect image references

**Objective:** Produce deterministic fingerprint JSON from PNG/JPEG references.

**Files:**
- Create: `src/office_design_builder/inspectors/image.py`
- Create: `tests/test_image_inspector.py`

**Steps:**
1. Write a failing test using a generated fixture image.
2. Verify RED.
3. Implement aspect-ratio and dominant-palette extraction.
4. Verify GREEN and determinism.
5. Commit.

### Task 3: Inspect PPTX references

**Objective:** Extract slide dimensions, layout names, font evidence, and color evidence from PPTX.

**Files:**
- Create: `src/office_design_builder/inspectors/pptx.py`
- Create: `tests/test_pptx_inspector.py`

**Steps:**
1. Write a failing test that creates a tiny reference deck.
2. Verify RED.
3. Implement extraction through python-pptx.
4. Verify GREEN.
5. Commit.

### Task 4: Build an editable PPTX

**Objective:** Render `title` and `two_column` layouts from a spec and fingerprint.

**Files:**
- Create: `src/office_design_builder/renderers/pptx.py`
- Create: `tests/test_pptx_renderer.py`

**Steps:**
1. Write a failing integration test for output slide count, text, editable shapes, colors, and dimensions.
2. Verify RED.
3. Implement minimal deterministic renderer.
4. Verify GREEN and full suite.
5. Commit.

### Task 5: CLI and verification

**Objective:** Expose `inspect`, `validate`, `build`, and `verify` commands.

**Files:**
- Create: `src/office_design_builder/cli.py`
- Create: `src/office_design_builder/verify.py`
- Create: `tests/test_cli.py`

**Steps:**
1. Write failing subprocess tests for command behavior and stable errors.
2. Verify RED.
3. Implement argparse CLI and structural verification.
4. Verify GREEN.
5. Commit.

### Task 6: Documentation and real acceptance fixture

**Objective:** Document the workflow and prove an end-to-end build locally.

**Files:**
- Modify: `README.md`
- Create: `examples/style-fingerprint.json`
- Create: `examples/presentation.json`
- Create: `PROJECT_LOG.md`

**Steps:**
1. Build the example PPTX.
2. Run `odb verify` against it.
3. Render with LibreOffice if available.
4. Run `pytest -q`, packaging build, and `git diff --check`.
5. Update project log and commit.

## MVP acceptance gates

- G1: `pytest -q` exits 0.
- G2: `python -m build` exits 0.
- G3: example build emits an editable PPTX that python-pptx reads back with expected slide texts and shapes.
- G4: invalid specs fail non-zero with `INVALID_SPEC`.
- G5: no network access is required at runtime or during tests.
- G6: the GitHub repository contains no generated secrets or user documents.

## Risks and tradeoffs

- Font identity from images is not reliably inferable; MVP records generic typography defaults for image references.
- Canva-exported PPTX may flatten or group content; the MVP inspects evidence but does not yet normalize it.
- Pixel-perfect reconstruction is intentionally excluded from MVP; semantic editability is prioritized.
- OfficeCLI remains an optional future adapter until its role is covered by acceptance tests.
