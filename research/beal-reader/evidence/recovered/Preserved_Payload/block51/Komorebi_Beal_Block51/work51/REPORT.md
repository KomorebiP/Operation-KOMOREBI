# Beal research, Block 51
## Integral monodromy and the depth of an opposite extension

**Release v5.1.0 — 19 September 2026**

The latest recovered material was the Block 50 extension checkpoint,
created after the complete Block 49 release. Both are preserved in this
package. Block 50 contained an interrupted independent-review request,
not a completed independent acceptance. Its calculations have now been
replayed and its arguments freshly self-reviewed. That distinction is
retained in the historical checkpoint and the new review report.

This block proves a sharp local theorem and uses it to narrow the
ramification support of the remaining reducible branch of

\[
A^3+B^5=C^7.
\]

It does **not** prove the complete signature or the full Beal conjecture.
The arithmetic application is a written proof conditional on the
explicit inherited representation and local/global inputs. No new Lean
certificate is claimed.

### What changed

Previously, the class-group argument forced an additional prime divisor
of C into six eligible residue classes modulo 35. Block 50 then showed
why several proposed shortcuts could not eliminate the surviving
extensions: principal polarization and real multiplication survive the
relevant lattice changes, while the cup-product relation includes a
higher diagonal character-lifting obstruction that need not vanish.

The new result retains the **integral monodromy of the natural lattice**.
This information is absent from an abstract list of residual extension
classes. It restricts how far a lattice can move before a particular
prime begins to ramify in the opposite extension.

### The local theorem

Let O be a characteristic-zero discrete valuation ring with uniformizer
pi and valuation w. Suppose F is invertible over O and a nonzero integral
matrix N satisfies

\[
N^2=0,\qquad FN=QN,\qquad NF=N,
\]

where Q is a unit distinct from 1. Write

\[
t=\min_{i,j} w(N_{ij}),\qquad h=w(Q-1).
\]

If the opposite extension ramifies at depth n, in the precise matrix
sense that w(N_21)=n>=1 and F_21 is divisible by pi^n, then

\[
\boxed{\quad n=t+2s,\qquad 0\le s\le h.\quad}
\]

The proof is short enough to expose its mechanism. The image and kernel
of N are the same line. A primitive generator (x,y) gives

\[
N=m\begin{pmatrix}-xy&x^2\\-y^2&xy\end{pmatrix},
\qquad w(m)=t.
\]

Thus n=t+2w(y). The Frobenius relations imply
F=I+(x,y)^T(a,b) and ax+by=Q-1. The lower-left divisibility condition
forces a to be divisible by pi^(t+w(y)), so Q-1 is divisible by pi^w(y).
This proves the equality and the upper bound without enumerating cases.

The factor two is necessary. Explicit matrices attain every allowed
depth in the stated integral representation category. In particular,
t=h=1 admits n=3, disproving the stronger proposed bound n<=t+h.
These sharpness examples are not asserted to be global Frey representations.

### The bridge to the actual arithmetic representation

On the inherited branch 3990|C, Frobenius at three has eigenvalues 9 and 1.
Their difference is a seven-adic unit. Its integral eigenspace projectors
therefore choose a common basis in which all stable lattices form a
finite segment. Natural monodromy at three fixes one endpoint. Absolute
irreducibility makes the opposite endpoint occur at a finite positive
integer n. This n is attached to the representation, not chosen as a
numerical cutoff.

For a variable rational prime q|C outside 2,3,5,7, the two split nodes
of the natural curve each have thickness 7v_q(C). The explicit local
coordinate calculation and the graph-to-period comparison give

\[
t_v=1+v_7\bigl(v_q(C)\bigr).
\]

Here v_q(C) is the multiplicity of q in C. For a prime v above q, let
Q_v=Nv=q^f, with f=1 or 2, and put h_v=v_7(Q_v-1). The old class-number
argument forces the actual opposite class to ramify somewhere. The new
local theorem says that at least one such prime must satisfy

\[
\boxed{\quad n=1+v_7\bigl(v_q(C)\bigr)+2s,
\qquad 0\le s\le v_7(q^f-1).\quad}
\]

It must also lie in the old eligible residue classes
{1,8,13,22,27,29} modulo 35. The condition is now sensitive to the same
prime's multiplicity, its norm congruence, and the actual lattice depth.
It remains a necessary condition, not a contradiction.

The exact geometric and class-group sources, their hypotheses, and their
application are recorded in `source_records/SOURCE_CHECK.md`. The full
argument is in `notes/ARITHMETIC_SUPPORT.md`.

### Consequences

If n is even, some eligible prime must occur in C with multiplicity
divisible by seven. If every eligible multiplicity is prime to seven,
then n is odd. If, in addition, every eligible norm is not congruent to
1 modulo 49, then

\[
\boxed{n\in\{1,3\}.}
\]

These are explicit hypotheses, not properties proved for every possible C.
Depth at least four therefore requires a stronger norm congruence or
a prime multiplicity divisible by seven somewhere in the eligible support.

The coupling obstruction is also localized more precisely. At a ramified
eligible prime it vanishes below the upper endpoint t_v+2h_v and is
nonzero at that endpoint. In the two-depth regime, n=1 has the cup-zero
condition, whereas n=3 forces a nonzero local diagonal lifting obstruction
at every ramified supporting prime. Neither possibility has been eliminated.

For Block 50's special ray-character prime q=1504231, h_v=1. If its
nonliftable character actually occurs in the present Frey representation
at depth n, the endpoint criterion requires

\[
n=3+v_7\bigl(v_q(C)\bigr).
\]

This excludes depth two for that proposed realization and gives an exact
multiplicity cost at higher depths. At depth five, for example, the
multiplicity would be divisible by 49 but not 343. The cost does not
prohibit such a multiplicity. Exact seventh-power symbols also force
a nonzero natural unit coefficient under the inherited Kummer-support
hypotheses, but that actual coefficient remains uncomputed.

### Verification

The verification distinguishes universal proofs from the finite assertions
implemented by code. All arithmetic checks are exact.

| Check | Result |
|---|---|
| Block 49 payload / Block 50 checkpoint hashes | 284 / 12 matched |
| Selected predecessor computations | Six successful exact JSON replays |
| Integer sharpness family | 252 cases passed |
| Independent quadratic basis grid | 8640 generated; 1530 admissible passed |
| Additional quadratic sharpness family | 252 cases passed, including non-F_7 directions |
| Explicit node identities | 17 exact identities passed |
| Support-selector equivalences | 24,000 checks passed |
| Negative controls | False stronger bound and three matrix mutations rejected; five invalid inputs rejected |

The 7110 inadmissible basis-grid cases fail the theorem's input hypotheses;
they are not counterexamples or timeouts. The targeted quadratic family
was added because the original grid did not cover nonzero cup endpoints.
Both test families are retained and their coverage is reported separately.

The portable verifier uses isolated temporary copies, removes each old
result before replay, and compares fresh JSON with the pinned reference.
Source and fixture hashes are checked before and after. Its reports
include commands, environment, elapsed time and timeout policy. Byte
integrity does not certify the truth of a mathematical theorem.

### What remains

The reducible branch now has a depth-sensitive support restriction, but
no general bound on the actual n and no calculation of the compatible
natural Kummer and higher diagonal characters. The ordinary depths one
and three remain viable. Exceptional norm congruences and multiplicities
also remain possible. Local sharpness shows that these cannot be removed
using only the displayed matrix hypotheses.

The surviving CM congruence and associated rational-point problem, and
the higher Hilbert levels, are separate unresolved branches. This block
does not advance their elimination. The next bounded target is therefore
representation-specific: calculate or constrain the common global
coordinates or toric-line angles, rather than add another abstract
extension class or assume that its diagonal character lifts.

See `CONTINUE_HERE.md` for the exact next-block contract. Review limitations
and rejected approaches are retained in `DEVELOPMENT_FAILURES.md` and
`notes/BLOCK50_FRESH_REVIEW.md`.
