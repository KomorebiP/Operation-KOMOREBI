# Euler congruences pushed beyond the threshold

Date: 2026-10-06. This checkpoint continues the solved Nishibuchi congruence problem and closes the threshold-free higher-difference conjecture proposed in the conversation.

The exact definitions are
\[
G_{N,j}(t)=j!\sum_{n\ge0}\frac{t^{Nn}}{(Nn+j)!},
\qquad
G_{N,j}(t)^{-1}=\sum_{n\ge0}C_{N,j}(n)\frac{t^{Nn}}{(Nn)!},
\qquad
E_{Nn}^{(N,j)}=j!C_{N,j}(n).
\]
Write \(\Delta_H f(n)=f(n+H)-f(n)\), \(v_p(0)=+\infty\), and \(C_j=C_{4,j}\). Every claim below uses the reciprocal of this actual generating series. Rows are indexed by \(n\); an advance of \(H\) rows advances the Euler subscript by \(NH\).

The original completed estimate was \(v_2(\Delta_H^k C_j(n))\ge\min(k,n)\). The new results hold at every row, including \(n=0\) and \(k>n\).

## Universal theorem at every dyadic section size

For \(N=2^a\), \(a\ge0\), \(0\le j<N\), \(n\ge0\), \(k\ge1\), and positive integer steps \(H_1,\ldots,H_k\),
\[
\boxed{
v_2\!\left(\Delta_{H_1}\cdots\Delta_{H_k}C_{N,j}(n)\right)
\ge k+\sum_{\nu=1}^k v_2(H_\nu).
}
\]
The original Euler normalization adds \(v_2(j!)\). A zero step makes the difference zero; order zero is coefficient integrality.

The mechanism is a reciprocal induction in the integral Hurwitz-series lattice. With \(D=d/dt\) and \(L_\lambda=(D^N-\lambda)/2\), the exact product identity is
\[
L_{\lambda+\mu}(AB)
=(L_\lambda A)B+A(L_\mu B)
+\sum_{i=1}^{N-1}\frac{\binom Ni}{2}(D^iA)(D^{N-i}B).
\]
The interior coefficients are integral. In the full commuting-operator expansion applied to \(GG^{-1}=1\), the unique term of inverse order \(k\) is \(G L_{-1}^kG^{-1}\). Every other term has lower inverse order, so induction proves its integrality at every coefficient degree. This is the step that removes the old row threshold. The source hypothesis follows directly from
\[
g_{N,j}(n)=\prod_{i=1}^j(1+(N/i)n)^{-1},
\qquad
\Delta_1^r(1+sn)^{-1}
=\frac{(-s)^r r!}{\prod_{h=0}^r(1+s(n+h))},
\quad s\in2\mathbb Z_2.
\]
The dyadic identity \(L_1=L_{-1}-1\) returns ordinary differences. Finite step-operator expansions give the precision contributed by each step.

Full proof: [combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md](combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md). Independent alternative: [measure/THRESHOLD_FREE_UMBRAL_INVERSE.md](measure/THRESHOLD_FREE_UMBRAL_INVERSE.md). Independent audit: [review/GLOBAL_PROOF_AUDIT.md](review/GLOBAL_PROOF_AUDIT.md).

For every prime-power section size \(N=p^a\), the corresponding theorem is valid for the sign-twisted sequence \((-1)^nC_{N,j}(n)\). Equivalently, put \(T_H=S^H-(-1)^H\), where \(Sf(n)=f(n+1)\). Then
\[
v_p\!\left(T_{H_1}\cdots T_{H_k}E^{(N,j)}(n)\right)
\ge v_p(j!)+\sum_{\nu=1}^k(1+v_p(H_\nu)),
\qquad E^{(N,j)}(n)=E_{Nn}^{(N,j)}.
\]
For odd primes the sign twist is necessary: already \(C_{N,0}(0)=1\), \(C_{N,0}(1)=-1\) gives the ordinary first difference \(-2\).

Proof and audit: [GENERAL_PRIME_POWER_TRANSFER.md](GENERAL_PRIME_POWER_TRANSFER.md), [review/PRIME_POWER_AUDIT.md](review/PRIME_POWER_AUDIT.md).

## Factorial gain for all four addresses

For \(n\ge0\), \(k\ge1\), and positive steps,
\[
\boxed{
v_2\!\left(\Delta_{H_1}\cdots\Delta_{H_k}C_j(n)\right)
\ge k+v_2(k!)+\sum_\nu v_2(H_\nu)+\beta_j,
\qquad
\beta=(0,0,3,1).
}
\]
In the original Euler normalization the address offsets are \((0,0,4,2)\).

This stronger result uses a divided-power algebra, rather than assuming a factorial version of the generic reciprocal induction. Its arithmetic leaf is the classical Frobenius congruence for ordinary Euler numbers with generating series \(\operatorname{sech}t\). The new transformations to the actual \(N=4\) series are proved explicitly. An elementary central-factorial Bernoulli argument handles address two; tangent and cotangent ratio identities transfer the estimates to addresses one and three.

Full proof, including the exact statements below: [measure/factorial_route.md](measure/factorial_route.md). Independent strengthened address-two check: [combinatorial/factorial_j2/INDEPENDENT_STRENGTHENED_J2_AUDIT.md](combinatorial/factorial_j2/INDEPENDENT_STRENGTHENED_J2_AUDIT.md). Final independent review: [review/FACTORIAL_ROUTE_AUDIT.md](review/FACTORIAL_ROUTE_AUDIT.md).

### Exact valuations for addresses zero and one

For \(j=0,1\), every \(n\ge0\), \(k\ge1\), and \(H>0\),
\[
\boxed{
v_2(\Delta_H^k C_j(n))
=k+v_2(k!)+k\,v_2(H).
}
\]
There is no omitted starting row or high-order exception.

For mixed steps put \(q=\#\{\nu:H_\nu\text{ is even}\}\) and
\[
V=k+v_2(k!)+\sum_\nu v_2(H_\nu).
\]
The normalized difference is odd precisely when \(k\) is odd or \(q\) is even. Thus its valuation equals \(V\) in those cases. If \(k\) is even and \(q\) is odd, the leading term cancels and the valuation is at least \(V+1\); the exact remaining depth is not supplied by this parity theorem.

For example,
\[
\Delta_1\Delta_2 C_0(0)=-33728,\qquad v_2=6,
\]
where the basic mixed bound is \(4\). This refutes an unrestricted exact mixed-step formula.

### Stronger address-two filtration and an infinite sharp family

For every positive order and positive mixed steps,
\[
\boxed{
v_2\!\left(\Delta_{H_1}\cdots\Delta_{H_k}C_2(n)\right)
\ge
2k+v_2(k!)+\lfloor k/2\rfloor+\sum_\nu v_2(H_\nu).
}
\]
Take the maximum of this bound and the preceding bound with \(\beta_2=3\). Neither is a claim about a finite tested range.

At every power-of-two order, exact mixed-step valuations hold:
\[
v_2\!\left(\Delta_{H_1}\cdots\Delta_{H_k}C_2(n)\right)
=V_2(k)+\sum_\nu v_2(H_\nu),
\]
where
\[
V_2(1)=4,\qquad V_2(2)=6,\qquad
V_2(k)=2k+v_2(k!)+k/2
\quad(k=2^r,\ r\ge2).
\]
These equalities hold for every base row and every positive step list. They prove sharpness at unbounded orders, rather than just at finitely many examples.

For other orders, a complete exact address-two valuation formula remains open in this checkpoint. A naive mixed-step extension of the observed Newton pattern is false; an exact witness is retained in the computation frontier report. No exact higher-order formula for address three is asserted.

## Sharp periods and analytic structure

All four normalized \(N=4\) sequences obey
\[
v_2(C_j(n+H)-C_j(n))=v_2(H)+b_j,
\qquad b=(1,1,4,2).
\]
The original Euler shifts are \(B=b+(v_2(j!))_{j=0}^3=(1,1,5,3)\). Therefore the least positive row period modulo \(2^r\) is
\[
\boxed{P_j(r)=2^{\max(0,r-B_j)}}.
\]
The corresponding advance in the Euler subscript is \(4P_j(r)\). The proof applies starting at row zero.

| Address \(j\) | Normalized shift \(b_j\) | Euler shift \(B_j\) | Least row period modulo \(2^r\) |
|---|---:|---:|---|
| 0 | 1 | 1 | \(2^{\max(0,r-1)}\) |
| 1 | 1 | 1 | \(2^{\max(0,r-1)}\) |
| 2 | 4 | 5 | \(2^{\max(0,r-5)}\) |
| 3 | 2 | 3 | \(2^{\max(0,r-3)}\) |

The continuous interpolations are scaled isometries and bijections:
\[
C_j:\mathbb Z_2\longrightarrow1+2^{b_j}\mathbb Z_2,
\qquad
E^{(4,j)}:\mathbb Z_2\longrightarrow j!+2^{B_j}\mathbb Z_2.
\]
Within a least row period, every permissible residue modulo \(2^r\) occurs exactly once.

The factorial theorem also yields ordinary analytic Taylor series. At every center in \(\mathbb Z_2\), the exact Taylor radii are
\[
R_0=R_1=2,\qquad R_2=2^{5/2}.
\]
For addresses zero and one, the degree-\(d\) Taylor coefficient has valuation exactly \(d\). For address two it has valuation at least \(2d+\lfloor d/2\rfloor\), with equality along the unbounded power-of-two degree family \(d\ge4\); this makes the radius exact. Address three has a proved radius at least \(2\), and its exact radius is not claimed.

The sharp first-difference laws are also proved for every address at \(N=2\) and \(N=8\), and for \(j<N/2\) at every \(N=2^a\ge4\). The same simple distance law is false for some larger upper-half addresses. Full statements and explicit counterexamples: [sharp_periods/PUBLIC_THEOREMS.md](sharp_periods/PUBLIC_THEOREMS.md). Proof and audit: [sharp_periods/SHARP_PERIOD_LEMMA.md](sharp_periods/SHARP_PERIOD_LEMMA.md), [review/SHARP_PERIOD_AUDIT.md](review/SHARP_PERIOD_AUDIT.md).

## Evidence, provenance, and remaining boundary

The universal conclusions above rest on algebraic proofs. The exact modular computation through row 512 corroborates them with more than 1.8 million bounded difference assertions and 68 independent rational-series cross-checks. Two later bounded audits through row 96 check the strengthened filtration, exact common-step laws, and mixed-step cancellation rule. Precision, tested domains, commands, code hashes, runtime limits, and manifest validators are retained.

Computational records: [computation/COMPUTATION_REPORT.md](computation/COMPUTATION_REPORT.md), [computation/FACTORIAL_FRONTIER_REPORT.md](computation/FACTORIAL_FRONTIER_REPORT.md). The earlier computation report is a historical pre-proof snapshot; its formerly conjectural address-zero/one formulas are now proved by the separately audited argument.

Source check: [SOURCE_CHECK.md](SOURCE_CHECK.md). Program status: [RESEARCH_STATUS.md](RESEARCH_STATUS.md). The root checkpoint manifest records final file hashes; computation manifests separately pin the executed revisions.

The baseline completed manuscript is included at [inputs/Nishibuchi_Conjecture_Completion.pdf](inputs/Nishibuchi_Conjecture_Completion.pdf). After extracting the archive, run python3 verify_checkpoint.py from this directory to verify its pinned bytes and report references. The computation directories contain their own execution commands and manifest validators.

This work closes the threshold-free congruence goal and supplies stronger exact laws. It does not settle the separate dyadic Euler-tail universal simplicity or stationary-discriminant nonvanishing problem. A new Lean compilation has not been performed. No global claim of literature novelty is made.
