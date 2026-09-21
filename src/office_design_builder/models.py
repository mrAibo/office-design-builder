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
        }
        allowed_fields = {
            "title": required_fields["title"] | {"subtitle"},
            "two_column": required_fields["two_column"],
            "section": required_fields["section"] | {"subtitle"},
            "title_bullets": required_fields["title_bullets"],
            "image_text": required_fields["image_text"] | {"image_position"},
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
        return spec

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
