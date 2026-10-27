# Beal research, Block 62
## Actual trace products and depth-one conductor exclusion

Version 6.2.0. 20 September 2026.

The next bounded block excludes actual depth-one opposite extensions whose
complete ramification is contained over
\[
S^+=\{43,113,127,197,883,1373,1667\}.
\]
Arbitrary additional primes may divide \(C\) without ramifying in \(\beta\).
**Additional \(\beta\)-ramification is not covered by the exclusion.**

The result uses the actual first Frobenius trace correction to couple the same
global natural class and opposite extension. It does not recycle the higher-depth
assumption that \(29\) and \(491\) must be bad. Both good and bad reduction are
checked at every relevant test prime.

All arithmetic applications retain the explicit inherited Frey-model, toric,
Kummer, endpoint and class-group hypotheses. These are written conditional proofs
with exact computational certificates and a separate arithmetic implementation.
No new Lean compilation or independent mathematical review is claimed. General
depth one, the complete reducible branch, the full signature and Beal remain open.

## 1. A same-representation trace identity

At depth one and a test place of norm \(Q\equiv1\pmod7\), write the actual
Frobenius in the same natural global basis as
\[
F=\begin{pmatrix}a&b\\7c&d\end{pmatrix},\qquad\det F=Q.
\]
Put \(d=1+7D\) and \(\operatorname{tr}_{\mathcal O}F=Q+1+7T\). The exact identity is
\[
bc=T+(Q-1)D+7TD-7D^2.
\]
The retained cocycles are \(\alpha=\bar b\) and \(\beta=\bar c/\bar\chi\).
Consequently, when \(\beta\) is unramified at the test place,
\[
\boxed{\frac{\operatorname{tr}_{\mathcal O}F-Q-1}{7}\bmod7
       =\alpha(F)\beta(F).}
\]
The natural class is unramified at both good places and inherited variable bad
places. Since both local residual coefficient characters are trivial, these
Frobenius values are values of the classes, not arbitrary cocycle representatives.
A global diagonal basis change rescales the factors inversely and preserves
the product.

At a bad place, the exact toric trace makes the product zero. At a good place,
it belongs to the finite set actually attained by the Frey reductions. A good
place need not give zero. The retained matrix \([[-6,1],[-35,1]]\) has determinant
29, trace \(-5\), and product 2 modulo seven; it prevents that shortcut.

See `notes/TRACE_PRODUCT_IDENTITY.md` for the proof, extraction of trace
corrections from the rational quartic, and the separate \(Q\not\equiv1\) control.

## 2. Correctly twisted values, with no artificial zero rows

First suppose all \(\beta\)-ramification lies over
\(S=\{197,883,1373,1667\}\). These inert primes are 1 modulo seven. The inherited
inertia injectivity and split-at-seven condition descend \(\beta\) **as a
\(\chi^{-1}\)-cohomology class**, not as a Tate lattice or Frey representation.

Over \(\mathbb Q(\zeta_7)\), the correctly twisted principal-idele calculation
gives the following rows, with columns in the order \(S\):

| Test prime | Twisted Frobenius row |
|---|---|
| 29 | (4,2,6,1) |
| 43 | (4,3,4,3) |
| 71 | (6,2,0,5) |
| 211 | (2,4,1,5) |
| 239 | (3,3,1,2) |
| 491 | (3,6,1,6) |

Only the 71 row is set to zero at the outset: 71 is actually forced bad at every
depth, and the inherited period obstruction gives full local \(\beta\)-vanishing.
At 29 and 491 the proof permits good reduction. Inert 43 uses the squared
Frobenius for the curve and the factor two for the descended opposite class.

All roots of unity, prime generators, signs and local logarithms are coordinated.
The coefficient symbol \(w\), with \(w^2=5\), is not identified with the base-field
radical. Either coefficient-conjugate trace is permitted independently at each
split test place, an overapproximation of the actual compatibility problem.
See `notes/TWISTED_TRACE_DATA.md`.

## 3. Actual point counts leave one tuple, then exclude it

The counted curve is
\[
z^2=x^6+10Bx^3+12Ax+5B^2.
\]
Every necessary good equation pair is included; each pair's seventh-power
admissibility is checked individually, not transferred from an orbit representative.

| Prime | Admissible good pairs | Full residual target pairs |
|---:|---:|---:|
| 29 | 116 | 8 |
| 43 | 258 | 36 |
| 211 | 6,330 | 210 |
| 239 | 8,126 | 170 |
| 491 | 34,370 | 490 |

There are 49,200 pairs in total. The two new primes, 211 and 239, contribute
14,456; the earlier-prime data are freshly reproduced. Both implementations
perform 1,025 degree-one and 188 degree-two counts. Some split-prime degree-two
counts are unnecessary after failure of the necessary degree-one residual test;
those entries are explicitly null, not claimed calculations.

Let \(\mathcal G_q\) be the possible first rank-two trace corrections. The sets
needed to see the final contradiction are
\[
\begin{aligned}
\mathcal G_{211}&=\{0,6,3\pm w,1\pm3w,3\pm3w\},\\
\mathcal G_{239}&=\{\pm w,1\pm w,2\pm w,3\pm3w\}.
\end{aligned}
\]
In particular \(\mathcal G_{239}\cap\mathbb F_7=\varnothing\).

Normalize the one global natural class by \(a_5=1\). The natural ramification
conditions and justified 71 row leave 119,952 coefficient/character candidates.
The exact sieve is:

| Test | Surviving candidates |
|---|---:|
| Before trace tests | 119,952 |
| 29 | 2,402 |
| 43 | 152 |
| 491 | 9 |
| 211 | 1 |
| 239 | 0 |

The unique tuple before 239 is
\[
\alpha=(0,1,1),\qquad
(s_{197},s_{883},s_{1373},s_{1667})=(0,2,6,2).
\]
At both places over 239, its natural Frobenius value is 3 and its opposite value
is 2. Their product is 6. Bad reduction requires product 0; good reduction
requires a member of \(\mathcal G_{239}\), which contains no rational residue-field
element. Neither alternative works.

Thus depth-one \(\beta\) cannot have all its ramification in \(S\). The proof
includes an explicit hand reduction to the nine intermediate tuples, so the
conclusion is not presented as an unsupported finite search.
See `notes/DEPTH_ONE_EXCLUSION.md`.

## 4. Three low-congruence ramification primes are included explicitly

Depth one may ramify at primes with congruence depth only one. The extension to
\(S^+\) includes 43, 113 and 127 with their correctly twisted columns. Their
natural Kummer rows require ratios \(a_3/a_5=5,4,2\), respectively. Each is
incompatible with the other added primes and with ramification at 197,1373,1667.
Only 883 may accompany it within the stipulated support.

The justified 71 row reduces the added cases to three two-place lines. Exact
trace products at 29 and 491 eliminate each line. No unramified Frobenius test
at 43 is used in the branch where 43 ramifies. Both implementations check all
7,056 extra parameter choices. This proves the announced \(S^+\) exclusion.
See `notes/LOW_CONGRUENCE_EXTENSION.md`.

## 5. Consequences beyond the seven-prime conductor

Put
\[
U=\{97,197,293,491,587,883,1373,1471,1567,1667\},\qquad
V=U\cup\{43,113,127\}.
\]
The six primes of \(U\setminus S\) already fail the actual nodal-period
eligibility test for \(\beta\) at every depth. Consequently
\[
\boxed{n=1\ \Longrightarrow\ \beta\text{ ramifies outside }V.}
\]
If the **complete** high-congruence divisor set satisfies \(H(C)\subseteq U\),
the predecessor gives \(n=1\), and the new supporting prime outside \(V\) must have
\[
v_7(q^{f_q}-1)=1,\qquad v_7(v_q(C))=0,
\]
with both \(\phi\) and \(75A\) seventh-power residues at the supporting place.
**The entire \(H(C)\subseteq U\) case is not eliminated.** Its possible new
low-congruence support remains unbounded.

There is a separate complete geometric-support exclusion. Define
\[
E(C)=\{q\mid C:q\notin\{2,3,5,7\},\ q^{f_q}\equiv1\pmod7,
\ \phi\in(\mathbb F_{q^{f_q}}^\times)^7\}.
\]
Then
\[
\boxed{E(C)\subseteq V\quad\Longrightarrow\quad
\text{no representation in the retained reducible branch}.}
\]
Here is the distinction making this valid. A nontrivial highest diagonal layer
must have geometric eligibility and congruence depth at least two. Within \(V\)
it could therefore use only \(U\), which Block 58 already excludes. Thus \(\eta_n\)
is fully trivial. At \(n\ge2\), the Block 61 local-zero/ratio proof extends
verbatim under full \(\eta_n=1\), and the three newly added low-congruence primes
cannot support \(\beta\). At \(n=1\), the new theorem supplies the contradiction.

This is a statement about the **complete eligible divisor set**, not a bound on
arbitrary support and not a proof of Beal. In the unrestricted nontrivial-diagonal
case, the new outside-\(V\) eligible divisor need not support \(\beta\), and is
not automatically 2549. See `notes/ARITHMETIC_CONSEQUENCES.md`.

## 6. Verification and preserved failures

All six production programs passed before packaging. The independent count and
residue program imports no primary arithmetic, uses another quadratic-field
basis and another curve canonicalization, and checks smoothness at all 49,200
pairs. It extracts corrections from coefficient trace and norm rather than the
primary exact-discriminant calculation. Both sieves agree on all intermediate
sets, not just the final empty result. The independent low-congruence checker
uses only its own separate arithmetic implementation.

The matrix identity additionally has an exhaustive check on 117,649 residual
triples, including 117,306 with nonrational input. It has one executable checker
and its displayed proof, not a claimed independent matrix implementation.

The original Block 61 bytes and named inherited leaves are hash-pinned. The
release verifier regenerates all six JSON outputs in scratch space and requires
rejection of altered point counts, twisted data, survivor claims, low-support data
and payload bytes. Final integrity and fresh-extracted replay records are external
to the immutable archive. All production code uses the standard library.

One inspection command used the nonexistent path `work61/scripts`; the correct
`work61/computations` path was then read. Broad source searches returned irrelevant
results, which were discarded in favor of directly opened and rendered primary
source pages. The intermediate mathematical survivors and the invalid shortcut
controls remain explicit. The four earlier local Frey positive families are not
retracted by this global argument.

No new Lean compilation, independent mathematical review, or independent proof
of the upstream analytical and class-group leaves occurred.

## 7. Next obligation

The next depth-one target is the outside-\(V\), low-congruence ramification
required on the old \(H(C)\subseteq U\) class, or a genuinely support-uniform
trace/reciprocity restriction. A new ramified prime adds a correctly twisted
column and can change every test value; it cannot be deleted because a smaller
system was empty. General depth two and higher support, the CM branch, higher
Hilbert levels, the full signature and Beal remain separate obligations.
