import pytest

from office_design_builder.errors import InvalidSpecError
from office_design_builder.models import PresentationSpecV1, StyleFingerprintV1


def test_style_fingerprint_round_trips_valid_payload() -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777},
        "palette": ["#112233", "#AABBCC"],
        "typography": {"heading_font": "Aptos Display", "body_font": "Aptos"},
        "geometry": {"corner_radius": 0.08},
        "density": "balanced",
        "motif": "offset_blocks",
    }

    fingerprint = StyleFingerprintV1.from_dict(payload)

    assert fingerprint.to_dict() == payload


@pytest.mark.parametrize(
    ("canvas", "field"),
    [
        ({"width": 13.333, "height": 7.5}, "aspect_ratio"),
        ({"width": "13.333", "height": 7.5, "aspect_ratio": 1.7777}, "width"),
        ({"width": True, "height": 7.5, "aspect_ratio": 1.7777}, "width"),
        ({"width": 13.333, "height": 0, "aspect_ratio": 1.7777}, "height"),
        ({"width": 13.333, "height": 7.5, "aspect_ratio": float("nan")}, "aspect_ratio"),
    ],
)
def test_style_fingerprint_rejects_invalid_canvas(canvas, field) -> None:
    payload = {
        "version": "1",
        "canvas": canvas,
        "palette": ["#112233"],
        "typography": {"heading_font": "Aptos Display", "body_font": "Aptos"},
        "geometry": {},
        "density": "balanced",
        "motif": "offset_blocks",
    }

    with pytest.raises(InvalidSpecError, match=rf"canvas\.{field}"):
        StyleFingerprintV1.from_dict(payload)


@pytest.mark.parametrize("palette", [[], "#112233", ["112233"], ["#GG2233"], [123]])
def test_style_fingerprint_rejects_invalid_palette(palette) -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777},
        "palette": palette,
        "typography": {"heading_font": "Aptos Display", "body_font": "Aptos"},
        "geometry": {},
        "density": "balanced",
        "motif": "offset_blocks",
    }

    with pytest.raises(InvalidSpecError, match="palette"):
        StyleFingerprintV1.from_dict(payload)


@pytest.mark.parametrize(
    ("typography", "field"),
    [
        ([], "typography"),
        ({"body_font": "Aptos"}, "typography.heading_font"),
        ({"heading_font": "", "body_font": "Aptos"}, "typography.heading_font"),
        ({"heading_font": "Aptos", "body_font": 42}, "typography.body_font"),
    ],
)
def test_style_fingerprint_rejects_invalid_typography(typography, field) -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777},
        "palette": ["#112233"],
        "typography": typography,
        "geometry": {},
        "density": "balanced",
        "motif": "offset_blocks",
    }

    with pytest.raises(InvalidSpecError, match=field):
        StyleFingerprintV1.from_dict(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("geometry", []),
        ("density", ""),
        ("density", 42),
        ("motif", ""),
        ("motif", 42),
    ],
)
def test_style_fingerprint_rejects_invalid_metadata(field, value) -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5, "aspect_ratio": 1.7777},
        "palette": ["#112233"],
        "typography": {"heading_font": "Aptos Display", "body_font": "Aptos"},
        "geometry": {},
        "density": "balanced",
        "motif": "offset_blocks",
    }
    payload[field] = value

    with pytest.raises(InvalidSpecError, match=field):
        StyleFingerprintV1.from_dict(payload)


def test_style_fingerprint_rejects_missing_required_field() -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5},
        "palette": ["#112233"],
        "typography": {"heading_font": "Aptos Display"},
        "geometry": {},
        "density": "balanced",
    }

    with pytest.raises(InvalidSpecError, match="motif") as caught:
        StyleFingerprintV1.from_dict(payload)

    assert caught.value.code == "INVALID_SPEC"


@pytest.mark.parametrize("title", ["", "   ", 42])
def test_presentation_spec_rejects_invalid_title(title) -> None:
    payload = {
        "version": "1",
        "title": title,
        "slides": [{"layout": "title", "title": "Slide"}],
    }

    with pytest.raises(InvalidSpecError, match="title"):
        PresentationSpecV1.from_dict(payload)


@pytest.mark.parametrize("slides", [[], {}, "slides", None])
def test_presentation_spec_rejects_invalid_slides_container(slides) -> None:
    payload = {"version": "1", "title": "Review", "slides": slides}

    with pytest.raises(InvalidSpecError, match="slides"):
        PresentationSpecV1.from_dict(payload)


@pytest.mark.parametrize("slide", [None, "slide", []])
def test_presentation_spec_rejects_non_object_slide(slide) -> None:
    payload = {"version": "1", "title": "Review", "slides": [slide]}

    with pytest.raises(InvalidSpecError, match=r"slides\[0\]"):
        PresentationSpecV1.from_dict(payload)


@pytest.mark.parametrize(
    ("slide", "field"),
    [
        ({"layout": "title", "title": ""}, "title"),
        ({"layout": "title", "title": 42}, "title"),
        ({"layout": "title", "title": "Title", "subtitle": ""}, "subtitle"),
        ({"layout": "title", "title": "Title", "subtitle": 42}, "subtitle"),
    ],
)
def test_presentation_spec_rejects_invalid_title_slide_fields(slide, field) -> None:
    payload = {"version": "1", "title": "Review", "slides": [slide]}

    with pytest.raises(InvalidSpecError, match=rf"slides\[0\]\.{field}"):
        PresentationSpecV1.from_dict(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("left", []),
        ("left", "text"),
        ("left", [""]),
        ("left", [42]),
        ("right", []),
        ("right", ["Valid", ""]),
    ],
)
def test_presentation_spec_rejects_invalid_two_column_items(field, value) -> None:
    slide = {
        "layout": "two_column",
        "title": "Results",
        "left": ["Left"],
        "right": ["Right"],
    }
    slide[field] = value
    payload = {"version": "1", "title": "Review", "slides": [slide]}

    with pytest.raises(InvalidSpecError, match=rf"slides\[0\]\.{field}"):
        PresentationSpecV1.from_dict(payload)


def test_presentation_spec_rejects_unknown_slide_fields() -> None:
    payload = {
        "version": "1",
        "title": "Review",
        "slides": [{"layout": "title", "title": "Title", "notes": "unsupported"}],
    }

    with pytest.raises(InvalidSpecError, match=r"slides\[0\].*notes"):
        PresentationSpecV1.from_dict(payload)


def test_presentation_spec_accepts_section_layout() -> None:
    payload = {
        "version": "1",
        "title": "Review",
        "slides": [
            {
                "layout": "section",
                "title": "Architecture",
                "subtitle": "How the pieces fit together",
            }
        ],
    }

    assert PresentationSpecV1.from_dict(payload).to_dict() == payload


@pytest.mark.parametrize(
    ("slide", "field"),
    [
        ({"layout": "section", "title": "x" * 81}, "title"),
        ({"layout": "section", "title": "Architecture", "subtitle": "x" * 161}, "subtitle"),
        ({"layout": "section", "title": "Architecture", "extra": "no"}, "extra"),
    ],
)
def test_presentation_spec_rejects_invalid_section_fields(slide, field) -> None:
    payload = {"version": "1", "title": "Review", "slides": [slide]}

    with pytest.raises(InvalidSpecError, match=rf"slides\[0\].*{field}"):
        PresentationSpecV1.from_dict(payload)


def test_presentation_spec_round_trips_supported_layouts() -> None:
    payload = {
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

    spec = PresentationSpecV1.from_dict(payload)

    assert spec.to_dict() == payload


def test_presentation_spec_rejects_unsupported_layout() -> None:
    payload = {
        "version": "1",
        "title": "Quarterly Review",
        "slides": [{"layout": "full_bleed_video", "title": "Unsupported"}],
    }

    with pytest.raises(InvalidSpecError, match="full_bleed_video") as caught:
        PresentationSpecV1.from_dict(payload)

    assert caught.value.code == "INVALID_SPEC"


@pytest.mark.parametrize(
    "slide",
    [
        {"layout": "title", "subtitle": "Missing title"},
        {"layout": "two_column", "title": "Missing right", "left": ["Only left"]},
    ],
)
def test_presentation_spec_rejects_missing_layout_slots(slide) -> None:
    payload = {"version": "1", "title": "Review", "slides": [slide]}

    with pytest.raises(InvalidSpecError, match=r"slides\[0\]") as caught:
        PresentationSpecV1.from_dict(payload)

    assert caught.value.code == "INVALID_SPEC"


@pytest.mark.parametrize(
    "factory",
    [StyleFingerprintV1.from_dict, PresentationSpecV1.from_dict],
)
@pytest.mark.parametrize("payload", [[], "json", None, 42])
def test_contracts_reject_non_object_payloads(factory, payload) -> None:
    with pytest.raises(InvalidSpecError, match="top-level value must be an object"):
        factory(payload)


@pytest.mark.parametrize(
    ("factory", "payload"),
    [
        (
            StyleFingerprintV1.from_dict,
            {
                "version": "2",
                "canvas": {"width": 13.333, "height": 7.5},
                "palette": ["#112233"],
                "typography": {"heading_font": "Aptos Display"},
                "geometry": {},
                "density": "balanced",
                "motif": "offset_blocks",
            },
        ),
        (
            PresentationSpecV1.from_dict,
            {"version": "2", "title": "Review", "slides": []},
        ),
    ],
)
def test_contracts_reject_unsupported_version(factory, payload) -> None:
    with pytest.raises(InvalidSpecError, match="version") as caught:
        factory(payload)

    assert caught.value.code == "INVALID_SPEC"
