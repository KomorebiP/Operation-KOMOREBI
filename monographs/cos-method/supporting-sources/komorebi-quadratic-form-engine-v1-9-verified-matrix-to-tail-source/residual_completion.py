from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from residual_trace_cap import orthonormalize, residual_spectrum_certificate


@dataclass(frozen=True)
class ResidualRankBounds:
    stable_rank_lower: float
    second_moment_rank_lower: float
    integer_lower_bound: int
    orthogonal_complement_upper_bound: int
    rank_certified: bool
    certified_rank: int | None


@dataclass(frozen=True)
class ResidualCompletion:
    original_basis_dim: int
    residual_rank: int
    completed_basis_dim: int
    residual_basis: np.ndarray
    completed_core: np.ndarray
    completed_singular_values: np.ndarray
    residual_frobenius_norm: float


def residual_rank_bounds(A, U, *, tolerance=1e-12):
    A = np.asarray(A, dtype=np.float64)
    U = orthonormalize(U)
    cert = residual_spectrum_certificate(A, U, compute_square_trace=True)

    t = float(cert.residual_trace)
    rho = float(cert.residual_cap)
    v = float(cert.residual_square_trace)

    if t <= tolerance:
        stable = 0.0
        second = 0.0
        lower = 0
    else:
        stable = t / rho if rho > 0 else math.inf
        second = (t * t) / v if v > 0 else math.inf
        # Both quantities are lower bounds on rank.  Round upward with a small
        # numerical tolerance so values like 1.999999999999998 certify rank 2.
        raw = max(stable, second)
        lower = int(math.ceil(raw - 1e-10))

    upper = max(0, A.shape[0] - U.shape[1])
    certified = lower == upper
    return ResidualRankBounds(
        stable_rank_lower=float(stable),
        second_moment_rank_lower=float(second),
        integer_lower_bound=lower,
        orthogonal_complement_upper_bound=upper,
        rank_certified=bool(certified),
        certified_rank=(upper if certified else None),
    )


def complete_residual_range(A, U, *, rank_tolerance=1e-11):
    """Exact residual completion in floating arithmetic up to QR tolerance.

    A = U B + F with U^T F=0.  Compact QR F=W D gives
        A = [U W] [B; D].
    Hence singular values of A equal singular values of the stacked core.
    """
    A = np.asarray(A, dtype=np.float64)
    U = orthonormalize(U)
    B = U.T @ A
    F = A - U @ B

    if F.size == 0 or np.linalg.norm(F) == 0:
        W = np.zeros((A.shape[0], 0), dtype=np.float64)
        D = np.zeros((0, A.shape[1]), dtype=np.float64)
    else:
        # SVD is used in the reference implementation to make numerical rank
        # explicit.  A production streamed implementation can replace this with
        # rank-revealing QR / TSQR without changing the theorem.
        Uf, sf, Vhf = np.linalg.svd(F, full_matrices=False)
        scale = max(float(sf[0]) if sf.size else 0.0, 1.0)
        keep = sf > rank_tolerance * scale
        W = Uf[:, keep]
        D = (sf[keep, None] * Vhf[keep, :])

    core = np.vstack([B, D])
    sv = np.linalg.svd(core, compute_uv=False)
    return ResidualCompletion(
        original_basis_dim=int(U.shape[1]),
        residual_rank=int(W.shape[1]),
        completed_basis_dim=int(U.shape[1] + W.shape[1]),
        residual_basis=W,
        completed_core=core,
        completed_singular_values=sv,
        residual_frobenius_norm=float(np.linalg.norm(F, ord='fro')),
    )


def stream_complete_residual_range(A, U, *, block_size=256, rank_tolerance=1e-11):
    """Column-streamed exact residual completion reference implementation.

    The factor A is consumed by column blocks.  U is kept resident.  The
    residual basis W grows only when a block contributes a new orthogonal
    direction.  Previously stored residual-core blocks receive zero rows when
    W grows, because future residual directions are orthogonal to all earlier
    residual blocks by construction.
    """
    A = np.asarray(A, dtype=np.float64)
    U = orthonormalize(U)
    n, m = A.shape
    block_size = max(1, int(block_size))

    W = np.zeros((n, 0), dtype=np.float64)
    B_blocks = []
    D_blocks = []

    for j0 in range(0, m, block_size):
        j1 = min(m, j0 + block_size)
        Ab = A[:, j0:j1]
        Bb = U.T @ Ab
        Fb = Ab - U @ Bb

        if W.shape[1]:
            C = W.T @ Fb
            Rb = Fb - W @ C
            # second projection pass for numerical stability
            corr = W.T @ Rb
            C = C + corr
            Rb = Rb - W @ corr
        else:
            C = np.zeros((0, Ab.shape[1]), dtype=np.float64)
            Rb = Fb

        if Rb.size and np.linalg.norm(Rb, ord='fro') > 0:
            Ur, sr, Vhr = np.linalg.svd(Rb, full_matrices=False)
            scale = max(float(sr[0]) if sr.size else 0.0, 1.0)
            keep = sr > rank_tolerance * scale
            Qnew = Ur[:, keep]
            Rnew = sr[keep, None] * Vhr[keep, :]
        else:
            Qnew = np.zeros((n, 0), dtype=np.float64)
            Rnew = np.zeros((0, Ab.shape[1]), dtype=np.float64)

        qnew = Qnew.shape[1]
        if qnew:
            # Future basis directions are orthogonal to every previous residual
            # block, so prior coordinate blocks extend by exact zeros.
            D_blocks = [
                np.vstack([Dold, np.zeros((qnew, Dold.shape[1]))])
                for Dold in D_blocks
            ]
            W = np.column_stack([W, Qnew])

        Db = np.vstack([C, Rnew])
        B_blocks.append(Bb)
        D_blocks.append(Db)

    B = np.hstack(B_blocks) if B_blocks else np.zeros((U.shape[1], 0))
    D = np.hstack(D_blocks) if D_blocks else np.zeros((W.shape[1], 0))
    core = np.vstack([B, D])
    sv = np.linalg.svd(core, compute_uv=False)

    return ResidualCompletion(
        original_basis_dim=int(U.shape[1]),
        residual_rank=int(W.shape[1]),
        completed_basis_dim=int(U.shape[1] + W.shape[1]),
        residual_basis=W,
        completed_core=core,
        completed_singular_values=sv,
        residual_frobenius_norm=float(np.linalg.norm(A - U @ (U.T @ A), ord='fro')),
    )
