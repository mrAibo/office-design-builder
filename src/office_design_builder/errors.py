"""Stable domain errors."""


class InvalidSpecError(ValueError):
    """A semantic specification does not satisfy its versioned contract."""

    code = "INVALID_SPEC"
