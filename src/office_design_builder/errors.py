"""Stable domain errors."""


class InvalidSpecError(ValueError):
    """A semantic specification does not satisfy its versioned contract."""

    code = "INVALID_SPEC"


class InvalidReferenceError(ValueError):
    """A visual reference is unsupported or cannot be inspected."""

    code = "INVALID_REFERENCE"


class OutputWriteError(OSError):
    """A requested output artifact cannot be written."""

    code = "OUTPUT_WRITE_FAILED"


class VerifyError(ValueError):
    """A generated artifact fails structural verification."""

    code = "VERIFY_FAILED"


class InputNotFoundError(FileNotFoundError):
    """A required local input path does not exist."""

    code = "INPUT_NOT_FOUND"
