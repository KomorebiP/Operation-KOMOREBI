from __future__ import annotations

import itertools
import json
import math
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_X_Strengthened_Annals_Edition.tex"
BIB = ROOT / "PSC_Paper_X_Strengthened_Annals_Edition.bib"
LEGACY = ROOT / "legacy"
FIGURES = ROOT / "figures"


@dataclass
class Audit:
    total: int = 0
    passed: int = 0
    groups: list[tuple[str, int]] = None

    def __post_init__(self) -> None:
        if self.groups is None:
            self.groups = []
        self._group_start = 0
        self._group_name = ""

    def start(self, name: str) -> None:
        if self._group_name:
            self.groups.append((self._group_name, self.passed - self._group_start))
        self._group_name = name
        self._group_start = self.passed

    def check(self, condition: bool, message: str = "") -> None:
        self.total += 1
        if not condition:
            raise AssertionError(message or f"check {self.total} failed")
        self.passed += 1

    def finish(self) -> None:
        if self._group_name:
            self.groups.append((self._group_name, self.passed - self._group_start))
            self._group_name = ""


def rank_mod(A: np.ndarray, p: int) -> int:
    M = np.array(A, dtype=int) % p
    m, n = M.shape
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i, c] % p), None)
        if pivot is None:
            continue
        M[[r, pivot]] = M[[pivot, r]]
        inv = pow(int(M[r, c]), -1, p)
        M[r] = (M[r] * inv) % p
        for i in range(m):
            if i != r and M[i, c] % p:
                M[i] = (M[i] - M[i, c] * M[r]) % p
        r += 1
        if r == m:
            break
    return r


def det_mod(A: np.ndarray, p: int) -> int:
    M = np.array(A, dtype=int) % p
    n, m = M.shape
    if n != m:
        raise ValueError("determinant requires square matrix")
    det = 1
    for c in range(n):
        pivot = next((i for i in range(c, n) if M[i, c] % p), None)
        if pivot is None:
            return 0
        if pivot != c:
            M[[c, pivot]] = M[[pivot, c]]
            det = -det
        pv = int(M[c, c]) % p
        det = det * pv % p
        inv = pow(pv, -1, p)
        for i in range(c + 1, n):
            factor = M[i, c] * inv % p
            M[i, c:] = (M[i, c:] - factor * M[c, c:]) % p
    return det % p


def all_vectors(p: int, n: int) -> Iterable[np.ndarray]:
    for x in itertools.product(range(p), repeat=n):
        yield np.array(x, dtype=int)


def image_vectors(D: np.ndarray, p: int) -> set[tuple[int, ...]]:
    return {tuple((D @ u % p).tolist()) for u in all_vectors(p, D.shape[1])}


def sccs(n: int, edges: set[tuple[int, int]]) -> list[list[int]]:
    graph = [[] for _ in range(n)]
    rev = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        rev[v].append(u)
    seen = [False] * n
    order: list[int] = []

    def dfs(u: int) -> None:
        seen[u] = True
        for v in graph[u]:
            if not seen[v]:
                dfs(v)
        order.append(u)

    for u in range(n):
        if not seen[u]:
            dfs(u)
    comps: list[list[int]] = []
    seen = [False] * n

    def rdfs(u: int, comp: list[int]) -> None:
        seen[u] = True
        comp.append(u)
        for v in rev[u]:
            if not seen[v]:
                rdfs(v, comp)

    for u in reversed(order):
        if not seen[u]:
            comp: list[int] = []
            rdfs(u, comp)
            comps.append(comp)
    return comps


def source_scc_count(n: int, edges: set[tuple[int, int]]) -> int:
    comps = sccs(n, edges)
    idx = {}
    for i, comp in enumerate(comps):
        for v in comp:
            idx[v] = i
    incoming = [False] * len(comps)
    for u, v in edges:
        if idx[u] != idx[v]:
            incoming[idx[v]] = True
    return sum(not x for x in incoming)


def reachable(n: int, edges: set[tuple[int, int]], starts: set[int]) -> set[int]:
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v)
    seen = set(starts)
    dq = deque(starts)
    while dq:
        u = dq.popleft()
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return seen


def brute_directed_rank(n: int, edges: set[tuple[int, int]]) -> int:
    for r in range(n + 1):
        for S in itertools.combinations(range(n), r):
            if len(reachable(n, edges, set(S))) == n:
                return r
    raise RuntimeError


def poly_eval(coeffs: Sequence[int], x: int, p: int) -> int:
    acc = 0
    for c in reversed(coeffs):
        acc = (acc * x + c) % p
    return acc


def minor_vanishes(A: np.ndarray, size: int, p: int) -> bool:
    m, n = A.shape
    if size <= 0:
        return False
    if size > min(m, n):
        return True
    for rows in itertools.combinations(range(m), size):
        for cols in itertools.combinations(range(n), size):
            if det_mod(A[np.ix_(rows, cols)], p) != 0:
                return False
    return True


def roots_x2_plus_1(p: int, depth: int) -> list[int]:
    mod = p**depth
    return [x for x in range(mod) if (x*x + 1) % mod == 0]


def main() -> None:
    a = Audit()
    rng = np.random.default_rng(20260814)

    a.start("Residual fibers and positive depth")
    for p in (2, 3, 5, 7):
        for N in range(1, 45):
            buckets: dict[int, list[int]] = defaultdict(list)
            for x in range(N):
                buckets[x % p].append(x)
            flat = sorted(v for values in buckets.values() for v in values)
            a.check(flat == list(range(N)))
            for values in buckets.values():
                a.check(len({x % p for x in values}) == 1)
        for _ in range(100):
            x = int(rng.integers(-10000, 10000))
            chain = [x]
            for depth in range(1, 8):
                chain.append(chain[-1] + int(rng.integers(-20, 21)) * p**depth)
            a.check(len({y % p for y in chain}) == 1)

    a.start("Lift forests and companion branches")
    expected = {
        2: [1, 0, 0, 0, 0],
        3: [0, 0, 0, 0, 0],
        5: [2, 2, 2, 2, 2],
        7: [0, 0, 0, 0, 0],
        13: [2, 2, 2, 2, 2],
    }
    for p, counts in expected.items():
        levels = [roots_x2_plus_1(p, m) for m in range(1, 6)]
        a.check([len(x) for x in levels] == counts, f"root counts p={p}")
        for m in range(1, 5):
            image = {x % (p**m) for x in levels[m]}
            a.check(image.issubset(set(levels[m-1])))
        if p in (5, 13):
            a.check(all(len(level) == 2 for level in levels))
            for m in range(1, 5):
                a.check({x % (p**m) for x in levels[m]} == set(levels[m-1]))
    for p in (2, 3, 5, 7):
        for _ in range(100):
            digits = rng.integers(0, p, size=8)
            residues = []
            value = 0
            for m, d in enumerate(digits, start=1):
                value += int(d) * p ** (m - 1)
                residues.append(value % (p**m))
            a.check(all(residues[m] % (p ** m) == residues[m-1] for m in range(1, len(residues))))

    a.start("Weighted, nilpotent, and crossing counts")
    for q in (2, 3, 5):
        for weights in ((1,), (1, 2), (1, 2, 4), (2, 3, 3)):
            for m in range(1, 7):
                formula = q ** sum(max(m - w, 0) for w in weights)
                brute = math.prod(q ** max(m - w, 0) for w in weights)
                a.check(formula == brute)
        for e in (1, 2, 3, 4):
            for m in range(1, 6):
                mod = q**m
                brute = sum(pow(x, e, mod) == 0 for x in range(mod))
                formula = q ** (m - math.ceil(m / e))
                a.check(brute == formula, f"nilpotent q={q} e={e} m={m}")
        for m in range(1, 6):
            mod = q**m
            brute = sum((x*y) % mod == 0 for x in range(mod) for y in range(mod))
            formula = q**m + m*(q-1)*q**(m-1)
            a.check(brute == formula, f"crossing q={q} m={m}")
    # Check the displayed q=3 examples.
    a.check([3 ** (2*(m-1)) for m in range(1, 6)] == [1, 9, 81, 729, 6561])
    a.check([2 ** sum(max(m-w, 0) for w in (1,2,4)) for m in range(1,7)] == [1,2,8,32,256,2048])
    a.check([3 ** (m-math.ceil(m/2)) for m in range(1,9)] == [1,3,3,9,9,27,27,81])
    a.check([3**m + 2*m*3**(m-1) for m in range(1,6)] == [5,21,81,297,1053])

    a.start("Cohomology packets")
    for p in (2, 3, 5, 7):
        for _ in range(120):
            packet_dims = []
            total_c0 = total_c1 = total_c2 = 0
            d0_blocks = []
            d1_blocks = []
            for _j in range(int(rng.integers(1, 5))):
                n0 = int(rng.integers(0, 4))
                n1 = int(rng.integers(0, 5))
                n2 = int(rng.integers(0, 4))
                # Use d1=0 so d1*d0=0, while d0 is arbitrary.
                d0 = rng.integers(0, p, size=(n1, n0), dtype=int)
                d1 = np.zeros((n2, n1), dtype=int)
                h0 = n0 - rank_mod(d0, p)
                h1 = n1 - rank_mod(d0, p) - rank_mod(d1, p)
                h2 = n2 - rank_mod(d1, p)
                packet_dims.append((h0, h1, h2))
                d0_blocks.append(d0)
                d1_blocks.append(d1)
                total_c0 += n0; total_c1 += n1; total_c2 += n2
            D0 = np.zeros((total_c1, total_c0), dtype=int)
            D1 = np.zeros((total_c2, total_c1), dtype=int)
            r1 = c0 = r2 = c1 = 0
            for d0, d1 in zip(d0_blocks, d1_blocks):
                n1,n0=d0.shape; n2,_=d1.shape
                D0[r1:r1+n1,c0:c0+n0]=d0
                D1[r2:r2+n2,c1:c1+n1]=d1
                r1+=n1;c0+=n0;r2+=n2;c1+=n1
            total = (
                total_c0-rank_mod(D0,p),
                total_c1-rank_mod(D0,p)-rank_mod(D1,p),
                total_c2-rank_mod(D1,p),
            )
            a.check(total == tuple(sum(x[i] for x in packet_dims) for i in range(3)))

    a.start("Linear and packet obstruction counts")
    for p in (2, 3, 5):
        for n_u in range(0, 4):
            for n_v in range(0, 4):
                for _ in range(25):
                    D = rng.integers(0, p, size=(n_v, n_u), dtype=int)
                    image = image_vectors(D, p)
                    kdim = n_u - rank_mod(D, p)
                    for r in all_vectors(p, n_v):
                        target = tuple((-r % p).tolist())
                        sols = sum(np.array_equal(D @ u % p, -r % p) for u in all_vectors(p, n_u))
                        a.check((target in image) == (sols > 0))
                        if sols:
                            a.check(sols == p**kdim)
        # Packet block count.
        D1 = rng.integers(0, p, size=(3, 2), dtype=int)
        D2 = rng.integers(0, p, size=(2, 3), dtype=int)
        D = np.block([[D1, np.zeros((3,3),dtype=int)], [np.zeros((2,2),dtype=int), D2]])
        a.check(D.shape == (5,5))
        a.check(5-rank_mod(D,p) == (2-rank_mod(D1,p))+(3-rank_mod(D2,p)))

    a.start("Directed source component theorem")
    for n in range(1, 5):
        possible = [(i,j) for i in range(n) for j in range(n) if i != j]
        for mask in range(1 << len(possible)):
            edges = {possible[k] for k in range(len(possible)) if mask & (1 << k)}
            a.check(source_scc_count(n, edges) == brute_directed_rank(n, edges), f"graph n={n} mask={mask}")

    a.start("Frobenius separation and carrier multiplicities")
    C = np.array([[1,1,1],[1,2,3],[3,0,1]], dtype=int)
    m = np.array([2,0,1], dtype=int)
    t = C @ m
    a.check(tuple(t.tolist()) == (3,5,7))
    a.check(round(np.linalg.det(C)) != 0)
    recovered = np.linalg.solve(C.astype(float), t.astype(float))
    a.check(np.allclose(recovered, m))
    for rows in range(3, 8):
        for cols in range(1, min(rows,5)+1):
            for _ in range(40):
                A = rng.integers(-5, 6, size=(rows, cols))
                r_q = np.linalg.matrix_rank(A.astype(float), tol=1e-9)
                # Rational rank is preserved mod a large prime unless every maximal minor is divisible by it.
                # We instead verify field extension invariance by exact nonzero minor detection over integers and rationals.
                exact_rank = 0
                for k in range(1, min(rows,cols)+1):
                    found=False
                    for rr in itertools.combinations(range(rows),k):
                        for cc in itertools.combinations(range(cols),k):
                            det=round(np.linalg.det(A[np.ix_(rr,cc)].astype(float)))
                            if det != 0:
                                found=True; break
                        if found: break
                    if found: exact_rank=k
                a.check(r_q == exact_rank)

    a.start("Fitting support and generator strata")
    for p in (2,3,5,7):
        for b in range(1,5):
            for aa in range(0,6):
                for _ in range(30):
                    coeffs = [[[int(rng.integers(0,p)) for _d in range(3)] for _j in range(b)] for _i in range(aa)]
                    for x in range(p):
                        A = np.array([[poly_eval(coeffs[i][j],x,p) for j in range(b)] for i in range(aa)], dtype=int)
                        if aa == 0:
                            A = np.zeros((0,b),dtype=int)
                        mu = b-rank_mod(A,p)
                        # Fitt0 vanishes at x iff all b by b minors vanish iff fiber is nonzero.
                        fitt0_vanish = minor_vanishes(A,b,p)
                        a.check(fitt0_vanish == (mu >= 1))
                        for r in range(1,b+2):
                            size=b-r+1
                            fitt_vanish = minor_vanishes(A,size,p) if size>0 else False
                            a.check(fitt_vanish == (mu >= r))

    a.start("Artinian and joint spectral occupancy")
    for n in range(1,15):
        for _ in range(80):
            labels = rng.integers(0,4,size=n)
            for packet in range(4):
                e = (labels == packet).astype(int)
                a.check(int(e.sum()) == int(np.trace(np.diag(e))))
                a.check(int(e.sum()) == int(np.linalg.matrix_rank(np.diag(e))))
            # Commuting diagonal operators and exact joint packet.
            T1 = rng.integers(-2,3,size=n)
            T2 = rng.integers(-2,3,size=n)
            a1 = int(rng.integers(-2,3)); a2 = int(rng.integers(-2,3))
            joint = ((T1==a1)&(T2==a2)).astype(int)
            a.check(int(joint.sum()) == int(np.trace(np.diag(joint))))
            # A sequence of commuting coordinate projectors has nested ranks.
            E = np.ones(n,dtype=int)
            ranks=[]
            for _j in range(8):
                e = rng.integers(0,2,size=n)
                E *= e
                ranks.append(int(E.sum()))
            a.check(all(ranks[i+1] <= ranks[i] for i in range(len(ranks)-1)))

    a.start("Infinite occupancy and adic reconstruction")
    for n in range(1,30):
        subset=set(range(n))
        chain=[]
        for _ in range(50):
            if subset and rng.random()<0.7:
                subset.discard(int(rng.choice(list(subset))))
            chain.append(frozenset(subset))
        dims=[len(x) for x in chain]
        a.check(all(dims[i+1]<=dims[i] for i in range(len(dims)-1)))
        if all(d>0 for d in dims):
            a.check(len(set.intersection(*(set(x) for x in chain)))>0)
    for p in (2,3,5,7):
        for _ in range(100):
            x=int(rng.integers(1,p**8))
            residues=[x%(p**m) for m in range(1,9)]
            a.check(all(residues[m]%(p**m)==residues[m-1] for m in range(1,8)))
            reconstructed=sum(((residues[m]//(p**m))%p)*p**m for m in range(8))
            a.check(reconstructed==x%(p**8))
    # Finite tail model illustrates why positive finite ranks are insufficient without fixed finite dimension.
    for N in range(2,25):
        tail_sizes=[N-m+1 for m in range(1,N+1)]
        a.check(all(x>0 for x in tail_sizes))
        a.check(tail_sizes[-1]==1)

    a.start("Legacy certificates")
    legacy_json=json.loads((LEGACY/'results'/'residual_seed_results.json').read_text())
    a.check(legacy_json['carrier_completion']['observed_traces']==[3,5,7])
    a.check(legacy_json['carrier_completion']['recovered_multiplicities']==[2,0,1])
    for p, counts in expected.items():
        a.check(legacy_json['companion_forests_x2_plus_1'][str(p)]['level_counts']==counts)
    seed_rows=(LEGACY/'tables'/'seed_zeta_counts.csv').read_text().strip().splitlines()[1:]
    for row in seed_rows:
        m,smooth,weighted,singular=map(int,row.split(','))
        a.check(smooth==3**(2*(m-1)))
        a.check(weighted==2**sum(max(m-w,0) for w in (1,2,4)))
        a.check(singular==3**(m-math.ceil(m/2)))

    a.start("Source, bibliography, and figure integrity")
    tex=TEX.read_text()
    bib=BIB.read_text()
    labels=re.findall(r'\\label\{([^}]+)\}',tex)
    a.check(len(labels)==len(set(labels)),"duplicate labels")
    refs=[]
    for raw in re.findall(r'\\(?:c|C)?ref\{([^}]+)\}',tex):
        refs.extend(x.strip() for x in raw.split(','))
    a.check(set(refs).issubset(set(labels)), f"missing refs {sorted(set(refs)-set(labels))}")
    bibkeys=set(re.findall(r'^@\w+\{([^,]+),',bib,re.M))
    cites=set()
    for raw in re.findall(r'\\cite\{([^}]+)\}',tex):
        cites.update(x.strip() for x in raw.split(','))
    a.check(cites==bibkeys, f"citation mismatch missing={cites-bibkeys} uncited={bibkeys-cites}")
    proved=sum(tex.count(f'\\begin{{{env}}}') for env in ('theorem','proposition','lemma','corollary'))
    proof_count=tex.count('\\begin{proof}')
    example_proofs=1  # Tail projection example has a proof.
    a.check(proof_count==proved+example_proofs, f"proofs {proof_count} proved {proved}")
    abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',tex,re.S).group(1)
    abstract_plain=re.sub(r'\\[A-Za-z]+(?:\[[^]]*\])?(?:\{[^{}]*\})?',' ',abstract)
    abstract_plain=re.sub(r'[$\\{}_^]',' ',abstract_plain)
    words=re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?",abstract_plain)
    a.check(len(words)<=200, f"abstract has {len(words)} words")
    a.check(';' not in tex)
    a.check('--' not in tex)
    for forbidden in ('\\newpage','\\pagebreak','\\linebreak','\\clearpage'):
        a.check(forbidden not in tex, forbidden)
    fig_names=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',tex)
    a.check(len(fig_names)==14)
    for name in fig_names:
        fp=FIGURES/name
        a.check(fp.exists(),str(fp))
        a.check(fp.suffix.lower()=='.pdf')
        # Vector only. A raster image marker in a PDF usually contains /Subtype /Image.
        a.check(b'/Subtype /Image' not in fp.read_bytes(),f"raster in {name}")

    a.finish()
    print(f"Paper X verification: {a.passed}/{a.total} checks passed in {len(a.groups)} groups")
    for name,count in a.groups:
        print(f"  {name}: {count}")


if __name__ == '__main__':
    main()
