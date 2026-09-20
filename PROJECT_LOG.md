# Project Log

## 2026-09-20 — Repository initialization and MVP design

- Task: Start Office Design Builder as a public GitHub project.
- Decisions: local-first Python CLI; semantic JSON specs; editable PPTX first; design fingerprints from PPTX/images; OfficeCLI reserved for tested Office-native adapters; LibreOffice for acceptance rendering.
- Files changed: design, implementation plan, `AGENTS.md`, `CONTEXT.md`, `PROJECT_LOG.md`.
- Tests run: none yet; implementation has not started.
- Open issues: image font inference, Canva export normalization, DOCX phase, OfficeCLI adapter acceptance criteria.
- Next action: implement Task 1 using strict TDD.

## 2026-09-20 — Task 1 bootstrap and schema contracts

- Task: Establish the Python package and versioned fingerprint/presentation contracts.
- Decisions: immutable dataclasses; explicit contract version `1`; supported MVP layouts limited to `title` and `two_column`; domain validation raises `InvalidSpecError` with stable code `INVALID_SPEC`.
- Files changed: `.gitignore`, `pyproject.toml`, `uv.lock`, package/error/model modules, and schema tests.
- Tests run: eight pytest cases on Python 3.12; package sdist and wheel built offline with preinstalled build dependencies; `git diff --check`.
- Open issues: the CLI entry point remains intentionally deferred to Task 5.
- Next action: implement Task 2 image reference inspection using strict TDD.

## 2026-09-20 — Task 2 image reference inspection

- Task: Derive deterministic style fingerprints from PNG and JPEG references.
- Decisions: Pillow median-cut quantization without dithering; palette ordering by frequency then hexadecimal color; generic typography defaults because font identity is not inferable from raster input.
- Files changed: Pillow dependency/lock data, image inspector package, and generated-image tests.
- Tests run: focused PNG and JPEG tests plus the full suite; offline package build; `git diff --check`.
- Open issues: raster fingerprints intentionally provide no font-identity inference.
- Next action: implement Task 3 PPTX reference inspection using strict TDD.

## 2026-09-20 — Task 3 PPTX reference inspection

- Task: Extract deterministic dimensions, layout inventory, and direct font/color evidence from PPTX references.
- Decisions: inspect native text runs without subprocesses; normalize evidence through `StyleFingerprintV1`; fall back to generic sans-serif typography when no explicit font is present.
- Files changed: python-pptx dependency/lock data, PPTX inspector, and generated-deck test.
- Tests run: focused generated-PPTX test plus the full suite; offline package build; `git diff --check`.
- Open issues: inherited theme colors/fonts are not yet resolved beyond directly materialized run evidence.
- Next action: implement Task 4 editable PPTX rendering using strict TDD.

## 2026-09-20 — Task 4 editable deterministic PPTX rendering

- Task: Render editable `title` and `two_column` slides from semantic contracts and style fingerprints.
- Decisions: native text boxes only; renderer-owned layout geometry; explicit font/color styling; canonical core metadata and ZIP timestamps for byte-identical output.
- Files changed: PPTX renderer package and structural/determinism integration tests.
- Tests run: focused structural renderer test; RED→GREEN byte-determinism regression; full suite; offline package build; `git diff --check`.
- Open issues: layout geometry is intentionally minimal and will need visual acceptance tuning with real fixtures.
- Next action: implement Task 5 CLI and structural verification using strict TDD.
