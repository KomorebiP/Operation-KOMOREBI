# Future research

**Status: proposed work beyond Research Preview 1. None of the targets below is claimed as a result of this release.**

The present endpoint is a finite-precision mathematical theorem: admissible rational masks yield a canonical minimum-cardinality finite linear realization under the fixed-ring, fixed-alphabet, all-word contract. The next stage should build on that endpoint without making the release contingent on an unlimited research program.

## 1. From a formal specification to a verified executable compiler

**Starting point.** The mathematical construction and its semantics are formalized. Exact Python reference implementations provide bounded cross-checks, including integer lattice calculations. Several Lean interfaces are noncomputable, so the theorem-level constructor is not yet an efficient executable implementation.

**Target.** Implement finite polynomials, modular arithmetic, transitions, submodule calculations, and quotient presentations using explicit data structures. Prove that the implementation refines the existing mathematical objects, including its treatment of zero divisors and nonfree modules. A certificate-producing implementation with a smaller verified checker is a possible route, not an established feature.

**Completion criterion.** A documented executable accepts the stated mask inputs and produces an evaluator whose output is proved equal to the canonical coefficient for every index. Performance claims would require separately stated cost models and measurements. No coefficient-sample test can replace this refinement theorem.

## 2. State maps between precisions

**Starting point.** Canonical series and outputs reduce compatibly from precision $p^r$ to $p^s$. The intrinsic residual description makes the state-level comparison a precise question.

**Target.** For $0<s\le r$, construct maps $\rho_{r,s}:M_r\to M_s$ that preserve the initial state, commute with every digit map and output, and compose:

$$
\rho_{s,t}\rho_{r,s}=\rho_{r,t}.
$$

The scalar convention must be explicit: these maps compare different coefficient rings and should respect scalar reduction, rather than being incorrectly described as linear over one unchanged ring.

**Completion criterion.** Prove the maps' definitions, compatibility laws, and exact kernel properties. Analyze separately whether the stronger identification $M_s\cong M_r/p^sM_r$ holds. A natural map or a compatible output is not a proof of that isomorphism. Where the stronger statement fails, retain a counterexample or a precise obstruction rather than altering the claim silently.

## 3. A single inverse-limit machine

**Starting point.** Every fixed precision has a finite realization. A tower of state maps is the preceding research target, not an assumption supplied by finite output agreement.

**Target.** For a fixed prime and fixed integer masks with $A(0)=B(0)$ in $\mathbb Z$ and $p\nmid B(0)$, investigate

$$
M_\infty=\varprojlim_r M_r.
$$

The integer constant equality is important here: compatibility at one modulus alone does not supply admissibility at all precisions. Construct the inverse-limit seed, digit operations, and output into $\mathbb Z_p$ once the state tower is available.

**Completion criterion.** Prove the required topology, continuity, coefficient output, and the exact finite-stage recovery statement that the transition maps justify. Keep a profinite module distinct from a finite-rank $\mathbb Z_p$-module. Bounded generator rank, finite generation, or one finite machine encoding every precision would require additional theorems and may hold only for restricted subclasses.

## 4. Effective comparison and structural classification

**Starting point.** Reachable-observable realizations of the same all-word behavior are uniquely isomorphic as structured linear machines. Cyclic-factor signatures classify their underlying finite modules, not their complete dynamics. A finite distinguishing-word horizon is already proved.

**Target.** Turn the existing comparison theorems into practical equality and inequivalence certificates. Investigate which mask transformations preserve the coefficient behavior, and which structural invariants help distinguish behaviors before constructing full comparison data.

**Completion criterion.** Verified comparison procedures with explicit inputs, finite bounds, and counterexamples when two masks differ. An equal signature or equal state count must not be accepted as evidence of equal behavior. A change of basis may conjugate transition matrices without making them literally equal.

## 5. A broader obstruction-resolution theorem

**Starting point.** The present example links a defect, filtration-increasing corrections, section operators, finite closure, and semantics-preserving reductions. It also contains generic module and realization theorems, but does not establish a universal arithmetic compiler.

**Target.** Identify explicit sufficient hypotheses for other filtered arithmetic systems to admit finite exact representations at finite precision. Candidate ingredients include a section-product law, a controlled correction expansion, nilpotence or filtration growth, and a finite state-closure argument. The nontrivial obligation is to prove these hypotheses in each application, not merely to name them in an interface.

**Completion criterion.** A reusable formal theorem and at least one substantively different worked instance, such as a suitable recurrence or rational-diagonal system, with its domain restrictions and failure cases stated. Investigating a candidate class is not a promise that every member fits. A broader theorem may require narrower hypotheses than the initial analogy suggests.

## Research policy after this release

These directions are questions, not hidden assumptions of the finite-precision theorem, and carry no promised completion dates. A future release should state which precise obligation it closes, preserve the predecessor's claims, and distinguish new proofs from finite experiments and implementation changes.

Independent review, attribution corrections, reproducibility repairs, and genuine errors in included claims can require changes to the current release. Additional theoretical ambition cannot, by itself, hold the release open.
