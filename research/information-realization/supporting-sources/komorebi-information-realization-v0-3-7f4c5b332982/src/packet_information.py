"""Exact prime-field packet information and restricted linear repair.

No NumPy, network or external theorem library is required. Matrix dimensions,
coefficient field and encoder access are explicit. Theorems are in THEORY.md.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import isqrt
from typing import Iterable, Sequence


def _integer(x: object, name: str) -> int:
    if type(x) is not int:
        raise ValueError(f'{name} must be a Python integer, not a float/bool')
    return x


def _prime(p: int) -> int:
    _integer(p, 'field characteristic')
    if p < 2 or any(p % d == 0 for d in range(2, isqrt(p) + 1)):
        raise ValueError('only prime fields are implemented')
    return p


@dataclass(frozen=True)
class Matrix:
    """An exact m-by-n matrix over GF(p); zero-row shapes are preserved."""
    p: int
    ncols: int
    rows: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        p = _prime(self.p)
        n = _integer(self.ncols, 'ncols')
        if n < 0:
            raise ValueError('ncols must be nonnegative')
        rows = tuple(tuple(row) for row in self.rows)
        if any(len(row) != n for row in rows):
            raise ValueError('ragged matrix or incorrect column dimension')
        if any(type(v) is not int for row in rows for v in row):
            raise ValueError('matrix entries must be exact integers')
        object.__setattr__(self, 'rows', tuple(tuple(v % p for v in row) for row in rows))

    @property
    def nrows(self) -> int:
        return len(self.rows)

    @property
    def shape(self) -> tuple[int, int]:
        return self.nrows, self.ncols

    @classmethod
    def zero(cls, p: int, m: int, n: int) -> Matrix:
        if _integer(m, 'nrows') < 0:
            raise ValueError('nrows must be nonnegative')
        return cls(p, n, ((0,) * n,) * m)

    @classmethod
    def identity(cls, p: int, n: int) -> Matrix:
        if _integer(n, 'dimension') < 0:
            raise ValueError('dimension must be nonnegative')
        return cls(p, n, tuple(tuple(int(i == j) for j in range(n)) for i in range(n)))

    def apply(self, x: Sequence[int]) -> tuple[int, ...]:
        x = tuple(x)
        if len(x) != self.ncols or any(type(v) is not int for v in x):
            raise ValueError('state must be an exact integer vector of the input dimension')
        return tuple(sum(a*b for a,b in zip(row,x)) % self.p for row in self.rows)

    def __matmul__(self, other: Matrix) -> Matrix:
        if not isinstance(other, Matrix) or self.p != other.p or self.ncols != other.nrows:
            raise ValueError('matrix product field or dimension mismatch')
        cols = tuple(zip(*other.rows)) if other.nrows else ((),) * other.ncols
        return Matrix(self.p, other.ncols, tuple(
            tuple(sum(a*b for a,b in zip(row,col)) % self.p for col in cols)
            for row in self.rows))

    def __add__(self, other: Matrix) -> Matrix:
        if self.p != other.p or self.shape != other.shape:
            raise ValueError('matrix sum field or dimension mismatch')
        return Matrix(self.p,self.ncols,tuple(tuple(a+b for a,b in zip(x,y)) for x,y in zip(self.rows,other.rows)))

    def stack(self, *others: Matrix) -> Matrix:
        if any(o.p != self.p or o.ncols != self.ncols for o in others):
            raise ValueError('stack field or input dimension mismatch')
        return Matrix(self.p,self.ncols,self.rows + tuple(r for o in others for r in o.rows))

    def take_rows(self, indices: Sequence[int]) -> Matrix:
        ix = tuple(indices)
        if any(type(i) is not int or i < 0 or i >= self.nrows for i in ix):
            raise ValueError('row index outside matrix')
        return Matrix(self.p,self.ncols,tuple(self.rows[i] for i in ix))

    def take_cols(self, indices: Sequence[int]) -> Matrix:
        ix = tuple(indices)
        if any(type(i) is not int or i < 0 or i >= self.ncols for i in ix):
            raise ValueError('column index outside matrix')
        return Matrix(self.p,len(ix),tuple(tuple(row[i] for i in ix) for row in self.rows))

    def transpose(self) -> Matrix:
        return Matrix(self.p,self.nrows,tuple(tuple(self.rows[i][j] for i in range(self.nrows)) for j in range(self.ncols)))

    def rref(self) -> tuple[Matrix, tuple[int, ...]]:
        a = [list(row) for row in self.rows]
        row = 0
        pivots = []
        for col in range(self.ncols):
            k = next((k for k in range(row,self.nrows) if a[k][col]),None)
            if k is None:
                continue
            a[row],a[k]=a[k],a[row]
            inv=pow(a[row][col],-1,self.p)
            a[row]=[v*inv % self.p for v in a[row]]
            for i in range(self.nrows):
                if i != row and a[i][col]:
                    factor=a[i][col]
                    a[i]=[(v-factor*w) % self.p for v,w in zip(a[i],a[row])]
            pivots.append(col)
            row += 1
            if row == self.nrows:
                break
        return Matrix(self.p,self.ncols,tuple(tuple(r) for r in a)),tuple(pivots)

    def basis(self) -> Matrix:
        reduced,pivots=self.rref()
        return reduced.take_rows(range(len(pivots)))

    def rank(self) -> int:
        return len(self.rref()[1])

    def kernel_basis(self) -> Matrix:
        """Return kernel basis vectors as rows in the original input space."""
        reduced,pivots=self.rref()
        free=[i for i in range(self.ncols) if i not in pivots]
        out=[]
        for j in free:
            v=[0]*self.ncols
            v[j]=1
            for k,col in enumerate(pivots):
                v[col]=-reduced.rows[k][j] % self.p
            out.append(tuple(v))
        return Matrix(self.p,self.ncols,tuple(out))

    def inverse(self) -> Matrix:
        if self.nrows != self.ncols:
            raise ValueError('inverse requires a square matrix')
        out=factor_rows(Matrix.identity(self.p,self.ncols),self)
        if out is None:
            raise ValueError('matrix is singular in this coefficient field')
        return out

    def payload(self) -> dict:
        return {'p':self.p,'shape':self.shape,'rows':self.rows}


def factor_rows(target: Matrix, observation: Matrix) -> Matrix | None:
    """Solve D observation = target, setting free coefficient variables to zero.

    Returns None iff no linear decoder exists. Independent tests compare this
    with fiber enumeration rather than another row-space test alone.
    """
    if target.p != observation.p or target.ncols != observation.ncols:
        raise ValueError('factorization field or state dimension mismatch')
    p=target.p
    k=observation.nrows
    rows=[]
    for t in target.rows:
        augmented=Matrix(p,k+1,tuple(tuple(observation.rows[j][i] for j in range(k))+(t[i],)
                                     for i in range(target.ncols)))
        reduced,pivots=augmented.rref()
        if k in pivots:
            return None
        c=[0]*k
        for row,pivot in enumerate(pivots):
            c[pivot]=reduced.rows[row][k]
        rows.append(tuple(c))
    return Matrix(p,k,tuple(rows))


def obstruction_dimension(observation: Matrix, target: Matrix) -> int:
    return observation.stack(target).rank()-observation.rank()


@dataclass(frozen=True)
class RepairCertificate:
    feasible: bool
    deficit_dimension: int
    inaccessible_dimension: int
    encoder: Matrix | None
    message: Matrix | None
    decoder: Matrix | None
    witness: tuple[int, ...] | None

    def payload(self) -> dict:
        return {'feasible':self.feasible,'deficit_dimension':self.deficit_dimension,
                'inaccessible_dimension':self.inaccessible_dimension,
                'encoder':None if self.encoder is None else self.encoder.payload(),
                'message':None if self.message is None else self.message.payload(),
                'decoder':None if self.decoder is None else self.decoder.payload(),
                'witness':self.witness}


def accessible_repair(observation: Matrix, target: Matrix, access: Matrix) -> RepairCertificate:
    """Minimal single-encoder, single-decoder repair using linear combinations of Ux.

    Feasibility: ker R intersect ker U <= ker F. If feasible, send exactly
    d=rank([R;F])-rank(R) field coordinates. This meets the q**d alphabet lower
    bound even among arbitrary nonlinear encoders. Otherwise return a witness
    v with Rv=Uv=0 and Fv!=0.
    """
    joined=observation.stack(access)
    d=obstruction_dimension(observation,target)
    e=obstruction_dimension(joined,target)
    if e:
        witness=next((v for v in joined.kernel_basis().rows if any(target.apply(v))),None)
        if witness is None:
            raise ArithmeticError('failed to construct inaccessible obstruction witness')
        return RepairCertificate(False,d,e,None,None,None,witness)
    current=observation
    selected=[]
    rank=current.rank()
    for i,row in enumerate(target.rows):
        extended=current.stack(Matrix(target.p,target.ncols,(row,)))
        newrank=extended.rank()
        if newrank > rank:
            selected.append(i)
            current=extended
            rank=newrank
    complement=target.take_rows(selected)
    split=factor_rows(complement,joined)
    if split is None:
        raise ArithmeticError('feasibility and factorization disagree')
    encoder=split.take_cols(range(observation.nrows,joined.nrows))
    message=encoder @ access
    decoder=factor_rows(target,observation.stack(message))
    if decoder is None or message.nrows != d:
        raise ArithmeticError('repair construction failed')
    return RepairCertificate(True,d,0,encoder,message,decoder,None)


def verify_repair(certificate: RepairCertificate, observation: Matrix, target: Matrix,
                  access: Matrix) -> bool:
    """Check returned algebraic identities; never assumes the producer succeeded."""
    if certificate.deficit_dimension != obstruction_dimension(observation,target):
        return False
    if certificate.inaccessible_dimension != obstruction_dimension(observation.stack(access),target):
        return False
    if not certificate.feasible:
        v=certificate.witness
        return (v is not None and not any(observation.apply(v)) and not any(access.apply(v))
                and any(target.apply(v)))
    h,c,d=certificate.encoder,certificate.message,certificate.decoder
    if h is None or c is None or d is None:
        return False
    return (h @ access == c and d @ observation.stack(c) == target
            and c.nrows == certificate.deficit_dimension
            and obstruction_dimension(observation,c) == certificate.deficit_dimension)


def minimal_raw_packets(observation: Matrix, target: Matrix, packets: Sequence[Matrix],
                        *, max_packets: int = 20) -> tuple[int,...] | None:
    """Exhaustive minimum packet count, NOT the compressed-message budget.

    Packets are indivisible groups of rows with unit cost. Exponential search is
    deliberate and guarded; no unsupported greedy-optimality claim is made.
    """
    if len(packets) > max_packets:
        raise ValueError('raw-packet search resource guard exceeded')
    for size in range(len(packets)+1):
        for subset in combinations(range(len(packets)),size):
            joined=observation.stack(*(packets[i] for i in subset))
            if obstruction_dimension(joined,target) == 0:
                return subset
    return None


def packet_transfer(analysis: Matrix, transfer: Matrix) -> Matrix:
    """Conjugate a state transfer into an invertible packet coordinate system."""
    return analysis @ transfer @ analysis.inverse()


def leakage_block(transfer_in_packets: Matrix, retained: Sequence[int],
                  target_rows: Sequence[int] | None = None) -> Matrix:
    b=transfer_in_packets
    if b.nrows != b.ncols:
        raise ValueError('packet transfer must be square')
    kept=tuple(retained)
    if len(set(kept)) != len(kept):
        raise ValueError('retained packet coordinates must be distinct')
    b.take_cols(kept)  # Explicit index validation, including the empty case.
    targets=kept if target_rows is None else tuple(target_rows)
    hidden=tuple(i for i in range(b.ncols) if i not in kept)
    return b.take_rows(targets).take_cols(hidden)


@dataclass(frozen=True)
class ClosureCertificate:
    state: Matrix
    decode_initial: Matrix
    transitions: tuple[Matrix,...]
    rank_history: tuple[int,...]

    def payload(self) -> dict:
        return {'state':self.state.payload(),'decode_initial':self.decode_initial.payload(),
                'transitions':[m.payload() for m in self.transitions],
                'rank_history':self.rank_history}


def predictive_closure(observation: Matrix, actions: Sequence[Matrix]) -> ClosureCertificate:
    """Smallest action-invariant row space containing the original observation.

    This is a future-sufficient state representation, not a causal algorithm for
    recovering its extra coordinates from observations already available.
    """
    actions=tuple(actions)
    n=observation.ncols
    if any(t.p != observation.p or t.shape != (n,n) for t in actions):
        raise ValueError('action has incompatible field or state dimension')
    state=observation.basis()
    history=[state.nrows]
    while True:
        new=state.stack(*(state @ t for t in actions)).basis()
        if new.nrows == state.nrows:
            break
        state=new
        history.append(state.nrows)
        if len(history) > n+1:
            raise ArithmeticError('finite-dimensional closure bound violated')
    transitions=tuple(factor_rows(state @ t,state) for t in actions)
    decoder=factor_rows(observation,state)
    if decoder is None or any(m is None for m in transitions):
        raise ArithmeticError('closure did not produce exact factorization certificates')
    return ClosureCertificate(state,decoder,transitions,tuple(history))


def finite_profile(p: int, deficit_dimension: int) -> dict:
    """Uniform full-vector-space source ONLY. Bits are joint fixed-width bits."""
    _prime(p)
    if _integer(deficit_dimension,'deficit dimension') < 0:
        raise ValueError('deficit dimension must be nonnegative')
    k=p**deficit_dimension
    return {'dimension':deficit_dimension,'alphabet':k,'fixed_width_bits':(k-1).bit_length(),
            'entropy_exact':f'{deficit_dimension} * log2({p})',
            'bayes_error':str(Fraction(k-1,k)),'categorical_residual':str(Fraction(k-1,k))}
