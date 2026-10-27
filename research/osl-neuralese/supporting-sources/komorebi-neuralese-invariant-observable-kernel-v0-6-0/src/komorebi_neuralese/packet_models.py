from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from .algebra import N_STATES
from .models import RecurrentOperatorModel, RunTrace


@dataclass(frozen=True)
class OperatorMatrixBundle:
    """Learned operator matrices and the residual parameterization behind them.

    ``matrices`` are the actual recurrent operators.  The distinction between
    ``raw_residuals`` and ``residuals`` makes the smooth norm cap observable to
    diagnostics and auxiliary objectives instead of hiding it in the encoder.
    """

    matrices: torch.Tensor
    residuals: torch.Tensor | None
    raw_residuals: torch.Tensor | None


@dataclass
class PacketRunTrace(RunTrace):
    """A projective rollout with the ambient quantities needed by v0.4 losses.

    ``hidden`` contains the normalized initial state followed by every
    normalized recurrent state. ``pre_normalized_hidden`` and ``radial_norms``
    retain the discarded radial information. They are deliberately not
    detached, so a caller may construct differentiable regularizers from them.
    """

    raw_operator_matrices: torch.Tensor | None
    residual_operator_matrices: torch.Tensor | None
    selected_operator_matrices: torch.Tensor
    pre_normalized_hidden: list[torch.Tensor]
    radial_norms: torch.Tensor
    metric: torch.Tensor

    @property
    def operator_matrices(self) -> torch.Tensor:
        if self.operator_codes is None:  # pragma: no cover - protected by construction
            raise RuntimeError("packet trace has no operator matrices")
        return self.operator_codes

    @property
    def hidden_tensor(self) -> torch.Tensor:
        """Return the normalized trajectory as ``(batch, time + 1, hidden)``."""

        return torch.stack(self.hidden, dim=1)

    @property
    def pre_normalized_hidden_tensor(self) -> torch.Tensor:
        """Return raw recurrent proposals as ``(batch, time, hidden)``."""

        if self.pre_normalized_hidden:
            return torch.stack(self.pre_normalized_hidden, dim=1)
        batch, _, hidden_dim, _ = self.selected_operator_matrices.shape
        return self.selected_operator_matrices.new_empty((batch, 0, hidden_dim))

    @property
    def log_radial_increments(self) -> torch.Tensor:
        """Log of the positive scale removed at each recurrent step."""

        return self.radial_norms.clamp_min(torch.finfo(self.radial_norms.dtype).tiny).log()


@dataclass
class TerminalTaskResult:
    """Terminal-only objective together with its causally inspectable rollout."""

    loss: torch.Tensor
    accuracy: torch.Tensor
    trace: PacketRunTrace


class ProjectiveResidualOperatorRNN(RecurrentOperatorModel):
    """Learned residual operators acting on oriented projective hidden states.

    Each visible operator table is processed independently by a learned
    hypernetwork. The resulting ambient map has the form ``I + Delta``. Delta
    is smoothly Frobenius-capped, but is otherwise unconstrained: it is not a
    supplied permutation matrix, anchor conjugation, group representation, or
    named-relation executor.

    After every application, the state is divided by its positive norm in a
    learned full SPD metric. The metric has a stable unit-determinant Cholesky
    parameterization, so global metric scale cannot become an unidentifiable
    escape route. This fixes only the radial gauge. Angular leakage, switching
    effects, and null-loop holonomy remain available for the v0.4 objectives to
    measure and penalize rather than being engineered away.
    """

    model_name = "projective_residual"

    def __init__(
        self,
        hidden_dim: int = 12,
        encoder_width: int = 32,
        residual_cap: float = 4.0,
        normalization_eps: float = 1e-8,
        metric_log_diagonal_cap: float = 1.5,
        metric_offdiagonal_cap: float = 0.75,
    ) -> None:
        super().__init__()
        if hidden_dim < 2:
            raise ValueError("hidden_dim must be at least 2")
        if encoder_width < 1:
            raise ValueError("encoder_width must be positive")
        if not (residual_cap > 0.0):
            raise ValueError("residual_cap must be positive")
        if not (normalization_eps > 0.0):
            raise ValueError("normalization_eps must be positive")
        if not (metric_log_diagonal_cap > 0.0):
            raise ValueError("metric_log_diagonal_cap must be positive")
        if not (metric_offdiagonal_cap > 0.0):
            raise ValueError("metric_offdiagonal_cap must be positive")

        self.hidden_dim = int(hidden_dim)
        self.encoder_width = int(encoder_width)
        self.residual_cap = float(residual_cap)
        self.normalization_eps = float(normalization_eps)
        self.metric_log_diagonal_cap = float(metric_log_diagonal_cap)
        self.metric_offdiagonal_cap = float(metric_offdiagonal_cap)

        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.operator_trunk = nn.Sequential(
            nn.Linear(N_STATES * N_STATES, self.encoder_width),
            nn.SiLU(),
            nn.Linear(self.encoder_width, self.encoder_width),
            nn.SiLU(),
        )
        self.operator_head = nn.Linear(
            self.encoder_width,
            self.hidden_dim * self.hidden_dim,
        )
        self.decoder = nn.Linear(self.hidden_dim, N_STATES, bias=False)
        self.metric_log_diagonal = nn.Parameter(torch.zeros(self.hidden_dim))
        lower_indices = torch.tril_indices(
            self.hidden_dim,
            self.hidden_dim,
            offset=-1,
        )
        self.metric_strict_lower = nn.Parameter(
            torch.zeros(lower_indices.shape[1])
        )
        self.register_buffer("_lower_rows", lower_indices[0], persistent=False)
        self.register_buffer("_lower_columns", lower_indices[1], persistent=False)
        self.register_buffer(
            "_identity",
            torch.eye(self.hidden_dim),
            persistent=False,
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.normal_(self.state_embedding.weight, std=0.30)
        for module in self.operator_trunk:
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
        # Start near, but not exactly at, the identity. This gives all layers a
        # gradient on the first update without supplying any operator semantics.
        nn.init.normal_(self.operator_head.weight, std=0.005)
        nn.init.zeros_(self.operator_head.bias)
        nn.init.normal_(self.decoder.weight, std=0.30)
        nn.init.zeros_(self.metric_log_diagonal)
        nn.init.zeros_(self.metric_strict_lower)

    def metric_factor(self) -> torch.Tensor:
        """Return ``L`` for the unit-determinant metric ``G = L L^T``.

        Bounded coordinates prevent the metric parameterization itself from
        producing singular or numerically extreme charts. Centering the log
        diagonal fixes ``det(L)=1`` and hence ``det(G)=1``.
        """

        log_diagonal = self.metric_log_diagonal_cap * torch.tanh(
            self.metric_log_diagonal
        )
        log_diagonal = log_diagonal - log_diagonal.mean()
        diagonal = torch.exp(log_diagonal)
        strict_values = self.metric_offdiagonal_cap * torch.tanh(
            self.metric_strict_lower
        )
        strict_lower = torch.zeros(
            self.hidden_dim,
            self.hidden_dim,
            dtype=diagonal.dtype,
            device=diagonal.device,
        ).index_put(
            (self._lower_rows, self._lower_columns),
            strict_values,
        )
        return torch.diag(diagonal) + strict_lower

    def invariant_metric(self) -> torch.Tensor:
        """Return the learned candidate metric used by the recurrence.

        The name denotes the metric targeted by auxiliary invariance losses;
        the model does not claim or enforce operator isometry by construction.
        """

        factor = self.metric_factor()
        return factor @ factor.transpose(-1, -2)

    def _validate_tables(self, tables: torch.Tensor) -> tuple[int, int]:
        if tables.ndim != 4:
            raise ValueError("tables must have shape (batch, operators, states, states)")
        if tables.shape[-2:] != (N_STATES, N_STATES):
            raise ValueError(
                f"table state axes must both have length {N_STATES}; got {tuple(tables.shape[-2:])}"
            )
        if tables.shape[0] < 1 or tables.shape[1] < 1:
            raise ValueError("tables must contain at least one batch item and one operator")
        return int(tables.shape[0]), int(tables.shape[1])

    def _bounded_residual(self, raw: torch.Tensor) -> torch.Tensor:
        """Smoothly map every raw matrix into an open Frobenius ball."""

        norm = torch.linalg.vector_norm(raw.flatten(start_dim=-2), dim=-1)
        denominator = torch.sqrt(1.0 + (norm / self.residual_cap).square())
        return raw / denominator[..., None, None]

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        features = tables.reshape(batch * operators, N_STATES * N_STATES)
        raw = self.operator_head(self.operator_trunk(features)).reshape(
            batch,
            operators,
            self.hidden_dim,
            self.hidden_dim,
        )
        residual = self._bounded_residual(raw)
        matrices = self._identity.to(dtype=residual.dtype) + residual
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=residual,
            raw_residuals=raw,
        )

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return self.encode_operator_bundle(tables).matrices

    def hidden_norm(
        self,
        hidden: torch.Tensor,
        metric: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Measure hidden vectors in the learned ambient metric."""

        if metric is None:
            metric = self.invariant_metric()
        squared_norm = torch.einsum("...i,ij,...j->...", hidden, metric, hidden)
        return squared_norm.clamp_min(self.normalization_eps**2).sqrt()

    def normalize_hidden(
        self,
        hidden: torch.Tensor,
        metric: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Choose the learned-metric unit representative of each positive ray."""

        norm = self.hidden_norm(hidden, metric)
        return hidden / norm.unsqueeze(-1)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.normalize_hidden(self.state_embedding(start))

    def state_anchors(self) -> torch.Tensor:
        """Return all learned semantic anchors as metric-unit row vectors."""

        states = torch.arange(N_STATES, device=self.state_embedding.weight.device)
        return self.initial_hidden(states)

    def anchor_matrix(self) -> torch.Tensor:
        """Return the learned ``(hidden, states)`` semantic anchor matrix."""

        return self.state_anchors().transpose(0, 1)

    @staticmethod
    def linear_step(hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        """Apply an ambient operator without fixing the radial gauge."""

        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return self.normalize_hidden(self.linear_step(hidden, code))

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)

    def _validate_rollout_inputs(
        self,
        operator_matrices: torch.Tensor,
        op_slots: torch.Tensor,
        hidden: torch.Tensor,
    ) -> None:
        batch, operators = operator_matrices.shape[:2]
        if operator_matrices.shape[2:] != (self.hidden_dim, self.hidden_dim):
            raise ValueError("operator matrix hidden dimensions do not match the model")
        if op_slots.ndim != 2 or op_slots.shape[0] != batch:
            raise ValueError("op_slots must have shape (batch, time)")
        if hidden.shape != (batch, self.hidden_dim):
            raise ValueError("hidden must have shape (batch, hidden_dim)")
        if op_slots.dtype != torch.long:
            raise TypeError("op_slots must use torch.long indices")
        if op_slots.numel() and bool(((op_slots < 0) | (op_slots >= operators)).any()):
            raise IndexError("op_slots contains an out-of-range operator index")

    def _rollout(
        self,
        hidden: torch.Tensor,
        operator_matrices: torch.Tensor,
        op_slots: torch.Tensor,
        *,
        raw_operator_matrices: torch.Tensor | None,
        residual_operator_matrices: torch.Tensor | None,
    ) -> PacketRunTrace:
        metric = self.invariant_metric()
        hidden = self.normalize_hidden(hidden, metric)
        self._validate_rollout_inputs(operator_matrices, op_slots, hidden)
        batch = hidden.shape[0]
        rows = torch.arange(batch, device=hidden.device)
        trajectory = [hidden]
        proposals: list[torch.Tensor] = []
        radial_norms: list[torch.Tensor] = []
        selected: list[torch.Tensor] = []

        for time_index in range(op_slots.shape[1]):
            code = operator_matrices[rows, op_slots[:, time_index]]
            proposal = self.linear_step(hidden, code)
            radius = self.hidden_norm(proposal, metric)
            hidden = proposal / radius.unsqueeze(-1)
            selected.append(code)
            proposals.append(proposal)
            radial_norms.append(radius)
            trajectory.append(hidden)

        if selected:
            selected_tensor = torch.stack(selected, dim=1)
            radius_tensor = torch.stack(radial_norms, dim=1)
        else:
            selected_tensor = operator_matrices.new_empty(
                (batch, 0, self.hidden_dim, self.hidden_dim)
            )
            radius_tensor = operator_matrices.new_empty((batch, 0))

        return PacketRunTrace(
            logits=self.decode_hidden(hidden),
            hidden=trajectory,
            operator_codes=operator_matrices,
            raw_operator_matrices=raw_operator_matrices,
            residual_operator_matrices=residual_operator_matrices,
            selected_operator_matrices=selected_tensor,
            pre_normalized_hidden=proposals,
            radial_norms=radius_tensor,
            metric=metric,
        )

    def run(
        self,
        tables: torch.Tensor,
        op_slots: torch.Tensor,
        start: torch.Tensor,
    ) -> PacketRunTrace:
        bundle = self.encode_operator_bundle(tables)
        if start.ndim != 1 or start.shape[0] != tables.shape[0]:
            raise ValueError("start must have shape (batch,)")
        return self._rollout(
            self.initial_hidden(start),
            bundle.matrices,
            op_slots,
            raw_operator_matrices=bundle.raw_residuals,
            residual_operator_matrices=bundle.residuals,
        )

    def continue_from_hidden(
        self,
        hidden: torch.Tensor,
        operator_codes: torch.Tensor,
        op_slots: torch.Tensor,
    ) -> PacketRunTrace:
        """Continue from a ray; positive rescaling of ``hidden`` is immaterial."""

        return self._rollout(
            hidden,
            operator_codes,
            op_slots,
            raw_operator_matrices=None,
            residual_operator_matrices=operator_codes - self._identity.to(
                dtype=operator_codes.dtype
            ),
        )

    def terminal_task(
        self,
        tables: torch.Tensor,
        op_slots: torch.Tensor,
        start: torch.Tensor,
        target: torch.Tensor,
        *,
        label_smoothing: float = 0.0,
    ) -> TerminalTaskResult:
        """Evaluate the terminal-answer objective without intermediate labels."""

        trace = self.run(tables, op_slots, start)
        loss = F.cross_entropy(
            trace.logits,
            target,
            label_smoothing=float(label_smoothing),
        )
        accuracy = (trace.logits.argmax(dim=-1) == target).to(trace.logits.dtype).mean()
        return TerminalTaskResult(loss=loss, accuracy=accuracy, trace=trace)

    def terminal_loss(
        self,
        tables: torch.Tensor,
        op_slots: torch.Tensor,
        start: torch.Tensor,
        target: torch.Tensor,
        *,
        label_smoothing: float = 0.0,
    ) -> torch.Tensor:
        """Convenience scalar for a terminal-only training loop."""

        return self.terminal_task(
            tables,
            op_slots,
            start,
            target,
            label_smoothing=label_smoothing,
        ).loss


class ProjectiveLinearTableOperatorRNN(ProjectiveResidualOperatorRNN):
    """Direct learned table-to-operator map with projective metric recurrence.

    This arm preserves the successful inductive bias of the original compact
    linear hypernetwork: the 64 visible entries of each anonymous operator
    table are mapped linearly to one ambient matrix. The encoder is bias-free,
    and its weights are learned. It does *not* insert the table itself, perform
    anchor conjugation, or compile an exact permutation action.

    With the default 12-dimensional ambient space the model has 9,486 learned
    parameters. The eight state anchors can therefore occupy an eight-
    dimensional semantic plane while leaving a genuine four-dimensional
    ambient complement for delayed-return tests.
    """

    model_name = "projective_linear_table"

    def __init__(
        self,
        hidden_dim: int = 12,
        normalization_eps: float = 1e-8,
        metric_log_diagonal_cap: float = 1.5,
        metric_offdiagonal_cap: float = 0.75,
    ) -> None:
        # Share the rollout and learned-metric implementation without
        # allocating the residual MLP used by the comparison arm.
        nn.Module.__init__(self)
        if hidden_dim < 2:
            raise ValueError("hidden_dim must be at least 2")
        if not (normalization_eps > 0.0):
            raise ValueError("normalization_eps must be positive")
        if not (metric_log_diagonal_cap > 0.0):
            raise ValueError("metric_log_diagonal_cap must be positive")
        if not (metric_offdiagonal_cap > 0.0):
            raise ValueError("metric_offdiagonal_cap must be positive")

        self.hidden_dim = int(hidden_dim)
        self.normalization_eps = float(normalization_eps)
        self.metric_log_diagonal_cap = float(metric_log_diagonal_cap)
        self.metric_offdiagonal_cap = float(metric_offdiagonal_cap)

        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.operator_encoder = nn.Linear(
            N_STATES * N_STATES,
            self.hidden_dim * self.hidden_dim,
            bias=False,
        )
        self.decoder = nn.Linear(self.hidden_dim, N_STATES, bias=False)
        self.metric_log_diagonal = nn.Parameter(torch.zeros(self.hidden_dim))
        lower_indices = torch.tril_indices(
            self.hidden_dim,
            self.hidden_dim,
            offset=-1,
        )
        self.metric_strict_lower = nn.Parameter(
            torch.zeros(lower_indices.shape[1])
        )
        self.register_buffer("_lower_rows", lower_indices[0], persistent=False)
        self.register_buffer("_lower_columns", lower_indices[1], persistent=False)
        self.register_buffer(
            "_identity",
            torch.eye(self.hidden_dim),
            persistent=False,
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.normal_(self.state_embedding.weight, std=0.30)
        nn.init.normal_(self.operator_encoder.weight, std=0.01)
        nn.init.normal_(self.decoder.weight, std=0.30)
        nn.init.zeros_(self.metric_log_diagonal)
        nn.init.zeros_(self.metric_strict_lower)

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        batch, operators = self._validate_tables(tables)
        matrices = self.operator_encoder(
            tables.reshape(batch * operators, N_STATES * N_STATES)
        ).reshape(
            batch,
            operators,
            self.hidden_dim,
            self.hidden_dim,
        )
        return OperatorMatrixBundle(
            matrices=matrices,
            residuals=None,
            raw_residuals=matrices,
        )

    def continue_from_hidden(
        self,
        hidden: torch.Tensor,
        operator_codes: torch.Tensor,
        op_slots: torch.Tensor,
    ) -> PacketRunTrace:
        return self._rollout(
            hidden,
            operator_codes,
            op_slots,
            raw_operator_matrices=None,
            residual_operator_matrices=None,
        )


class PolarIsometricTableOperatorRNN(ProjectiveLinearTableOperatorRNN):
    """Hard Euclidean-polar control in the canonical ``G = I`` gauge.

    The same bias-free learned table encoder first produces an unconstrained
    ambient matrix ``A``. Its recurrent code is the closest orthogonal factor
    ``U V^T`` from a full SVD ``A = U Sigma V^T``. No determinant correction is
    applied, so both connected components of ``O(12)`` remain available and
    the factor has determinant ``+1`` or ``-1`` according to the learned raw
    matrix. This is an isometric architectural control, not an exact task or
    permutation compiler.

    The metric parameters are retained, zeroed, and frozen solely for state-
    dict and trace compatibility with the other v0.4 models. Recurrence and
    normalization use the exact identity metric.
    """

    model_name = "polar_isometric_table"

    def __init__(
        self,
        hidden_dim: int = 12,
        normalization_eps: float = 1e-8,
    ) -> None:
        if hidden_dim != 12:
            raise ValueError("polar-isometric v0.4 control requires hidden_dim == 12")
        super().__init__(
            hidden_dim=hidden_dim,
            normalization_eps=normalization_eps,
        )
        with torch.no_grad():
            self.metric_log_diagonal.zero_()
            self.metric_strict_lower.zero_()
        self.metric_log_diagonal.requires_grad_(False)
        self.metric_strict_lower.requires_grad_(False)

    def invariant_metric(self) -> torch.Tensor:
        """Return the exact canonical Euclidean metric."""

        return self._identity

    @staticmethod
    def polar_retraction(raw_matrices: torch.Tensor) -> torch.Tensor:
        """Retract square matrices to ``O(d)`` without choosing an orientation."""

        if not isinstance(raw_matrices, torch.Tensor):
            raise TypeError("raw_matrices must be a torch.Tensor")
        if not raw_matrices.is_floating_point():
            raise TypeError("raw_matrices must have a floating dtype")
        if raw_matrices.ndim < 2 or raw_matrices.shape[-1] != raw_matrices.shape[-2]:
            raise ValueError("raw_matrices must end in equal square dimensions")
        left, _, right_transpose = torch.linalg.svd(
            raw_matrices,
            full_matrices=False,
        )
        return left @ right_transpose

    def encode_operator_bundle(self, tables: torch.Tensor) -> OperatorMatrixBundle:
        raw_bundle = super().encode_operator_bundle(tables)
        raw_matrices = raw_bundle.matrices
        isometries = self.polar_retraction(raw_matrices)
        return OperatorMatrixBundle(
            matrices=isometries,
            residuals=None,
            raw_residuals=raw_matrices,
        )


__all__ = [
    "OperatorMatrixBundle",
    "PacketRunTrace",
    "PolarIsometricTableOperatorRNN",
    "ProjectiveLinearTableOperatorRNN",
    "ProjectiveResidualOperatorRNN",
    "TerminalTaskResult",
]
