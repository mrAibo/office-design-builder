# DOCX MVP design — 2026-09-23

## Decision
Add an opt-in, local-first editable DOCX path without changing the PPTX v1 contract or its renderer. A separate `DocumentSpecV1` contract has `{ "version": "1", "title": "...", "blocks": [...] }`. Blocks are ordered one-key objects: `heading` has `text` and optional `level` (1–3); `paragraph` has `text`; `bullets` has nonempty `items`; `table` has `columns` and nonempty equal-width `rows`; `image` has spec-relative local PNG/JPEG `path` and nonempty `alt`. Unknown fields, invalid/oversized content, URL/absolute/traversal paths and missing/bad images fail closed. The asset boundary must reject symlinks escaping the spec directory too.

`odb validate` dispatches to document or presentation by the exclusive top-level discriminator `blocks` versus `slides`; neither or both is invalid. `odb build` dispatches to DOCX only for a document spec and `.docx` output, PPTX only for a presentation spec and `.pptx` output; mismatches fail `INVALID_SPEC`. `odb verify` dispatches by `.docx`/`.pptx` and structurally checks editable paragraphs/tables and embedded images for DOCX. Reuse the existing `StyleFingerprintV1` for heading/body fonts and palette, but not its slide canvas. Preserve CLI error identifiers.

Render with `python-docx` as a runtime dependency. Apply explicit styles and sensible fixed page margins/width; all text/table content remains native/editable and images are embedded with bounded width. Set stable core metadata and normalize ZIP member timestamps/order/metadata so identical input bytes produce byte-identical DOCX output across processes. Keep domain modules subprocess-free.

## Alternatives rejected
- Convert PPTX slides to DOCX: mismatched semantics and poor editability.
- Pixel-perfect template replication: not achievable from a simple image fingerprint and outside the agreed MVP.

## Acceptance
TDD tests for strict schema, CLI format dispatch, path traversal/symlink and corrupt/missing image failures, editable headings/paragraphs/list/table/image structure, byte determinism, source example validate/build/verify, offline package build and wheel smoke. LibreOffice PDF rendering is an additional visual check when installed. No push, release tag or PyPI publication until separately agreed.
