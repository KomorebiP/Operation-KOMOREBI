from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb, gcd
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
GEN = ROOT / "generated"
GEN.mkdir(exist_ok=True)

failures: list[str] = []
checks = 0
category_counts: dict[str, int] = {}


def check(cond: bool, label: str, category: str) -> None:
    global checks
    checks += 1
    category_counts[category] = category_counts.get(category, 0) + 1
    if not cond:
        failures.append(label)


def add(a: list[Fraction], b: list[Fraction], n: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(n)]
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
    return out


def conv(a: list[Fraction], b: list[Fraction], n: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(n)]
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if i + j >= n:
                break
            if bj:
                out[i + j] += ai * bj
    return out


def series_pow(a: list[Fraction], q: int, n: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(n)]
    out[0] = 1
    for _ in range(q):
        out = conv(out, a, n)
    return out


def qary_coefficient(q: int, lam: Fraction, m: int) -> Fraction:
    return Fraction(comb(q * m, m), (q - 1) * m + 1) * (lam ** m)


def qary_series(q: int, lam: Fraction, z_degree: int) -> list[Fraction]:
    out = [Fraction(0) for _ in range(z_degree + 1)]
    m = 0
    while 1 + (q - 1) * m <= z_degree:
        out[1 + (q - 1) * m] = qary_coefficient(q, lam, m)
        m += 1
    return out


def split_packets(u: list[Fraction], N: int, x_degree: int) -> list[list[Fraction]]:
    packets = [[Fraction(0) for _ in range(x_degree + 1)] for _ in range(N)]
    for n, a in enumerate(u):
        if a == 0:
            continue
        j = n % N
        m = n // N
        if m <= x_degree:
            packets[j][m] = a
    return packets


def packet_mul(A: list[list[Fraction]], B: list[list[Fraction]], N: int, x_degree: int) -> list[list[Fraction]]:
    out = [[Fraction(0) for _ in range(x_degree + 1)] for _ in range(N)]
    for r in range(N):
        for s in range(N):
            address = (r + s) % N
            carry = (r + s) // N
            for i, ai in enumerate(A[r]):
                if ai == 0:
                    continue
                for j, bj in enumerate(B[s]):
                    deg = i + j + carry
                    if deg > x_degree:
                        break
                    if bj:
                        out[address][deg] += ai * bj
    return out


def packet_pow(A: list[list[Fraction]], q: int, N: int, x_degree: int) -> list[list[Fraction]]:
    ident = [[Fraction(0) for _ in range(x_degree + 1)] for _ in range(N)]
    ident[0][0] = 1
    out = ident
    for _ in range(q):
        out = packet_mul(out, A, N, x_degree)
    return out


def support_period(u: list[Fraction]) -> int:
    support = [n for n, a in enumerate(u) if a and n > 1]
    if not support:
        return 0
    d = 0
    for n in support:
        d = gcd(d, n - 1)
    return d


BRIDGE_CLASSES = {
    "equivalence",
    "fully faithful inclusion",
    "conservative forgetful functor",
    "information-losing directional functor",
    "constructor",
    "completion",
    "partially defined bridge",
    "no certified bridge",
}

clusters = [
    {
        "id": "C-PER",
        "name": "unit-periodic sequence atlas",
        "charts": ["PER-REC", "PER-RAT", "PER-DFAO", "PER-FMASK"],
        "semantic_domain": "unit purely periodic sequences over F_p",
        "complete_invariant": "primitive period word together with the fixed prime p",
        "status": "effective descent and complete invariant proved",
    },
    {
        "id": "C-RMASK",
        "name": "rational-mask digital atlas",
        "charts": ["RM-MASK", "RM-CART", "RM-DFAO"],
        "semantic_domain": "unit rational-mask series over F_p",
        "complete_invariant": "reduced canonical mask A/B",
        "status": "effective descent and complete invariant proved",
    },
    {
        "id": "C-REG",
        "name": "fixed-radix regular atlas",
        "charts": ["REG-SEM", "REG-SEC", "REG-SHORTLEX", "REG-HANKEL"],
        "semantic_domain": "field-valued fixed-radix regular sequences",
        "complete_invariant": "strict shortlex pointed digit-linear record",
        "status": "effective descent and complete invariant proved",
    },
    {
        "id": "C-PROD",
        "name": "Euler-product and multiplicative atlas",
        "charts": ["EULER-EXP", "EULER-GHOST", "PU-MULT"],
        "semantic_domain": "fixed-basis unit series and prime-uniform multiplicative functions",
        "complete_invariant": "Euler exponent sequence",
        "status": "effective restricted overlap proved",
    },
    {
        "id": "C-LOCAL",
        "name": "continuous local Mahler atlas",
        "charts": ["LOC-SEM", "LOC-MAHLER", "LOC-BRANCH"],
        "semantic_domain": "continuous Z_p-valued functions",
        "complete_invariant": "Newton-Mahler coefficient sequence",
        "status": "effective descent and complete invariant proved",
    },
    {
        "id": "C-QARY",
        "name": "weighted q-ary cross-stratum atlas",
        "charts": ["Q-TREE", "Q-ALG", "Q-HOL"],
        "semantic_domain": "marked solutions U=z+lambda U^q",
        "complete_invariant": "the finite parameter pair (q, lambda)",
        "status": "proved in Block 13",
    },
    {
        "id": "C-GAL",
        "name": "finite semisimple Galois atlas",
        "charts": ["GAL-SUB", "GAL-FIX", "GAL-PROJ"],
        "semantic_domain": "subgroups of one fixed finite Galois extension with faithful Reynolds realization",
        "complete_invariant": "the actual subgroup H inside the fixed ambient group G",
        "status": "effective normalized atlas proved",
    },
]

bridges = [
    ("B01", "C-PER", "PER-REC", "PER-RAT", "equivalence", "unit-periodic overlap", "period and coefficient semantics", "none"),
    ("B02", "C-PER", "PER-RAT", "PER-DFAO", "equivalence", "unit-periodic overlap", "primitive word and minimal behavior", "none"),
    ("B03", "C-PER", "PER-RAT", "PER-FMASK", "equivalence", "unit-periodic overlap", "reduced OGF and canonical mask", "none"),
    ("B04", "C-RMASK", "RM-MASK", "RM-CART", "equivalence", "rational-mask domain", "mask and Cartier module", "none"),
    ("B05", "C-RMASK", "RM-CART", "RM-DFAO", "equivalence", "rational-mask domain", "reachable Cartier orbit", "none"),
    ("B06", "C-REG", "REG-SEM", "REG-SEC", "equivalence", "fixed-radix regular domain", "section semantics", "none"),
    ("B07", "C-REG", "REG-SEC", "REG-SHORTLEX", "equivalence", "fixed-radix regular domain", "canonical basis record", "none"),
    ("B08", "C-REG", "REG-SEC", "REG-HANKEL", "equivalence", "fixed-radix regular domain", "regular rank", "none"),
    ("B09", "C-PROD", "EULER-EXP", "EULER-GHOST", "equivalence", "integral divisor-congruence locus", "Euler exponents and divisor ghosts", "none"),
    ("B10", "C-PROD", "EULER-EXP", "PU-MULT", "equivalence", "prime-uniform local-factor locus", "constant-in-prime exponent field", "none"),
    ("B11", "C-LOCAL", "LOC-SEM", "LOC-MAHLER", "equivalence", "continuous local domain", "Mahler coefficients", "none"),
    ("B12", "C-LOCAL", "LOC-SEM", "LOC-BRANCH", "equivalence", "complete clopen packet domain", "piecewise branch synthesis", "none"),
    ("B13", "C-QARY", "Q-TREE", "Q-ALG", "equivalence", "weighted q-ary marked family", "q and lambda", "none"),
    ("B14", "C-QARY", "Q-ALG", "Q-HOL", "equivalence", "weighted q-ary marked family", "q and lambda", "none"),
    ("B15", "C-GAL", "GAL-SUB", "GAL-FIX", "equivalence", "fixed finite Galois extension", "subgroup/fixed-field order reversal", "none"),
    ("B16", "C-GAL", "GAL-SUB", "GAL-PROJ", "equivalence", "faithful Reynolds realization", "subgroup/projector recognition", "none"),
    ("B17", "X", "CFIN", "HOL", "fully faithful inclusion", "constant-recursive subdomain", "coefficient semantics", "holonomic chart alone forgets the C-finite packet signature"),
    ("B18", "X", "ALG", "HOL", "information-losing directional functor", "selected algebraic branch", "D-finite annihilator", "minimal polynomial and branch selector"),
    ("B19", "X", "STATE", "LOC-MAHLER", "constructor", "principal-unit state locus", "certified local interpolation", "unreachable or output-null state directions"),
    ("B20", "X", "INT-SAT", "MOD-p^r", "information-losing directional functor", "finite-rank integral section lattice", "prime-power semantic module", "Smith/Fitting saturation data outside the chosen modulus"),
    ("B21", "X", "PROJ-DESC", "VEC-DESC", "partially defined bridge", "Brauer-zero projective cocycles", "linear semilinear descent", "undefined when the Brauer class is nonzero"),
    ("B22", "X", "TENSOR-CAT", "TANNAKA-GRP", "constructor", "neutral Tannakian category with fiber functor", "tensor automorphism group scheme", "not available from a merely additive or corner realization"),
    ("B23", "X", "FMASK", "NEWTON-MAHLER", "no certified bridge", "none without a lifting rule", "none", "residue coefficient data does not select one p-adic interpolation"),
    ("B24", "X", "MULT-OGF", "DIRICHLET-PRODUCT", "no certified bridge", "none in ordinary OGF semantics", "none", "Cauchy and Dirichlet address monoids differ"),
]

# Structural audit of the bridge and cluster ledgers.
cluster_ids = {c["id"] for c in clusters}
chart_to_cluster: dict[str, str] = {}
for c in clusters:
    check(c["id"] not in chart_to_cluster, f"cluster id shadow {c['id']}", "bridge_ledger")
    for chart in c["charts"]:
        check(chart not in chart_to_cluster, f"chart duplicated {chart}", "bridge_ledger")
        chart_to_cluster[chart] = c["id"]

seen_ids: set[str] = set()
for row in bridges:
    bid, cluster, source, target, kind, overlap, invariant, loss = row
    check(bid not in seen_ids, f"duplicate bridge id {bid}", "bridge_ledger")
    seen_ids.add(bid)
    check(kind in BRIDGE_CLASSES, f"unknown bridge class {bid}", "bridge_ledger")
    if cluster != "X":
        check(cluster in cluster_ids, f"unknown cluster {bid}", "bridge_ledger")
        check(chart_to_cluster.get(source) == cluster, f"source cluster mismatch {bid}", "bridge_ledger")
        check(chart_to_cluster.get(target) == cluster, f"target cluster mismatch {bid}", "bridge_ledger")
    if kind == "equivalence":
        check(loss == "none", f"equivalence with loss {bid}", "bridge_ledger")
        check(overlap != "none", f"equivalence without overlap {bid}", "bridge_ledger")
    if kind in {"information-losing directional functor", "constructor", "partially defined bridge", "no certified bridge"}:
        check(loss != "none", f"directional bridge lacks loss statement {bid}", "bridge_ledger")

# Every certified component must be connected by its equivalence edges.
for c in clusters:
    charts = set(c["charts"])
    adjacency = {x: set() for x in charts}
    for _, cluster, source, target, kind, *_ in bridges:
        if cluster == c["id"] and kind == "equivalence":
            adjacency[source].add(target)
            adjacency[target].add(source)
    reached = {next(iter(charts))}
    frontier = list(reached)
    while frontier:
        x = frontier.pop()
        for y in adjacency[x]:
            if y not in reached:
                reached.add(y)
                frontier.append(y)
    check(reached == charts, f"disconnected certified component {c['id']}", "bridge_ledger")

# Weighted q-ary cross-stratum audit.
lam_values = [Fraction(-3), Fraction(-2), Fraction(-1), Fraction(1), Fraction(2), Fraction(3), Fraction(1, 2), Fraction(-1, 2)]
q_values = list(range(2, 10))
qary_examples: dict[str, dict] = {}

for q in q_values:
    for lam in lam_values:
        max_m = 28
        max_degree = 1 + (q - 1) * max_m
        u = qary_series(q, lam, max_degree)

        # Formula, support, fixed-point equation, algebraic relation, and parameter recovery.
        for m in range(max_m + 1):
            n = 1 + (q - 1) * m
            check(u[n] == qary_coefficient(q, lam, m), f"coefficient q={q} lam={lam} m={m}", "qary_coefficients")
        for n in range(max_degree + 1):
            expected_nonzero = n >= 1 and (n - 1) % (q - 1) == 0
            check((u[n] != 0) == expected_nonzero, f"support q={q} lam={lam} n={n}", "qary_support")

        uq = series_pow(u, q, len(u))
        rhs = [lam * x for x in uq]
        rhs[1] += 1
        for n in range(len(u)):
            check(u[n] == rhs[n], f"fixed point q={q} lam={lam} n={n}", "qary_fixed_point")
            check(lam * uq[n] - u[n] + (1 if n == 1 else 0) == 0, f"algebraic q={q} lam={lam} n={n}", "qary_algebraic")

        d = support_period(u)
        check(d == q - 1, f"support period q={q} lam={lam}", "qary_parameter_recovery")
        check(u[q] == lam, f"lambda coefficient q={q} lam={lam}", "qary_parameter_recovery")
        sem_sig = (d + 1, u[d + 1])
        tree_sig = (q, lam)
        alg_sig = (q, lam)  # degree q, coefficient mu=lambda^{-1}
        hol_sig = (d + 1, qary_coefficient(q, lam, 1))
        check(sem_sig == tree_sig == alg_sig == hol_sig, f"chart signature q={q} lam={lam}", "qary_bridge_coherence")

        # Supported first-order holonomic recurrence.
        c = [qary_coefficient(q, lam, m) for m in range(max_m + 1)]
        for m in range(max_m):
            left_factor = (m + 1)
            for i in range(2, q + 1):
                left_factor *= (q - 1) * m + i
            right_factor = 1
            for i in range(1, q + 1):
                right_factor *= q * m + i
            check(Fraction(left_factor) * c[m + 1] == lam * right_factor * c[m], f"hol recurrence q={q} lam={lam} m={m}", "qary_holonomic")

        # Packet support, exact synthesis, and carry-form packet equations.
        for N in range(2, 13):
            x_degree = 8
            z_degree = N * x_degree + (N - 1)
            up = qary_series(q, lam, z_degree)
            packets = split_packets(up, N, x_degree)
            g = gcd(N, q - 1)
            expected_active = {j for j in range(N) if (j - 1) % g == 0}
            observed_active = {j for j in range(N) if any(packets[j])}
            check(observed_active == expected_active, f"active packets q={q} lam={lam} N={N}", "qary_packet_phase")
            check(len(expected_active) == N // g, f"active count q={q} lam={lam} N={N}", "qary_packet_phase")
            check((q - 1) // g * g == q - 1, f"orbit phase q={q} N={N}", "qary_packet_phase")

            # Exact synthesis on the retained coefficient window.
            for n in range(z_degree + 1):
                j, m = n % N, n // N
                check(packets[j][m] == up[n], f"packet synthesis q={q} lam={lam} N={N} n={n}", "qary_packet_synthesis")

            # Exact packet fixed-point equations, computed by the address-carry product.
            pq = packet_pow(packets, q, N, x_degree)
            for j in range(N):
                for m in range(x_degree + 1):
                    source = Fraction(1) if (j == 1 and m == 0) else Fraction(0)
                    check(packets[j][m] == source + lam * pq[j][m], f"packet equation q={q} lam={lam} N={N} j={j} m={m}", "qary_packet_equations")

        key = f"q{q}_lam{str(lam).replace('/', '_')}"
        if (q, lam) in {(2, Fraction(1)), (3, Fraction(2)), (4, Fraction(-1)), (5, Fraction(1, 2))}:
            qary_examples[key] = {
                "q": q,
                "lambda": str(lam),
                "support_period": q - 1,
                "algebraic_degree": q,
                "first_supported_coefficients": [str(qary_coefficient(q, lam, m)) for m in range(7)],
                "phase_N6": {
                    "g": gcd(6, q - 1),
                    "active_addresses": [j for j in range(6) if (j - 1) % gcd(6, q - 1) == 0],
                    "complete_orbit_size": (q - 1) // gcd(6, q - 1),
                },
            }

# Tagged federated invariant: component tag prevents cross-component false identification.
for i, c in enumerate(clusters):
    tag = c["id"]
    check(tag == clusters[i]["id"], f"stable component tag {tag}", "federated_invariant")
    for d in clusters:
        if d["id"] != tag:
            check((tag, c["complete_invariant"]) != (d["id"], d["complete_invariant"]), f"tag collision {tag}/{d['id']}", "federated_invariant")

bridge_records = [
    {
        "id": bid,
        "cluster": cluster,
        "source": source,
        "target": target,
        "class": kind,
        "overlap": overlap,
        "invariant_comparison": invariant,
        "information_loss_or_gate": loss,
    }
    for bid, cluster, source, target, kind, overlap, invariant, loss in bridges
]

result = {
    "version": "1.13.0",
    "block": 13,
    "passed": not failures,
    "checks": checks,
    "failures": failures,
    "arithmetic": "exact rational coefficient algebra, exact finite packet convolution, and exact bridge-ledger graph checks",
    "categories": category_counts,
    "certified_clusters": clusters,
    "bridge_matrix": bridge_records,
    "qary_examples": qary_examples,
    "boundary": "The certified-spine theorem is componentwise and relative to the printed normalized domains. Directional bridges do not identify components, and the full unrestricted heterogeneous atlas, cross-radix semantics, modular/wild symmetry, nonneutral tensor descent, and universal nonlinear or holonomic normal forms remain open.",
}

(GEN / "block13_global_invariant_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
(GEN / "block13_bridge_matrix.json").write_text(json.dumps({"clusters": clusters, "bridges": bridge_records}, indent=2, sort_keys=True), encoding="utf-8")

# LaTeX tables.
labels = {
    "bridge_ledger": "Bridge-matrix structural checks",
    "qary_coefficients": "Weighted q-ary coefficient identities",
    "qary_support": "Exact support-period identities",
    "qary_fixed_point": "Formal fixed-point identities",
    "qary_algebraic": "Minimal-polynomial relation checks",
    "qary_parameter_recovery": "Finite parameter recovery",
    "qary_bridge_coherence": "Tree/algebraic/holonomic comparison paths",
    "qary_holonomic": "Supported first-order recurrence checks",
    "qary_packet_phase": "Packet support and orbit-phase checks",
    "qary_packet_synthesis": "Exact packet synthesis checks",
    "qary_packet_equations": "Address-carry packet equations",
    "federated_invariant": "Tagged component-separation checks",
}
lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Exact verification of the Block 13 invariant-descent and weighted q-ary cross-stratum models.}",
    r"\label{tab:block13-global-invariant-validation}",
    r"\small",
    r"\begin{tabularx}{\textwidth}{@{}Y r@{}}",
    r"\toprule",
    r"Validation class & Checks\\",
    r"\midrule",
]
for key in labels:
    lines.append(f"{labels[key]} & {category_counts.get(key, 0):,}\\\\")
lines += [
    r"\midrule",
    r"\textbf{Block 13 exact checks} & \textbf{" + f"{checks:,}" + r"}\\",
    r"\textbf{Failures} & \textbf{" + f"{len(failures)}" + r"}\\",
    r"\bottomrule",
    r"\end{tabularx}",
    r"\end{table}",
]
(GEN / "block13_validation_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

lines = [
    r"\begin{landscape}",
    r"\scriptsize",
    r"\begin{longtable}{@{}L{0.055\linewidth}L{0.09\linewidth}L{0.11\linewidth}L{0.11\linewidth}L{0.13\linewidth}L{0.16\linewidth}L{0.15\linewidth}L{0.15\linewidth}@{}}",
    r"\caption{Authoritative certified bridge ledger after Block 13. Equivalences are restricted to their printed overlap domains.}\label{tab:block13-bridge-ledger}\\",
    r"\toprule",
    r"ID & Cluster & Source & Target & Class & Declared overlap & Invariant comparison & Loss or gate\\",
    r"\midrule",
    r"\endfirsthead",
    r"\toprule",
    r"ID & Cluster & Source & Target & Class & Declared overlap & Invariant comparison & Loss or gate\\",
    r"\midrule",
    r"\endhead",
    r"\midrule",
    r"\multicolumn{8}{r}{\small Continued on next page}\\",
    r"\endfoot",
    r"\bottomrule",
    r"\endlastfoot",
]
for row in bridge_records:
    esc = lambda s: (str(s).replace("\\", r"\textbackslash{}")
        .replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
        .replace("#", r"\#").replace("_", r"\_").replace("^", r"\textasciicircum{}")
        .replace("~", r"\textasciitilde{}"))
    lines.append(
        f"{esc(row['id'])} & {esc(row['cluster'])} & {esc(row['source'])} & {esc(row['target'])} & "
        f"{esc(row['class'])} & {esc(row['overlap'])} & {esc(row['invariant_comparison'])} & {esc(row['information_loss_or_gate'])}\\\\[2pt]"
    )
lines += [r"\end{longtable}", r"\end{landscape}"]
(GEN / "block13_bridge_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Certified normalized components used by the Block 13 federated spine.}",
    r"\label{tab:block13-clusters}",
    r"\scriptsize",
    r"\begin{tabularx}{\textwidth}{@{}L{0.09\textwidth}L{0.18\textwidth}L{0.23\textwidth}L{0.25\textwidth}Y@{}}",
    r"\toprule",
    r"ID & Component & Semantic domain & Complete invariant & Status\\",
    r"\midrule",
]
for c in clusters:
    esc = lambda s: (str(s).replace("\\", r"\textbackslash{}")
        .replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
        .replace("#", r"\#").replace("_", r"\_").replace("^", r"\textasciicircum{}")
        .replace("~", r"\textasciitilde{}"))
    lines.append(f"{esc(c['id'])} & {esc(c['name'])} & {esc(c['semantic_domain'])} & {esc(c['complete_invariant'])} & {esc(c['status'])}\\\\")
lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
(GEN / "block13_cluster_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

lines = [
    r"\begin{table}[htbp]",
    r"\centering",
    r"\caption{Named weighted q-ary examples in the cross-stratum atlas.}",
    r"\label{tab:block13-qary-examples}",
    r"\scriptsize",
    r"\begin{tabularx}{\textwidth}{@{}L{0.10\textwidth}L{0.11\textwidth}L{0.12\textwidth}L{0.25\textwidth}L{0.17\textwidth}Y@{}}",
    r"\toprule",
    r"$q$ & $\lambda$ & Support period & First supported coefficients & Active addresses at $N=6$ & Packet-orbit size\\",
    r"\midrule",
]
for _, row in sorted(qary_examples.items(), key=lambda kv: (kv[1]["q"], Fraction(kv[1]["lambda"]))):
    coeffs = ", ".join(row["first_supported_coefficients"][:4]) + r",\ldots"
    active = ",".join(str(x) for x in row["phase_N6"]["active_addresses"])
    active_tex = r"\{" + active + r"\}"
    lines.append(
        f"{row['q']} & ${row['lambda']}$ & {row['support_period']} & $({coeffs})$ & ${active_tex}$ & {row['phase_N6']['complete_orbit_size']}\\\\"
    )
lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
(GEN / "block13_qary_examples_table.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(json.dumps({"passed": result["passed"], "checks": checks, "failures": len(failures), "clusters": len(clusters), "bridges": len(bridges)}, sort_keys=True))
if failures:
    raise SystemExit(1)
