# Bounded traditional prose-proof audit

**Normalized claim.** SR-01 through SR-48 assert the displayed algebraic identities, exact state and memory certificates, bounded-flow estimates, Hilbert reconstruction contracts, regularization limits, and discrepancy results under their final printed hypotheses.

**Primary verdict: conditional on a named input.** No unresolved internal proof defect was found in this bounded pass. The classical infrastructure imported from pinned Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` remains a named external input: its exact implementation bodies were not independently audited here. This is not a fresh Lean check.

## Scope and revisions

This independent delegated read-only review read all 48 prose statements and proofs, their local conventions and final printed setups. It inspected 62 unique raw source declarations or definitions across 26 production modules, with their scoped variables and imports. All 219 principal source anchors for these 48 groups were separately matched to the declaration inventory and current source hashes. Locator validation is not a proof audit of all 219 declarations.

The JSON companion records the exact claim IDs, source declarations and line locators, source-file hashes, statement/proof hashes, and final manuscript/concordance hashes. Coverage does not include substantive proof auditing of SR-49–SR-64, all 1,159 declarations, a fresh Lean compile or kernel replay, PDF layout, independently verified Python, or historical novelty.

Final audited TeX SHA-256: `05f52b2a7e0e687fdcd60eb5fc9e71ce2343a352b811081f447c2c8d16d87483`.

Final concordance JSON SHA-256: `0876e7a6040ec46ce1af1ab147246c7da741e1880106dcfe2707d18e48be2a83`.

## Resolved findings

1. Initial assembly omitted the per-claim hypothesis fields. SR-22 printed a growth budget without its whole-flow envelope premises; SR-02 used `C,R` before typing them; SR-16 did not clearly retain true-operation nonexpansiveness in its contractive branch. The author corrected the assembly to print all 64 setups. SR-22 now explicitly retains real rates of either sign, nonnegative time, nonnegative amplitudes and allowances, both whole-flow envelopes for every nonnegative time, and both defect bounds.
2. Generic setup conversion left the SR-03 labelled chain and SR-47 noise allowance awkward to type. The final source prints the actual `G → V → W` chain with map labels and the chain condition, and both pointwise and indexed noise inequalities with acceptance and total-selection gates separately.

These were actual scope/typing corrections. Without true nonexpansiveness, the scalar choice `T=2`, `U=0`, `q=I`, `epsilon=2` has word defect `2^n`, contradicting a proposed uniform contractive budget of 2. Without actual envelopes, zero amplitudes alongside `L=I`, `A=0`, `q=I` give a zero budget despite a nonzero evolution defect. The corrected hypotheses exclude these cases.

## Dependency graph and obligation matrix

| Claim groups | Required implication chain | Internal status | Named or unchecked leaves |
|---|---|---|---|
| SR-01–04 | supplied splits → encoding/defect; all-word kernel → invariant quotient | Passed | Standard module quotient infrastructure |
| SR-05–08 | actual powers → hidden recurrence → prefix converse → finite certificate → canonical discarded state | Passed | Cayley–Hamilton and characteristic-polynomial degree |
| SR-09–12 | descending kernels → plateau/horizon → reachable-image comparison → finite certificate | Passed | Finite-dimensional rank/nullity and quotient infrastructure |
| SR-13–16 | chronological telescoping → whole-map budgets → rate/contractive specialization | Passed | Standard norm and finite-sum infrastructure |
| SR-17–20 | bounded exponential derivatives → variation of constants → flow/power transfer → moments/jets | Passed | Banach exponential calculus and interval FTC |
| SR-21–24 | mixed-flow differentiation → Duhamel → actual envelopes → initialization/scalar failure | Passed | Operator integral inequalities and exponential calculus |
| SR-25–28 | actual nested projections → unique sectors → harmonic class → conditioned residual/refinement | Passed | Orthogonal projection and finite-dimensional lower norm bounds |
| SR-29–32 | actual complete closed range → bounded inverse → ambiguity/coercivity → closed-range equivalences | Passed | Bounded inverse and completeness/closedness infrastructure |
| SR-33–36 | native quotient seminorm → harmonic isometry → transport/refinement → nonclosed boundary | Passed | Quotient norm and metric closure criterion |
| SR-37–40 | positive normal coercivity → constructed inverse → objective → bias/noise/perturbation | Passed | Hilbert adjoint, Riesz, Lax–Milgram infrastructure |
| SR-41–44 | normal-range density → strong limit → approximate-recovery closedness → fitted closure limit | Passed | Double orthogonal complement and filter uniqueness |
| SR-45–48 | continuous residual → strict floor brackets/IVT → norm domination → accepted-source consistency | Passed | IVT and standard limit infrastructure |

The selected project-source invocations and their hypotheses were inspected. Exact pinned Mathlib bodies remain outside this pass, so those dependency leaves are conditional.

## Decisive scope checks

- Prepared closure is distinct from closure for every hidden initialization. The latter requires `B=0`; nonzero couplings can coexist with every prepared return moment zero.
- Return moment `k` appears at depth `k+2`; hidden dimension `d` gives complete-map tests through `d+1`. A zero-dimensional hidden space has an empty sufficient memory list.
- Chronological words apply their right factor first. Exact and scalar concatenation formulas preserve this order. A bounded word-length horizon with arbitrary alphabet does not imply a finite enumeration.
- Behavioral minimality compares the competitor's actual reachable image. Full ambient-state equivalence needs surjectivity. Finite certificates are sound without finite-dimensional source; finite dimension provides the bounded-horizon existence guarantee.
- Flow results retain real Banach spaces, bounded autonomous generators, actual differential equations/exponentials, and all-real-time equalities. Quantitative envelope estimates restrict to nonnegative time. No unbounded-generator or sampled-time closure claim is made.
- Orthogonal components use actual projected subspaces and the actual realization range. A nonclosed algebraic quotient can have a nonzero zero-seminorm class. Bounded exact identifiable recovery requires closed range; positive Tikhonov does not.
- Strong convergence fixes a source; operator-norm convergence has exactly the closed-range boundary. Converse and absent-source-limit claims retain a nontrivial filter. A fitted limit in the closure is not upgraded to realizability or source-norm divergence.
- Discrepancy selection retains the strict floor/upper endpoint, positive parameter, genuine true-noise allowance, and small-data branch. Its selector remains noncomputable. Accepted sources are actual Tikhonov sources; later contracts handle numerical solve errors.

Hand checks included zero hidden dimension, empty word/alphabet, an exact competitor retaining an extra future-invisible distinction, the zero forward operator, and discrepancy's constant orthogonal-data case. These clarify boundaries rather than substituting for the universal proofs.

## Remaining gap and strongest safe statement

No unresolved internal implication was identified in the 48 reviewed prose proofs after correction. These reconstructed arguments match their stated contracts in this bounded review, conditional on the named classical Mathlib inputs and without a new Lean execution. A fresh pinned-runtime compile and kernel replay is the cheapest remaining formal check when the runtime becomes available; runtime recovery failures are recorded separately.

## Conservative proofreading

Review-only mode. This reviewer made no author-file edits. Requested corrections were explicit setup rendering and the two local setup typing fixes above. All final 48 statement, proof, and setup fields were checked to occur exactly in the assembled TeX. No unresolved meaning-changing issue remains in this scope. Other release reviews cover rendered layout and later claim groups.
