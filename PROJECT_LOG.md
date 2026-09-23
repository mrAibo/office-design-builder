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
- Open issues: none for Task 3. GitHub Actions run `35545580823` passed on exact commit `1235ed71acc8174729e9a7e9f2e3cdbd1bd3eb5e` for both `ubuntu-latest / Python 3.12` and `windows-latest / Python 3.12`.
- Next action: prepare Task 4 PyPI publication and stop at its human gate.

## 2026-09-21 — Task 4 PyPI publication preparation

- Task: Prepare complete public package metadata, checked distributions, and a tag-gated PyPI Trusted Publishing workflow without uploading a release.
- Decisions: use the protected GitHub environment `pypi`; scope `id-token: write` to the publish job; build and run `twine check` before publishing; never store a long-lived PyPI token; retain explicit approval for PyPI setup and first upload.
- Files changed: package metadata and locked development dependencies, publish workflow and regression tests, publishing guide, README, and this project log.
- Tests run: focused RED→GREEN metadata/workflow tests; local YAML parsing; full pytest suite; offline package build; `twine check`; CLI help; example validate/build/verify; `git diff --check`.
- Open issues: the PyPI project/pending publisher and protected GitHub `pypi` environment are not configured; no package has been uploaded.
- Next action: stop at the human gate and request approval before configuring PyPI/GitHub or creating the first publishing tag.

## 2026-09-21 — v0.1.1 PyPI release candidate

- Task: Execute the approved first PyPI publication as patch release `v0.1.1`.
- Decisions: bump the package version before tagging; require the pending PyPI publisher to exist before pushing the release tag; do not fall back to an API token.
- Files changed: package version, lockfile, publishing regression test, and this project log.
- Tests run: focused RED→GREEN version test; full pytest suite; offline package build; `twine check`; CLI help; example validate/build/verify; `git diff --check`.
- Open issues: none for the first PyPI publication.
- Next action: Task 4 is complete. Tag `v0.1.1` resolves to commit `af3227c60a14b45a43aac372b8ddb3aee7ae2fb9`; Publish workflow run `35549960252` succeeded; PyPI exposes both wheel and sdist; a clean Python 3.12 environment installed `office-design-builder==0.1.1`, built and verified the example, and reproduced byte-identical PPTX output.

## 2026-09-21 — Task 5 layout expansion design

- Task: Define the public contracts, fail-closed limits, asset rules, native Office semantics, and implementation sequence for seven additional editable layouts.
- Decisions: keep layout-specific dictionaries in `PresentationSpecV1`; reject overflow before rendering; resolve local PNG/JPEG assets relative to the specification file; support native column and line charts; implement and accept one layout per commit.
- Files changed: approved layout design, detailed implementation plan, and this project log.
- Tests run: documentation read-back and `git diff --check`; production behavior is unchanged at this design checkpoint.
- Open issues: implementation has not started.
- Next action: establish the shared validation/rendering foundation, then implement `section`, `title_bullets`, `image_text`, `comparison`, `timeline`, `table`, and `chart` in order.

## 2026-09-21 — Task 5 editable layout expansion

- Task: Add seven strict, native, editable PowerPoint layouts and prove them through a single nine-slide example.
- Decisions: preserve the version 1 dictionary API; fail closed on overflow; embed spec-relative PNG/JPEG assets; use native PowerPoint tables and column/line charts; recursively canonicalize embedded chart workbooks for cross-process byte determinism.
- Files changed: presentation validation, PPTX rendering, model/renderer/example tests, nine-slide example and image asset, README, and this project log.
- Tests run: focused RED→GREEN validation and renderer tests for every layout; 142-test suite; offline sdist/wheel build; CLI help; example validate/build/verify; delayed cross-process byte comparison; structural native table/chart/picture checks; LibreOffice PDF/PNG rendering and visual review of all nine slides; `git diff --check`.
- Open issues: automated visual regression and deeper PPTX inspection remain future work; DOCX output is not implemented.
- Next action: review the completed Task 5 changes and decide whether to prepare a new patch release.

## 2026-09-23 — DOCX MVP and v0.2.0 release candidate

- Task: Complete a separate editable DOCX path alongside the nine-layout PPTX renderer and prepare v0.2.0.
- Decisions: `DocumentSpecV1` uses ordered one-key heading/paragraph/bullets/table/image blocks; CLI dispatches by `blocks` versus `slides` and requires matching `.docx`/`.pptx` output. Reuse the style fingerprint's fonts/palette, not slide canvas. Reject invalid, missing, or symlink-escaped image assets before writing output; preserve deterministic native Office output. Keep publication behind full CI and wheel download-back acceptance.
- Files changed: document model/renderer/verifier/CLI, python-docx dependency and lock, DOCX example and tests, README, publishing guide, release version, and design note.
- Tests run: 162 tests; offline sdist/wheel build; `twine check`; fresh offline venv wheel install and both example build/verify flows; LibreOffice DOCX-to-PDF rendering and text inspection (one page). Exact release CI and PyPI download-back remain pending.
- Open issues: automatic visual regression and deeper PPTX theme inspection remain future work; DOCX supports the agreed basic block types, not pixel-perfect reference recreation.
- Next action: commit and push v0.2.0 candidate, require Linux/Windows CI on exact SHA, then push the version tag for Trusted Publishing and verify PyPI download-back.

## 2026-09-23 — v0.2.0 publication and index propagation check

- Task: Publish the verified DOCX/PPTX release.
- Decisions: push the clean candidate commit `230acb3d19203d88189bd670d034b45aa6b7b37a` and annotated tag `v0.2.0`; preserve OIDC Trusted Publishing without a long-lived token.
- Files changed: this post-release log only; the tagged package source is unchanged.
- Tests run: 162 local tests; offline build and `twine check`; clean local-wheel install and both DOCX/PPTX build/verify flows; Linux/Windows CI on the candidate commit (`35852478370`) and tag (`35852598452`) successful; Publish workflow `35852598570` build and PyPI publish jobs successful. Version-specific PyPI JSON exposes wheel and sdist with SHA-256 hashes. Downloaded the public wheel by its version-specific JSON URL, verified its SHA-256, installed it in a clean Python 3.12 environment, and built/verified byte-identical DOCX and PPTX examples.
- Open issues: automatic visual regression and deeper PPTX theme inspection remain future work; DOCX is an MVP, not pixel-perfect reference recreation. The canonical Simple API initially lagged the version-specific PyPI endpoint, then propagated.
- Next action: v0.2.0 release accepted. Exact-version install from `https://pypi.org/simple` in a new Python 3.12 environment succeeded; both installed DOCX and PPTX example build/verify paths passed with byte-identical duplicate builds. GitHub Release: `https://github.com/mrAibo/office-design-builder/releases/tag/v0.2.0`.

## 2026-09-23 — README output previews

- Task: Add visual examples to the GitHub README.
- Decisions: use two real LibreOffice renders of the repository fixtures (a PPTX chart slide and the upper portion of the DOCX page), not synthetic mockups; explicitly distinguish editable native elements from the embedded document illustration.
- Files changed: `README.md`, `assets/readme/presentation-preview.png`, `assets/readme/document-preview.png`, `PROJECT_LOG.md`.
- Tests run: 162 local tests, offline wheel/sdist build, CLI help and `git diff --check` passed; both PNGs were inspected and README paths resolved. GitHub image read-back follows push.
- Open issues: screenshots demonstrate appearance, not visual-regression coverage.
- Next action: verify previews and links, push docs-only change, confirm GitHub README images load.
