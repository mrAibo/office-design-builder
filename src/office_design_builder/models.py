"""Versioned semantic specification contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import PurePosixPath, PureWindowsPath
from re import fullmatch
from typing import Any

from .errors import InvalidSpecError


def _require_v1(version: str) -> None:
    if version != "1":
        raise InvalidSpecError(f"unsupported contract version: {version}")


def _require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InvalidSpecError(f"{path} must be an object")
    return value


def _require_positive_number(value: Any, path: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidSpecError(f"{path} must be a number")
    if not isfinite(value) or value <= 0:
        raise InvalidSpecError(f"{path} must be a finite positive number")


def _require_nonempty_string(value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise InvalidSpecError(f"{path} must be a non-empty string")


def _require_bounded_string(value: Any, path: str, maximum: int) -> None:
    _require_nonempty_string(value, path)
    if len(value) > maximum:
        raise InvalidSpecError(f"{path} must contain at most {maximum} characters")


def _require_nonempty_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise InvalidSpecError(f"{path} must be a non-empty array")
    return value


def _require_nonempty_string_list(value: Any, path: str) -> None:
    items = _require_nonempty_list(value, path)
    for index, item in enumerate(items):
        _require_nonempty_string(item, f"{path}[{index}]")


def _require_bounded_string_list(
    value: Any, path: str, *, maximum_items: int, maximum_length: int
) -> None:
    items = _require_nonempty_list(value, path)
    if len(items) > maximum_items:
        raise InvalidSpecError(f"{path} must contain at most {maximum_items} items")
    for index, item in enumerate(items):
        _require_bounded_string(item, f"{path}[{index}]", maximum_length)


def _require_relative_image_path(value: Any, path: str) -> None:
    _require_nonempty_string(value, path)
    assert isinstance(value, str)
    posix = PurePosixPath(value.replace("\\", "/"))
    windows = PureWindowsPath(value)
    if "://" in value or posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise InvalidSpecError(f"{path} must be a relative local path")
    if ".." in posix.parts:
        raise InvalidSpecError(f"{path} must not contain parent traversal")
    if posix.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise InvalidSpecError(f"{path} must reference a PNG or JPEG file")


def _validate_canvas(value: Any) -> None:
    canvas = _require_object(value, "canvas")
    for field in ("width", "height", "aspect_ratio"):
        if field not in canvas:
            raise InvalidSpecError(f"canvas.{field} is required")
        _require_positive_number(canvas[field], f"canvas.{field}")


def _validate_palette(value: Any) -> None:
    if not isinstance(value, list) or not value:
        raise InvalidSpecError("palette must be a non-empty array")
    for index, color in enumerate(value):
        if not isinstance(color, str) or fullmatch(r"#[0-9A-Fa-f]{6}", color) is None:
            raise InvalidSpecError(f"palette[{index}] must be a #RRGGBB color")


def _validate_typography(value: Any) -> None:
    typography = _require_object(value, "typography")
    for field in ("heading_font", "body_font"):
        if field not in typography:
            raise InvalidSpecError(f"typography.{field} is required")
        _require_nonempty_string(typography[field], f"typography.{field}")


@dataclass(frozen=True, slots=True)
class StyleFingerprintV1:
    version: str
    canvas: dict[str, float]
    palette: list[str]
    typography: dict[str, str]
    geometry: dict[str, Any]
    density: str
    motif: str

    @classmethod
    def from_dict(cls, payload: Any) -> StyleFingerprintV1:
        payload = _require_object(payload, "top-level value")
        try:
            fingerprint = cls(**payload)
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc
        _require_v1(fingerprint.version)
        _validate_canvas(fingerprint.canvas)
        _validate_palette(fingerprint.palette)
        _validate_typography(fingerprint.typography)
        _require_object(fingerprint.geometry, "geometry")
        _require_nonempty_string(fingerprint.density, "density")
        _require_nonempty_string(fingerprint.motif, "motif")
        return fingerprint

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PresentationSpecV1:
    version: str
    title: str
    slides: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, payload: Any) -> PresentationSpecV1:
        payload = _require_object(payload, "top-level value")
        try:
            spec = cls(**payload)
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc
        _require_v1(spec.version)
        _require_nonempty_string(spec.title, "title")
        _require_nonempty_list(spec.slides, "slides")
        required_fields = {
            "title": {"layout", "title"},
            "two_column": {"layout", "title", "left", "right"},
            "section": {"layout", "title"},
            "title_bullets": {"layout", "title", "bullets"},
            "image_text": {"layout", "title", "image", "image_alt", "body"},
            "comparison": {
                "layout",
                "title",
                "left_title",
                "left",
                "right_title",
                "right",
            },
            "timeline": {"layout", "title", "events"},
            "table": {"layout", "title", "columns", "rows"},
            "chart": {"layout", "title", "chart_type", "categories", "series"},
        }
        allowed_fields = {
            "title": required_fields["title"] | {"subtitle"},
            "two_column": required_fields["two_column"],
            "section": required_fields["section"] | {"subtitle"},
            "title_bullets": required_fields["title_bullets"],
            "image_text": required_fields["image_text"] | {"image_position"},
            "comparison": required_fields["comparison"],
            "timeline": required_fields["timeline"],
            "table": required_fields["table"],
            "chart": required_fields["chart"],
        }
        for index, raw_slide in enumerate(spec.slides):
            slide = _require_object(raw_slide, f"slides[{index}]")
            layout = slide.get("layout")
            if layout not in required_fields:
                raise InvalidSpecError(
                    f"slides[{index}].layout has unsupported value: {layout}"
                )
            missing = required_fields[layout] - slide.keys()
            if missing:
                fields = ", ".join(sorted(missing))
                raise InvalidSpecError(f"slides[{index}] missing required fields: {fields}")
            unknown = slide.keys() - allowed_fields[layout]
            if unknown:
                fields = ", ".join(sorted(unknown))
                raise InvalidSpecError(f"slides[{index}] has unknown fields: {fields}")
            title_limit = 80 if layout == "section" else 100
            _require_bounded_string(
                slide["title"], f"slides[{index}].title", title_limit
            )
            if "subtitle" in slide:
                _require_bounded_string(
                    slide["subtitle"], f"slides[{index}].subtitle", 160
                )
            if layout == "two_column":
                _require_nonempty_string_list(slide["left"], f"slides[{index}].left")
                _require_nonempty_string_list(slide["right"], f"slides[{index}].right")
            if layout == "title_bullets":
                _require_bounded_string_list(
                    slide["bullets"],
                    f"slides[{index}].bullets",
                    maximum_items=6,
                    maximum_length=160,
                )
            if layout == "image_text":
                _require_relative_image_path(
                    slide["image"], f"slides[{index}].image"
                )
                _require_bounded_string(
                    slide["image_alt"], f"slides[{index}].image_alt", 160
                )
                _require_bounded_string_list(
                    slide["body"],
                    f"slides[{index}].body",
                    maximum_items=5,
                    maximum_length=160,
                )
                position = slide.get("image_position", "left")
                if position not in {"left", "right"}:
                    raise InvalidSpecError(
                        f"slides[{index}].image_position must be left or right"
                    )
            if layout == "comparison":
                for field in ("left_title", "right_title"):
                    _require_bounded_string(
                        slide[field], f"slides[{index}].{field}", 40
                    )
                for field in ("left", "right"):
                    _require_bounded_string_list(
                        slide[field],
                        f"slides[{index}].{field}",
                        maximum_items=4,
                        maximum_length=160,
                    )
            if layout == "timeline":
                events = _require_nonempty_list(
                    slide["events"], f"slides[{index}].events"
                )
                if not 2 <= len(events) <= 6:
                    raise InvalidSpecError(
                        f"slides[{index}].events must contain between 2 and 6 items"
                    )
                for event_index, raw_event in enumerate(events):
                    path = f"slides[{index}].events[{event_index}]"
                    event = _require_object(raw_event, path)
                    if event.keys() != {"label", "description"}:
                        raise InvalidSpecError(
                            f"{path} must contain exactly label and description"
                        )
                    _require_bounded_string(event["label"], f"{path}.label", 40)
                    _require_bounded_string(
                        event["description"], f"{path}.description", 200
                    )
            if layout == "table":
                columns = slide["columns"]
                _require_bounded_string_list(
                    columns,
                    f"slides[{index}].columns",
                    maximum_items=6,
                    maximum_length=40,
                )
                if len(columns) < 2:
                    raise InvalidSpecError(
                        f"slides[{index}].columns must contain between 2 and 6 items"
                    )
                rows = _require_nonempty_list(slide["rows"], f"slides[{index}].rows")
                if len(rows) > 8:
                    raise InvalidSpecError(f"slides[{index}].rows must contain at most 8 items")
                for row_index, raw_row in enumerate(rows):
                    path = f"slides[{index}].rows[{row_index}]"
                    if not isinstance(raw_row, list) or len(raw_row) != len(columns):
                        raise InvalidSpecError(
                            f"{path} must contain exactly {len(columns)} cells"
                        )
                    for cell_index, cell in enumerate(raw_row):
                        _require_bounded_string(cell, f"{path}[{cell_index}]", 80)
            if layout == "chart":
                if slide["chart_type"] not in {"column", "line"}:
                    raise InvalidSpecError(
                        f"slides[{index}].chart_type must be column or line"
                    )
                categories = slide["categories"]
                _require_bounded_string_list(
                    categories,
                    f"slides[{index}].categories",
                    maximum_items=8,
                    maximum_length=30,
                )
                if len(categories) < 2:
                    raise InvalidSpecError(
                        f"slides[{index}].categories must contain between 2 and 8 items"
                    )
                series_items = _require_nonempty_list(
                    slide["series"], f"slides[{index}].series"
                )
                if len(series_items) > 4:
                    raise InvalidSpecError(
                        f"slides[{index}].series must contain at most 4 items"
                    )
                for series_index, raw_series in enumerate(series_items):
                    path = f"slides[{index}].series[{series_index}]"
                    series = _require_object(raw_series, path)
                    if series.keys() != {"name", "values"}:
                        raise InvalidSpecError(
                            f"{path} must contain exactly name and values"
                        )
                    _require_bounded_string(series["name"], f"{path}.name", 40)
                    values = _require_nonempty_list(series["values"], f"{path}.values")
                    if len(values) != len(categories):
                        raise InvalidSpecError(
                            f"{path}.values must match slides[{index}].categories length"
                        )
                    for value_index, value in enumerate(values):
                        if (
                            isinstance(value, bool)
                            or not isinstance(value, (int, float))
                            or not isfinite(value)
                        ):
                            raise InvalidSpecError(
                                f"{path}.values[{value_index}] must be a finite number"
                            )
        return spec

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DocumentSpecV1:
    version: str
    title: str
    blocks: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, payload: Any) -> DocumentSpecV1:
        payload = _require_object(payload, "top-level value")
        try:
            validated_blocks = _validate_document_spec_blocks_new(payload.get("blocks", []))
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc

        updated_payload = {**payload, "blocks": validated_blocks}
        try:
            spec = cls(**updated_payload)
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc

        _require_v1(spec.version)
        _require_nonempty_string(spec.title, "title")
        return spec

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_document_block(value: Any, path: str) -> dict[str, Any]:
    block = _require_object(value, path)
    if len(block.keys()) != 1:
        raise InvalidSpecError(f"{path} must contain exactly one field")
    block_type = next(iter(block.keys()))
    if block_type not in {"heading", "paragraph", "bullets", "table", "image"}:
        raise InvalidSpecError(f"{path} block must be one of: heading, paragraph, bullets, table, image")

    # Validate the content based on block type
    block_info = block[block_type]
    if block_type == "heading":
        _validate_heading(block_info, f"{path}.heading")
    elif block_type == "paragraph":
        _validate_paragraph(block_info, f"{path}.paragraph")
    elif block_type == "bullets":
        _validate_bullets(block_info, f"{path}.bullets")
    elif block_type == "table":
        _validate_table(block_info, f"{path}.table")
    elif block_type == "image":
        _validate_image(block_info, f"{path}.image")

    return block


def _validate_heading(value: Any, path: str) -> None:
    heading = _require_object(value, path)
    if heading.keys() - {"text", "level"}:
        raise InvalidSpecError(f"{path} has unknown fields")
    if "text" not in heading:
        raise InvalidSpecError(f"{path}.text is required")
    _require_bounded_string(heading["text"], f"{path}.text", 400)
    if "level" in heading:
        level = heading["level"]
        if isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 3:
            raise InvalidSpecError(f"{path}.level must be an integer between 1 and 3")


def _validate_paragraph(value: Any, path: str) -> None:
    paragraph = _require_object(value, path)
    if paragraph.keys() != {"text"}:
        raise InvalidSpecError(f"{path} must contain exactly text")
    if "text" not in paragraph:
        raise InvalidSpecError(f"{path}.text is required")
    _require_bounded_string(paragraph["text"], f"{path}.text", 800)


def _validate_bullets(value: Any, path: str) -> None:
    bullets = _require_object(value, path)
    if bullets.keys() != {"items"}:
        raise InvalidSpecError(f"{path} must contain exactly items")
    if "items" not in bullets:
        raise InvalidSpecError(f"{path}.items is required")
    _require_nonempty_list(bullets["items"], f"{path}.items")
    _require_bounded_string_list(bullets["items"], f"{path}.items", maximum_items=20, maximum_length=160)


def _validate_table(value: Any, path: str) -> None:
    table = _require_object(value, path)
    if table.keys() != {"columns", "rows"}:
        raise InvalidSpecError(f"{path} must contain exactly columns and rows")
    if "columns" not in table:
        raise InvalidSpecError(f"{path}.columns is required")
    _require_bounded_string_list(table["columns"], f"{path}.columns", maximum_items=10, maximum_length=40)
    if len(table["columns"]) < 2:
        raise InvalidSpecError(f"{path}.columns must contain at least 2 items")
    if "rows" not in table:
        raise InvalidSpecError(f"{path}.rows is required")
    rows = _require_nonempty_list(table["rows"], f"{path}.rows")
    if len(rows) > 8:
        raise InvalidSpecError(f"{path}.rows must contain at most 8 items")
    for row_index, raw_row in enumerate(rows):
        if not isinstance(raw_row, list) or len(raw_row) != len(table["columns"]):
            raise InvalidSpecError(
                f"{path}.rows[{row_index}] must contain exactly {len(table['columns'])} cells"
            )
        row_path = f"{path}.rows[{row_index}]"
        for cell_index, cell in enumerate(raw_row):
            _require_bounded_string(cell, f"{row_path}[{cell_index}]", 80)


def _validate_image(value: Any, path: str) -> None:
    image = _require_object(value, path)
    if image.keys() != {"path", "alt"}:
        raise InvalidSpecError(f"{path} must contain exactly path and alt")
    if "path" not in image:
        raise InvalidSpecError(f"{path}.path is required")
    _require_relative_image_path(image["path"], f"{path}.path")
    if "alt" not in image:
        raise InvalidSpecError(f"{path}.alt is required")
    _require_bounded_string(image["alt"], f"{path}.alt", 200)


def _validate_document_spec_blocks_new(value: Any) -> list[dict[str, Any]]:
    blocks = _require_nonempty_list(value, "blocks")
    for index, block in enumerate(blocks):
        path = f"blocks[{index}]"
        _validate_document_block(block, path)
    return blocks
