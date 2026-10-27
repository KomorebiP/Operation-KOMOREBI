"""Fixed-gauge invariant-kernel recurrent models for the v0.6 block.

The v0.4/v0.5 hard-polar model makes every recurrent operator an element of
``O(12)`` but does not stop an operator from mixing task-observable directions
with the four-dimensional ambient complement.  This module makes that missing
invariant explicit without choosing a privileged *ambient* coordinate system.

Let ``W in SO(12)`` be a fixed, seeded global orthogonal frame and write

``W = [S | L | K]`` with widths seven, one, and four.  ``S`` is the
centered-logit behavioral space, ``L`` is the common-logit gauge line, and
``K`` is the registered ambient fiber.  The model is constructed so that

``h_start = sqrt(7/8) S z_start + (1/sqrt(8)) L``
``M(table) = W diag(A(table), 1, R(table)) W.T``
``logits = D_sem S.T h + 1 (L.T h)``

where each ``z_start`` is a unit vector, ``A(table) in O(7)`` is learned, and
``R(table) in O(4)`` is a frozen
nuisance-fiber polar factor.  Centering the logits annihilates both ``L`` and
``K``.  Every block is invariant, so the cross-block terms vanish in exact
arithmetic.  The public audit reports the finite-precision residual rather
than silently assuming the invariant.

The seven-dimensional choice is not a posthoc singular-value cutoff.  For
eight logits, the centering map has exact rank seven; the discarded line is
the softmax-invariant common shift.  Thus the total exact kernel of centered
instantaneous behavior has dimension five: ``L + K``.  The global frame is
intentionally a gauge: terminal task behavior is invariant under a
simultaneous change of ``W`` in the embeddings, operators, and decoder.
Learning it would therefore add an unidentifiable parameter.  We instead draw
it deterministically from a local seed and store it in the state dict.
The shared line component allows eight anchors to become an orthonormal frame
when their seven-dimensional parts form a regular simplex, while contributing
only a behaviorally irrelevant common-logit shift.  Likewise, the fiber block ``R`` is dormant under terminal-only task loss: it
is available for explicit fiber experiments, but cannot be presented as
learned memory without a separate causally justified objective.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from .algebra import N_STATES
from .models import RecurrentOperatorModel


HIDDEN_DIM = 12
OBSERVABLE_DIM = N_STATES - 1
# Backward-compatible name inside this new module: "semantic" always means
# centered-logit behavioral coordinates, not the eight raw logit coordinates.
SEMANTIC_DIM = OBSERVABLE_DIM
COMMON_LOGIT_DIM = 1
AMBIENT_DIM = HIDDEN_DIM - OBSERVABLE_DIM - COMMON_LOGIT_DIM
CENTERED_NULL_DIM = COMMON_LOGIT_DIM + AMBIENT_DIM


@dataclass(frozen=True)
class InvariantKernelOperatorBundle:
    """Executed operators together with their learned-frame factorization."""

    matrices: torch.Tensor
    semantic_blocks: torch.Tensor
    common_blocks: torch.Tensor
    ambient_blocks: torch.Tensor
    gauge: torch.Tensor


@dataclass(frozen=True)
class InvariantKernelAudit:
    """Fail-closed numerical receipt for the structural invariant.

    Residuals are maximum Frobenius norms over all supplied operators.  The
    embedding and decoder fields audit the other sides of the contract: every
    state anchor has its prescribed shared ``L`` coefficient, no state anchor
    enters ``K``, and neither ``L`` nor ``K`` is visible after logit centering.
    """

    tolerance: float
    frame_orthogonality_residual: float
    projector_partition_residual: float
    operator_orthogonality_residual: float
    pmq_residual: float
    qmp_residual: float
    null_cross_residual: float
    embedding_kernel_residual: float
    embedding_common_residual: float
    embedding_norm_residual: float
    decoder_kernel_residual: float
    common_logit_residual: float
    all_finite: bool

    @property
    def passed(self) -> bool:
        residuals = (
            self.frame_orthogonality_residual,
            self.projector_partition_residual,
            self.operator_orthogonality_residual,
            self.pmq_residual,
            self.qmp_residual,
            self.null_cross_residual,
            self.embedding_kernel_residual,
            self.embedding_common_residual,
            self.embedding_norm_residual,
            self.decoder_kernel_residual,
            self.common_logit_residual,
        )
        return self.all_finite and all(value <= self.tolerance for value in residuals)

    def as_dict(self) -> dict[str, float | bool]:
        return {
            "tolerance": self.tolerance,
            "frame_orthogonality_residual": self.frame_orthogonality_residual,
            "projector_partition_residual": self.projector_partition_residual,
            "operator_orthogonality_residual": self.operator_orthogonality_residual,
            "pmq_residual": self.pmq_residual,
            "qmp_residual": self.qmp_residual,
            "null_cross_residual": self.null_cross_residual,
            "embedding_kernel_residual": self.embedding_kernel_residual,
            "embedding_common_residual": self.embedding_common_residual,
            "embedding_norm_residual": self.embedding_norm_residual,
            "decoder_kernel_residual": self.decoder_kernel_residual,
            "common_logit_residual": self.common_logit_residual,
            "all_finite": self.all_finite,
            "passed": self.passed,
        }


class LearnedFrameBlockIsometricOperatorRNN(RecurrentOperatorModel):
    """Twelve-dimensional recurrence with an exact invariant 7+1+4 split.

    The behavioral operator block is learned from each visible 8-by-8 table. A
    separately initialized *frozen* ambient encoder supplies a nuisance-fiber
    block.  A polar retraction makes both blocks orthogonal before they are
    assembled in the fixed global gauge.  Freezing the ambient encoder makes
    the scientific boundary explicit: terminal supervision cannot be credited
    with learning a fiber that is architecturally invisible and dynamically
    isolated.  No canonical group name, generator identity, conjugating
    permutation, or exact table action is inserted into the learned model.

    The learned part of each state anchor and every centered decoder contrast
    are parameterized inside ``S``.  Each anchor also receives the same fixed
    ``1/sqrt(8)`` component in ``L``; this makes an orthonormal eight-anchor
    solution possible when the ``S`` components form a regular simplex.
    ``L`` contributes only an identical shift to every logit, and ``K``
    contributes nothing.  This makes the centered-kernel contract architectural.
    """

    model_name = "learned_frame_block_isometric"

    def __init__(
        self,
        hidden_dim: int = HIDDEN_DIM,
        semantic_dim: int = SEMANTIC_DIM,
        *,
        gauge_seed: int = 607,
        normalization_eps: float = 1e-12,
    ) -> None:
        super().__init__()
        if hidden_dim != HIDDEN_DIM:
            raise ValueError(f"invariant-kernel v0.6 requires hidden_dim == {HIDDEN_DIM}")
        if semantic_dim != SEMANTIC_DIM:
            raise ValueError(
                f"invariant-kernel v0.6 requires semantic_dim == {SEMANTIC_DIM}"
            )
        if isinstance(gauge_seed, bool) or not isinstance(gauge_seed, int):
            raise TypeError("gauge_seed must be an integer")
        if not math.isfinite(normalization_eps) or normalization_eps <= 0.0:
            raise ValueError("normalization_eps must be finite and positive")

        self.hidden_dim = int(hidden_dim)
        self.semantic_dim = int(semantic_dim)
        self.common_logit_dim = COMMON_LOGIT_DIM
        self.ambient_dim = AMBIENT_DIM
        initialization_gauge_seed = int(gauge_seed)
        self.normalization_eps = float(normalization_eps)

        # These weights live in the seven-dimensional behavioral chart. Their
        # effective ambient forms are exposed by methods below for auditing.
        self.semantic_state_embedding = nn.Embedding(N_STATES, self.semantic_dim)
        self.semantic_decoder = nn.Linear(self.semantic_dim, N_STATES, bias=False)

        features = N_STATES * N_STATES
        self.semantic_operator_encoder = nn.Linear(
            features,
            self.semantic_dim * self.semantic_dim,
            bias=False,
        )
        self.ambient_operator_encoder = nn.Linear(
            features,
            self.ambient_dim * self.ambient_dim,
            bias=False,
        )

        # W is pure gauge in this hard direct-sum architecture.  A local CPU
        # generator makes it deterministic without perturbing the experiment's
        # global training RNG.  Sign-normalized QR removes platform-dependent
        # column signs, and the last column is flipped to choose SO(12).
        generator = torch.Generator(device="cpu").manual_seed(initialization_gauge_seed)
        raw_gauge = torch.randn(
            self.hidden_dim,
            self.hidden_dim,
            generator=generator,
            dtype=torch.float64,
        )
        gauge, triangular = torch.linalg.qr(raw_gauge)
        signs = torch.sign(torch.diagonal(triangular))
        signs = torch.where(signs == 0, torch.ones_like(signs), signs)
        gauge = gauge @ torch.diag(signs)
        if float(torch.linalg.det(gauge)) < 0.0:
            gauge[:, -1].neg_()
        # Preserve the sealed frame at construction precision.  Float32
        # executions receive an explicit cast at the operator boundary; a
        # later float64 audit must not merely promote already-rounded entries.
        self.register_buffer("_gauge", gauge, persistent=True)
        self.register_buffer(
            "_gauge_seed",
            torch.tensor(initialization_gauge_seed, dtype=torch.int64),
            persistent=True,
        )
        self.register_buffer(
            "_hidden_identity",
            torch.eye(self.hidden_dim),
            persistent=False,
        )
        self.register_buffer(
            "_semantic_identity",
            torch.eye(self.semantic_dim),
            persistent=False,
        )
        self.register_buffer(
            "_common_identity",
            torch.eye(COMMON_LOGIT_DIM),
            persistent=False,
        )
        self.register_buffer(
            "_ambient_identity",
            torch.eye(self.ambient_dim),
            persistent=False,
        )
        self.register_buffer(
            "_common_logit_scale",
            torch.ones(COMMON_LOGIT_DIM),
            persistent=True,
        )
        self.register_buffer(
            "_anchor_behavioral_scale",
            torch.tensor(
                math.sqrt(OBSERVABLE_DIM / N_STATES),
                dtype=torch.float64,
            ),
            persistent=True,
        )
        self.register_buffer(
            "_anchor_common_scale",
            torch.tensor(1.0 / math.sqrt(N_STATES), dtype=torch.float64),
            persistent=True,
        )
        self.reset_parameters()
        # The ambient block is a sealed nuisance control, not a terminally
        # learned scratchpad.  Keeping it as a frozen Parameter preserves a
        # conventional state_dict entry while excluding it from optimization.
        self.ambient_operator_encoder.weight.requires_grad_(False)

    def reset_parameters(self) -> None:
        nn.init.normal_(self.semantic_state_embedding.weight, std=0.30)
        nn.init.normal_(self.semantic_decoder.weight, std=0.30)
        nn.init.normal_(self.semantic_operator_encoder.weight, std=0.02)
        nn.init.normal_(self.ambient_operator_encoder.weight, std=0.02)

    @staticmethod
    def polar_retraction(raw_matrices: torch.Tensor) -> torch.Tensor:
        """Return the closest O(d) factor without determinant correction."""

        if not isinstance(raw_matrices, torch.Tensor):
            raise TypeError("raw_matrices must be a torch.Tensor")
        if not raw_matrices.is_floating_point():
            raise TypeError("raw_matrices must have a floating dtype")
        if raw_matrices.ndim < 2 or raw_matrices.shape[-2] != raw_matrices.shape[-1]:
            raise ValueError("raw_matrices must end in square dimensions")
        left, _, right_transpose = torch.linalg.svd(raw_matrices, full_matrices=False)
        return left @ right_transpose

    def gauge_matrix(self) -> torch.Tensor:
        """Return the fixed seeded global orthogonal frame ``W``."""

        return self._gauge

    @property
    def gauge_seed(self) -> int:
        """Initialization seed stored alongside the persistent gauge."""

        return int(self._gauge_seed.item())

    @property
    def S(self) -> torch.Tensor:
        """Centered-logit behavioral frame, shape ``(12, 7)``."""

        return self._gauge[:, : self.semantic_dim]

    @property
    def L(self) -> torch.Tensor:
        """Common-logit gauge frame, shape ``(12, 1)``."""

        begin = self.semantic_dim
        return self._gauge[:, begin : begin + COMMON_LOGIT_DIM]

    @property
    def K(self) -> torch.Tensor:
        """Registered ambient-fiber frame, shape ``(12, 4)``."""

        return self._gauge[:, self.semantic_dim + COMMON_LOGIT_DIM :]

    @property
    def P_S(self) -> torch.Tensor:
        """Rank-seven centered-logit behavioral projector ``S S.T``."""

        return self.S @ self.S.transpose(-1, -2)

    @property
    def P_L(self) -> torch.Tensor:
        """Rank-one common-logit gauge projector ``L L.T``."""

        return self.L @ self.L.transpose(-1, -2)

    @property
    def P_K(self) -> torch.Tensor:
        """Rank-four registered ambient-fiber projector ``K K.T``."""

        return self.K @ self.K.transpose(-1, -2)

    @property
    def P_centered_null(self) -> torch.Tensor:
        """Rank-five exact null projector of centered instantaneous logits."""

        return self.P_L + self.P_K

    # Explicit method aliases make evaluator code readable and avoid treating
    # S as a claim about a privileged coordinate basis.
    def behavioral_frame(self) -> torch.Tensor:
        return self.S

    def common_logit_frame(self) -> torch.Tensor:
        return self.L

    def ambient_frame(self) -> torch.Tensor:
        return self.K

    def behavioral_projector(self) -> torch.Tensor:
        return self.P_S

    def common_logit_projector(self) -> torch.Tensor:
        return self.P_L

    def ambient_projector(self) -> torch.Tensor:
        return self.P_K

    def centered_null_projector(self) -> torch.Tensor:
        return self.P_centered_null

    # Narrow compatibility aliases.  They deliberately denote the registered
    # behavioral and ambient-fiber pieces only; callers concerned with the
    # exact behavioral null must use P_centered_null, which also includes L.
    @property
    def U(self) -> torch.Tensor:
        return self.S

    @property
    def V(self) -> torch.Tensor:
        return self.K

    @property
    def P(self) -> torch.Tensor:
        return self.P_S

    @property
    def Q(self) -> torch.Tensor:
        """Compatibility alias for the full centered-behavioral null projector."""

        return self.P_centered_null

    def semantic_frame(self) -> torch.Tensor:
        return self.S

    def semantic_projector(self) -> torch.Tensor:
        return self.P_S

    def invariant_metric(self) -> torch.Tensor:
        """The executed recurrence is isometric in the Euclidean metric."""

        return self._hidden_identity

    def state_anchors(self) -> torch.Tensor:
        """Return all effective twelve-dimensional semantic state anchors."""

        states = torch.arange(N_STATES, device=self._gauge.device)
        return self.initial_hidden(states)

    def anchor_matrix(self) -> torch.Tensor:
        return self.state_anchors().transpose(0, 1)

    def effective_state_embedding(self) -> torch.Tensor:
        """Return unit anchors with learned ``S`` and fixed shared ``L`` parts."""

        semantic = F.normalize(
            self.semantic_state_embedding.weight,
            dim=-1,
            eps=self.normalization_eps,
        )
        frame = self.behavioral_frame().to(dtype=semantic.dtype)
        common_frame = self.common_logit_frame().to(dtype=semantic.dtype)
        behavioral = (
            self._anchor_behavioral_scale.to(dtype=semantic.dtype)
            * (semantic @ frame.transpose(-1, -2))
        )
        common = self._anchor_common_scale.to(dtype=semantic.dtype) * common_frame.T
        return behavioral + common.expand(N_STATES, -1)

    def effective_decoder_weight(self) -> torch.Tensor:
        """Return the full readout, including the common-logit gauge line."""

        frame = self.behavioral_frame().to(dtype=self.semantic_decoder.weight.dtype)
        behavioral = self.semantic_decoder.weight @ frame.transpose(-1, -2)
        common = torch.ones(
            N_STATES,
            COMMON_LOGIT_DIM,
            dtype=behavioral.dtype,
            device=behavioral.device,
        )
        common = common * self._common_logit_scale.to(dtype=behavioral.dtype)
        common_frame = self.common_logit_frame().to(dtype=behavioral.dtype)
        return behavioral + common @ common_frame.transpose(-1, -2)

    def centered_effective_decoder_weight(self) -> torch.Tensor:
        """Return the readout after exact removal of the common-logit shift."""

        decoder = self.effective_decoder_weight()
        centering = torch.eye(
            N_STATES,
            dtype=decoder.dtype,
            device=decoder.device,
        ) - torch.full(
            (N_STATES, N_STATES),
            1.0 / float(N_STATES),
            dtype=decoder.dtype,
            device=decoder.device,
        )
        return centering @ decoder

    def _validate_tables(self, tables: torch.Tensor) -> tuple[int, int]:
        if not isinstance(tables, torch.Tensor):
            raise TypeError("tables must be a torch.Tensor")
        if not tables.is_floating_point():
            raise TypeError("tables must have a floating dtype")
        if tables.ndim != 4 or tables.shape[-2:] != (N_STATES, N_STATES):
            raise ValueError(
                "tables must have shape (batch, operators, states, states)"
            )
        if tables.shape[0] < 1 or tables.shape[1] < 1:
            raise ValueError("tables must contain a batch item and an operator")
        return int(tables.shape[0]), int(tables.shape[1])

    def semantic_operator_blocks(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = self._validate_tables(tables)
        raw = self.semantic_operator_encoder(
            tables.reshape(batch * operators, N_STATES * N_STATES)
        ).reshape(batch, operators, self.semantic_dim, self.semantic_dim)
        return self.polar_retraction(raw)

    def ambient_operator_blocks(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = self._validate_tables(tables)
        raw = self.ambient_operator_encoder(
            tables.reshape(batch * operators, N_STATES * N_STATES)
        ).reshape(batch, operators, self.ambient_dim, self.ambient_dim)
        return self.polar_retraction(raw)

    def assemble_operator_blocks(
        self,
        semantic_blocks: torch.Tensor,
        ambient_blocks: torch.Tensor,
    ) -> torch.Tensor:
        """Assemble ``W diag(A, R) W.T`` without a leakage-prone soft mask."""

        if semantic_blocks.shape[:-2] != ambient_blocks.shape[:-2]:
            raise ValueError("semantic and ambient blocks must share leading axes")
        if semantic_blocks.shape[-2:] != (self.semantic_dim, self.semantic_dim):
            raise ValueError("semantic blocks have the wrong dimensions")
        if ambient_blocks.shape[-2:] != (self.ambient_dim, self.ambient_dim):
            raise ValueError("ambient blocks have the wrong dimensions")
        leading = semantic_blocks.shape[:-2]
        common = self._common_identity.to(dtype=semantic_blocks.dtype).expand(
            *leading, COMMON_LOGIT_DIM, COMMON_LOGIT_DIM
        )
        block_diagonal = semantic_blocks.new_zeros(
            (*leading, self.hidden_dim, self.hidden_dim)
        )
        s_end = self.semantic_dim
        l_end = s_end + COMMON_LOGIT_DIM
        block_diagonal[..., :s_end, :s_end] = semantic_blocks
        block_diagonal[..., s_end:l_end, s_end:l_end] = common
        block_diagonal[..., l_end:, l_end:] = ambient_blocks
        gauge = self.gauge_matrix().to(dtype=block_diagonal.dtype)
        # W B W^T, written as an einsum so arbitrary batch/operator leading
        # dimensions remain intact.
        return torch.einsum("ia,...ab,jb->...ij", gauge, block_diagonal, gauge)

    def encode_operator_bundle(self, tables: torch.Tensor) -> InvariantKernelOperatorBundle:
        semantic = self.semantic_operator_blocks(tables)
        ambient = self.ambient_operator_blocks(tables)
        matrices = self.assemble_operator_blocks(semantic, ambient)
        common = self._common_identity.to(dtype=matrices.dtype).expand(
            *semantic.shape[:-2], COMMON_LOGIT_DIM, COMMON_LOGIT_DIM
        )
        return InvariantKernelOperatorBundle(
            matrices=matrices,
            semantic_blocks=semantic,
            common_blocks=common,
            ambient_blocks=ambient,
            gauge=self.gauge_matrix().to(dtype=matrices.dtype),
        )

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return self.encode_operator_bundle(tables).matrices

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        if start.dtype != torch.long:
            raise TypeError("start must use torch.long indices")
        if start.ndim != 1:
            raise ValueError("start must have shape (batch,)")
        semantic = F.normalize(
            self.semantic_state_embedding(start),
            dim=-1,
            eps=self.normalization_eps,
        )
        frame = self.behavioral_frame().to(dtype=semantic.dtype)
        common_frame = self.common_logit_frame().to(dtype=semantic.dtype)
        behavioral = (
            self._anchor_behavioral_scale.to(dtype=semantic.dtype)
            * (semantic @ frame.transpose(-1, -2))
        )
        common = self._anchor_common_scale.to(dtype=semantic.dtype) * common_frame.T
        return behavioral + common.expand(start.shape[0], -1)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        if hidden.ndim != 2 or hidden.shape[-1] != self.hidden_dim:
            raise ValueError("hidden must have shape (batch, hidden_dim)")
        if code.ndim != 3 or code.shape != (
            hidden.shape[0],
            self.hidden_dim,
            self.hidden_dim,
        ):
            raise ValueError("code must have shape (batch, hidden_dim, hidden_dim)")
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        if hidden.ndim != 2 or hidden.shape[-1] != self.hidden_dim:
            raise ValueError("hidden must have shape (batch, hidden_dim)")
        semantic_coordinates = hidden @ self.behavioral_frame().to(dtype=hidden.dtype)
        common_coordinate = hidden @ self.common_logit_frame().to(dtype=hidden.dtype)
        common_shift = common_coordinate * self._common_logit_scale.to(
            dtype=hidden.dtype
        )
        return self.semantic_decoder(semantic_coordinates) + common_shift

    @staticmethod
    def _maximum_frobenius(value: torch.Tensor) -> torch.Tensor:
        norms = torch.linalg.matrix_norm(value, ord="fro", dim=(-2, -1))
        return norms.max() if norms.ndim else norms

    def audit_invariant_kernel(
        self,
        operator_codes: torch.Tensor,
        *,
        tolerance: float | None = None,
    ) -> InvariantKernelAudit:
        """Audit isometry, subspace isolation, embedding, and readout leakage."""

        if operator_codes.ndim < 2 or operator_codes.shape[-2:] != (
            self.hidden_dim,
            self.hidden_dim,
        ):
            raise ValueError("operator_codes must end in (hidden_dim, hidden_dim)")
        if not operator_codes.is_floating_point():
            raise TypeError("operator_codes must have a floating dtype")
        if operator_codes.numel() == 0:
            raise ValueError("operator_codes must not be empty")
        if tolerance is None:
            tolerance = 5e-5 if operator_codes.dtype in (torch.float16, torch.float32) else 5e-11
        tolerance = float(tolerance)
        if not math.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError("tolerance must be finite and positive")

        # Audit in the executed dtype: promoting after execution would conceal
        # native rounding at the very boundary being certified.
        gauge = self.gauge_matrix().to(dtype=operator_codes.dtype)
        semantic_frame = gauge[:, : self.semantic_dim]
        common_frame = gauge[
            :, self.semantic_dim : self.semantic_dim + COMMON_LOGIT_DIM
        ]
        ambient_frame = gauge[:, self.semantic_dim + COMMON_LOGIT_DIM :]
        projector = semantic_frame @ semantic_frame.transpose(-1, -2)
        common_projector = common_frame @ common_frame.transpose(-1, -2)
        ambient_projector = ambient_frame @ ambient_frame.transpose(-1, -2)
        centered_kernel = common_projector + ambient_projector
        identity = torch.eye(
            self.hidden_dim,
            dtype=operator_codes.dtype,
            device=operator_codes.device,
        )
        pmq = projector @ operator_codes @ centered_kernel
        qmp = centered_kernel @ operator_codes @ projector
        null_cross_forward = common_projector @ operator_codes @ ambient_projector
        null_cross_reverse = ambient_projector @ operator_codes @ common_projector
        gram = operator_codes.transpose(-1, -2) @ operator_codes - identity
        frame_gram = gauge.transpose(-1, -2) @ gauge - identity
        partition = projector + common_projector + ambient_projector - identity
        anchors = self.effective_state_embedding().to(dtype=operator_codes.dtype)
        decoder = self.effective_decoder_weight().to(dtype=operator_codes.dtype)
        centered_decoder = self.centered_effective_decoder_weight().to(
            dtype=operator_codes.dtype
        )
        # Anchors intentionally occupy L with the same coefficient.  Only K
        # is forbidden; treating the entire centered-logit null as an anchor
        # leak would make the eight-anchor Gram objective rank-infeasible.
        embedding_kernel = (
            ambient_projector @ anchors.transpose(-1, -2)
        ).transpose(-1, -2)
        expected_common = self._anchor_common_scale.to(
            dtype=operator_codes.dtype
        ).expand(N_STATES, COMMON_LOGIT_DIM)
        embedding_common = anchors @ common_frame - expected_common
        embedding_norm = torch.linalg.vector_norm(anchors, dim=-1) - 1.0
        decoder_kernel = centered_decoder @ centered_kernel
        common_logit = centered_decoder @ common_projector

        tensors = (
            frame_gram,
            partition,
            gram,
            pmq,
            qmp,
            null_cross_forward,
            null_cross_reverse,
            embedding_kernel,
            embedding_common,
            embedding_norm,
            decoder_kernel,
            common_logit,
        )
        all_finite = all(bool(torch.isfinite(value).all()) for value in tensors)

        def scalar(value: torch.Tensor) -> float:
            return float(self._maximum_frobenius(value).detach().cpu())

        return InvariantKernelAudit(
            tolerance=tolerance,
            frame_orthogonality_residual=scalar(frame_gram),
            projector_partition_residual=scalar(partition),
            operator_orthogonality_residual=scalar(gram),
            pmq_residual=scalar(pmq),
            qmp_residual=scalar(qmp),
            null_cross_residual=max(
                scalar(null_cross_forward), scalar(null_cross_reverse)
            ),
            embedding_kernel_residual=float(
                torch.linalg.vector_norm(embedding_kernel, dim=-1).max().detach().cpu()
            ),
            embedding_common_residual=float(
                torch.linalg.vector_norm(embedding_common, dim=-1).max().detach().cpu()
            ),
            embedding_norm_residual=float(embedding_norm.abs().max().detach().cpu()),
            decoder_kernel_residual=scalar(decoder_kernel),
            common_logit_residual=scalar(common_logit),
            all_finite=all_finite,
        )


class ExactInvariantKernelOperatorRNN(LearnedFrameBlockIsometricOperatorRNN):
    """Exact observable-and-ambient representation control.

    This positive control compiles each visible permutation table into its
    seven-dimensional standard representation, fixes the common-logit line,
    and uses identity on the ambient fiber.  It is not a learned-model claim;
    it verifies that the frame construction can realize exact behavior and
    full flatness simultaneously.
    """

    model_name = "exact_invariant_kernel_control"

    def __init__(self, *, gauge_seed: int = 607) -> None:
        super().__init__(gauge_seed=gauge_seed)
        # Explicit Helmert contrasts give a deterministic orthonormal basis for
        # the seven-dimensional standard representation of S_8.  This avoids
        # any posthoc SVD cutoff or platform-dependent QR sign convention.
        basis = torch.zeros(N_STATES, OBSERVABLE_DIM, dtype=torch.float64)
        for column in range(OBSERVABLE_DIM):
            count = column + 1
            scale = math.sqrt(float(count * (count + 1)))
            basis[:count, column] = 1.0 / scale
            basis[count, column] = -float(count) / scale
        self.register_buffer(
            "_standard_basis",
            basis,
            persistent=False,
        )
        with torch.no_grad():
            self.semantic_state_embedding.weight.copy_(
                self._standard_basis.to(self.semantic_state_embedding.weight.dtype)
            )
            self.semantic_decoder.weight.copy_(
                self._standard_basis.to(self.semantic_decoder.weight.dtype)
            )
        for parameter in self.parameters():
            parameter.requires_grad_(False)

    def semantic_operator_blocks(self, tables: torch.Tensor) -> torch.Tensor:
        self._validate_tables(tables)
        basis = self._standard_basis.to(dtype=tables.dtype)
        action = tables.transpose(-1, -2)
        return torch.einsum("ia,...ij,jb->...ab", basis, action, basis)

    def ambient_operator_blocks(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = self._validate_tables(tables)
        return self._ambient_identity.to(dtype=tables.dtype).expand(
            batch, operators, self.ambient_dim, self.ambient_dim
        )


class QuotientCurvedInvariantKernelOperatorRNN(ExactInvariantKernelOperatorRNN):
    """Exact observable quotient with deliberately curved kernel dynamics.

    The semantic block remains the exact visible permutation action, so every
    answer and every semantic path identity is exact.  A deterministic,
    table-conditioned rotation acts only inside the four-dimensional kernel.
    Generic null words therefore retain full-space ambient holonomy while being
    rigorously invisible to the decoder.  This is a separation control for
    quotient flatness versus full ambient flatness.
    """

    model_name = "quotient_curved_invariant_kernel_control"

    def ambient_operator_blocks(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = self._validate_tables(tables)
        flattened = tables.reshape(batch, operators, N_STATES * N_STATES)
        weights = torch.linspace(
            -1.0,
            1.0,
            N_STATES * N_STATES,
            dtype=tables.dtype,
            device=tables.device,
        )
        phase = (flattened * weights).sum(dim=-1) / float(N_STATES)
        angle = 0.19 + 0.04 * torch.tanh(phase)
        cosine = torch.cos(angle)
        sine = torch.sin(angle)
        result = tables.new_zeros((batch, operators, self.ambient_dim, self.ambient_dim))
        # One table-conditioned Givens rotation plus a fixed untouched plane.
        # f^2 and r^4 are generically nonidentity in this kernel, by design.
        result[..., 0, 0] = cosine
        result[..., 0, 1] = -sine
        result[..., 1, 0] = sine
        result[..., 1, 1] = cosine
        result[..., 2, 2] = 1.0
        result[..., 3, 3] = 1.0
        return result


__all__ = [
    "AMBIENT_DIM",
    "CENTERED_NULL_DIM",
    "COMMON_LOGIT_DIM",
    "HIDDEN_DIM",
    "OBSERVABLE_DIM",
    "SEMANTIC_DIM",
    "ExactInvariantKernelOperatorRNN",
    "InvariantKernelAudit",
    "InvariantKernelOperatorBundle",
    "LearnedFrameBlockIsometricOperatorRNN",
    "QuotientCurvedInvariantKernelOperatorRNN",
]
