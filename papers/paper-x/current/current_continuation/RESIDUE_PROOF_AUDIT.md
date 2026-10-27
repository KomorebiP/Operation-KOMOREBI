# Independent audit of the residue and norm-character continuation

Verdict: **proved as written at the declared conditional block scope**. All 34 new production modules independently rebuilt with strict exit 0 and identical proof objects. The block contains 156 theorem/lemma declarations. The transitive audit covered 319 owned environment declarations and found only `propext`, `Classical.choice`, and `Quot.sound`. All 221 predecessor sources and proof objects are unchanged. The five compiler controls produced their intended outcomes.

The principal audited theorem is `PaperX.NormResidueLattice.exists_classNormSum_bound_of_unit`. Let K be a number field of degree d, C an ordinary ideal class, J a nonzero integral ideal representing C inverse, m a nonzero natural modulus, and chi a complex multiplicative character with zero on Z/mZ. Let N_m be the actual determinant norm on O_K/mO_K. The supplied arithmetic conditions are a residue-ring unit u with chi(N_m(u)) != 1 and chi(N(J)) != 0. Under exactly those conditions, the actual finite sum over nonzero integral ideals satisfies

`|| sum_{N(I)<=X, [I]=C} chi(N(I) mod m) || <= B * X^(1-1/d)`

for some B>=0 and every real X>=1. The theorem derives its geometric estimate, both finite sign averages, and the exact lattice/generator/ideal identifications. None of these is a premise of the final theorem.

The arithmetic conditions are not proved for every target needed by Paper X. Full Claim 9.1, the required Euler identities and prime-series nonsummability, and the source separator assembly remain incomplete. The full ledger stays at 17 checked / 3 partial.

## Dependency graph

Frozen actual lattice-coset discrepancy -> actual additive quotient and fiber/coset equivalence -> quotient index and covolume normalization -> actual ideal-congruence counts -> finite weighted error estimate.

Actual mixed-cone boundary atlas -> positive and negative real-coordinate sign regions -> signed field-norm product formula -> integral norm sign on each region -> sign-corrected norm weights.

Integral multiplication matrices -> actual residue-ring determinant norm -> descent from ideal-lattice residues -> actual multiplication action on J/M -> unit permutation, using mJ<=M -> zero mean of both norm-sign weights, using chi(N_m(u))!=1.

Those three paths -> cancellation in the two actual sign regions -> exact recombination of finite point sums -> exact bounded-generator sum -> roots-of-unity multiplicity and inverse-class norm scaling -> actual ideal norm-character sum, using chi(N(J))!=0.

Separately, frozen ordinary ideal-class counts -> exact ordinary-class weighted ideal sum -> finite-group character orthogonality -> unconditional ordinary class-character power saving -> global floor-step measurability -> logarithmic Mellin first moment and O(h) endpoint error. Its pole consumer still assumes the nonzero residues and product identity.

## Mathematical source review

The residue space is the genuine additive quotient L/(L intersection L0). For the counting theorem L0<=L is explicit, so this is L/L0. The quotient map is surjective by construction. Its cardinality is the actual relative index, and its covolume ratio is proved. Every residue has the same main-term density, divided by this index. The proof never substitutes the cardinality of an arbitrary target ring for the index. Uniformity in the residue comes from the predecessor's uniformity over all translations.

The ideal-lattice embedding is linked to actual algebraic integers by an explicit equivalence. Residue equality is proved equivalent to x-a belonging to the smaller ideal. Finiteness of the point domains is proved from discreteness and boundedness. Weighted residue counts are exactly finite sums over those actual points, including at threshold boundaries. The norm-threshold conversion uses the positive scale Y^(1/d), d>0, and the exact degree homogeneity. Degree one retains an O(1) error.

The signed/absolute distinction is handled explicitly. The integral multiplication norm descends to the actual quotient ring, independently of the chosen integral basis. The principal ideal norm is the absolute value of that signed norm. The signed product formula retains the product of the real embeddings and the positive complex norm-square factors. The sign-cut construction creates no frontier outside the already charted cone frontier, because the real-coordinate product is nonzero on the cone. The origin remains outside the counted cone and inside its boundary where appropriate. When there are no real places, the real-coordinate product is 1 and the negative sign region is empty; no equal-volume assertion about the two sign regions is used.

The map from ideal residues to O_K/mO_K is not assumed surjective. The earlier draft wording J/M was corrected to J/(J intersection M) where no M<=J hypothesis is present. The mean on the actual ideal quotient is proved directly: multiplication by a lift of a residue-ring unit is a permutation when mJ<=M, and it scales the actual residue norm by N_m(u). A nontrivial scalar multiplier forces the finite sum to vanish. Taking M=mJ proves containment and finiteness internally for every nonzero J and nonzero m. Nontriviality of chi on the larger codomain is never substituted for nontriviality on the unit norm image.

The two sign regions are recombined by a point-preserving disjoint-union equivalence. At every point, the computed finite residue weight equals the character of the actual absolute principal ideal norm. The resulting lattice-point sum is then identified with the actual bounded generator sum by the predecessor cone correspondence, with the natural-number norm preserved exactly.

The full roots-of-unity factor is applied only after sign recombination. The weighted generator-to-ideal identity holds for arbitrary norm weights and all real thresholds. It retains both the factor w_K and the scaling N(I)N(J), at threshold XN(J). For a multiplicative norm character the coefficient is exactly w_K*chi(N(J)). The recovery theorem explicitly requires chi(N(J))!=0. It does not cancel a possibly zero scalar. The final estimate uses N(J)>=1 and X^(1-1/d)>=1 for X>=1 to absorb the additive constant.

The ordinary class-character path is different. Its exact finite ideal sum is grouped by the ordinary class group, and a nontrivial class character cancels the common leading coefficient. These functions are step functions on the integer norm scale, so measurability is derived. The Mellin integral uses those actual sums. It does not yet identify the distinct norm-residue character sum with an arithmetic L-series, and its ordinary-character pole criterion still takes the residues and product identity as inputs.

## Obligation matrix

| Required implication | Verdict at block scope |
|---|---|
| Actual additive residue fiber = actual lattice coset | Passed |
| Finite quotient, correct index and covolume normalization | Passed |
| Uniform discrepancy and actual ideal congruence counts | Passed |
| Exact finite weighted lattice-point sum | Passed |
| Signed integral norm descends to the actual finite quotient | Passed |
| Arithmetic sign equals geometric sign, including the no-real-place case | Passed |
| Actual sign regions inherit boundary charts and counting estimates | Passed |
| Unit permutation proves mean zero on the actual ideal quotient | Passed under the displayed unit norm-character witness |
| Sign recombination and actual bounded-generator sum identity | Passed |
| Full weighted roots-of-unity and inverse-class norm attachment | Passed |
| Actual ideal norm-character power saving | Passed under the displayed unit witness and representative nonvanishing |
| Ordinary ideal-class character power saving and Mellin endpoint control | Passed; no supplied counting or measurability hypothesis |
| Ordinary-character pole nonvanishing and index one | Passed under the displayed residues and product identity |
| Unit/representative inputs for all intended arithmetic targets | Not supplied by this block |
| Norm-residue character measurability/Mellin attachment | Not supplied by the ordinary-character Mellin modules |
| Actual Euler identity, prescribed-prime nonsummability, and full Claim 9.1 | Incomplete |

## Independent execution protocol

The audit copies only the 221 manifest-listed frozen predecessor proof objects into its first PaperX module root. Each new source is copied into an isolated audit source tree and compiled there. New dependencies are the audit's own previously rebuilt objects, never the author's new objects. The author and audit source hashes and proof-object hashes are compared exactly. All 221 baseline source and proof-object hashes are also rechecked.

The compiler is the pinned Lean 4.34.0-rc2 with `-DwarningAsError=true`. Dependency-ready compiler streams have unique per-module logs. Combined result updates use an exclusive lock and an atomic rename. The final latest-only compilation table is separate from the preserved full attempt history.

The transitive axiom query selects every environment declaration owned by the 34 new modules, including generated declarations, and recursively collects its axioms. The only permitted axioms are `propext`, `Classical.choice`, and `Quot.sound`. Named source theorem counts and owned environment declaration counts are reported separately.

This is an independent rebuild of the 34 new modules against hash-verified baseline objects. It is not a fresh compilation of all 255 cumulative modules and not a replay from an empty source-dependency closure.

## Controls and recorded failures

| Control | Result |
|---|---|
| Exact signed/absolute residues modulo 3, odd sum-of-two-squares residues modulo 4, and attainable/empty fibers of multiplication by 2 on Z/4Z | Strict exit 0 |
| False equality of signed and absolute residues for -1 modulo 3 | Rejected after reduction to False |
| False surjectivity of the mod-4 sum-of-two-squares norm form onto residue 3 | Rejected after reduction to False |
| False common count on an unattained target residue | Rejected after reduction to False |
| Explicit placeholder in an import-free file | Rejected specifically for using sorry |

These finite examples test sign and image restrictions. They are not offered as universal proofs or as a newly formalized theorem about every ideal of the Gaussian field.

The first sign-control validation failed because `norm_num` stopped at the false goal `-1 = 1` rather than the validator's required literal False. An independently kernel-decidable inequality reduced the unchanged false assertion to False. The first source, diagnostic, and failed validator record are preserved.

Two independent audit sessions were interrupted at the parent's request while simultaneous imports were blocked by I/O contention. The tool confirmed session exit 130 for NormResidueAlgebra and NormSignArithmetic. The queued NormResidueArithmetic compile had not started. These were harness interruptions, not proof rejections. Both interrupted sources later rebuilt unchanged with exit 0 and identical author proof objects. A preliminary process-child lookup failed to locate the targets and sent no signal; the supported session interruption then succeeded.

Some author attempt logs used the same norm_filter_attempt name in different lanes. Those mixed logs are excluded as reliable per-module evidence. The final uniquely named author records and independent matching rebuilds establish the accepted results. Other author failures concerned elaboration, namespace/import lookup, or strict style checks and are documented in the route records; the accepted mathematical hypotheses were not weakened to repair them.

## Reproduction and exact evidence

`privatechecks/audit_replay.py` rebuilds explicitly frozen modules in dependency order. It requires the pinned kit and the frozen baseline object tree. `privatechecks/audit_axioms.py` audits all owned declarations, `privatechecks/audit_controls.py` runs the controls, and `privatechecks/audit_finalize.py` checks exact module coverage and hashes.

The final record is `privatechecks/audit_summary.json`. Latest successful compiler records are in `privatechecks/audit_replay/compilation.json`; all attempts, including the two interruptions, are preserved in `compilation_history.json`. Complete axiom output is in `privatechecks/audit_replay/logs/AuditAxioms.log`, with its status in `axioms.json`. Control results are in `controls.json`. The release replay is a separate user-facing route with the same declared baseline/new-module verification scope.

The strongest safe conclusion is completion of this arithmetic counting block under its displayed arithmetic hypotheses. The cheapest subsequent attachment is measurability and Mellin control for the actual norm-character sum, followed by proving the arithmetic witness/representative inputs for the intended characters and completing the Euler and prime-series path. Full Claim 9.1 remains partial.
