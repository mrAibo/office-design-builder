"""Command-line interface for Office Design Builder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from office_design_builder.errors import InputNotFoundError, InvalidSpecError, VerifyError
from office_design_builder.inspectors.image import inspect_image
from office_design_builder.inspectors.pptx import inspect_pptx
from office_design_builder.models import PresentationSpecV1, StyleFingerprintV1
from office_design_builder.renderers.pptx import build_presentation
from office_design_builder.verify import verify_pptx


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="odb")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="inspect an image or PPTX reference")
    inspect.add_argument("reference", type=Path)
    inspect.add_argument("--output", required=True, type=Path)
    validate = commands.add_parser("validate", help="validate a semantic JSON specification")
    validate.add_argument("spec", type=Path)
    build = commands.add_parser("build", help="build an editable PPTX")
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


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "validate":
            PresentationSpecV1.from_dict(_read_json(arguments.spec))
        elif arguments.command == "inspect":
            if not arguments.reference.exists():
                raise InputNotFoundError(str(arguments.reference))
            inspector = inspect_pptx if arguments.reference.suffix.lower() == ".pptx" else inspect_image
            fingerprint = inspector(arguments.reference)
            arguments.output.write_text(
                json.dumps(fingerprint.to_dict(), indent=2, sort_keys=True) + "\n"
            )
        elif arguments.command == "build":
            spec = PresentationSpecV1.from_dict(_read_json(arguments.spec))
            fingerprint = StyleFingerprintV1.from_dict(_read_json(arguments.fingerprint))
            build_presentation(spec, fingerprint, arguments.output)
        elif arguments.command == "verify":
            print(json.dumps(verify_pptx(arguments.artifact), sort_keys=True))
    except (InputNotFoundError, InvalidSpecError, VerifyError) as exc:
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
