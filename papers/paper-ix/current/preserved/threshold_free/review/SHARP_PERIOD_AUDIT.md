# Independent audit of sharp periods and dyadic interpolation

Audit date: 2026-10-06. Primary verdict: **proved as written**.

For the actual normalized rank-four reciprocal lanes,
\[
C_j(n)=(4n)![t^{4n}]\left(j!\sum_{q\ge0}\frac{t^{4q}}{(4q+j)!}\right)^{-1},
\]
the audited conclusion is
\[
v_2(C_j(n+H)-C_j(n))=v_2(H)+b_j,
\qquad b=(1,1,4,2),
\]
for every natural \(n\) and positive natural \(H\). It holds starting at row zero. The continuous extensions satisfy the same law for all distinct \(x,y\in\mathbb Z_2\), and \(C_j\) bijects \(\mathbb Z_2\) onto \(1+2^{b_j}\mathbb Z_2\). The later rank-two, rank-eight, and all-rank lower-half claims also pass the checks below. No universal exact law for all upper lanes is inferred.

## Reviewed revisions and dependencies

Reviewed `sharp_periods/SHARP_PERIOD_LEMMA.md`, including the continuous residue-distribution and all-rank additions. Its SHA-256 was `a6cf023d84a37bce57f70ead3096729add33fb7fa23bc936a45ede7abaf7ed7b`. The earlier rank-four-only text had hash `2020c562087e50dab27d837bb19e9d49bc4b0154eafdf77e51fa4f7e433b606e`.

The essential universal input is the threshold-free theorem in `combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md`: \(a_k=\Delta_1^kC(0)\in2^k\mathbb Z_2\). That theorem was independently audited in `GLOBAL_PROOF_AUDIT.md`; its all-dyadic-order appendix supplies the input for ranks beyond four. This sharpness proof does not prove that input by numerical testing.

The dependency graph is:

1. Exact reciprocal definition → exact low Newton coefficients.
2. Global threshold-free theorem + complete low-order checks → bounds on every higher Newton coefficient.
3. Newton inversion + Vandermonde + binomial valuation bound → exact integer first-difference law.
4. Uniform Newton convergence + density → continuous exact law on \(\mathbb Z_2\).
5. Finite residue bijections + completeness → bijection onto the prescribed ball.
6. Multiplication by \(j!\) + exact valuation law → sharp row periods and complete residue distribution.

The only finite leaves in the rank-four proof are the explicitly listed rational coefficient calculations. Their sufficiency follows from a proved bound on all omitted orders.

## General sharpness lemma

Let \(C:\mathbb N\to\mathbb Z_2\), \(a_k=\Delta_1^kC(0)\), and suppose
\[
v_2(a_1)=b,\qquad
v_2(a_k)\ge b+1+\lfloor\log_2k\rfloor\quad(k\ge2).
\]
Newton's finite identity reconstructs each natural value exactly:
\[
C(M)=\sum_{k=0}^{M}a_k\binom Mk.
\]
For \(n\ge0,H>0\), pad the two finite sums through \(n+H\). Vandermonde gives
\[
\binom{n+H}k-\binom nk
=\sum_{i=1}^k\binom Hi\binom n{k-i}.
\]
For \(1\le i\le H\),
\[
i\binom Hi=H\binom{H-1}{i-1}
\quad\Longrightarrow\quad
v_2\binom Hi\ge v_2(H)-v_2(i)
\ge v_2(H)-\lfloor\log_2k\rfloor.
\]
Terms with \(i>H\) vanish. Thus every \(k\ge2\) Newton summand in the difference lies in \(2^{b+v_2(H)+1}\mathbb Z_2\), while the \(k=1\) term is \(Ha_1\), of valuation exactly \(b+v_2(H)\). The unique leading term cannot cancel against a sum of strictly higher valuation. This proves the exact law with all stated quantifiers. The constant term cancels, and no infinite-series assertion is used for natural inputs.

## Independent rank-four coefficient reconstruction

The coefficients were recomputed first in the ordinary variable \(z=t^4\), directly from the definition. Set
\[
A_q=\frac{j!}{(4q+j)!},\qquad
B_0=1,\quad B_n=-\sum_{q=1}^n A_qB_{n-q},\qquad
C_j(n)=(4n)!B_n.
\]
This avoids copying the manuscript's factorial-scaled recurrence. Then
\(a_j(k)=\sum_{r=0}^k(-1)^{k-r}\binom kr C_j(r)\).
All fourteen listed coefficients and their exact valuations match:

| \(j\) | \(k\) | Independently reconstructed \(a_j(k)\) | \(v_2\) |
|---|---|---|---|
| 0 | 1 | −2 | 1 |
| 0 | 2 | 72 | 3 |
| 1 | 1 | −6/5 | 1 |
| 1 | 2 | 184/45 | 3 |
| 2 | 1 | −16/15 | 4 |
| 2 | 2 | 64/45 | 6 |
| 2 | 3 | −14848/1365 | 9 |
| 2 | 4 | 71426048/69615 | 13 |
| 2 | 5 | −25509691392/85085 | 16 |
| 2 | 6 | 149113198870528/765765 | 22 |
| 3 | 1 | −36/35 | 2 |
| 3 | 2 | 256/231 | 8 |
| 3 | 3 | −65792/35035 | 8 |
| 3 | 4 | 161644544/4849845 | 15 |

The generic bound \(v_2(a_k)\ge k\) implies the needed stronger bound exactly when
\(q(k):=k-\lfloor\log_2k\rfloor\ge b+1\). For \(k\ge1\), \(q(k+1)-q(k)\) is zero at a power-of-two transition and one otherwise. Hence \(q\) is globally nondecreasing. This proves the complete cutoff reduction, without an extrapolation from finitely many tested orders:

| \(b\) | All exceptional orders \(k\ge2\) | Generic bound valid for every |
|---|---|---|
| 1 | 2 | \(k\ge3\) |
| 2 | 2,3,4 | \(k\ge5\) |
| 3 | 2,3,4,5 | \(k\ge6\) |
| 4 | 2,3,4,5,6 | \(k\ge7\) |

The coefficient table checks every exceptional order required for rank four. No omitted coefficient is needed.

## Continuous interpolation, isometry, and surjectivity

For each fixed \(k\), the rational polynomial \(\binom xk\) is continuous on \(\mathbb Z_2\) and integral there: approximate \(x\) by nonnegative integers, where its values are integers, and use that \(\mathbb Z_2\) is closed. Since \(v_2(a_k)\ge k\),
\[
\widehat C(x)=\sum_{k\ge0}a_k\binom xk
\]
converges uniformly on \(\mathbb Z_2\), defines a continuous integral-valued function, and agrees with \(C\) on the naturals. More generally, the sharp lemma's own lower bound tends to infinity and suffices for uniform convergence.

For distinct \(x,y\), let \(s=v_2(x-y)\). Choose natural approximations \(n_r\to x\), \(m_r\to y\) accurate beyond \(2^{s+1}\). Then \(v_2(n_r-m_r)=s\) eventually. The integer law gives
\(\widehat C(n_r)-\widehat C(m_r)\in2^{b+s}\mathbb Z_2^\times\). This set is closed, so continuity gives
\[
v_2(\widehat C(x)-\widehat C(y))=b+v_2(x-y).
\]
In particular \(\widehat C(0)=1\), and
\[
T(x)=\frac{\widehat C(x)-1}{2^b}
\]
is an isometry \(\mathbb Z_2\to\mathbb Z_2\). The map induced by \(T\) modulo \(2^r\) is well-defined and injective by that exact law. Its domain and codomain both have \(2^r\) elements, so it is bijective. These quotient bijections are compatible under reduction; their inverse images of any target form a compatible sequence. Completeness gives its unique lift in \(\mathbb Z_2\). Thus \(T\) is onto, and \(\widehat C\) is a continuous bijection onto \(1+2^b\mathbb Z_2\).

This is a purely continuous argument. Neither it nor this audit asserts global analyticity of the interpolation. Multiplying by \(j!\) transports the image ball to \(j!+2^{B_j}\mathbb Z_2\), where \(B_j=b_j+v_2(j!)\); the odd unit in \(j!\) does not alter that ball.

## Exact periods and residue counts

For rank four \(B=(1,1,5,3)\). The exact law implies that a positive natural displacement \(H\) is a period modulo \(2^r\) at every row precisely when \(v_2(H)+B_j\ge r\). The same condition is necessary even for congruence at one row. Therefore the least positive row period is
\[
P_j(r)=2^{\max(0,r-B_j)}.
\]
When \(r>B_j\), the first \(P_j(r)\) rows correspond to all inputs modulo \(2^{r-B_j}\), and the isometry induces a bijection onto the \(P_j(r)\) permissible residues in \(j!+2^{B_j}\mathbb Z/2^r\mathbb Z\). When \(r\le B_j\), the values are constant modulo \(2^r\) and the least period is one. The period in allowed Euler subscripts is the section order times the row period.

## All-rank lower-half extension

For \(N=2^a\ge4\), \(0\le j<N/2\), and \(1\le i\le j\),
\(v_2(N/i)\ge2\). Hence the exact source satisfies
\(g(1)\equiv1\pmod4\), \(g(2)\equiv1\pmod8\), and \(g(1)^2\equiv1\pmod8\). The reciprocal recurrence gives
\[
a_1=-g(1)-1,\qquad
a_2=\binom{2N}N g(1)^2-g(2)+2g(1)+1.
\]
The first has valuation exactly one. To check the central-binomial input, put
\[
B_a=\binom{2^{a+1}}{2^a}
=2\prod_{k=1}^{2^a-1}(1+2^a/k).
\]
Splitting the product into even and odd \(k\) gives \(B_a=B_{a-1}U_a\), where \(U_a\equiv1\pmod4\) for \(a\ge2\). The base \(B_1=6\) is divisible by two; inductively this remains true, so \(B_a\equiv B_{a-1}\pmod8\). Therefore \(B_a\equiv6\pmod8\) for every \(a\ge1\). The expression for \(a_2\) is thus zero modulo eight. The generic bound handles all \(k\ge3\), proving the exact law with \(b=1\) for every asserted lower-half lane. The same calculation directly covers \(N=2,j=0\), whose source is constant.

This is a symbolic proof for an unbounded family. The finite central-binomial checks in the JSON are supplementary, not the justification of the universal congruence. The statement does not include \(N=1\), for which the raw reciprocal coefficients \((-1)^n\) are not an isometry after scaling.

## Rank-two and rank-eight certificates

Reviewed `verify_all_rank_extensions.py` and `all_rank_extensions_verified.json`, hashes respectively:

* `f5efceb52dc589700ead328e2a17cfe55beb20ff40c75bddc4a4148c2e4be685`;
* `a0e5c0c0dcaa3389b2358e9cb19c67b21b7ad8ddf7f226c437cb52a44f322906`.

The code uses exact `Fraction` arithmetic and the correct source \(1/\binom{Nq+j}j\). Its `needed_orders` routine is exhaustive because \(q(k)\) is nondecreasing, as proved above. Each coefficient in the saved record was independently recomputed from the ordinary-series inverse \(A_q=j!/(Nq+j)!\), then scaled by \((Nn)!\). All 33 saved exact coefficients and valuations match, and the listed orders equal the complete exceptional-order sets. The normalized and unnormalized shifts are:

| Rank | Normalized shifts, in increasing lane order | Shifts after multiplication by \(j!\) |
|---|---|---|
| 2 | 1,2 | 1,2 |
| 4 | 1,1,4,2 | 1,1,5,3 |
| 8 | 1,1,1,1,4,3,2,2 | 1,1,2,2,7,6,6,6 |

For the upper rank-eight lanes the higher checked valuations are respectively:

| Lane | Checked orders \(k\ge2\) | Independently matched valuations |
|---|---|---|
| \(N=8,j=4\) | 2,3,4,5,6 | 6,9,13,16,20 |
| \(N=8,j=5\) | 2,3,4,5 | 6,10,13,17 |
| \(N=8,j=6\) | 2,3,4 | 6,8,13 |
| \(N=8,j=7\) | 2,3,4 | 11,8,15 |

Each meets the criterion, and the proved cutoff reduction handles every omitted order. Thus the complete exact laws, periods, and continuous ball bijections at ranks two and eight follow; this is more than bounded numerical evidence.

The three preserved counterchecks also match independently:

| \(N,j,n,H\) | \(v_2(C(1)-C(0))\) | Actual \(v_2(C(2)-C(0))\) | Naive prediction |
|---|---:|---:|---:|
| 16,9,0,2 | 5 | 7 | 6 |
| 32,18,0,2 | 6 | 6 | 7 |
| 32,19,0,2 | 5 | 7 | 6 |

These refute the proposed universal upper-lane exact law while leaving the audited lower bound intact.

## Obligation matrix and computation scope

| Obligation | Status |
|---|---|
| Correct exact reciprocal normalization | Passed |
| General Newton sharpness lemma | Passed |
| Every low coefficient required at rank four | Passed, independent exact calculation |
| All omitted higher orders | Passed, monotonic cutoff argument |
| Row zero and arbitrary positive integer steps | Passed |
| Continuous interpolation on \(\mathbb Z_2\) | Passed, uniform convergence |
| Exact law for all distinct dyadic pairs | Passed, continuity and closed unit cosets |
| Surjectivity onto stated ball | Passed, compatible finite quotient bijections |
| Sharp periods and full allowed residue distribution | Passed |
| Uniform lower-half family | Passed, symbolic central-binomial argument |
| Complete rank-two and rank-eight certificate coverage | Passed, independent exact reconstruction |
| General upper-lane isometry | Out of scope; explicitly false in listed examples |
| Global analyticity or Lean formal verification | Not claimed or established |

Computation contract: exact rational coefficients, no numerical tolerance, no random sampling, and no inference from a finite row test to an infinite assertion. The independent low-coefficient run used Python 3.12.14, retained every coefficient needed for each claimed order, and read the saved JSON without changing it. A separate illustrative rank-four check verified the exact first-difference law for all pairs with \(0\le n<n+H\le24\). That sample is not used in the proof. The universal theorem follows from the global divisibility theorem, the displayed cutoff proof, and the finite exact coefficient certificates.

## Remaining gap and safe conclusion

No remaining gap was found in the reviewed claims. The continuous scaled maps are isometries and bijections onto the stated dyadic balls by the argument above. The upper-lane exceptions must remain part of the scope boundary; the all-rank global lower bound alone does not supply their missing sharpness criterion.
