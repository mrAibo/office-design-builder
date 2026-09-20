from pathlib import Path
from time import sleep
from typing import Any, cast

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from office_design_builder.models import PresentationSpecV1, StyleFingerprintV1
from office_design_builder.renderers.pptx import build_presentation


def test_build_presentation_creates_editable_title_and_two_column_slides(
    tmp_path: Path,
) -> None:
    spec = PresentationSpecV1.from_dict(
        {
            "version": "1",
            "title": "Quarterly Review",
            "slides": [
                {"layout": "title", "title": "Quarterly Review", "subtitle": "Q3"},
                {
                    "layout": "two_column",
                    "title": "Results",
                    "left": ["Revenue increased"],
                    "right": ["Costs decreased"],
                },
            ],
        }
    )
    fingerprint = StyleFingerprintV1.from_dict(
        {
            "version": "1",
            "canvas": {"width": 10.0, "height": 5.0, "aspect_ratio": 2.0},
            "palette": ["#112233", "#DDEEFF"],
            "typography": {"heading_font": "Aptos", "body_font": "Aptos"},
            "geometry": {},
            "density": "balanced",
            "motif": "none",
        }
    )
    output_path = tmp_path / "output.pptx"

    build_presentation(spec, fingerprint, output_path)

    result = Presentation(str(output_path))
    assert len(result.slides) == 2
    assert result.slide_width == 9_144_000
    assert result.slide_height == 4_572_000
    text_shapes = [
        cast(Any, shape)
        for slide in result.slides
        for shape in slide.shapes
        if shape.has_text_frame
    ]
    texts = [shape.text for shape in text_shapes]
    assert texts == [
        "Quarterly Review",
        "Q3",
        "Results",
        "Revenue increased",
        "Costs decreased",
    ]
    assert all(
        shape.shape_type != MSO_SHAPE_TYPE.PICTURE
        for slide in result.slides
        for shape in slide.shapes
    )
    title_shape = cast(Any, result.slides[0].shapes[0])
    title_run = title_shape.text_frame.paragraphs[0].runs[0]
    assert str(title_run.font.color.rgb) == "112233"
    assert title_run.font.name == "Aptos"


def test_build_presentation_is_byte_deterministic(tmp_path: Path) -> None:
    spec = PresentationSpecV1.from_dict(
        {
            "version": "1",
            "title": "Determinism",
            "slides": [{"layout": "title", "title": "Same", "subtitle": "Input"}],
        }
    )
    fingerprint = StyleFingerprintV1.from_dict(
        {
            "version": "1",
            "canvas": {"width": 10.0, "height": 5.0, "aspect_ratio": 2.0},
            "palette": ["#112233"],
            "typography": {"heading_font": "Aptos", "body_font": "Aptos"},
            "geometry": {},
            "density": "balanced",
            "motif": "none",
        }
    )
    first = tmp_path / "first.pptx"
    second = tmp_path / "second.pptx"

    build_presentation(spec, fingerprint, first)
    sleep(2.1)
    build_presentation(spec, fingerprint, second)

    assert first.read_bytes() == second.read_bytes()
