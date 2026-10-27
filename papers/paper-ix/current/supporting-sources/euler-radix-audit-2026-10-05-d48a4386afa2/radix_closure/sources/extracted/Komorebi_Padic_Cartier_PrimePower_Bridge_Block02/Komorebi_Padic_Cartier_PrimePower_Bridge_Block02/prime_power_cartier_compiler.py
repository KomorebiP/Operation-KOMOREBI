from __future__ import annotations

from dataclasses import dataclass
from math import ceil, comb
from typing import Dict, Iterable, List, Tuple


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def trim(a: Iterable[int]) -> List[int]:
    out = list(a)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out or [0]


def is_zero(a: Iterable[int], m: int) -> bool:
    return all((x % m) == 0 for x in a)


def padd(a, b, m):
    n = max(len(a), len(b))
    return trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % m for i in range(n)])


def pmul(a, b, m=None):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
            if m is not None:
                out[i+j] %= m
    if m is not None:
        out = [x % m for x in out]
    return trim(out)


def ppow(a, n, m=None):
    out = [1]
    base = list(a)
    while n:
        if n & 1:
            out = pmul(out, base, m)
        n >>= 1
        if n:
            base = pmul(base, base, m)
    return out


def pscale(a, c, m):
    return trim([(c*x) % m for x in a])


def subst_p(a, p):
    out = [0] * ((len(a)-1)*p + 1)
    for i, x in enumerate(a):
        out[p*i] = x
    return trim(out)


def cartier_poly(a, d, p, m):
    if d >= len(a):
        return [0]
    return trim([a[i] % m for i in range(d, len(a), p)] or [0])


def frobenius_defect(B, p):
    bp = ppow(B, p)
    bz = subst_p(B, p)
    n = max(len(bp), len(bz))
    diff = [(bp[i] if i < len(bp) else 0) - (bz[i] if i < len(bz) else 0) for i in range(n)]
    if not all(x % p == 0 for x in diff):
        raise AssertionError("freshman's-dream divisibility failure")
    return trim([x // p for x in diff])


def vp_int(n: int, p: int, infinity: int = 10**9) -> int:
    n = abs(n)
    if n == 0:
        return infinity
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def carry_count_add(a: int, b: int, p: int) -> int:
    if a < 0 or b < 0 or p < 2:
        raise ValueError("carry count requires nonnegative a,b and p>=2")
    carries = 0
    carry = 0
    while a or b or carry:
        da, db = a % p, b % p
        a //= p; b //= p
        total = da + db + carry
        carry = 1 if total >= p else 0
        carries += carry
    return carries


def vp_poly(poly: Iterable[int], p: int, infinity: int = 10**9) -> int:
    vals = [vp_int(x, p, infinity) for x in poly if x != 0]
    return min(vals) if vals else infinity


def deg_mod(poly, m):
    q = trim([x % m for x in poly])
    if is_zero(q, m):
        return -1
    return len(q) - 1


@dataclass(frozen=True)
class Branch:
    source_layer: int
    k: int
    target_layer: int
    q: int
    t: int
    scalar: int
    weight_poly: Tuple[int, ...]  # scalar * E^k mod p^r
    kernel_poly: Tuple[int, ...]  # A * B^t * weight_poly mod p^r
    kernel_degree: int
    valuation_lower_bound: int


@dataclass(frozen=True)
class CompilerBounds:
    coarse_layer_bound: int
    valuation_layer_bound: int
    max_correction_order: int
    layers: Tuple[int, ...]
    degree_by_layer: Tuple[Tuple[int, int], ...]
    coarse_global_degree_bound: int
    valuation_global_degree_bound: int
    coarse_dimension: int
    valuation_dimension: int
    sharpened_dimension: int


class PrimePowerCartierCompiler:
    """Sparse fixed-precision Cartier compiler for B(z)F(z)=A(z)F(z^p) mod p^r."""

    def __init__(self, A: Iterable[int], B: Iterable[int], p: int, r: int):
        if not is_prime(p) or r < 1:
            raise ValueError("require p prime and r>=1")
        self.p = int(p)
        self.r = int(r)
        self.m = p**r
        self.A = tuple(trim(A))
        self.B = tuple(trim(B))
        if (self.A[0] - self.B[0]) % self.m != 0:
            raise ValueError("A(0) must equal B(0) modulo p^r")
        if self.B[0] % p == 0:
            raise ValueError("B(0) must be a p-adic unit")
        self.E = tuple(frobenius_defect(self.B, p))
        self.defect_valuation = vp_poly(self.E, p)
        self.coarse_L = (r - 1) + ceil(r/(p-1))
        if self.defect_valuation > 10**8:
            self.max_k = 0
        else:
            self.max_k = (r - 1) // (1 + self.defect_valuation)
        self.valuation_L = self.max_k + ceil((self.max_k + 1)/(p-1))
        self._branch_cache: Dict[int, Tuple[Branch, ...]] = {}
        self.layers = self._compute_pruned_layers()
        self.degree_by_layer = self._compute_layer_degrees()
        self.index, self.basis = self._build_basis()
        self.dimension = len(self.basis)
        self.transitions = tuple(self._build_sparse_transition(d) for d in range(p))
        self.initial_state = self._build_initial_state()
        self.output_weights = self._build_output_weights()

    def _branches(self, ell: int) -> Tuple[Branch, ...]:
        if ell in self._branch_cache:
            return self._branch_cache[ell]
        p, r, m = self.p, self.r, self.m
        q = ceil((ell+1)/p)
        t = p*q - (ell+1)
        Epow = [1]
        Bpow = ppow(self.B, t, m)
        ABt = pmul(self.A, Bpow, m)
        out = []
        for k in range(self.max_k + 1):
            if k:
                Epow = pmul(Epow, self.E, m)
            carry_v = carry_count_add(k, q-1, p)
            if self.defect_valuation < 10**8 and k*(1+self.defect_valuation) + carry_v >= r:
                continue
            scalar_raw = ((-1)**k) * comb(q+k-1, k) * (p**k)
            scalar = scalar_raw % m
            W = pscale(Epow, scalar, m)
            if is_zero(W, m):
                continue
            K = pmul(ABt, W, m)
            kd = deg_mod(K, m)
            if kd < 0:
                continue
            vlow = k + vp_int(comb(q+k-1, k), p)
            if self.defect_valuation < 10**8:
                vlow += k * self.defect_valuation
            out.append(Branch(ell, k, q+k, q, t, scalar, tuple(W), tuple(K), kd, vlow))
        self._branch_cache[ell] = tuple(out)
        return tuple(out)

    def _compute_pruned_layers(self) -> Tuple[int, ...]:
        seen = {1}
        frontier = [1]
        while frontier:
            ell = frontier.pop()
            for br in self._branches(ell):
                if br.target_layer > self.valuation_L:
                    raise AssertionError("branch exceeded proved valuation-sharpened layer bound")
                if br.target_layer not in seen:
                    seen.add(br.target_layer)
                    frontier.append(br.target_layer)
        return tuple(sorted(seen))

    def _original_global_degree_bound(self) -> int:
        a = len(trim(self.A)) - 1
        b = len(trim(self.B)) - 1
        e = 0 if all(x == 0 for x in self.E) else len(trim(self.E)) - 1
        T = 0
        for ell in range(1, self.coarse_L+1):
            q = ceil((ell+1)/self.p)
            T = max(T, self.p*q-(ell+1))
        C = a + T*b + (self.r-1)*e
        return max(b, ceil(C/(self.p-1)))

    def _global_degree_bound(self) -> int:
        a = len(trim(self.A)) - 1
        b = len(trim(self.B)) - 1
        e = 0 if all(x == 0 for x in self.E) else len(trim(self.E)) - 1
        T = 0
        for ell in range(1, self.valuation_L+1):
            q = ceil((ell+1)/self.p)
            T = max(T, self.p*q-(ell+1))
        C = a + T*b + self.max_k*e
        return max(b, ceil(C/(self.p-1)))

    def _compute_layer_degrees(self) -> Dict[int, int]:
        # Least fixed point of the degree-only propagation inequalities on the pruned layer graph.
        degs = {ell: -1 for ell in self.layers}
        degs[1] = len(trim(self.B))-1
        global_D = self._global_degree_bound()
        changed = True
        while changed:
            changed = False
            for ell in self.layers:
                Din = degs[ell]
                if Din < 0:
                    continue
                for br in self._branches(ell):
                    if br.target_layer not in degs:
                        continue
                    cand = (Din + br.kernel_degree) // self.p
                    if cand > global_D:
                        raise AssertionError("layer-specific degree exceeded proved global degree bound")
                    if cand > degs[br.target_layer]:
                        degs[br.target_layer] = cand
                        changed = True
        return degs

    def _build_basis(self):
        basis = []
        index = {}
        for ell in self.layers:
            D = self.degree_by_layer[ell]
            if D < 0:
                continue
            for j in range(D+1):
                index[(ell,j)] = len(basis)
                basis.append((ell,j))
        return index, tuple(basis)

    def _build_sparse_transition(self, digit: int):
        # Column representation: cols[src] = tuple((dst, coeff), ...)
        cols = []
        for ell, j in self.basis:
            accum: Dict[int,int] = {}
            P = [0]*(j+1)
            P[j] = 1
            for br in self._branches(ell):
                if br.target_layer not in self.degree_by_layer:
                    continue
                H = pmul(P, br.kernel_poly, self.m)
                Q = cartier_poly(H, digit, self.p, self.m)
                Dt = self.degree_by_layer[br.target_layer]
                if len(Q)-1 > Dt and not is_zero(Q, self.m):
                    raise AssertionError("sparse transition exceeded layer degree bound")
                for jj, c in enumerate(Q):
                    c %= self.m
                    if not c:
                        continue
                    dst = self.index[(br.target_layer, jj)]
                    accum[dst] = (accum.get(dst,0)+c) % self.m
            cols.append(tuple(sorted((i,c) for i,c in accum.items() if c % self.m)))
        return tuple(cols)

    def _build_initial_state(self):
        v = [0]*self.dimension
        for j,c in enumerate(self.B):
            if (1,j) not in self.index:
                raise AssertionError("initial B polynomial outside layer-1 degree bound")
            v[self.index[(1,j)]] = c % self.m
        return tuple(v)

    def _build_output_weights(self):
        invb0 = pow(self.B[0] % self.m, -1, self.m)
        w = [0]*self.dimension
        for ell,j in self.basis:
            if j == 0:
                w[self.index[(ell,j)]] = pow(invb0, ell, self.m)
        return tuple(w)

    def apply_digit(self, state: Iterable[int], digit: int) -> Tuple[int,...]:
        if not (0 <= digit < self.p):
            raise ValueError("digit out of range")
        state = tuple(x % self.m for x in state)
        out = [0]*self.dimension
        cols = self.transitions[digit]
        for src,x in enumerate(state):
            if not x:
                continue
            for dst,c in cols[src]:
                out[dst] = (out[dst] + x*c) % self.m
        return tuple(out)

    def output(self, state: Iterable[int]) -> int:
        return sum((x % self.m)*w for x,w in zip(state,self.output_weights)) % self.m

    def coefficient(self, n: int) -> int:
        if n < 0:
            raise ValueError("n must be nonnegative")
        state = self.initial_state
        x = n
        while x:
            state = self.apply_digit(state, x % self.p)
            x //= self.p
        return self.output(state)

    def coefficient_prefix(self, nmax: int) -> List[int]:
        return [self.coefficient(n) for n in range(nmax+1)]

    def bound_summary(self) -> CompilerBounds:
        coarse_D = self._original_global_degree_bound()
        val_D = self._global_degree_bound()
        coarse_dim = self.coarse_L*(coarse_D+1)
        val_dim = self.valuation_L*(val_D+1)
        return CompilerBounds(
            self.coarse_L,
            self.valuation_L,
            self.max_k,
            self.layers,
            tuple(sorted(self.degree_by_layer.items())),
            coarse_D,
            val_D,
            coarse_dim,
            val_dim,
            self.dimension,
        )

    def nonzero_entries(self) -> Tuple[int,...]:
        return tuple(sum(len(col) for col in T) for T in self.transitions)

    def one_layer_stabilization_depth(self) -> int | None:
        """Largest r for which the literal characteristic-p one-layer formula persists; None = infinite."""
        if all(x == 0 for x in self.E):
            return None
        return 1 + self.defect_valuation

    def obstruction_packet(self, s: int) -> Tuple[int,...]:
        """If one-layer form holds mod p^s, return p^{-(s-1)} E_B mod p, the next-lift obstruction packet."""
        if s < 1:
            raise ValueError("s must be >=1")
        div = self.p**(s-1)
        if any(x % div for x in self.E):
            raise ValueError("one-layer form does not hold through precision p^s")
        return tuple((x//div) % self.p for x in self.E)

    def reachable_automaton(self, max_states: int = 100000):
        """Enumerate the exact reachable finite-output automaton, with a hard state cap."""
        if max_states < 1:
            raise ValueError("max_states must be positive")
        states = [self.initial_state]
        ids = {self.initial_state: 0}
        transitions = []
        i = 0
        while i < len(states):
            row = []
            for d in range(self.p):
                nxt = self.apply_digit(states[i], d)
                j = ids.get(nxt)
                if j is None:
                    if len(states) >= max_states:
                        raise RuntimeError(f"reachable-state cap {max_states} exceeded")
                    j = len(states)
                    ids[nxt] = j
                    states.append(nxt)
                row.append(j)
            transitions.append(tuple(row))
            i += 1
        outputs = tuple(self.output(v) for v in states)
        return tuple(states), tuple(transitions), outputs

    @staticmethod
    def minimize_output_automaton(transitions, outputs):
        """Moore minimization for a complete deterministic output automaton."""
        n = len(outputs)
        if len(transitions) != n:
            raise ValueError("transition/output size mismatch")
        if n == 0:
            return (), (), (), ()
        by_out = {}
        for i,o in enumerate(outputs):
            by_out.setdefault(o, []).append(i)
        blocks = [tuple(v) for _,v in sorted(by_out.items(), key=lambda kv: repr(kv[0]))]
        while True:
            block_of = {}
            for bi,b in enumerate(blocks):
                for s in b:
                    block_of[s] = bi
            groups = {}
            for s in range(n):
                sig = (outputs[s], tuple(block_of[t] for t in transitions[s]))
                groups.setdefault(sig, []).append(s)
            new_blocks = [tuple(v) for _,v in sorted(groups.items(), key=lambda kv: repr(kv[0]))]
            if len(new_blocks) == len(blocks) and {frozenset(b) for b in new_blocks} == {frozenset(b) for b in blocks}:
                blocks = new_blocks
                break
            blocks = new_blocks
        block_of = {}
        for bi,b in enumerate(blocks):
            for s in b:
                block_of[s] = bi
        min_trans = tuple(tuple(block_of[t] for t in transitions[b[0]]) for b in blocks)
        min_outputs = tuple(outputs[b[0]] for b in blocks)
        return tuple(blocks), min_trans, min_outputs, tuple(block_of[i] for i in range(n))


def direct_coefficients(A, B, p, r, nmax):
    m = p**r
    A = [x % m for x in trim(A)]
    B = [x % m for x in trim(B)]
    if (A[0]-B[0]) % m:
        raise ValueError("constant terms differ")
    invb0 = pow(B[0], -1, m)
    f = [0]*(nmax+1)
    f[0] = 1
    for n in range(1,nmax+1):
        rhs = 0
        for i,a in enumerate(A):
            if i <= n and (n-i)%p == 0:
                rhs = (rhs + a*f[(n-i)//p]) % m
        lhs = 0
        for i in range(1,len(B)):
            if i <= n:
                lhs = (lhs+B[i]*f[n-i]) % m
        f[n] = ((rhs-lhs)*invb0) % m
    return f
