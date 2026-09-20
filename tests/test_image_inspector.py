from pathlib import Path

from PIL import Image

from office_design_builder.inspectors.image import inspect_image


def test_inspect_image_extracts_canvas_and_dominant_palette(tmp_path: Path) -> None:
    image_path = tmp_path / "reference.png"
    image = Image.new("RGB", (4, 2))
    image.putdata(
        [
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
            (255, 0, 0),
            (255, 0, 0),
            (0, 0, 255),
            (0, 0, 255),
        ]
    )
    image.save(image_path)

    fingerprint = inspect_image(image_path, palette_size=2)

    assert fingerprint.canvas == {"width": 4.0, "height": 2.0, "aspect_ratio": 2.0}
    assert fingerprint.palette == ["#0000FF", "#FF0000"]


def test_inspect_jpeg_is_deterministic(tmp_path: Path) -> None:
    image_path = tmp_path / "reference.jpg"
    Image.new("RGB", (6, 4), color=(12, 34, 56)).save(
        image_path, quality=100, subsampling=0
    )

    first = inspect_image(image_path, palette_size=3)
    second = inspect_image(image_path, palette_size=3)

    assert first == second
    assert first.canvas["aspect_ratio"] == 1.5
    assert first.palette == ["#0C2239"]
