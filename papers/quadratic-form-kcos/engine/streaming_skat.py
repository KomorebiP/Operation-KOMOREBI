from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


def orthonormalize_covariates(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    Q, _ = np.linalg.qr(X, mode="reduced")
    return Q


def project_out(Q: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Apply M_X = I - Q Q^T without forming M_X."""
    Q = np.asarray(Q, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    return Y - Q @ (Q.T @ Y)


def full_factor(G: np.ndarray, w: np.ndarray, Q: np.ndarray) -> np.ndarray:
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    H = G * np.sqrt(w)[None, :]
    return project_out(Q, H)


def stream_sample_gram(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    *,
    variant_block: int,
) -> np.ndarray:
    """Exact K = A A^T by additive variant-block accumulation."""
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    n, m = G.shape
    K = np.zeros((n, n), dtype=np.float64)
    for j0 in range(0, m, variant_block):
        j1 = min(m, j0 + variant_block)
        H = G[:, j0:j1] * np.sqrt(w[j0:j1])[None, :]
        A = project_out(Q, H)
        K += A @ A.T
    return 0.5 * (K + K.T)


def stream_kernel_action(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    V: np.ndarray,
    *,
    variant_block: int,
) -> np.ndarray:
    """Exact K V without forming A or K.

    K = M_X G W G^T M_X.
    """
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    V = np.asarray(V, dtype=np.float64)
    n, m = G.shape
    U = project_out(Q, V)
    Y = np.zeros_like(U)
    for j0 in range(0, m, variant_block):
        j1 = min(m, j0 + variant_block)
        Gb = G[:, j0:j1]
        T = Gb.T @ U
        Y += Gb @ (w[j0:j1, None] * T)
    return project_out(Q, Y)


def stream_A_times_V(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    V: np.ndarray,
    *,
    variant_block: int,
) -> np.ndarray:
    """Exact A V with A=M_X G W^(1/2), V partitioned by variants."""
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    V = np.asarray(V, dtype=np.float64)
    n, m = G.shape
    if V.shape[0] != m:
        raise ValueError("V must have m rows")
    Y = np.zeros((n, V.shape[1]), dtype=np.float64)
    for j0 in range(0, m, variant_block):
        j1 = min(m, j0 + variant_block)
        Y += G[:, j0:j1] @ (
            np.sqrt(w[j0:j1])[:, None] * V[j0:j1, :]
        )
    return project_out(Q, Y)


def stream_AT_times_U(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    U: np.ndarray,
    *,
    variant_block: int,
) -> np.ndarray:
    """Exact A^T U, producing right-coordinate blocks sequentially."""
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    U0 = project_out(Q, np.asarray(U, dtype=np.float64))
    n, m = G.shape
    Z = np.empty((m, U0.shape[1]), dtype=np.float64)
    for j0 in range(0, m, variant_block):
        j1 = min(m, j0 + variant_block)
        Z[j0:j1, :] = (
            np.sqrt(w[j0:j1])[:, None]
            * (G[:, j0:j1].T @ U0)
        )
    return Z


def stream_dual_action(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    V: np.ndarray,
    *,
    variant_block: int,
) -> np.ndarray:
    """Exact (A^T A)V using two streamed passes."""
    Y = stream_A_times_V(G, w, Q, V, variant_block=variant_block)
    return stream_AT_times_U(G, w, Q, Y, variant_block=variant_block)


def tiled_sample_gram(
    G: np.ndarray,
    w: np.ndarray,
    Q: np.ndarray,
    *,
    variant_block: int,
    sample_tile: int,
) -> np.ndarray:
    """Exact 2D streamed Gram construction.

    Reference implementation using an in-memory G as backing storage.
    The algorithm itself only needs two sample tiles of a variant block
    plus the p x c residualization core at a time.
    """
    G = np.asarray(G, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    Q = np.asarray(Q, dtype=np.float64)
    n, m = G.shape
    K = np.zeros((n, n), dtype=np.float64)

    for j0 in range(0, m, variant_block):
        j1 = min(m, j0 + variant_block)
        sw = np.sqrt(w[j0:j1])

        # First sample pass: R_b = Q^T H_b, without retaining H_b.
        R = np.zeros((Q.shape[1], j1-j0), dtype=np.float64)
        for i0 in range(0, n, sample_tile):
            i1 = min(n, i0 + sample_tile)
            H_i = G[i0:i1, j0:j1] * sw[None, :]
            R += Q[i0:i1, :].T @ H_i

        # Second pass: form pairs of residualized sample tiles.
        for i0 in range(0, n, sample_tile):
            i1 = min(n, i0 + sample_tile)
            H_i = G[i0:i1, j0:j1] * sw[None, :]
            A_i = H_i - Q[i0:i1, :] @ R
            for k0 in range(i0, n, sample_tile):
                k1 = min(n, k0 + sample_tile)
                H_k = G[k0:k1, j0:j1] * sw[None, :]
                A_k = H_k - Q[k0:k1, :] @ R
                tile = A_i @ A_k.T
                K[i0:i1, k0:k1] += tile
                if k0 != i0:
                    K[k0:k1, i0:i1] += tile.T
    return K


@dataclass(frozen=True)
class MemoryEstimate:
    n: int
    m: int
    p: int
    krylov_width: int
    variant_block: int
    sample_tile: int
    scalar_bytes: int
    full_factor_bytes: int
    full_kernel_bytes: int
    streamed_kernel_action_bytes: int
    streamed_factor_action_bytes: int
    tiled_gram_bytes: int


def estimate_working_set(
    n: int,
    m: int,
    p: int,
    krylov_width: int,
    variant_block: int,
    sample_tile: int,
    *,
    scalar_bytes: int = 8,
    genotype_scalar_bytes: int | None = None,
) -> MemoryEstimate:
    """Conservative algebraic working-set estimate.

    Excludes BLAS/cuBLAS workspace, allocator overhead, and the backing
    genotype store.  It is therefore a planning lower-level model, not
    an exact device allocator forecast.
    """
    d = int(scalar_bytes)
    dg = d if genotype_scalar_bytes is None else int(genotype_scalar_bytes)
    n, m, p = map(int, (n,m,p))
    s = int(krylov_width)
    c = int(variant_block)
    t = int(sample_tile)

    full_A = d*n*m
    full_K = d*n*n

    # G_b + U + Y + T + Q + small p x s scratch
    stream_K = dg*n*c + d*(2*n*s + c*s + n*p + p*s + c)

    # A V / A^T U action: G_b + sample accumulator + block right vectors
    stream_A = dg*n*c + d*(n*s + c*s + n*p + p*s + c)

    # Two sample tiles of G_b, two residualized tiles, R_b, output tile, Q tiles.
    tiled = (
        dg*(2*t*c)
        + d*(2*t*c + p*c + t*t + 2*t*p + c)
    )

    return MemoryEstimate(
        n=n, m=m, p=p, krylov_width=s, variant_block=c,
        sample_tile=t, scalar_bytes=d,
        full_factor_bytes=full_A,
        full_kernel_bytes=full_K,
        streamed_kernel_action_bytes=stream_K,
        streamed_factor_action_bytes=stream_A,
        tiled_gram_bytes=tiled,
    )


def human_bytes(x: int) -> str:
    x=float(x)
    units=["B","KiB","MiB","GiB","TiB"]
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:.2f} {u}"
        x /= 1024
