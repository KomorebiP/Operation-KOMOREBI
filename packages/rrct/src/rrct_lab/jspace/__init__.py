"""Public NumPy-only Jacobian workspace primitives."""

from .core import (
    JacobianFrame,
    JacobianFrameMetrics,
    MovingJacobianFrame,
    activation_variance_fraction,
    discover_jacobian_frame,
    jacobian_energy_capture,
    measure_jacobian_frame,
    projector_idempotence_defect,
    report_r2,
)

__all__ = [
    "JacobianFrame",
    "JacobianFrameMetrics",
    "MovingJacobianFrame",
    "activation_variance_fraction",
    "discover_jacobian_frame",
    "jacobian_energy_capture",
    "measure_jacobian_frame",
    "projector_idempotence_defect",
    "report_r2",
]

