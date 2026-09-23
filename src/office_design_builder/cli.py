"""Command-line interface for Office Design Builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PIL import UnidentifiedImageError
from pptx.exc import PackageNotFoundError

from office_design_builder.errors import (
    InputNotFoundError,
    InvalidReferenceError,
    InvalidSpecError,
    OutputWriteError,
    VerifyError,
)
from office_design_builder.inspectors.image import inspect_image
from office_design_builder.inspectors.pptx import inspect_pptx
from office_design_builder.models import DocumentSpecV1, PresentationSpecV1, StyleFingerprintV1
from office_design_builder.renderers.docx import build_document
from office_design_builder.renderers.pptx import build_presentation
from office_design_builder.verify import verify_docx, verify_pptx


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="odb")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="inspect an image or PPTX reference")
    inspect.add_argument("reference", type=Path)
    inspect.add_argument("--output", required=True, type=Path)
    validate = commands.add_parser("validate", help="validate a semantic JSON specification")
    validate.add_argument("spec", type=Path)
    build = commands.add_parser("build", help="build an editable PPTX or DOCX")
    build.add_argument("spec", type=Path)
    build.add_argument("--fingerprint", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    verify = commands.add_parser("verify", help="verify a generated Office artifact")
    verify.add_argument("artifact", type=Path)
    return parser


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise InputNotFoundError(str(path))
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise InvalidSpecError(f"{path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise InvalidSpecError(f"{path}: top-level JSON value must be an object")
    return payload


def _parse_spec(payload: dict[str, Any]) -> PresentationSpecV1 | DocumentSpecV1:
    if ("slides" in payload) == ("blocks" in payload):
        raise InvalidSpecError("spec must contain exactly one of slides or blocks")
    if "blocks" in payload:
        return DocumentSpecV1.from_dict(payload)
    return PresentationSpecV1.from_dict(payload)


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "validate":
            _parse_spec(_read_json(arguments.spec))
        elif arguments.command == "inspect":
            if not arguments.reference.exists():
                raise InputNotFoundError(str(arguments.reference))
            suffix = arguments.reference.suffix.lower()
            inspectors = {
                ".png": inspect_image,
                ".jpg": inspect_image,
                ".jpeg": inspect_image,
                ".pptx": inspect_pptx,
            }
            if suffix not in inspectors:
                raise InvalidReferenceError(f"unsupported extension: {suffix or '<none>'}")
            inspector = inspectors[suffix]
            try:
                fingerprint = inspector(arguments.reference)
            except (OSError, ValueError, KeyError, PackageNotFoundError, UnidentifiedImageError) as exc:
                raise InvalidReferenceError(
                    f"{arguments.reference}: {exc}"
                ) from exc
            try:
                arguments.output.write_text(
                    json.dumps(fingerprint.to_dict(), indent=2, sort_keys=True) + "\n"
                )
            except OSError as exc:
                raise OutputWriteError(f"{arguments.output}: {exc}") from exc
        elif arguments.command == "build":
            spec = _parse_spec(_read_json(arguments.spec))
            fingerprint = StyleFingerprintV1.from_dict(_read_json(arguments.fingerprint))
            expected_suffix = ".docx" if isinstance(spec, DocumentSpecV1) else ".pptx"
            if arguments.output.suffix.lower() != expected_suffix:
                raise InvalidSpecError(f"output must have {expected_suffix} extension")
            try:
                if isinstance(spec, DocumentSpecV1):
                    build_document(spec, fingerprint, arguments.output, asset_root=arguments.spec.parent)
                else:
                    build_presentation(spec, fingerprint, arguments.output, asset_root=arguments.spec.parent)
            except OSError as exc:
                raise OutputWriteError(f"{arguments.output}: {exc}") from exc
        elif arguments.command == "verify":
            suffix = arguments.artifact.suffix.lower()
            if suffix not in {".pptx", ".docx"}:
                raise VerifyError("artifact must have .pptx or .docx extension")
            verifier = verify_docx if suffix == ".docx" else verify_pptx
            print(json.dumps(verifier(arguments.artifact), sort_keys=True))
    except (
        InputNotFoundError,
        InvalidReferenceError,
        InvalidSpecError,
        OutputWriteError,
        VerifyError,
    ) as exc:
        source = getattr(
            arguments,
            "spec",
            getattr(arguments, "reference", getattr(arguments, "artifact", "input")),
        )
        print(f"{exc.code}: {source}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
