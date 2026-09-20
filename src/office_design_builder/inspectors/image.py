"""Deterministic style evidence extraction from raster images."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from PIL import Image

from office_design_builder.models import StyleFingerprintV1


def inspect_image(path: Path, *, palette_size: int = 5) -> StyleFingerprintV1:
    with Image.open(path) as source:
        image = source.convert("RGB")
        width, height = image.size
        quantized = image.quantize(
            colors=palette_size,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.NONE,
        )
        color_counts = quantized.getcolors() or []
        raw_palette = quantized.getpalette() or []

    colors: list[tuple[int, str]] = []
    for count, color_index in color_counts:
        index = cast(int, color_index)
        offset = index * 3
        red, green, blue = raw_palette[offset : offset + 3]
        colors.append((count, f"#{red:02X}{green:02X}{blue:02X}"))
    palette = [color for _, color in sorted(colors, key=lambda item: (-item[0], item[1]))]

    return StyleFingerprintV1(
        version="1",
        canvas={
            "width": float(width),
            "height": float(height),
            "aspect_ratio": width / height,
        },
        palette=palette,
        typography={"heading_font": "sans-serif", "body_font": "sans-serif"},
        geometry={},
        density="balanced",
        motif="none",
    )
