# Prescribed parameter towers: independent proof audit

**Normalized claim and verdict: proved as written.** The mathematical verdict
below concerns the raw proof sources. Lean compilation and exact revision
reconciliation are separate evidence, recorded after the fresh release gate.

Let \(q>0\), \(L\geq1\), and let \(m,k,e\geq0\). Write
\[
F\in\mathbb Z[Y_1,\ldots,Y_m,T_1,\ldots,T_k]^e,
\qquad x=(x_Y,x_T)\in\mathbb Z^{m+k},\qquad F(x)\equiv0\pmod{q^L}.
\]
The actual solved block is
\[
J_x=D_YF(x)\bmod q:(\mathbb Z/q)^m\longrightarrow(\mathbb Z/q)^e.
\]
Assume that this map is surjective. For every integer parameter path
\(t_n\in\mathbb Z^k\) with \(t_0=x_T\) and
\(t_{n+1}\equiv t_n\pmod{q^{L+n}}\), the proof constructs a single tower
\(z_n\in\mathbb Z^{m+k}\) satisfying
\[
z_0=x,\qquad (z_n)_T=t_n,\qquad
F(z_n)\equiv0\pmod{q^{L+n}},\qquad
z_{n+1}\equiv z_n\pmod{q^{L+n}},\qquad J_{z_n}=J_x.
\]
The parameter equality is equality of integers, not only equality of residue
classes. The stronger integer theorem also retains every earlier residue and
the full reduced Jacobian itself.

For a prime \(p\), every target \(\tau\in\mathbb Z_p^k\) with
\(\tau\equiv x_T\pmod{p^L}\) supplies a compatible integer parameter path.
The resulting polynomial tower converges in \(\mathbb Z_p^{m+k}\) to an exact
root \(b\), with
\[
F(b)=0,\qquad b_T=\tau,\qquad
b-z_n\in p^{L+n}\mathbb Z_p^{m+k}\quad(n\geq0).
\]
For each stage \(n\) and each prescribed parameter digit
\(v\in\mathbb F_p^k\), the actual next-level residue fiber has exactly
\(p^{m-e}\) elements. These are distinct residue classes modulo
\(p^{L+n+1}\), not integer representatives or an asserted count of complete
infinite towers. When \(m=e\), arbitrary exact roots in the base ball with the
same parameters coincide. Consequently the square-case endpoint is independent
of every lifting and parameter-approximation choice.

## Review boundary

The reviewer is separate from the proof builders. The six new mathematical
modules, new boundary control, final contract, negative control and exposition
are reviewed from their raw sources; their exact hashes are recorded in
`REVIEWED_SOURCES.json`. The relevant inherited polynomial, finite-residue,
completion and chart interfaces were reread. Earlier Paper IX arithmetic results
are preserved but are not independently re-audited in this block. Independence
of agents does not itself prove correctness.

The source review verifies the mathematical implication. The fresh gate verifies
elaboration and kernel-checkable proof terms against the pinned Lean and Mathlib
runtime. Reconciliation checks that these two passes concern identical source
revisions and logs. None of these is a global novelty claim.

## Dependency graph

1. The inherited residual theorem derives \(F(x)=q^Lr\) from the actual
   lower-root hypothesis. No residual or Taylor conclusion is an extra public
   hypothesis.
2. The exact step writes the prescribed integer difference as
   \(t'-x_T=q^Lw\), reduces \(w\) modulo \(q\), and uses surjectivity of
   the actual solved block to solve
   \(\bar r+K_x\bar w+J_xu=0\).
3. It forms the integer correction
   \(s=(\operatorname{integerLift}(u),w)\). The unrestricted Taylor theorem
   applies to this arbitrary integer correction, so
   \(y=x+q^Ls\) is an actual next root. Because \(w\) itself is retained,
   \(y_T=t'\) exactly. Positive depth preserves the actual reduced Jacobian.
4. Dependent natural-number recursion stores the root depth, exact parameter
   coordinates and equality to the initial solved Jacobian. Each next step
   therefore derives its surjectivity from the single initial assumption.
   There is no assumed compatible solution tower or per-step solvability.
5. The parameter path is patched truncation: \(t_0=x_T\), and
   \(t_{n+1}\) is the canonical integer truncation of \(\tau\) modulo
   \(p^{L+n+1}\). The initial residue hypothesis handles the patched first
   term. Faithful integer divisibility inside \(\mathbb Z_p\) proves its
   integer compatibility. Norm bounds prove convergence to \(\tau\).
6. The inherited compatible-vector theorem proves Cauchy convergence in the
   actual p-adic product topology and retains every finite precision at the
   limit. Polynomial continuity and diverging root depth imply \(F(b)=0\).
   Exact free coordinates identify their limit with \(\tau\) by uniqueness
   of a Hausdorff limit.
7. Solved-block surjectivity kills every shifted residual obstruction. The
   inherited exact digit-to-actual-residue equivalence and finite-field
   rank-nullity give the prescribed count; surjectivity also proves \(e\leq m\).
   The main wrapper applies this at every stage and for every digit.
8. For \(m=e\), the new rectangular block is definitionally the existing
   square chart block. Arbitrary exact roots with fixed parameters equal the
   established chart point in the base ball. Tower endpoint independence
   follows by taking the retained precision at stage zero.

The graph is acyclic. Completion is used only after the new tower construction;
uniqueness uses the earlier square chart theorem and is not fed into the tower
existence proof.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Actual polynomial and actual solved Jacobian | Passed | Explicit integer polynomial evaluation and reduced partial derivatives |
| Independent solved, parameter and equation dimensions | Passed | Variables \(m,k,e\); solved block has domain dimension \(m\) |
| Arbitrary compatible integer parameter path | Passed | `exists_prescribed_tower` quantifies over supplied `t` |
| Exact initial integer point and exact free coordinates | Passed | Recursive initial state and unaltered parameter quotient `w` |
| Only initial solved-block surjectivity | Passed | State stores equality to `solvedJacobian q F x` |
| Actual next polynomial root | Passed | Inherited integer Taylor obstruction for the constructed correction |
| Every higher level and cross-level precision | Passed | Dependent induction and `tower_pairwise_congruent` |
| Parameter path existence from arbitrary p-adic target | Passed | Patched truncation, its compatibility and convergence theorems |
| Actual p-adic endpoint and exact parameter equality | Passed | Cauchy completion, polynomial continuity, Hausdorff limit uniqueness |
| All retained endpoint precisions | Passed | Coordinatewise limit theorem applied before polynomial evaluation |
| Every next digit has exactly \(p^{m-e}\) residue lifts | Passed | Explicit `∀ n v` in the final tower wrapper |
| Exponent \(m-e\) has mathematical meaning | Passed | Surjectivity proves rank \(e\) and \(e\leq m\) |
| Square-case uniqueness for arbitrary exact roots | Passed | Chart uniqueness, without assuming they came from a chosen tower |
| Independence of tower and parameter-path choices | Passed | Endpoint uniqueness requires only common parameters and initial precision |
| Composite \(q\), \(q=1\), prime \(p=2\) | Passed | Integer theorem has only positivity; completion/count have primality, without oddness |
| Zero dimensions and minimum positive depth | Passed | No nonemptiness of finite coordinate types is assumed; induction uses \(L\geq1\) |
| General singular persistence | Out of scope | Solved-block surjectivity is essential here |
| Analyticity, native invariance or descent | Out of scope | Fixed integer polynomial presentation; no such conclusion asserted |

## Boundary cases and counterexamples

- **Full Jacobian surjectivity does not suffice.** The inherited dyadic
  control \(F(Y,T)=T\), \(x=0\), \(p=2\), \(L=1\) has surjective full
  Jacobian but zero solved block. Parameter digit \(1\) forces
  \(T=2\pmod4\), excluding a root. The new target correctly assumes the
  solved block is surjective.
- **Rectangular surjectivity does not imply endpoint uniqueness.** The new
  Lean control uses \(F(Y_1,Y_2,T)=Y_1\), \(p=2\), \(L=1\), \(x=0\).
  The solved block \((1,0)\) is surjective, while \((0,0,0)\) and
  \((0,2,0)\) are different exact roots in the same base ball with the same
  parameter. This directly refutes extending the square uniqueness conclusion
  to all \(m>e\).
- **Positive depth matters.** The Taylor remainder is divisible by
  \(q^{2L}\); \(2L\geq L+1\) requires positive depth. The older written
  example \(F(Y)=Y^2\), \(q=2\), \(L=0\), \(x=0\) shows failure of the
  unrestricted linear digit criterion: digit \(1\) is not a root modulo two.
  This is a mathematical boundary argument, not a newly compiled control.
- **The modulus one is allowed only in the integer result.** Every root and
  compatibility congruence modulo one is tautological, and the reduced modules
  are singletons. Exact prescribed integer parameters still hold. No p-adic
  completion or prime-field exponent is assigned to \(q=1\).
- **No equations.** If \(e=0\), every compatible parameter path extends;
  over a prime the next prescribed fiber has \(p^m\) elements.
- **No solved coordinates.** Over a prime, surjectivity with \(m=0\) forces
  \(e=0\); this excludes an unsupported assertion about solving nontrivial
  equations with no unknowns. For \(q=1\) the trivial-module case remains valid.
- **No parameters.** If \(k=0\), the parameter path is unique and the result
  specializes to the established smooth polynomial tower construction.
- **Uniqueness is local.** Both compared roots must lie in the stated base
  residue ball. No assertion about roots outside that ball is made.

## Source and computation checks

Exact source leaves in the pinned Mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` were checked locally for p-adic
completeness, the divisibility/norm correspondence, the quotient kernel,
separation by all residue quotients, and uniqueness of Hausdorff limits. The
previous prescribed-fiber audit already records the exact rank-nullity and
finite cardinality leaves. The new proof makes no unverified external-paper
claim. This is a source verification scope, not a literature novelty search.

Development outcomes, including observed proof-script failures, are recorded
in the `dev` notes. Not every development compiler output was retained as a raw
file. No reconstructed log is presented as raw compiler evidence. All raw logs
from the authoritative fresh release gate are retained. Development failures
must not be conflated with mathematical counterexamples or hidden by a later
successful gate. The authoritative final compilation report is
`verification/polynomial_parameter_towers_verification.json`; its source, log,
compiled-output and axiom-closure reconciliation is
`audit/reconciliation.json` when the gate has completed.

**Exact remaining gap in this target: none.** The safe conclusion is the full
fixed-presentation smooth prescribed-parameter tower theorem and its square
uniqueness statement above. General rank-deficient singular persistence,
analyticity, native presentation invariance and global or completed descent
remain outside this result.
