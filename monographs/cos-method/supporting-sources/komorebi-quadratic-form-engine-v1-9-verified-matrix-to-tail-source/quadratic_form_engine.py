from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Sequence
import math

import numpy as np
from scipy.optimize import brentq

from kcos_v2_hardened import adaptive_kcos_logsf, spectral_metrics
from generalized_tail import noncentral_positive_logsf
from generalized_packets import packetized_signed_central_logsf

Array = np.ndarray


@dataclass(frozen=True)
class TailResult:
    log_p: float
    log10_p: float
    p_value: float
    certified_relative_bound: float
    certificate_passed: bool
    rank: int
    source: str


@dataclass(frozen=True)
class SpectrumSummary:
    rank: int
    trace: float
    variance: float
    effective_rank: float
    lambda_max: float
    source: str


@dataclass(frozen=True)
class NoncentralSpectrumSummary:
    rank: int
    weights: np.ndarray
    noncentrality: np.ndarray
    deterministic_shift: float
    mean: float
    variance: float
    source: str


@dataclass(frozen=True)
class SignedSpectrumSummary:
    rank: int
    positive_count: int
    negative_count: int
    mean: float
    variance: float
    lower_support: float
    upper_support: float
    lambda_max: float
    lambda_min: float
    source: str


class BlockFactorSource:
    """Replayable source of column blocks of a factor A.

    The mathematical object is A=[A_1 ... A_B].  The source only determines
    how those blocks are stored/retrieved.  Each call to ``blocks()`` must
    yield the same factor blocks in the same column order.
    """

    def __init__(
        self,
        n_rows: int,
        n_cols: int,
        block_factory: Callable[[], Iterable[Array]],
        *,
        name: str = "block-factor",
    ):
        self.n_rows = int(n_rows)
        self.n_cols = int(n_cols)
        self._factory = block_factory
        self.name = str(name)

    @classmethod
    def from_array(cls, A: Array, block_size: int, *, name: str = "array-factor"):
        A = np.asarray(A, dtype=np.float64)
        n, m = A.shape
        block_size = int(block_size)
        if block_size < 1:
            raise ValueError("block_size must be positive")

        def factory():
            for j in range(0, m, block_size):
                yield A[:, j:j+block_size]

        return cls(n, m, factory, name=name)

    def blocks(self) -> Iterator[Array]:
        seen = 0
        for block in self._factory():
            B = np.asarray(block, dtype=np.float64)
            if B.ndim != 2 or B.shape[0] != self.n_rows:
                raise ValueError("factor block has incompatible shape")
            seen += B.shape[1]
            yield B
        if seen != self.n_cols:
            raise ValueError(f"factor source yielded {seen} columns, expected {self.n_cols}")

    def sample_gram(self) -> Array:
        K = np.zeros((self.n_rows, self.n_rows), dtype=np.float64)
        for B in self.blocks():
            K += B @ B.T
        return 0.5 * (K + K.T)

    def sample_gram_action(self, V: Array) -> Array:
        V = np.asarray(V, dtype=np.float64)
        if V.ndim == 1:
            V = V[:, None]
        if V.shape[0] != self.n_rows:
            raise ValueError("V has incompatible leading dimension")
        Y = np.zeros_like(V)
        for B in self.blocks():
            Y += B @ (B.T @ V)
        return Y


class PositiveQuadraticFormEngine:
    """Certified positive Gaussian quadratic-form tail engine.

    Represents
        Q = sum_j lambda_j Z_j^2,   lambda_j >= 0,
    where Z_j are independent N(0,1).

    The eigenvalues may come directly from a spectrum, a PSD matrix, a dense
    factor, or a streamed block factor.  Domain-specific applications such as
    SKAT are adapters that construct one of these representations.
    """

    def __init__(self, eigenvalues: Sequence[float], *, source: str = "spectrum"):
        lam = np.asarray(tuple(eigenvalues), dtype=np.float64)
        if lam.ndim != 1 or lam.size == 0:
            raise ValueError("eigenvalues must be a nonempty vector")
        if np.any(lam < -1e-12 * max(1.0, float(np.max(np.abs(lam))))):
            raise ValueError("positive engine requires a PSD spectrum")
        lam = np.maximum(lam, 0.0)
        lam = np.sort(lam)[::-1]
        if lam[0] <= 0.0:
            raise ValueError("at least one eigenvalue must be positive")
        lam = lam[lam > lam[0] * 1e-14]
        self.eigenvalues = lam
        self.source = source

    @classmethod
    def from_spectrum(cls, eigenvalues, *, source="spectrum"):
        return cls(eigenvalues, source=source)

    @classmethod
    def from_psd_matrix(cls, H: Array, *, scale: float = 1.0, source="PSD matrix"):
        H = np.asarray(H, dtype=np.float64)
        if H.ndim != 2 or H.shape[0] != H.shape[1]:
            raise ValueError("H must be square")
        Hs = 0.5 * (H + H.T)
        lam = float(scale) * np.linalg.eigvalsh(Hs)
        return cls(lam, source=source)

    @classmethod
    def from_gaussian_quadratic(
        cls,
        covariance: Array,
        quadratic_matrix: Array,
        *,
        scale: float = 1.0,
        source: str = "Gaussian quadratic form",
    ):
        """Construct from X~N(0,Sigma) and Q=scale*X^T M X, M PSD.

        The spectrum is that of Sigma^(1/2) M Sigma^(1/2).
        """
        Sigma = np.asarray(covariance, dtype=np.float64)
        M = np.asarray(quadratic_matrix, dtype=np.float64)
        if Sigma.ndim != 2 or Sigma.shape[0] != Sigma.shape[1]:
            raise ValueError("covariance must be square")
        if M.shape != Sigma.shape:
            raise ValueError("quadratic_matrix must match covariance shape")
        Sigma = 0.5 * (Sigma + Sigma.T)
        M = 0.5 * (M + M.T)
        se, sv = np.linalg.eigh(Sigma)
        me = np.linalg.eigvalsh(M)
        tol = 1e-12 * max(1.0, float(np.max(np.abs(se))), float(np.max(np.abs(me))))
        if np.min(se) < -tol:
            raise ValueError("covariance must be PSD")
        if np.min(me) < -tol:
            raise ValueError("quadratic_matrix must be PSD for the positive engine")
        se = np.maximum(se, 0.0)
        S = (sv * np.sqrt(se)[None, :]) @ sv.T
        H = S @ M @ S
        lam = float(scale) * np.linalg.eigvalsh(0.5 * (H + H.T))
        return cls(lam, source=source)

    @classmethod
    def from_factor(cls, A: Array, *, scale: float = 1.0, source="factor"):
        A = np.asarray(A, dtype=np.float64)
        if A.ndim != 2:
            raise ValueError("A must be a matrix")
        # Work in the smaller Gram space.
        if A.shape[0] <= A.shape[1]:
            gram = A @ A.T
        else:
            gram = A.T @ A
        lam = float(scale) * np.linalg.eigvalsh(0.5 * (gram + gram.T))
        return cls(lam, source=source)

    @classmethod
    def from_block_factor(
        cls,
        source: BlockFactorSource,
        *,
        scale: float = 1.0,
        label: str | None = None,
    ):
        K = source.sample_gram()
        lam = float(scale) * np.linalg.eigvalsh(K)
        return cls(lam, source=label or source.name)

    @property
    def mean(self) -> float:
        return float(np.sum(self.eigenvalues))

    @property
    def variance(self) -> float:
        return float(2.0 * np.sum(self.eigenvalues**2))

    def summary(self) -> SpectrumSummary:
        m = spectral_metrics(self.eigenvalues)
        return SpectrumSummary(
            rank=m["rank"],
            trace=m["trace"],
            variance=self.variance,
            effective_rank=m["effective_rank"],
            lambda_max=float(self.eigenvalues[0]),
            source=self.source,
        )

    def logsf(self, q: float, *, relative_tolerance: float = 1e-8, **kwargs) -> TailResult:
        r = adaptive_kcos_logsf(
            float(q),
            self.eigenvalues,
            relative_tolerance=relative_tolerance,
            **kwargs,
        )
        return TailResult(
            log_p=float(r.log_p),
            log10_p=float(r.log10_p),
            p_value=float(r.p_value),
            certified_relative_bound=float(r.certificate.certified_relative_bound),
            certificate_passed=bool(r.certificate.passed),
            rank=int(r.certificate.rank),
            source=self.source,
        )

    def threshold(self, tail_probability: float, *, relative_tolerance: float = 1e-8) -> float:
        p = float(tail_probability)
        if not (0.0 < p < 0.5):
            raise ValueError("tail_probability must lie in (0, 0.5)")
        target = math.log(p)
        sd = math.sqrt(self.variance)
        lo = self.mean * (1.0 + 1e-12)
        hi = self.mean + 4.0 * sd

        def f(q):
            return self.logsf(q, relative_tolerance=relative_tolerance).log_p - target

        while f(hi) > 0.0:
            hi += 4.0 * sd
        return float(brentq(f, lo, hi, xtol=1e-10, rtol=1e-10))


class NoncentralPositiveQuadraticFormEngine:
    """Positive Gaussian quadratic form with nonzero mean.

    Represents
        Q = shift + sum_j weight_j * chi2_1(nc_j),
    with positive weights and nonnegative noncentralities.
    """

    def __init__(self, weights, noncentrality, *, shift=0.0, source="noncentral spectrum"):
        w = np.asarray(tuple(weights), dtype=np.float64)
        d = np.asarray(tuple(noncentrality), dtype=np.float64)
        if w.ndim != 1 or d.ndim != 1 or w.size == 0 or w.size != d.size:
            raise ValueError("weights and noncentrality must be equal nonempty vectors")
        if np.any(w <= 0.0) or np.any(d < 0.0):
            raise ValueError("weights must be positive and noncentralities nonnegative")
        order = np.argsort(w)[::-1]
        self.weights = w[order]
        self.noncentrality = d[order]
        self.shift = float(shift)
        self.source = str(source)

    @classmethod
    def from_gaussian_quadratic(
        cls, mean: Array, covariance: Array, quadratic_matrix: Array, *,
        scale: float = 1.0,
        source: str = "noncentral Gaussian quadratic form",
        tolerance: float = 1e-12,
    ):
        """Reduce X~N(mu,Sigma), Q=scale*X^T M X, M PSD."""
        mu = np.asarray(mean, dtype=np.float64)
        Sigma = np.asarray(covariance, dtype=np.float64)
        M = np.asarray(quadratic_matrix, dtype=np.float64)
        if mu.ndim != 1:
            raise ValueError("mean must be a vector")
        n = mu.size
        if Sigma.shape != (n, n) or M.shape != (n, n):
            raise ValueError("dimensions must match")

        Sigma = 0.5*(Sigma + Sigma.T)
        M = 0.5*(M + M.T)
        se, sv = np.linalg.eigh(Sigma)
        me = np.linalg.eigvalsh(M)
        tol = float(tolerance) * max(
            1.0,
            float(np.max(np.abs(se))),
            float(np.max(np.abs(me))),
        )
        if np.min(se) < -tol:
            raise ValueError("covariance must be PSD")
        if np.min(me) < -tol:
            raise ValueError("quadratic_matrix must be PSD")
        if scale <= 0:
            raise ValueError("scale must be positive")

        se = np.maximum(se, 0.0)
        S = (sv * np.sqrt(se)[None, :]) @ sv.T
        H = S @ M @ S
        H = 0.5*(H + H.T)

        lam, V = np.linalg.eigh(H)
        lam = np.maximum(lam, 0.0)
        lam_max = float(lam.max()) if lam.size else 0.0
        keep = lam > max(tol, float(tolerance)*max(1.0, lam_max))

        deterministic_total = float(mu @ M @ mu)
        if not np.any(keep):
            raise ValueError(
                f"quadratic form is deterministic under supplied covariance; "
                f"value={float(scale)*deterministic_total:.17g}"
            )

        lam_pos = lam[keep]
        V_pos = V[:, keep]
        c = V_pos.T @ (S @ (M @ mu))
        nc = (c / lam_pos)**2

        represented_constant = float(np.sum((c*c)/lam_pos))
        shift = deterministic_total - represented_constant
        if shift < -100*tol:
            raise RuntimeError("negative deterministic shift beyond rounding tolerance")
        shift = max(shift, 0.0)

        return cls(
            float(scale)*lam_pos,
            nc,
            shift=float(scale)*shift,
            source=source,
        )

    @property
    def mean(self) -> float:
        return float(self.shift + np.sum(self.weights*(1.0+self.noncentrality)))

    @property
    def variance(self) -> float:
        return float(2.0*np.sum(self.weights**2*(1.0+2.0*self.noncentrality)))

    def summary(self) -> NoncentralSpectrumSummary:
        return NoncentralSpectrumSummary(
            rank=int(self.weights.size),
            weights=self.weights.copy(),
            noncentrality=self.noncentrality.copy(),
            deterministic_shift=float(self.shift),
            mean=self.mean,
            variance=self.variance,
            source=self.source,
        )

    def logsf(self, q: float, *, relative_tolerance: float = 1e-8, **kwargs) -> TailResult:
        adjusted = float(q) - self.shift
        if adjusted <= 0:
            return TailResult(0.0, 0.0, 1.0, 0.0, True, int(self.weights.size), self.source)
        r = noncentral_positive_logsf(
            adjusted, self.weights,
            df=np.ones_like(self.weights),
            nc=self.noncentrality,
            relative_tolerance=relative_tolerance,
            **kwargs,
        )
        return TailResult(
            float(r.log_p), float(r.log10_p), float(r.p_value),
            float(r.certified_relative_bound), bool(r.passed),
            int(self.weights.size), self.source,
        )




class SignedCentralQuadraticFormEngine:
    """Central Gaussian quadratic forms with signed eigenvalues.

    Represents
        Q = sum_j lambda_j Z_j^2,
    where lambda_j may be positive or negative.

    The production path is an upper-tail solver for q above the mean.  Pure
    positive spectra are routed to the positive engine.  Pure negative spectra
    have a finite upper endpoint at zero and are evaluated by the signed
    packetized solver whenever q<0; q>=0 has exact probability zero.
    """

    def __init__(self, eigenvalues, *, source="signed spectrum"):
        w=np.asarray(tuple(eigenvalues),dtype=np.float64)
        if w.ndim!=1 or w.size==0:
            raise ValueError("eigenvalues must be a nonempty vector")
        scale=max(1.0,float(np.max(np.abs(w))))
        w=w[np.abs(w)>1e-14*scale]
        if w.size==0:
            raise ValueError("at least one nonzero eigenvalue is required")
        self.eigenvalues=np.asarray(w,dtype=np.float64)
        self.source=str(source)

    @classmethod
    def from_spectrum(cls,eigenvalues,*,source="signed spectrum"):
        return cls(eigenvalues,source=source)

    @classmethod
    def from_symmetric_operator(cls,H: Array,*,scale: float=1.0,source="symmetric operator"):
        H=np.asarray(H,dtype=np.float64)
        if H.ndim!=2 or H.shape[0]!=H.shape[1]:
            raise ValueError("H must be square")
        H=0.5*(H+H.T)
        lam=float(scale)*np.linalg.eigvalsh(H)
        return cls(lam,source=source)

    @classmethod
    def from_gaussian_quadratic(
        cls,
        covariance: Array,
        quadratic_matrix: Array,
        *,
        scale: float=1.0,
        source: str="central Gaussian indefinite quadratic form",
        tolerance: float=1e-12,
    ):
        """Construct X^T M X for X~N(0,Sigma), M symmetric indefinite."""
        Sigma=np.asarray(covariance,dtype=np.float64)
        M=np.asarray(quadratic_matrix,dtype=np.float64)
        if Sigma.ndim!=2 or Sigma.shape[0]!=Sigma.shape[1] or M.shape!=Sigma.shape:
            raise ValueError("covariance and quadratic_matrix must be matching square matrices")
        Sigma=0.5*(Sigma+Sigma.T)
        M=0.5*(M+M.T)
        se,sv=np.linalg.eigh(Sigma)
        tol=float(tolerance)*max(1.0,float(np.max(np.abs(se))))
        if np.min(se)<-tol:
            raise ValueError("covariance must be PSD")
        se=np.maximum(se,0.0)
        S=(sv*np.sqrt(se)[None,:])@sv.T
        H=S@M@S
        lam=float(scale)*np.linalg.eigvalsh(0.5*(H+H.T))
        return cls(lam,source=source)

    @property
    def mean(self)->float:
        return float(np.sum(self.eigenvalues))

    @property
    def variance(self)->float:
        return float(2.0*np.sum(self.eigenvalues**2))

    @property
    def lower_support(self)->float:
        return 0.0 if np.all(self.eigenvalues>=0.0) else -math.inf

    @property
    def upper_support(self)->float:
        return 0.0 if np.all(self.eigenvalues<=0.0) else math.inf

    def summary(self)->SignedSpectrumSummary:
        w=self.eigenvalues
        return SignedSpectrumSummary(
            rank=int(w.size),
            positive_count=int(np.sum(w>0)),
            negative_count=int(np.sum(w<0)),
            mean=self.mean,
            variance=self.variance,
            lower_support=self.lower_support,
            upper_support=self.upper_support,
            lambda_max=float(np.max(w)),
            lambda_min=float(np.min(w)),
            source=self.source,
        )

    def logsf(self,q: float,*,relative_tolerance: float=1e-8,**kwargs)->TailResult:
        q=float(q)
        w=self.eigenvalues
        if np.all(w>0):
            return PositiveQuadraticFormEngine(w,source=self.source).logsf(
                q,relative_tolerance=relative_tolerance,**kwargs
            )
        if np.all(w<0) and q>=0.0:
            return TailResult(
                log_p=-math.inf,log10_p=-math.inf,p_value=0.0,
                certified_relative_bound=0.0,certificate_passed=True,
                rank=int(w.size),source=self.source,
            )
        if q<=self.mean:
            raise ValueError("signed production path currently handles upper tails q>mean")
        r=packetized_signed_central_logsf(
            q,w,relative_tolerance=relative_tolerance,**kwargs
        )
        return TailResult(
            log_p=float(r.log_p),
            log10_p=float(r.log10_p),
            p_value=float(r.p_value),
            certified_relative_bound=float(r.certified_relative_bound),
            certificate_passed=bool(r.passed),
            rank=int(r.original_rank),
            source=self.source,
        )

    def threshold(self,tail_probability: float,*,relative_tolerance: float=1e-8,**kwargs)->float:
        p=float(tail_probability)
        if not (0.0<p<0.5):
            raise ValueError("tail_probability must lie in (0,0.5)")
        target=math.log(p)
        sd=math.sqrt(self.variance)
        lo=self.mean+max(1e-12*max(1.0,sd),np.finfo(float).eps)
        if math.isfinite(self.upper_support):
            hi=np.nextafter(self.upper_support,-math.inf)
        else:
            hi=self.mean+4.0*sd
            while self.logsf(hi,relative_tolerance=relative_tolerance,**kwargs).log_p>target:
                hi+=4.0*sd
        def f(x):
            return self.logsf(x,relative_tolerance=relative_tolerance,**kwargs).log_p-target
        return float(brentq(f,lo,hi,xtol=1e-12,rtol=1e-10))


__all__ = [
    "BlockFactorSource",
    "PositiveQuadraticFormEngine",
    "NoncentralPositiveQuadraticFormEngine",
    "NoncentralSpectrumSummary",
    "SignedCentralQuadraticFormEngine",
    "SignedSpectrumSummary",
    "SpectrumSummary",
    "TailResult",
]
