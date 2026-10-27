"""Exact ANC-4 calibration for a necessary four-dimensional ambient fiber.

The calibration deliberately sits outside the learned flatness experiment.  It
is an oracle and assay fixture for a stronger question: can four independent
continuous lag values be retained while the eight-dimensional semantic state
is reset to an exact one-hot anchor after every update?

The canonical state is ``h = (p, q)`` with ``p in R^8`` and ``q in R^4``.
The semantic projection is saturated, ``p = e_s``.  The ambient coordinate
``q`` is a length-four shift register.  At time ``t`` it contains
``(u[t-4], u[t-3], u[t-2], u[t-1])``, so its first coordinate is the online
delay-four output.  No claim about a learned model follows from this explicit
direct-sum positive control.

Every construction is transported under an arbitrary invertible coordinate
map ``x' = T x``.  Consequently the invariant ambient object is the vertical
fiber ``ker(semantic_projection)``.  A particular matrix called ``Q`` is only
the projector associated with the chosen splitting.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

import torch
from torch.nn import functional as F


SEMANTIC_DIMENSION = 8
AMBIENT_DIMENSION = 4
STATE_DIMENSION = SEMANTIC_DIMENSION + AMBIENT_DIMENSION
DELAY = 4
SCHEMA_PREFIX = "komorebi.neuralese.ambient_delay"
SUPPORTED_DTYPES = frozenset(
    {
        torch.float16,
        torch.bfloat16,
        torch.float32,
        torch.float64,
    }
)


def _require_supported_dtype(dtype: torch.dtype) -> None:
    if not isinstance(dtype, torch.dtype) or dtype not in SUPPORTED_DTYPES:
        raise TypeError("dtype must be float16, bfloat16, float32, or float64")


def _audit_tensor(value: torch.Tensor) -> torch.Tensor:
    """Copy a small receipt tensor to CPU float64 for backend-independent audit math."""

    return value.detach().to(device="cpu", dtype=torch.float64)


def _validation_relative_tolerance(dtype: torch.dtype, dimension: int) -> float:
    """Return a bounded, dtype- and dimension-aware invariant tolerance."""

    _require_supported_dtype(dtype)
    if isinstance(dimension, bool) or not isinstance(dimension, int) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    epsilon = float(torch.finfo(dtype).eps)
    # The cap is essential: the old 512*n*eps rule exceeded one in low
    # precision and therefore accepted zero matrices as identities.
    return min(1.0 / 16.0, max(32.0 * float(torch.finfo(torch.float64).eps), 4.0 * dimension * epsilon))


def _rank_relative_tolerance(
    dtype: torch.dtype,
    dimension: int,
    requested: float | None,
) -> float:
    _require_supported_dtype(dtype)
    if requested is not None and (
        not math.isfinite(requested) or not 0.0 < requested < 1.0
    ):
        raise ValueError("relative_tolerance must lie strictly between zero and one")
    floor = min(
        1.0 / 8.0,
        max(
            32.0 * float(torch.finfo(torch.float64).eps),
            2.0 * dimension * float(torch.finfo(dtype).eps),
        ),
    )
    return max(floor, requested or 0.0)


def _condition_number(value: torch.Tensor) -> float:
    singular = torch.linalg.svdvals(_audit_tensor(value))
    if singular.numel() == 0 or float(singular[-1]) == 0.0:
        return math.inf
    return float(singular[0] / singular[-1])


def _require_resolvable_coordinates(
    coordinate_map: torch.Tensor,
    *,
    dtype: torch.dtype,
    rank_tolerance: float | None = None,
) -> float:
    tolerance = _rank_relative_tolerance(dtype, STATE_DIMENSION, rank_tolerance)
    condition = _condition_number(coordinate_map)
    if not math.isfinite(condition) or condition * tolerance >= 0.25:
        raise ValueError(
            "coordinate map is not numerically resolvable at the registered dtype and rank tolerance"
        )
    return condition


def _require_close(
    observed: torch.Tensor,
    expected: torch.Tensor,
    *,
    dtype: torch.dtype,
    dimension: int,
    label: str,
) -> None:
    observed64 = _audit_tensor(observed)
    expected64 = _audit_tensor(expected)
    if observed64.shape != expected64.shape:
        raise ValueError(f"oracle failed {label}: shape mismatch")
    scale = max(1.0, float(expected64.abs().max()))
    error = float((observed64 - expected64).abs().max())
    tolerance = _validation_relative_tolerance(dtype, dimension) * scale
    if not math.isfinite(error) or error > tolerance:
        raise ValueError(
            f"oracle failed {label}: maximum error {error:.6g} exceeds {tolerance:.6g}"
        )


def _fraction(mask: torch.Tensor) -> float:
    """Compute a receipt fraction on CPU, including for devices without float64."""

    if mask.numel() == 0:
        return 0.0
    return float(mask.detach().to(device="cpu", dtype=torch.float64).mean())


def _floating_matrix(
    value: torch.Tensor,
    shape: tuple[int, int],
    name: str,
) -> torch.Tensor:
    if not isinstance(value, torch.Tensor):
        raise TypeError(f"{name} must be a torch.Tensor")
    if not value.is_floating_point():
        raise TypeError(f"{name} must have a floating dtype")
    if tuple(value.shape) != shape:
        raise ValueError(f"{name} must have shape {shape}")
    if not bool(torch.isfinite(value).all()):
        raise ValueError(f"{name} must contain only finite values")
    return value


def _integer_states(
    states: torch.Tensor | int,
    *,
    device: torch.device,
) -> torch.Tensor:
    if isinstance(states, bool):
        raise TypeError("semantic states must be integers")
    if isinstance(states, int):
        result = torch.tensor(states, dtype=torch.long, device=device)
    elif isinstance(states, torch.Tensor):
        if states.dtype == torch.bool or states.is_floating_point() or states.is_complex():
            raise TypeError("semantic states must have an integer dtype")
        result = states.to(device=device, dtype=torch.long)
    else:
        raise TypeError("semantic states must be an integer or integer tensor")
    if bool(((result < 0) | (result >= SEMANTIC_DIMENSION)).any()):
        raise ValueError("semantic state is outside the eight-state alphabet")
    return result


def _rank(
    matrix: torch.Tensor,
    *,
    relative_tolerance: float | None,
    source_dtype: torch.dtype | None = None,
) -> "RankCertificate":
    if not isinstance(matrix, torch.Tensor) or matrix.ndim != 2:
        raise TypeError("rank input must be a rank-two tensor")
    if not matrix.is_floating_point() or not bool(torch.isfinite(matrix).all()):
        raise ValueError("rank input must be finite and floating point")
    decision_dtype = source_dtype or matrix.dtype
    effective_tolerance = _rank_relative_tolerance(
        decision_dtype,
        max(1, *matrix.shape),
        relative_tolerance,
    )
    singular = torch.linalg.svdvals(_audit_tensor(matrix))
    leading = float(singular[0]) if singular.numel() else 0.0
    threshold = effective_tolerance * leading
    retained = singular > threshold
    rank = int(retained.sum())
    minimum_retained = float(singular[rank - 1]) if rank else None
    maximum_discarded = float(singular[rank]) if rank < singular.numel() else None
    return RankCertificate(
        rows=int(matrix.shape[0]),
        columns=int(matrix.shape[1]),
        rank=rank,
        relative_tolerance=effective_tolerance,
        threshold=threshold,
        singular_values=tuple(float(value) for value in singular),
        minimum_retained=minimum_retained,
        maximum_discarded=maximum_discarded,
    )


def _right_inverse_rank(
    matrix: torch.Tensor,
    right_inverse: torch.Tensor,
    *,
    relative_tolerance: float | None,
) -> "RankCertificate":
    """Certify full row rank from a registered right-inverse witness.

    Raw singular-value thresholds are not invariant under an ill-scaled but
    invertible change of state coordinates.  For the semantic projection we
    have stronger information: the registered injection is a right inverse.
    The identity witness fixes the rank algebraically while the raw singular
    values remain in the receipt as conditioning diagnostics.
    """

    diagnostic = _rank(
        matrix,
        relative_tolerance=relative_tolerance,
        source_dtype=matrix.dtype,
    )
    if right_inverse.ndim != 2 or right_inverse.shape != (
        matrix.shape[1],
        matrix.shape[0],
    ):
        raise ValueError("right_inverse has incompatible shape")
    product = _audit_tensor(matrix) @ _audit_tensor(right_inverse)
    identity = torch.eye(matrix.shape[0], dtype=torch.float64)
    residual = float((product - identity).abs().max())
    _require_close(
        product,
        identity,
        dtype=matrix.dtype,
        dimension=max(matrix.shape),
        label="registered right-inverse rank witness",
    )
    singular = diagnostic.singular_values
    return RankCertificate(
        rows=diagnostic.rows,
        columns=diagnostic.columns,
        rank=int(matrix.shape[0]),
        relative_tolerance=diagnostic.relative_tolerance,
        threshold=diagnostic.threshold,
        singular_values=singular,
        minimum_retained=singular[-1] if singular else None,
        maximum_discarded=None,
        method="validated_right_inverse",
        witness_residual=residual,
    )


@dataclass(frozen=True)
class RankCertificate:
    """A fixed-tolerance numerical rank receipt."""

    rows: int
    columns: int
    rank: int
    relative_tolerance: float
    threshold: float
    singular_values: tuple[float, ...]
    minimum_retained: float | None
    maximum_discarded: float | None
    method: str = "relative_svd"
    witness_residual: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AmbientDelayMinimalityCertificate:
    """Linear and conditional dimension certificates for ANC-4.

    The Hankel, controllability, and observability ranks certify that the
    delay channel has minimal linear realization dimension four.  The total
    lower bound of twelve additionally assumes an exact rank-eight saturated
    semantic anchor and that recurrent state is the sole temporal channel.
    It is not an unconditional lower bound for a finite classification task.
    """

    semantic_projection: RankCertificate
    vertical_fiber_dimension: int
    controllability: RankCertificate
    observability: RankCertificate
    hankel: RankCertificate
    hankel_reversal_max_error: float
    transition_nilpotency_max_error: float
    strict_delay_markov_max_error: float
    memory_realization_minimal: bool
    conditional_state_lower_bound: int
    assumptions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": f"{SCHEMA_PREFIX}.minimality.v1",
            "semantic_projection": self.semantic_projection.to_dict(),
            "vertical_fiber_dimension": self.vertical_fiber_dimension,
            "controllability": self.controllability.to_dict(),
            "observability": self.observability.to_dict(),
            "hankel": self.hankel.to_dict(),
            "hankel_reversal_max_error": self.hankel_reversal_max_error,
            "transition_nilpotency_max_error": self.transition_nilpotency_max_error,
            "strict_delay_markov_max_error": self.strict_delay_markov_max_error,
            "memory_realization_minimal": self.memory_realization_minimal,
            "conditional_state_lower_bound": self.conditional_state_lower_bound,
            "assumptions": list(self.assumptions),
        }


@dataclass(frozen=True)
class AmbientDelayOracle:
    """An exact rank-eight semantic anchor plus rank-four delay fiber."""

    semantic_injection: torch.Tensor
    semantic_projection: torch.Tensor
    memory_injection: torch.Tensor
    memory_projection: torch.Tensor
    memory_transition: torch.Tensor
    memory_input: torch.Tensor
    memory_output: torch.Tensor
    state_transition: torch.Tensor
    state_input: torch.Tensor
    delay_readout: torch.Tensor
    p_projector: torch.Tensor
    q_projector: torch.Tensor
    coordinate_map: torch.Tensor
    inverse_coordinate_map: torch.Tensor

    def __post_init__(self) -> None:
        dtype = self.coordinate_map.dtype
        device = self.coordinate_map.device
        _require_supported_dtype(dtype)
        for name, value, shape in (
            ("semantic_injection", self.semantic_injection, (STATE_DIMENSION, SEMANTIC_DIMENSION)),
            ("semantic_projection", self.semantic_projection, (SEMANTIC_DIMENSION, STATE_DIMENSION)),
            ("memory_injection", self.memory_injection, (STATE_DIMENSION, AMBIENT_DIMENSION)),
            ("memory_projection", self.memory_projection, (AMBIENT_DIMENSION, STATE_DIMENSION)),
            ("memory_transition", self.memory_transition, (AMBIENT_DIMENSION, AMBIENT_DIMENSION)),
            ("memory_input", self.memory_input, (AMBIENT_DIMENSION, 1)),
            ("memory_output", self.memory_output, (1, AMBIENT_DIMENSION)),
            ("state_transition", self.state_transition, (STATE_DIMENSION, STATE_DIMENSION)),
            ("state_input", self.state_input, (STATE_DIMENSION, 1)),
            ("delay_readout", self.delay_readout, (1, STATE_DIMENSION)),
            ("p_projector", self.p_projector, (STATE_DIMENSION, STATE_DIMENSION)),
            ("q_projector", self.q_projector, (STATE_DIMENSION, STATE_DIMENSION)),
            ("coordinate_map", self.coordinate_map, (STATE_DIMENSION, STATE_DIMENSION)),
            ("inverse_coordinate_map", self.inverse_coordinate_map, (STATE_DIMENSION, STATE_DIMENSION)),
        ):
            checked = _floating_matrix(value, shape, name)
            if checked.dtype != dtype or checked.device != device:
                raise ValueError("all oracle tensors must share dtype and device")

        _require_resolvable_coordinates(self.coordinate_map, dtype=dtype)
        audit = {
            name: _audit_tensor(value)
            for name, value in (
                ("semantic_injection", self.semantic_injection),
                ("semantic_projection", self.semantic_projection),
                ("memory_injection", self.memory_injection),
                ("memory_projection", self.memory_projection),
                ("memory_transition", self.memory_transition),
                ("memory_input", self.memory_input),
                ("memory_output", self.memory_output),
                ("state_transition", self.state_transition),
                ("state_input", self.state_input),
                ("delay_readout", self.delay_readout),
                ("p_projector", self.p_projector),
                ("q_projector", self.q_projector),
                ("coordinate_map", self.coordinate_map),
                ("inverse_coordinate_map", self.inverse_coordinate_map),
            )
        }
        identity = torch.eye(STATE_DIMENSION, dtype=torch.float64)
        semantic_identity = torch.eye(SEMANTIC_DIMENSION, dtype=torch.float64)
        ambient_identity = torch.eye(AMBIENT_DIMENSION, dtype=torch.float64)
        expected_shift = torch.zeros(
            AMBIENT_DIMENSION,
            AMBIENT_DIMENSION,
            dtype=torch.float64,
        )
        for index in range(AMBIENT_DIMENSION - 1):
            expected_shift[index, index + 1] = 1.0
        expected_input = torch.zeros(AMBIENT_DIMENSION, 1, dtype=torch.float64)
        expected_input[-1, 0] = 1.0
        expected_output = torch.zeros(1, AMBIENT_DIMENSION, dtype=torch.float64)
        expected_output[0, 0] = 1.0

        # These three tensors are canonical in the internal memory coordinates.
        # Exact comparison is valid for every supported dtype because all target
        # entries are zero or one, and it excludes arbitrarily small echo terms.
        for observed, expected, label in (
            (audit["memory_transition"], expected_shift, "delay-four shift"),
            (audit["memory_input"], expected_input, "delay-four input"),
            (audit["memory_output"], expected_output, "delay-four output"),
        ):
            if not torch.equal(observed, expected):
                raise ValueError(f"oracle failed exact {label}")

        exact_definitions = (
            (
                self.coordinate_map,
                torch.cat((self.semantic_injection, self.memory_injection), dim=1),
                "coordinate injection",
            ),
            (
                self.inverse_coordinate_map,
                torch.cat((self.semantic_projection, self.memory_projection), dim=0),
                "coordinate projection",
            ),
            (
                self.p_projector,
                self.semantic_injection @ self.semantic_projection,
                "P split definition",
            ),
            (
                self.q_projector,
                self.memory_injection @ self.memory_projection,
                "Q split definition",
            ),
            (
                self.state_transition,
                self.memory_injection
                @ self.memory_transition
                @ self.memory_projection,
                "full-state transition definition",
            ),
            (
                self.state_input,
                self.memory_injection @ self.memory_input,
                "full-state input definition",
            ),
            (
                self.delay_readout,
                self.memory_output @ self.memory_projection,
                "full-state delay readout definition",
            ),
        )
        for observed, expected, label in exact_definitions:
            if not torch.equal(observed, expected):
                raise ValueError(f"oracle failed exact {label}")

        combined_injection = torch.cat(
            (audit["semantic_injection"], audit["memory_injection"]),
            dim=1,
        )
        combined_projection = torch.cat(
            (audit["semantic_projection"], audit["memory_projection"]),
            dim=0,
        )
        zero_state = torch.zeros_like(identity)
        checks = (
            (
                audit["coordinate_map"] @ audit["inverse_coordinate_map"],
                identity,
                "coordinate right inverse",
            ),
            (
                audit["inverse_coordinate_map"] @ audit["coordinate_map"],
                identity,
                "coordinate left inverse",
            ),
            (
                combined_injection,
                audit["coordinate_map"],
                "transported coordinate injection",
            ),
            (
                combined_projection,
                audit["inverse_coordinate_map"],
                "transported coordinate projection",
            ),
            (
                audit["semantic_projection"] @ audit["semantic_injection"],
                semantic_identity,
                "semantic split",
            ),
            (
                audit["memory_projection"] @ audit["memory_injection"],
                ambient_identity,
                "memory split",
            ),
            (
                audit["semantic_projection"] @ audit["memory_injection"],
                torch.zeros(
                    SEMANTIC_DIMENSION,
                    AMBIENT_DIMENSION,
                    dtype=torch.float64,
                ),
                "vertical kernel",
            ),
            (
                audit["memory_projection"] @ audit["semantic_injection"],
                torch.zeros(
                    AMBIENT_DIMENSION,
                    SEMANTIC_DIMENSION,
                    dtype=torch.float64,
                ),
                "horizontal kernel",
            ),
            (
                audit["p_projector"],
                audit["semantic_injection"] @ audit["semantic_projection"],
                "P split definition",
            ),
            (
                audit["q_projector"],
                audit["memory_injection"] @ audit["memory_projection"],
                "Q split definition",
            ),
            (audit["p_projector"] + audit["q_projector"], identity, "projector resolution"),
            (audit["p_projector"] @ audit["p_projector"], audit["p_projector"], "P idempotence"),
            (audit["q_projector"] @ audit["q_projector"], audit["q_projector"], "Q idempotence"),
            (audit["p_projector"] @ audit["q_projector"], zero_state, "P-Q separation"),
            (audit["q_projector"] @ audit["p_projector"], zero_state, "Q-P separation"),
            (
                audit["state_transition"],
                audit["memory_injection"]
                @ audit["memory_transition"]
                @ audit["memory_projection"],
                "full-state transition definition",
            ),
            (
                audit["state_input"],
                audit["memory_injection"] @ audit["memory_input"],
                "full-state input definition",
            ),
            (
                audit["delay_readout"],
                audit["memory_output"] @ audit["memory_projection"],
                "full-state delay readout definition",
            ),
        )
        for observed, expected, label in checks:
            _require_close(
                observed,
                expected,
                dtype=dtype,
                dimension=STATE_DIMENSION,
                label=label,
            )

    def validate(self) -> None:
        """Revalidate tensor contents after construction or deserialization."""

        # ``frozen=True`` prevents field reassignment but PyTorch tensors remain
        # mutable.  Public execution and certification paths call this method so
        # in-place mutation cannot make them execute a system different from the
        # one certified at construction.
        self.__post_init__()

    @property
    def dtype(self) -> torch.dtype:
        return self.coordinate_map.dtype

    @property
    def device(self) -> torch.device:
        return self.coordinate_map.device

    def encode(
        self,
        semantic_states: torch.Tensor | int,
        memory: torch.Tensor,
    ) -> torch.Tensor:
        self.validate()
        states = _integer_states(semantic_states, device=self.device)
        if not isinstance(memory, torch.Tensor) or not memory.is_floating_point():
            raise TypeError("memory must be a floating tensor")
        memory = memory.to(dtype=self.dtype, device=self.device)
        expected = tuple(states.shape) + (AMBIENT_DIMENSION,)
        if tuple(memory.shape) != expected:
            raise ValueError(f"memory must have shape {expected}")
        if not bool(torch.isfinite(memory).all()):
            raise ValueError("memory must be finite")
        semantic = F.one_hot(states, SEMANTIC_DIMENSION).to(self.dtype)
        return (
            semantic @ self.semantic_injection.transpose(0, 1)
            + memory @ self.memory_injection.transpose(0, 1)
        )

    def semantic_coordinates(self, state: torch.Tensor) -> torch.Tensor:
        state = self._state_tensor(state)
        return state @ self.semantic_projection.transpose(0, 1)

    def memory_coordinates(self, state: torch.Tensor) -> torch.Tensor:
        state = self._state_tensor(state)
        return state @ self.memory_projection.transpose(0, 1)

    def _state_tensor(self, state: torch.Tensor) -> torch.Tensor:
        self.validate()
        if not isinstance(state, torch.Tensor) or not state.is_floating_point():
            raise TypeError("state must be a floating tensor")
        state = state.to(dtype=self.dtype, device=self.device)
        if state.shape[-1:] != (STATE_DIMENSION,):
            raise ValueError("state must end in dimension twelve")
        if not bool(torch.isfinite(state).all()):
            raise ValueError("state must be finite")
        return state

    def delay_output(self, state: torch.Tensor) -> torch.Tensor:
        state = self._state_tensor(state)
        return (state @ self.delay_readout.transpose(0, 1)).squeeze(-1)

    def delete_q(self, state: torch.Tensor) -> torch.Tensor:
        state = self._state_tensor(state)
        return state @ self.p_projector.transpose(0, 1)

    def transplant_q(self, recipient: torch.Tensor, donor: torch.Tensor) -> torch.Tensor:
        recipient = self._state_tensor(recipient)
        donor = self._state_tensor(donor)
        if recipient.shape != donor.shape:
            raise ValueError("recipient and donor states must have the same shape")
        return (
            recipient @ self.p_projector.transpose(0, 1)
            + donor @ self.q_projector.transpose(0, 1)
        )

    def advance(
        self,
        state: torch.Tensor,
        next_semantic_states: torch.Tensor | int,
        input_value: torch.Tensor | float,
    ) -> torch.Tensor:
        state = self._state_tensor(state)
        labels = _integer_states(next_semantic_states, device=self.device)
        if tuple(labels.shape) != tuple(state.shape[:-1]):
            raise ValueError("next semantic states must match the state batch shape")
        if isinstance(input_value, bool):
            raise TypeError("input values must be real")
        values = torch.as_tensor(input_value, dtype=self.dtype, device=self.device)
        if tuple(values.shape) != tuple(state.shape[:-1]):
            raise ValueError("input values must match the state batch shape")
        if not bool(torch.isfinite(values).all()):
            raise ValueError("input values must be finite")
        semantic = F.one_hot(labels, SEMANTIC_DIMENSION).to(self.dtype)
        return (
            semantic @ self.semantic_injection.transpose(0, 1)
            + state @ self.state_transition.transpose(0, 1)
            + values.unsqueeze(-1) * self.state_input.squeeze(-1)
        )

    def future_delay_outputs(
        self,
        state: torch.Tensor,
        *,
        steps: int = DELAY,
        future_inputs: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Read future online outputs while re-saturating the semantic anchor."""

        if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
            raise ValueError("steps must be a positive integer")
        current = self._state_tensor(state)
        batch_shape = current.shape[:-1]
        if future_inputs is None:
            inputs = torch.zeros(
                batch_shape + (steps,),
                dtype=self.dtype,
                device=self.device,
            )
        else:
            if not isinstance(future_inputs, torch.Tensor) or not future_inputs.is_floating_point():
                raise TypeError("future_inputs must be a floating tensor")
            inputs = future_inputs.to(dtype=self.dtype, device=self.device)
            if tuple(inputs.shape) != tuple(batch_shape) + (steps,):
                raise ValueError("future_inputs has the wrong shape")
            if not bool(torch.isfinite(inputs).all()):
                raise ValueError("future_inputs must be finite")

        semantic = self.semantic_coordinates(current)
        outputs: list[torch.Tensor] = []
        for index in range(steps):
            outputs.append(self.delay_output(current))
            current = (
                semantic @ self.semantic_injection.transpose(0, 1)
                + current @ self.state_transition.transpose(0, 1)
                + inputs[..., index, None] * self.state_input.squeeze(-1)
            )
        return torch.stack(outputs, dim=-1)

    def conjugate(self, change_of_coordinates: torch.Tensor) -> "AmbientDelayOracle":
        """Transport the complete oracle under ``x' = T x``."""

        self.validate()
        transform = _floating_matrix(
            change_of_coordinates,
            (STATE_DIMENSION, STATE_DIMENSION),
            "change_of_coordinates",
        ).to(dtype=self.dtype, device=self.device)
        _require_resolvable_coordinates(transform, dtype=self.dtype)
        transform64 = _audit_tensor(transform)
        inverse64 = torch.linalg.inv(transform64)
        if not bool(torch.isfinite(inverse64).all()):
            raise ValueError("change_of_coordinates must be invertible")

        def restored(value: torch.Tensor) -> torch.Tensor:
            return value.to(dtype=self.dtype, device=self.device)

        semantic_injection64 = _audit_tensor(self.semantic_injection)
        semantic_projection64 = _audit_tensor(self.semantic_projection)
        memory_injection64 = _audit_tensor(self.memory_injection)
        memory_projection64 = _audit_tensor(self.memory_projection)
        semantic_injection = restored(transform64 @ semantic_injection64)
        semantic_projection = restored(semantic_projection64 @ inverse64)
        memory_injection = restored(transform64 @ memory_injection64)
        memory_projection = restored(memory_projection64 @ inverse64)
        # Derived fields have a single source of truth.  Constructing them from
        # the stored split makes bitwise coherence checkable even in low
        # precision; independently transporting redundant copies would not.
        p_projector = semantic_injection @ semantic_projection
        q_projector = memory_injection @ memory_projection
        state_transition = (
            memory_injection @ self.memory_transition @ memory_projection
        )
        state_input = memory_injection @ self.memory_input
        delay_readout = self.memory_output @ memory_projection
        return AmbientDelayOracle(
            semantic_injection=semantic_injection,
            semantic_projection=semantic_projection,
            memory_injection=memory_injection,
            memory_projection=memory_projection,
            memory_transition=self.memory_transition,
            memory_input=self.memory_input,
            memory_output=self.memory_output,
            state_transition=state_transition,
            state_input=state_input,
            delay_readout=delay_readout,
            p_projector=p_projector,
            q_projector=q_projector,
            coordinate_map=torch.cat(
                (semantic_injection, memory_injection),
                dim=1,
            ),
            inverse_coordinate_map=torch.cat(
                (semantic_projection, memory_projection),
                dim=0,
            ),
        )


def canonical_anc4_oracle(
    *,
    dtype: torch.dtype = torch.float64,
    device: torch.device | str = "cpu",
) -> AmbientDelayOracle:
    """Build the canonical exact eight-plus-four online delay oracle."""

    _require_supported_dtype(dtype)
    device = torch.device(device)
    identity = torch.eye(STATE_DIMENSION, dtype=dtype, device=device)
    semantic_injection = torch.zeros(
        STATE_DIMENSION,
        SEMANTIC_DIMENSION,
        dtype=dtype,
        device=device,
    )
    semantic_injection[:SEMANTIC_DIMENSION] = torch.eye(
        SEMANTIC_DIMENSION,
        dtype=dtype,
        device=device,
    )
    semantic_projection = semantic_injection.transpose(0, 1)
    memory_injection = torch.zeros(
        STATE_DIMENSION,
        AMBIENT_DIMENSION,
        dtype=dtype,
        device=device,
    )
    memory_injection[SEMANTIC_DIMENSION:] = torch.eye(
        AMBIENT_DIMENSION,
        dtype=dtype,
        device=device,
    )
    memory_projection = memory_injection.transpose(0, 1)

    shift = torch.zeros(
        AMBIENT_DIMENSION,
        AMBIENT_DIMENSION,
        dtype=dtype,
        device=device,
    )
    for index in range(AMBIENT_DIMENSION - 1):
        shift[index, index + 1] = 1.0
    memory_input = torch.zeros(AMBIENT_DIMENSION, 1, dtype=dtype, device=device)
    memory_input[-1, 0] = 1.0
    memory_output = torch.zeros(1, AMBIENT_DIMENSION, dtype=dtype, device=device)
    memory_output[0, 0] = 1.0

    p_projector = semantic_injection @ semantic_projection
    q_projector = memory_injection @ memory_projection
    state_transition = memory_injection @ shift @ memory_projection
    state_input = memory_injection @ memory_input
    delay_readout = memory_output @ memory_projection
    return AmbientDelayOracle(
        semantic_injection=semantic_injection,
        semantic_projection=semantic_projection,
        memory_injection=memory_injection,
        memory_projection=memory_projection,
        memory_transition=shift,
        memory_input=memory_input,
        memory_output=memory_output,
        state_transition=state_transition,
        state_input=state_input,
        delay_readout=delay_readout,
        p_projector=p_projector,
        q_projector=q_projector,
        coordinate_map=identity,
        inverse_coordinate_map=identity,
    )


def deterministic_change_of_basis(
    seed: int = 1701,
    *,
    dtype: torch.dtype = torch.float64,
    device: torch.device | str = "cpu",
) -> torch.Tensor:
    """Return a reproducible dense, well-conditioned coordinate map.

    Both off-diagonal blocks are populated, so neither the semantic image nor
    the vertical fiber remains aligned with the displayed coordinate axes.
    """

    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    _require_supported_dtype(dtype)
    result = torch.eye(STATE_DIMENSION, dtype=torch.float64)
    for row in range(SEMANTIC_DIMENSION):
        for column in range(AMBIENT_DIMENSION):
            integer = ((seed + 11 * (row + 1) + 17 * (column + 1)) % 7) - 3
            result[row, SEMANTIC_DIMENSION + column] = integer / 48.0
            reverse_integer = (
                (seed + 19 * (row + 1) + 23 * (column + 1)) % 7
            ) - 3
            result[SEMANTIC_DIMENSION + column, row] = reverse_integer / 64.0
    for column in range(AMBIENT_DIMENSION):
        result[SEMANTIC_DIMENSION + column, SEMANTIC_DIMENSION + column] = (
            1.0 + (column + 1) / 20.0
        )
    return result.to(dtype=dtype, device=torch.device(device))


def controllability_matrix(transition: torch.Tensor, input_map: torch.Tensor, horizon: int) -> torch.Tensor:
    """Return ``[B, AB, ..., A^(horizon-1)B]``."""

    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
        raise ValueError("horizon must be a positive integer")
    if not isinstance(transition, torch.Tensor) or transition.ndim != 2:
        raise TypeError("transition must be a rank-two tensor")
    if transition.shape[0] != transition.shape[1]:
        raise ValueError("transition must be square")
    if not isinstance(input_map, torch.Tensor) or input_map.ndim != 2:
        raise TypeError("input_map must be a rank-two tensor")
    if input_map.shape[0] != transition.shape[0]:
        raise ValueError("input_map row count must match transition")
    current = input_map
    blocks: list[torch.Tensor] = []
    for _ in range(horizon):
        blocks.append(current)
        current = transition @ current
    return torch.cat(blocks, dim=1)


def observability_matrix(transition: torch.Tensor, output_map: torch.Tensor, horizon: int) -> torch.Tensor:
    """Return ``[C; CA; ...; CA^(horizon-1)]``."""

    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon < 1:
        raise ValueError("horizon must be a positive integer")
    if not isinstance(transition, torch.Tensor) or transition.ndim != 2:
        raise TypeError("transition must be a rank-two tensor")
    if transition.shape[0] != transition.shape[1]:
        raise ValueError("transition must be square")
    if not isinstance(output_map, torch.Tensor) or output_map.ndim != 2:
        raise TypeError("output_map must be a rank-two tensor")
    if output_map.shape[1] != transition.shape[0]:
        raise ValueError("output_map column count must match transition")
    current = output_map
    blocks: list[torch.Tensor] = []
    for _ in range(horizon):
        blocks.append(current)
        current = current @ transition
    return torch.cat(blocks, dim=0)


def delay_hankel(
    transition: torch.Tensor,
    input_map: torch.Tensor,
    output_map: torch.Tensor,
    *,
    block_rows: int = DELAY,
    block_columns: int = DELAY,
) -> torch.Tensor:
    """Build ``H[i,j] = C A^(i+j) B`` from strict-proper Markov blocks."""

    if min(block_rows, block_columns) < 1:
        raise ValueError("Hankel block dimensions must be positive")
    powers: list[torch.Tensor] = [input_map]
    for _ in range(block_rows + block_columns - 2):
        powers.append(transition @ powers[-1])
    rows = [
        torch.cat(
            [output_map @ powers[row + column] for column in range(block_columns)],
            dim=1,
        )
        for row in range(block_rows)
    ]
    return torch.cat(rows, dim=0)


def certify_anc4_minimality(
    oracle: AmbientDelayOracle,
    *,
    relative_tolerance: float | None = None,
) -> AmbientDelayMinimalityCertificate:
    """Certify the exact delay-four memory rank and conditional 8+4 bound."""

    oracle.validate()
    transition = _audit_tensor(oracle.memory_transition)
    input_map = _audit_tensor(oracle.memory_input)
    output_map = _audit_tensor(oracle.memory_output)
    reachability = controllability_matrix(
        transition,
        input_map,
        DELAY,
    )
    observability = observability_matrix(
        transition,
        output_map,
        DELAY,
    )
    hankel = delay_hankel(
        transition,
        input_map,
        output_map,
    )
    reversal = torch.flip(
        torch.eye(DELAY, dtype=hankel.dtype, device=hankel.device),
        dims=(1,),
    )
    semantic_rank = _right_inverse_rank(
        oracle.semantic_projection,
        oracle.semantic_injection,
        relative_tolerance=relative_tolerance,
    )
    controllability_rank = _rank(
        reachability,
        relative_tolerance=relative_tolerance,
        source_dtype=oracle.dtype,
    )
    observability_rank = _rank(
        observability,
        relative_tolerance=relative_tolerance,
        source_dtype=oracle.dtype,
    )
    hankel_rank = _rank(
        hankel,
        relative_tolerance=relative_tolerance,
        source_dtype=oracle.dtype,
    )
    reversal_error = float((hankel - reversal).abs().max())
    nilpotency_error = float(
        torch.linalg.matrix_power(transition, DELAY).abs().max()
    )
    markov_values: list[torch.Tensor] = []
    propagated_input = input_map
    for _ in range(2 * DELAY):
        markov_values.append((output_map @ propagated_input).reshape(()))
        propagated_input = transition @ propagated_input
    observed_markov = torch.stack(markov_values)
    expected_markov = torch.zeros_like(observed_markov)
    expected_markov[DELAY - 1] = 1.0
    strict_delay_error = float((observed_markov - expected_markov).abs().max())
    memory_minimal = (
        controllability_rank.rank
        == observability_rank.rank
        == hankel_rank.rank
        == AMBIENT_DIMENSION
        # S, b, and d are exact zero/one tensors in registered internal
        # coordinates.  Exact nilpotency is the sufficient tail exclusion;
        # the eight Markov coefficients remain an explicit diagnostic.
        and reversal_error == 0.0
        and nilpotency_error == 0.0
        and strict_delay_error == 0.0
    )
    return AmbientDelayMinimalityCertificate(
        semantic_projection=semantic_rank,
        vertical_fiber_dimension=STATE_DIMENSION - semantic_rank.rank,
        controllability=controllability_rank,
        observability=observability_rank,
        hankel=hankel_rank,
        hankel_reversal_max_error=reversal_error,
        transition_nilpotency_max_error=nilpotency_error,
        strict_delay_markov_max_error=strict_delay_error,
        memory_realization_minimal=memory_minimal,
        conditional_state_lower_bound=(
            semantic_rank.rank + hankel_rank.rank
            if memory_minimal
            else 0
        ),
        assumptions=(
            "four consecutive scalar inputs range over an open subset of R^4",
            "delay output y_t = u_(t-4) at every t >= 4",
            "exact rank-eight saturated semantic anchor after every update",
            "recurrent state is the sole temporal information channel",
            "H is a finite-dimensional real vector space and pi is a fixed surjective linear map",
            "state update and readout are continuous",
            "semantic trajectory, future continuation, and inputs before the four-lag window are fixed",
        ),
    )


@dataclass(frozen=True)
class QDeletionEvaluation:
    native_outputs: torch.Tensor
    deleted_outputs: torch.Tensor
    expected_outputs: torch.Tensor
    examples: int
    nonzero_examples: int
    native_match_fraction: float
    deleted_zero_fraction: float
    changed_fraction: float
    unconditional_changed_fraction: float
    changed_fraction_on_nonzero: float
    semantic_preserved_fraction: float
    maximum_native_error: float
    maximum_deleted_magnitude: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": f"{SCHEMA_PREFIX}.q_deletion.v1",
            "examples": self.examples,
            "nonzero_examples": self.nonzero_examples,
            "native_match_fraction": self.native_match_fraction,
            "deleted_zero_fraction": self.deleted_zero_fraction,
            "changed_fraction": self.changed_fraction,
            "unconditional_changed_fraction": self.unconditional_changed_fraction,
            "changed_fraction_on_nonzero": self.changed_fraction_on_nonzero,
            "semantic_preserved_fraction": self.semantic_preserved_fraction,
            "maximum_native_error": self.maximum_native_error,
            "maximum_deleted_magnitude": self.maximum_deleted_magnitude,
        }


@dataclass(frozen=True)
class QTransplantEvaluation:
    recipient_outputs: torch.Tensor
    donor_outputs: torch.Tensor
    transplanted_outputs: torch.Tensor
    examples: int
    distinct_examples: int
    donor_match_fraction: float
    recipient_changed_fraction_on_distinct: float
    semantic_recipient_preserved_fraction: float
    maximum_donor_error: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": f"{SCHEMA_PREFIX}.q_transplant.v1",
            "examples": self.examples,
            "distinct_examples": self.distinct_examples,
            "donor_match_fraction": self.donor_match_fraction,
            "recipient_changed_fraction_on_distinct": (
                self.recipient_changed_fraction_on_distinct
            ),
            "semantic_recipient_preserved_fraction": (
                self.semantic_recipient_preserved_fraction
            ),
            "maximum_donor_error": self.maximum_donor_error,
        }


def _delay_windows(
    oracle: AmbientDelayOracle,
    histories: torch.Tensor,
    semantic_states: torch.Tensor | int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if not isinstance(histories, torch.Tensor) or not histories.is_floating_point():
        raise TypeError("histories must be a floating tensor")
    histories = histories.to(dtype=oracle.dtype, device=oracle.device)
    if histories.ndim != 2 or histories.shape[1] != DELAY or histories.shape[0] < 1:
        raise ValueError("histories must have shape (examples, 4)")
    if not bool(torch.isfinite(histories).all()):
        raise ValueError("histories must be finite")
    labels = _integer_states(semantic_states, device=oracle.device)
    if tuple(labels.shape) != (histories.shape[0],):
        raise ValueError("semantic_states must have one label per history")
    state = oracle.encode(labels, histories)
    return histories, labels, state


def _evaluation_tolerance(
    oracle: AmbientDelayOracle,
    tolerance: float | None,
) -> float:
    if tolerance is None:
        return min(
            1.0 / 32.0,
            max(
                32.0 * float(torch.finfo(torch.float64).eps),
                8.0 * float(torch.finfo(oracle.dtype).eps),
            ),
        )
    if not math.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    return float(tolerance)


def _rowwise_bounds(reference: torch.Tensor, tolerance: float) -> torch.Tensor:
    """Return ``tolerance * max(1, ||reference_i||_inf)`` per example."""

    return tolerance * reference.abs().amax(dim=1).clamp_min(1.0)


def evaluate_q_deletion(
    oracle: AmbientDelayOracle,
    histories: torch.Tensor,
    semantic_states: torch.Tensor | int,
    *,
    tolerance: float | None = None,
) -> QDeletionEvaluation:
    """Delete the vertical fiber and test the next four delayed outputs."""

    tolerance = _evaluation_tolerance(oracle, tolerance)
    histories, _, state = _delay_windows(oracle, histories, semantic_states)
    deleted = oracle.delete_q(state)
    native_outputs = oracle.future_delay_outputs(state)
    deleted_outputs = oracle.future_delay_outputs(deleted)
    native_error = (native_outputs - histories).abs()
    history_bounds = _rowwise_bounds(histories, tolerance)
    native_match = native_error.amax(dim=1) <= history_bounds
    deleted_zero = deleted_outputs.abs().amax(dim=1) <= history_bounds
    changed = (
        native_outputs - deleted_outputs
    ).abs().amax(dim=1) > history_bounds
    nonzero = histories.abs().amax(dim=1) > history_bounds
    changed_on_nonzero = _fraction(changed[nonzero])
    unconditional_changed = _fraction(changed)
    semantic_error = (
        oracle.semantic_coordinates(deleted) - oracle.semantic_coordinates(state)
    ).abs().amax(dim=1)
    return QDeletionEvaluation(
        native_outputs=native_outputs.detach(),
        deleted_outputs=deleted_outputs.detach(),
        expected_outputs=histories.detach(),
        examples=int(histories.shape[0]),
        nonzero_examples=int(nonzero.detach().to(device="cpu").sum()),
        native_match_fraction=_fraction(native_match),
        deleted_zero_fraction=_fraction(deleted_zero),
        changed_fraction=changed_on_nonzero,
        unconditional_changed_fraction=unconditional_changed,
        changed_fraction_on_nonzero=changed_on_nonzero,
        semantic_preserved_fraction=_fraction(semantic_error <= history_bounds),
        maximum_native_error=float(native_error.max()),
        maximum_deleted_magnitude=float(deleted_outputs.abs().max()),
    )


def evaluate_q_transplant(
    oracle: AmbientDelayOracle,
    recipient_histories: torch.Tensor,
    donor_histories: torch.Tensor,
    semantic_states: torch.Tensor | int,
    *,
    tolerance: float | None = None,
) -> QTransplantEvaluation:
    """Transplant Q between equal-semantic histories and audit the prediction."""

    tolerance = _evaluation_tolerance(oracle, tolerance)
    recipients, labels, recipient_state = _delay_windows(
        oracle,
        recipient_histories,
        semantic_states,
    )
    donors, donor_labels, donor_state = _delay_windows(
        oracle,
        donor_histories,
        semantic_states,
    )
    if not torch.equal(labels, donor_labels):
        raise RuntimeError("donor and recipient semantic labels diverged")
    transplanted_state = oracle.transplant_q(recipient_state, donor_state)
    recipient_outputs = oracle.future_delay_outputs(recipient_state)
    donor_outputs = oracle.future_delay_outputs(donor_state)
    transplanted_outputs = oracle.future_delay_outputs(transplanted_state)
    donor_error = (transplanted_outputs - donors).abs()
    donor_bounds = _rowwise_bounds(donors, tolerance)
    donor_match = donor_error.amax(dim=1) <= donor_bounds
    pair_scale = torch.maximum(donors.abs(), recipients.abs())
    pair_bounds = _rowwise_bounds(pair_scale, tolerance)
    distinct = (donors - recipients).abs().amax(dim=1) > pair_bounds
    changed = (
        transplanted_outputs - recipient_outputs
    ).abs().amax(dim=1) > pair_bounds
    changed_on_distinct = _fraction(changed[distinct])
    semantic_error = (
        oracle.semantic_coordinates(transplanted_state)
        - oracle.semantic_coordinates(recipient_state)
    ).abs().amax(dim=1)
    return QTransplantEvaluation(
        recipient_outputs=recipient_outputs.detach(),
        donor_outputs=donor_outputs.detach(),
        transplanted_outputs=transplanted_outputs.detach(),
        examples=int(recipients.shape[0]),
        distinct_examples=int(distinct.detach().to(device="cpu").sum()),
        donor_match_fraction=_fraction(donor_match),
        recipient_changed_fraction_on_distinct=changed_on_distinct,
        semantic_recipient_preserved_fraction=_fraction(
            semantic_error <= pair_bounds
        ),
        maximum_donor_error=float(donor_error.max()),
    )


def _coordinate_residuals(
    canonical: AmbientDelayOracle,
    transported: AmbientDelayOracle,
    transform: torch.Tensor,
) -> dict[str, float]:
    return {
        "state_transition": float(
            (transported.state_transition @ transform - transform @ canonical.state_transition)
            .abs()
            .max()
        ),
        "state_input": float((transported.state_input - transform @ canonical.state_input).abs().max()),
        "delay_readout": float((transported.delay_readout @ transform - canonical.delay_readout).abs().max()),
        "p_projector": float((transported.p_projector @ transform - transform @ canonical.p_projector).abs().max()),
        "q_projector": float((transported.q_projector @ transform - transform @ canonical.q_projector).abs().max()),
    }


def deterministic_self_check(seed: int = 1701) -> dict[str, Any]:
    """Run a small coordinate-invariant ANC-4 calibration without training."""

    canonical = canonical_anc4_oracle()
    transform = deterministic_change_of_basis(seed)
    transported = canonical.conjugate(transform)
    histories = torch.tensor(
        (
            (0.25, -0.50, 0.75, -1.00),
            (1.25, 0.50, -0.25, 0.875),
            (-0.375, 1.50, 0.625, -0.125),
            (0.90, -1.10, 1.30, -1.50),
        ),
        dtype=torch.float64,
    )
    donors = histories.roll(shifts=1, dims=0)
    semantic_states = torch.tensor((0, 3, 5, 7), dtype=torch.long)
    canonical_deletion = evaluate_q_deletion(canonical, histories, semantic_states)
    transported_deletion = evaluate_q_deletion(transported, histories, semantic_states)
    canonical_transplant = evaluate_q_transplant(
        canonical,
        histories,
        donors,
        semantic_states,
    )
    transported_transplant = evaluate_q_transplant(
        transported,
        histories,
        donors,
        semantic_states,
    )
    extended_expected = torch.cat((histories, torch.zeros_like(histories)), dim=1)
    canonical_extended = canonical.future_delay_outputs(
        canonical.encode(semantic_states, histories),
        steps=2 * DELAY,
    )
    transported_extended = transported.future_delay_outputs(
        transported.encode(semantic_states, histories),
        steps=2 * DELAY,
    )
    canonical_extended_error = float(
        (canonical_extended - extended_expected).abs().max()
    )
    transported_extended_error = float(
        (transported_extended - extended_expected).abs().max()
    )
    certificate = certify_anc4_minimality(transported)
    coordinate_residuals = _coordinate_residuals(
        canonical,
        transported,
        transform,
    )
    native_coordinate_error = float(
        (canonical_deletion.native_outputs - transported_deletion.native_outputs)
        .abs()
        .max()
    )
    transplant_coordinate_error = float(
        (
            canonical_transplant.transplanted_outputs
            - transported_transplant.transplanted_outputs
        )
        .abs()
        .max()
    )
    tolerance = 1e-12
    passed = (
        certificate.memory_realization_minimal
        and certificate.semantic_projection.rank == SEMANTIC_DIMENSION
        and certificate.vertical_fiber_dimension == AMBIENT_DIMENSION
        and certificate.conditional_state_lower_bound == STATE_DIMENSION
        and max(coordinate_residuals.values()) <= tolerance
        and native_coordinate_error <= tolerance
        and transplant_coordinate_error <= tolerance
        and canonical_extended_error <= tolerance
        and transported_extended_error <= tolerance
        and all(
            result.native_match_fraction == 1.0
            and result.deleted_zero_fraction == 1.0
            and result.changed_fraction_on_nonzero == 1.0
            and result.semantic_preserved_fraction == 1.0
            for result in (canonical_deletion, transported_deletion)
        )
        and all(
            result.donor_match_fraction == 1.0
            and result.recipient_changed_fraction_on_distinct == 1.0
            and result.semantic_recipient_preserved_fraction == 1.0
            for result in (canonical_transplant, transported_transplant)
        )
    )
    payload: dict[str, Any] = {
        "schema": f"{SCHEMA_PREFIX}.self_check.v1",
        "status": "PASS" if passed else "FAIL",
        "seed": seed,
        "dimensions": {
            "semantic": SEMANTIC_DIMENSION,
            "vertical_fiber": AMBIENT_DIMENSION,
            "state": STATE_DIMENSION,
            "delay": DELAY,
        },
        "coordinate_condition_number": _condition_number(transform),
        "coordinate_conjugacy_max_residuals": coordinate_residuals,
        "minimality": certificate.to_dict(),
        "canonical_q_deletion": canonical_deletion.to_dict(),
        "transported_q_deletion": transported_deletion.to_dict(),
        "canonical_q_transplant": canonical_transplant.to_dict(),
        "transported_q_transplant": transported_transplant.to_dict(),
        "native_output_coordinate_max_error": native_coordinate_error,
        "transplant_output_coordinate_max_error": transplant_coordinate_error,
        "canonical_extended_delay_max_error": canonical_extended_error,
        "transported_extended_delay_max_error": transported_extended_error,
    }
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    payload["receipt_sha256"] = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return payload


def main() -> int:
    result = deterministic_self_check()
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "AMBIENT_DIMENSION",
    "DELAY",
    "SEMANTIC_DIMENSION",
    "STATE_DIMENSION",
    "AmbientDelayMinimalityCertificate",
    "AmbientDelayOracle",
    "QDeletionEvaluation",
    "QTransplantEvaluation",
    "RankCertificate",
    "canonical_anc4_oracle",
    "certify_anc4_minimality",
    "controllability_matrix",
    "delay_hankel",
    "deterministic_change_of_basis",
    "deterministic_self_check",
    "evaluate_q_deletion",
    "evaluate_q_transplant",
    "observability_matrix",
]
