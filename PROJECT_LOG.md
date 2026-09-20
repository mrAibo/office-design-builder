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
