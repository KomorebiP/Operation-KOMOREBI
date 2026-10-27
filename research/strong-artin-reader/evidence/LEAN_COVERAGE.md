# Strong Artin formal coverage and replay record

Date: 8 October 2026

Primary verdict for the proposed unrestricted Strong Artin deduction:
**incomplete, with essential arithmetic comparison, obstruction vanishing and
automorphic existence implications missing.** The exact v0.38 local matrix
theorem is a proved conditional statement with a supplied inverse certificate.
This report is source review and evidence authentication. It is not a fresh
Lean proof replay or independent human referee report.

## Exact current checkpoint

The authoritative archive is
`Strong_Artin_Lean_v0.38.0_Effective_Matrix_Hensel_Checked.zip`, 37,581,726 bytes,
SHA-256
`d5f065bcb05ee02465082804dfb14800f82b86f43a8838eded2e3d3519abcb9a`.
Its exact v0.37 parent has SHA-256
`71eb1f38502ce089e9a5ae58bea8fc831f875d6bd83144fe0f4663328e77c689`.

The seven new production modules contain 754 lines and 60 explicitly named
declarations. The declared kinds are 44 theorems, 15 definitions and one
abbreviation. These include helper results and concrete controls. They are not
a count of independent discoveries or a measure of conjecture completion.
No sum of copied dependency declarations across releases is used here.

Let p be prime, let the finite matrix index type be nonempty, and take
integral p-adic matrices A and U. Let d, s and m be natural numbers, with m>s.
Supply an integral pair-indexed coefficient matrix B and the exact two-sided
inverse certificate for the ordered derivative

\[
D_A(X)=\sum_{i=0}^{d-1}A^iXA^{d-1-i},\qquad
BD_A=D_AB=p^s I.
\]

Then the proved integral-matrix criterion is

\[
\exists!F\in\operatorname{Mat}_n(\mathbf Z_p),\quad
F^d=U,\quad F\equiv A\pmod{p^m}
\quad\Longleftrightarrow\quad
B\operatorname{vec}(U-A^d)\equiv0\pmod{p^{m+s}}.
\]

The certificate is checked on the matrix units and extended to all matrices
by linearity. B is an n² by n² coefficient operator. Its action is not
ordinary n by n multiplication. The finite condition uses reductions of A,
U and B in Z/(p^(m+s)); it does not certify the exact inverse identities by
finite approximation.

The integral theorem does not require A or U to be units and has no explicit
positive-degree hypothesis. Degenerate degrees cannot manufacture an inverse
certificate in positive dimension. The exported unit theorem takes A and U
as matrix-ring units and explicitly requires d≠0. It proves an actual unique
unit F, not a surrogate inverse-limit element.

The coefficient bound for Q=p^(-s)B is ||Qz||≤p^s||z||. The ordered nonlinear
remainder has Lipschitz factor ρ on the ρ-ball, and m>s gives strict contraction
p^(s−m)<1. This is the mathematical reason for the precision restriction.

Principal source declarations, in `Komorebi.StrongArtin.MatrixHensel`:

| Declaration | Exact role |
| --- | --- |
| `tangent_eq_sum` | Recursive tangent equals the full ordered derivative |
| `remainder_lipschitz` | Ultrametric remainder estimate on the stated ball |
| `power_ball_image` | Exact image and unique existence from a bounded two-sided inverse |
| `matrix_reduction_iff_norm` | Entrywise congruence agrees with the p-adic distance bound |
| `InverseCertificate` | Explicit algebraic two-sided inverse input on matrix units |
| `matrix_power_exists_iff` | Integral matrix existence criterion |
| `matrix_power_unique_iff` | Integral matrix unique-existence criterion |
| `matrix_unit_root_iff` | Unit-root criterion for positive degree |
| `matrix_unit_root_finite_iff` | Equivalent finite residue-ring target test |

The declaration inventory and all source paths are retained in
`lean/history/v0.38/`. Each source hash matches the September 12 extracted
archive replay, which is separate from this publication's checks.

## Concrete v0.38 controls

For p=2, d=2 and

\[
A=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad
B=\begin{pmatrix}
2&0&-1&0\\-1&2&1&-1\\0&0&2&0\\0&0&-1&2
\end{pmatrix},
\]

the exact inverse identities are BD_A=D_AB=4I. Thus s=2 and m=3 yields a
target test modulo 32 for roots in the class of A modulo 8. The residual
derivative is singular modulo 2, while the derivative is invertible over Q₂.
This distinction is essential.

The positive control

\[
F=\begin{pmatrix}1&1\\8&1\end{pmatrix},\quad
F^2=\begin{pmatrix}9&2\\16&9\end{pmatrix}
\]

does not commute with A. In row-major coordinates, δ=vec(F²−A²)=(8,0,16,8)
and Bδ=(0,0,32,0), so the finite test passes.

For U_bad=[[1,10],[0,1]], δ=(0,8,0,0), Bδ=(0,16,0,0), so it fails modulo 32
and has no square root in the specified modulo 8 class. These controls appear
in `EffectiveMatrixControls.lean`; they are exact theorem statements.

The square derivative at diag(1,−1) annihilates both off-diagonal matrix units
over Q_p. It cannot satisfy the inverse certificate. The v0.38 theorem does
not classify that genuinely singular locus or general shallow prefixes m≤s.
It does not supply automatic certificate discovery for arbitrary p-adic
inputs, nor a new simultaneous gauge-prescription theorem.

## Historical mathematical coverage and explicit interfaces

The source map follows the exact nested ancestry, not an all-branch union.
The historical audit records reused version labels on sibling branches. Such
siblings have not been silently merged into this release.

| Checkpoint and selected source | Strongest safe content | Required input or boundary |
| --- | --- | --- |
| v0.9 `StrongArtinFiniteCore` | Faithful semisimple finite trace image obeys group order ≤t^(n²), over an algebraically closed field of characteristic ell with n<ell | Semisimplicity, faithfulness and representation data are assumed; a residual Galois representation is not constructed |
| v0.9 `large_residual_post_lift_exact` | Cross-characteristic image order and exact polynomial recovery from a supplied lift and separating reduction | Characteristic-zero lift, alphabet membership, separating map and matching reductions are explicit inputs |
| v0.10 `BrauerNesbittStep04` | Prime-cyclic semisimple residual restriction collapse | Normal H, quotient G/H≃C_p, finite-dimensional semisimple representations and equivalent restrictions; this bypasses the still general `SemisimpleCharpolyRigidityFp` interface |
| v0.11 cyclic defect and equivariant quotient modules | Cyclic generic branch symmetry and propagation of nonempty equivariant support | Actual quotient/module, nonzero support and twist equivariance are required |
| v0.17 local Frobenius and generic survival modules | Perfect centralizer/coinvariant trace pairing and conditional special-to-generic support | Arithmetic comparison, module occurrence, flatness or regularity and the stated symmetry hypotheses |
| v0.18 `FiniteCyclicH1Model`, `FiniteCyclicTamePairing` | Actual finite cyclic H¹ model and trace duality under a zero-norm operator | Continuous arithmetic comparison is separate; one-dimensional Tate normalization requires an actual one-dimensional compared space |
| v0.23 intrinsic syzygy modules | Minimal scalar labels cut the raw evaluation kernel down to relation syzygies | Supplied cotangent/Selmer comparison and one-prime detection interface; labels are not automatically actual arithmetic primes |
| v0.25 `PolynomialMovingSyzygyHensel` | Exact root of the original finite polynomial system over a principal nilpotent residue extension | Exact moving identity B(x)F(x)=0 and actual residual image(J)=kernel(B); compatibility is not correction exactness |
| v0.26 square-zero H² modules | Genuine normalized two-cocycle, choice-independent H² class, and representation lift iff its class vanishes | A criterion, not general vanishing; fixed subgroup has a stricter relative class; groups are abstract at this stage |
| v0.27 continuous modules | Continuous lifting criteria and finite-quotient averaging in the stated unit-order sector | Exact topologies, continuous sections and coefficient assumptions; no unrestricted arithmetic vanishing |
| v0.28 local gluing modules | Simultaneous strict local matching has a constructed gluing obstruction | Separate local solvability and pairwise agreement do not imply joint global solvability |
| v0.29 continuous local gauge modules | Local-conjugacy lift criterion and injection coker(H¹_global→H¹_local)→gauge H², with image the kernel of forgetting to absolute H² | Explicit continuous inhomogeneous quotients; no terminal surjectivity or automatic identification with an arithmetic Selmer complex |
| v0.30–v0.34 procyclic, norm and mixed-characteristic modules | Actual coefficient-layer coordinates and ordered Frobenius norm obstruction, including nonsemisimple and simultaneous cases at stated scope | Arithmetic local-field identification, global localization and allowed local conditions remain distinct |
| v0.35 compatible Frobenius tower modules | Actual PadicInt unit root and coherent tower under bijective residual norm; simultaneous literal prescriptions under a nonresonant pivot | Exact target power compatibility and specified nonresonance hypotheses |
| v0.36 compactness modules | Root above a fixed prefix iff finite extensions exist at every depth, including finite joint gauge prescriptions | Joint all-depth premise is not proved by finite sampling; finite survivor horizon is non-effective |
| v0.37 effective scalar horizon modules | Scalar unit-prefix horizon H=max(m,v_p(d)+1)+v_p(d), and fixed diagonal algebra consequence | Scalar units, d>0 and m≥1; it is not a classification of arbitrary matrix roots |
| v0.38 seven current modules | Exact deep local matrix-power criterion under the certified Q_p inverse | m>s and exact inverse certificate; genuinely singular Q_p derivatives remain uncovered |

## Interpretation corrections retained from the audit

The September 11 audit through v0.25 rejected several stronger application
claims without rejecting the correctly stated conditional algebra theorems.
The publication should retain these distinctions:

* A root of F(x)+C(y) does not automatically descend to F(x)=0. Killing
  auxiliary variables or removing auxiliary ramification needs a theorem.
* Bare cotangent H₁, its residue fibre, its dual, an Ext obstruction and a
  dual Selmer space have different coefficient, degree and base-change data.
* A residual comparison theorem is uniqueness, not automorphic occurrence.
* A determinant selects inside a known twist torsor. It does not prove torsor
  membership or Galois attachment of an automorphic descent.
* A two-cocycle is compatible. It is correctable precisely when its class is
  a boundary. Absolute vanishing does not imply relative or local vanishing.
* Minimal scalar-functional counts are not automatically minimal prime counts.

In the finite cyclic C₆ action on two by two matrices over F₃ by
diag(1,−1), the norm is zero but H¹ has dimension 2. It cannot be compared
to a line merely by naming a one-dimensional normalization theorem.

The current later releases construct actual ordinary and continuous classes
and repair several formerly missing algebraic arrows. They still do not prove
the arithmetic vanishing or nonzero determinant-bearing automorphic carrier.

## Evidence dates and verification scope

| Evidence | What ran | What it establishes |
| --- | --- | --- |
| September 11 v0.25 audit | Seventeen source modules plus one axiom-audit module; thirty additional ancestry modules completed | Latest direct source closure passed. Full ancestry run did not finish; two outer wrappers interrupted it |
| September 12 extracted v0.38 archive replay | Seven new modules plus one all-named-constant axiom audit | All completed compiler invocations returned 0; all 60 named constants reported only propext, Classical.choice and Quot.sound |
| October 8 publication byte audit | Thirty unique nested archives, 3004 recorded payload hashes, static production-source screening | CRC and SHA authentication pass; seven current source hashes match historical replay; no screened proof-escape marker found |
| October 8 attempted current Lean replay | Kit lookup, failed dependency download and bounded wrapper preflight | BLOCKED. Zero Lean compiler invocations. No fresh theorem replay |

The historical v0.38 replay uses Lean 4.34.0-rc2, commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, and pinned Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. It rebuilds current project
sources, reuses Mathlib's compiled cache, and authenticates rather than
replays the v0.37 parent. It does not use a second Lean kernel.

The current runtime has no Lean, Lake or Elan binary and none of the recorded
historical kit aliases exists. Seven matching offline kit parts were resolved
in the file collection, totaling 2,896,789,714 raw chunk bytes. Retrieval failed
with HTTP403 and materialized zero parts. No alternate smaller matching kit
was found. The isolated replay wrapper therefore returned BLOCKED with exit 2
before compiler launch. This is an environment/access failure, not a failed
Lean theorem.

An initial byte-audit parser emitted 512 false missing-member findings because
it mishandled historical `./` and absolute manifest paths. The failed output
is retained. Path normalization was corrected, and recursive traversal was
expanded to include the v0.9 child outside a `base` directory. The final audit
passes all thirty byte-distinct archive nodes. Original archive/source bytes
were unchanged throughout.

Final review also caught an arithmetic error in this report's positive control:
its second Bδ coordinate was written as −32. Direct exact integer multiplication
gives −8+16−8=0, so the corrected vector is (0,0,32,0). The root square,
negative target vector (0,16,0,0), both identities BD_A=D_AB=4I, and AF≠FA
were independently recomputed and pass. The mistaken coordinate still happened
to be divisible by 32, but it was incorrect and has been replaced. This correction
changes the exposition only. The original Lean sources were unchanged.

Current records: `lean/AUTHENTICATION_2026-10-08.json`,
`lean/CURRENT_REPLAY_STATUS.json`, `lean/ANCESTRY_INDEX.json`, and
`lean/replay_attempt_2026-10-08/WRAPPER_RESULT.json`.

## Exact remaining application boundary

The local algebra supplies certificates for given objects. It does not
manufacture the objects needed for Strong Artin. The outstanding application
must specify the actual locally constrained continuous deformation problem,
prove its arithmetic cochain and pairing comparisons, prove vanishing of the
distinguished relative/local obstruction, realize genuine auxiliary local
conditions and their descent, construct a nonzero determinant-bearing
automorphic carrier with the needed support and equivariance, and establish
the required ramified compatibility and attachment. None of those inputs is
discharged merely by a formal interface or source declaration count.

The strongest safe publication statement is a substantial formal algebraic
lifting and obstruction library motivated by cyclic Strong Artin descent,
with an exact effective noncommutative matrix Hensel sector and explicitly
unresolved arithmetic realization gates.
