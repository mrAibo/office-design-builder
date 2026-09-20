"""Office Design Builder domain package."""

from .errors import InvalidSpecError
from .models import PresentationSpecV1, StyleFingerprintV1

__all__ = ["InvalidSpecError", "PresentationSpecV1", "StyleFingerprintV1"]
