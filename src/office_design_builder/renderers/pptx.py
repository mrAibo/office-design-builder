"""Deterministic editable PPTX rendering."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from zipfile import ZipFile, ZipInfo

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

from office_design_builder.models import PresentationSpecV1, StyleFingerprintV1

_FIXED_TIMESTAMP = datetime(2000, 1, 1)
_FIXED_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def _canonicalize_package(path: Path) -> None:
    with ZipFile(path, "r") as package:
        entries = [(info, package.read(info.filename)) for info in package.infolist()]

    temporary = path.with_suffix(".tmp")
    with ZipFile(temporary, "w") as package:
        for original, data in entries:
            canonical = ZipInfo(original.filename, date_time=_FIXED_ZIP_DATE)
            canonical.compress_type = original.compress_type
            canonical.external_attr = original.external_attr
            canonical.internal_attr = original.internal_attr
            canonical.create_system = original.create_system
            package.writestr(canonical, data)
    temporary.replace(path)


def _add_text(
    slide: Any,
    text: str,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    font_name: str,
    font_size: int,
    color: RGBColor,
) -> None:
    shape = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    paragraph = shape.text_frame.paragraphs[0]
    run = paragraph.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.color.rgb = color


def build_presentation(
    spec: PresentationSpecV1,
    fingerprint: StyleFingerprintV1,
    output_path: Path,
) -> Path:
    presentation = Presentation()
    presentation.core_properties.created = _FIXED_TIMESTAMP
    presentation.core_properties.modified = _FIXED_TIMESTAMP
    presentation.core_properties.last_modified_by = "office-design-builder"
    presentation.core_properties.revision = 1
    presentation.slide_width = Inches(fingerprint.canvas["width"])
    presentation.slide_height = Inches(fingerprint.canvas["height"])
    blank_layout = presentation.slide_layouts[6]
    color = RGBColor.from_string(fingerprint.palette[0].removeprefix("#"))
    heading_font = fingerprint.typography["heading_font"]
    body_font = fingerprint.typography["body_font"]

    for slide_spec in spec.slides:
        slide = presentation.slides.add_slide(blank_layout)
        if slide_spec["layout"] == "title":
            _add_text(
                slide,
                slide_spec["title"],
                left=0.8,
                top=1.3,
                width=8.4,
                height=0.8,
                font_name=heading_font,
                font_size=30,
                color=color,
            )
            _add_text(
                slide,
                slide_spec.get("subtitle", ""),
                left=0.8,
                top=2.3,
                width=8.4,
                height=0.5,
                font_name=body_font,
                font_size=18,
                color=color,
            )
            continue

        _add_text(
            slide,
            slide_spec["title"],
            left=0.6,
            top=0.4,
            width=8.8,
            height=0.6,
            font_name=heading_font,
            font_size=24,
            color=color,
        )
        _add_text(
            slide,
            "\n".join(slide_spec["left"]),
            left=0.6,
            top=1.3,
            width=4.1,
            height=3.0,
            font_name=body_font,
            font_size=16,
            color=color,
        )
        _add_text(
            slide,
            "\n".join(slide_spec["right"]),
            left=5.2,
            top=1.3,
            width=4.1,
            height=3.0,
            font_name=body_font,
            font_size=16,
            color=color,
        )

    presentation.save(str(output_path))
    _canonicalize_package(output_path)
    return output_path
