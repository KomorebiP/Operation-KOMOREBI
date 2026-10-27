"""OSL Discovery Bridge v0.1.0."""

from .adapter import emit_osl
from .core import ProposalError, digest_object, quotient_classes, synthesize, verify_certificate
from .registry import RegistryError, append_admission, verify_registry

__version__ = "0.1.0"

__all__ = [
    "ProposalError",
    "RegistryError",
    "append_admission",
    "digest_object",
    "emit_osl",
    "quotient_classes",
    "synthesize",
    "verify_certificate",
    "verify_registry",
]
