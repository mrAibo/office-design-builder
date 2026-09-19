# Agent Instructions

## Scope

Build a local-first, deterministic tool for editable DOCX/PPTX generation from semantic specs and visual references. Prefer minimal dependencies and versioned contracts.

## Validation

Run from repository root:

```bash
pytest -q
python -m build
python -m office_design_builder.cli --help
```

For targeted tests:

```bash
pytest tests/path_to_test.py -q
```

Before commit:

```bash
git diff --check
```

## Engineering rules

- TDD: observe a focused test fail before production implementation.
- Domain modules do not call subprocesses.
- CLI errors use stable identifiers and non-zero exit codes.
- No network dependency for builds or tests.
- Do not commit generated user documents, proprietary templates, fonts, credentials, or downloaded Canva assets.
- Preserve editability; do not satisfy reconstruction by using a full-slide screenshot as the output.
- Keep deterministic output for identical inputs.

## Human Zones

Require explicit user confirmation before:

- publishing releases;
- changing repository visibility;
- adding cloud/API integrations or credentials;
- uploading user documents or assets to external services;
- introducing paid dependencies or services;
- deleting branches, releases, or stored artifacts.
