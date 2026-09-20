"""Stable domain errors."""


class InvalidSpecError(ValueError):
    """A semantic specification does not satisfy its versioned contract."""

    code = "INVALID_SPEC"


class VerifyError(ValueError):
    """A generated artifact fails structural verification."""

    code = "VERIFY_FAILED"


class InputNotFoundError(FileNotFoundError):
    """A required local input path does not exist."""

    code = "INPUT_NOT_FOUND"
