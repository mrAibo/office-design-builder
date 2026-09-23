"""Focused tests for DocumentSpecV1 and DOCX renderer."""

import tempfile
from pathlib import Path

import pytest

from office_design_builder.models import DocumentSpecV1, StyleFingerprintV1
from office_design_builder.renderers.docx import build_document, _preflight_images


def test_document_spec_v1_valid():
    """Test DocumentSpecV1 accepts valid document blocks."""
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [
            {"heading": {"text": "Title", "level": 1}},
            {"paragraph": {"text": "This is a paragraph."}},
            {"bullets": {"items": ["Item 1", "Item 2", "Item 3"]}},
            {"table": {"columns": ["Header 1", "Header 2"], "rows": [["Cell 1", "Cell 2"], ["Cell 3", "Cell 4"]]}},
        ],
    }

    spec = DocumentSpecV1.from_dict(payload)
    assert spec.title == "Test Document"
    assert len(spec.blocks) == 4


def test_document_spec_v1_rejects_invalid_block():
    """Test DocumentSpecV1 rejects invalid block types."""
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [
            {"invalid_block": {"text": "Hello"}},
        ],
    }

    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_rejects_multiple_fields_per_block():
    """Test DocumentSpecV1 rejects blocks with multiple fields."""
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [
            {"heading": {"text": "Title"}, "extra": "field"},
        ],
    }

    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_heading_validation():
    """Test DocumentSpecV1 heading validation."""
    # Valid heading
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"heading": {"text": "Title", "level": 2}}],
    }
    spec = DocumentSpecV1.from_dict(payload)
    assert len(spec.blocks) == 1

    # Invalid level
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"heading": {"text": "Title", "level": 5}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_paragraph_validation():
    """Test DocumentSpecV1 paragraph validation."""
    # Valid paragraph
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"paragraph": {"text": "This is a valid paragraph with enough text length."}}],
    }
    spec = DocumentSpecV1.from_dict(payload)
    assert len(spec.blocks) == 1

    # Too long text
    long_text = "This is a paragraph that is way too long and exceeds the maximum allowed length for paragraph text. " * 10
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"paragraph": {"text": long_text}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_bullets_validation():
    """Test DocumentSpecV1 bullets validation."""
    # Valid bullets
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"bullets": {"items": ["Item 1", "Item 2", "Item 3"]}}],
    }
    spec = DocumentSpecV1.from_dict(payload)
    assert len(spec.blocks) == 1

    # Too many items
    too_many_items = [f"Item {i}" for i in range(25)]
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"bullets": {"items": too_many_items}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_table_validation():
    """Test DocumentSpecV1 table validation."""
    # Valid table
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"table": {"columns": ["Col 1", "Col 2"], "rows": [["Row 1 Cell 1", "Row 1 Cell 2"], ["Row 2 Cell 1", "Row 2 Cell 2"]]}}],
    }
    spec = DocumentSpecV1.from_dict(payload)
    assert len(spec.blocks) == 1

    # Too few columns
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"table": {"columns": ["Col 1"], "rows": [["Cell 1", "Cell 2"]]}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)

    # Too many rows
    too_many_rows = [[f"Cell {j}" for j in range(2)] for i in range(10)]
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"table": {"columns": ["Col 1", "Col 2"], "rows": too_many_rows}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_document_spec_v1_image_validation():
    """Test DocumentSpecV1 image validation."""
    # Valid image path
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"image": {"path": "test.png", "alt": "Test image"}}],
    }
    spec = DocumentSpecV1.from_dict(payload)
    assert len(spec.blocks) == 1

    # Too long alt text
    long_alt = "A" * 250
    payload = {
        "version": "1",
        "title": "Test Document",
        "blocks": [{"image": {"path": "test.png", "alt": long_alt}}],
    }
    with pytest.raises(Exception):  # Should raise InvalidSpecError
        DocumentSpecV1.from_dict(payload)


def test_preflight_images_empty():
    """Test _preflight_images with no image blocks."""
    spec = DocumentSpecV1(
        version="1",
        title="Test Document",
        blocks=[
            {"heading": {"text": "Title"}},
            {"paragraph": {"text": "Content"}},
        ],
    )
    assets = _preflight_images(spec, Path("/test/assets"))
    assert assets == {}


def test_build_document_basic():
    """Test build_document creates DOCX file."""
    spec = DocumentSpecV1(
        version="1",
        title="Test Document",
        blocks=[
            {"heading": {"text": "Title"}},
            {"paragraph": {"text": "This is a paragraph."}},
        ],
    )

    fingerprint = StyleFingerprintV1(
        version="1",
        canvas={"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777333333},
        palette=["#17324D", "#E7EEF5"],
        typography={"heading_font": "Aptos Display", "body_font": "Aptos"},
        geometry={},
        density="balanced",
        motif="offset_blocks",
    )

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        output_path = Path(tmp.name)

    try:
        result = build_document(spec, fingerprint, output_path, asset_root=Path("/tmp"))
        assert result.exists()
        assert result.suffix == ".docx"
    finally:
        output_path.unlink(missing_ok=True)


def test_build_document_with_bullets_and_table():
    """Test build_document handles bullets and table blocks."""
    spec = DocumentSpecV1(
        version="1",
        title="Test Document",
        blocks=[
            {"heading": {"text": "Document with Lists and Tables"}},
            {"bullets": {"items": ["First bullet point", "Second bullet point", "Third bullet point"]}},
            {"table": {"columns": ["Name", "Value"], "rows": [["Alice", "25"], ["Bob", "30"]]}},
        ],
    )

    fingerprint = StyleFingerprintV1(
        version="1",
        canvas={"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777333333},
        palette=["#17324D", "#E7EEF5"],
        typography={"heading_font": "Aptos Display", "body_font": "Aptos"},
        geometry={},
        density="balanced",
        motif="offset_blocks",
    )

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        output_path = Path(tmp.name)

    try:
        result = build_document(spec, fingerprint, output_path, asset_root=Path("/tmp"))
        assert result.exists()
        assert result.suffix == ".docx"
    finally:
        output_path.unlink(missing_ok=True)


def test_build_document_image_validation():
    """Test build_document validates image paths."""
    spec = DocumentSpecV1(
        version="1",
        title="Test Document with Image",
        blocks=[
            {"heading": {"text": "Title"}},
            {"image": {"path": "nonexistent.png", "alt": "Missing image"}},
        ],
    )

    fingerprint = StyleFingerprintV1(
        version="1",
        canvas={"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777333333},
        palette=["#17324D", "#E7EEF5"],
        typography={"heading_font": "Aptos Display", "body_font": "Aptos"},
        geometry={},
        density="balanced",
        motif="offset_blocks",
    )

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        output_path = Path(tmp.name)

    try:
        # Should raise InputNotFoundError because image doesn't exist
        with pytest.raises(Exception):
            build_document(spec, fingerprint, output_path, asset_root=Path("/tmp"))
    finally:
        output_path.unlink(missing_ok=True)
