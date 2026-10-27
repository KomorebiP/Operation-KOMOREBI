class RRCTLabError(Exception):
    """Base error for the configurable research laboratory."""


class ConfigError(RRCTLabError):
    """Raised when a configuration is invalid."""


class SafetyBoundaryError(ConfigError):
    """Raised when a configuration crosses a hard safety boundary."""


class DependencyError(RRCTLabError):
    """Raised when an optional experiment dependency is unavailable."""
