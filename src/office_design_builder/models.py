"""Versioned semantic specification contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .errors import InvalidSpecError


def _require_v1(version: str) -> None:
    if version != "1":
        raise InvalidSpecError(f"unsupported contract version: {version}")


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
    def from_dict(cls, payload: dict[str, Any]) -> StyleFingerprintV1:
        try:
            fingerprint = cls(**payload)
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc
        _require_v1(fingerprint.version)
        return fingerprint

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PresentationSpecV1:
    version: str
    title: str
    slides: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PresentationSpecV1:
        try:
            spec = cls(**payload)
        except TypeError as exc:
            raise InvalidSpecError(str(exc)) from exc
        _require_v1(spec.version)
        supported_layouts = {
            "title": {"layout", "title"},
            "two_column": {"layout", "title", "left", "right"},
        }
        for index, slide in enumerate(spec.slides):
            layout = slide.get("layout")
            if layout not in supported_layouts:
                raise InvalidSpecError(
                    f"slides[{index}].layout has unsupported value: {layout}"
                )
            missing = supported_layouts[layout] - slide.keys()
            if missing:
                fields = ", ".join(sorted(missing))
                raise InvalidSpecError(f"slides[{index}] missing required fields: {fields}")
        return spec

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
