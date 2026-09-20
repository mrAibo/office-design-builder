import pytest

from office_design_builder.errors import InvalidSpecError
from office_design_builder.models import PresentationSpecV1, StyleFingerprintV1


def test_style_fingerprint_round_trips_valid_payload() -> None:
    payload = {
        "version": "1",
        "canvas": {"width": 13.333, "height": 7.5},
        "palette": ["#112233", "#AABBCC"],
        "typography": {"heading_font": "Aptos Display", "body_font": "Aptos"},
        "geometry": {"corner_radius": 0.08},
        "density": "balanced",
        "motif": "offset_blocks",
    }

    fingerprint = StyleFingerprintV1.from_dict(payload)

    assert fingerprint.to_dict() == payload


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
