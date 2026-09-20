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

## 2026-09-20 — Task 5 CLI and structural verification

- Task: Expose `inspect`, `validate`, `build`, and `verify` commands with stable failures.
- Decisions: stdlib argparse/JSON; stable `INVALID_SPEC`, `INPUT_NOT_FOUND`, and `VERIFY_FAILED` identifiers; structural read-back requires slides and editable text shapes.
- Files changed: CLI entry point, verifier, error contracts, packaging command, and subprocess integration tests.
- Tests run: focused RED→GREEN subprocess tests plus the full suite; offline package build; module and installed-script help; `git diff --check`.
- Open issues: visual rendering verification remains optional until the real acceptance fixture in Task 6.
- Next action: complete Task 6 documentation and end-to-end acceptance fixture.

## 2026-09-20 — Task 6 documentation and acceptance fixture

- Task: Document the MVP workflow and prove a real local build from versioned examples.
- Decisions: keep generated PPTX/PDF/PNG artifacts outside the repository; document offline gates and explicit MVP boundaries.
- Files changed: `README.md`, example fingerprint/spec JSON, and this project log.
- Tests run: example validate/build/verify; python-pptx structural read-back; LibreOffice PDF export; two-slide PNG render with visual review; full pytest/build/help/diff gates.
- Open issues: the minimal layouts are technically clean but visually sparse, with substantial unused whitespace; composition refinement remains future work.
- Next action: review MVP acceptance gates and decide whether to tag a first release candidate.

## 2026-09-20 — Release-candidate visual refinement

- Task: Resolve the visual acceptance failures from the first MVP render and prepare a local RC candidate.
- Decisions: preserve the existing schema; use native editable accent shapes, compact responsive cards, and an offset-block title motif; do not publish or create a release tag without explicit confirmation.
- Files changed: PPTX renderer, structural verifier, renderer regression tests, and this project log.
- Tests run: focused RED→GREEN geometry and title-motif tests; full test/build/help/diff gates; example build/verify; LibreOffice rendering; visual review of both final slide PNGs.
- Open issues: richer content-density strategies and additional layouts remain post-MVP work.
- Next action: await explicit approval before creating or publishing a release tag.

## 2026-09-20 — v0.1.0 publication and user documentation

- Task: Publish the first release, verify downloaded assets, and replace the short README with an end-user guide.
- Decisions: distribute through GitHub Releases; document installation from the wheel, both version 1 JSON contracts, command behavior, troubleshooting, and current limitations; keep developer gates in the same README.
- Files changed: `README.md` and this project log.
- Tests run: 21-test suite; offline sdist/wheel build; clean-environment install from the downloaded release wheel; checksum verification; deterministic test presentation build; structural and visual verification; README command and link checks.
- Open issues: PyPI publication, Windows CI, stable handling of corrupt inspection inputs, deeper schema type validation, additional layouts, and visual verification automation remain future work.
- Next action: prioritize post-v0.1.0 work from user feedback and the remaining issue list.

## 2026-09-20 — Task 1 strict version 1 schema validation

- Task: Enforce field types, required values, allowed slide fields, and renderer-safe constraints at the version 1 contract boundary.
- Decisions: keep validation dependency-free in `models.py`; report field paths through `InvalidSpecError`; reject empty presentations, invalid slide containers, unknown slide fields, malformed colors, non-finite dimensions, and empty text slots.
- Files changed: schema models, model and CLI tests, README contract documentation, and this project log.
- Tests run: focused RED→GREEN tests for each new rule; full pytest suite; offline package build; CLI help; example validate/build/verify; `git diff --check`.
- Open issues: reference-file decoding and output-write failures are handled in Task 2.
- Next action: implement Task 2 stable reference-inspection failures.

## 2026-09-21 — Task 2 stable reference-inspection failures

- Task: Convert corrupt, unsupported, semantically empty, and unwritable reference workflows into stable CLI failures.
- Decisions: reserve `INPUT_NOT_FOUND` for absent inputs; use `INVALID_REFERENCE` for unreadable or unsupported references and empty PPTX files; use `OUTPUT_WRITE_FAILED` for fingerprint and presentation write failures.
- Files changed: CLI and domain errors, PPTX inspector, CLI regression tests, README error documentation, and this project log.
- Tests run: focused RED→GREEN subprocess tests for corrupt PNG/PPTX, empty PPTX, unsupported extensions, and missing output parents; full pytest suite; offline package build; CLI help; example validate/build/verify; `git diff --check`.
- Open issues: CI currently has no Windows job.
- Next action: implement Task 3 Linux and Windows CI.

## 2026-09-21 — Task 3 Linux and Windows CI

- Task: Add locked GitHub Actions checks for Python 3.12 on Ubuntu and Windows.
- Decisions: use one fail-independent OS matrix; install from `uv.lock` with `uv sync --frozen --extra dev`; run pytest, package build, and CLI help on both systems; keep LibreOffice rendering outside the Windows job.
- Files changed: GitHub Actions workflow, workflow regression test, README CI scope, and this project log.
- Tests run: focused RED→GREEN workflow test; local YAML parsing; full pytest suite; offline package build; CLI help; example validate/build/verify; `git diff --check`.
- Open issues: remote Ubuntu and Windows jobs must pass on the exact pushed commit before Task 3 is closed.
- Next action: push the Task 3 commit and verify both GitHub Actions jobs by commit SHA.
