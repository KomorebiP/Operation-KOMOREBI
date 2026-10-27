# Paper I: bounded independent mathematical audit

Date: 2026-10-05. Publication author: Komorebi P.

**Primary verdict: correct only after a stated restriction.** The four requested areas support the intended mathematics, but the expanded source has two corollaries that omit a necessary nonzero-packet hypothesis. The two counterexamples below are valid in the domain defined by the source. Neither issue refutes its preceding theorem. The corrected statements are proved by the existing proofs once the omitted hypothesis is restored.

This is a read-only audit of the supplied expanded source and the corrected journal companion. It is not a global novelty check, a proof audit of all Paper I, an audit of Papers II–XII, or a claim that the expanded statements are all covered by the companion's Lean declarations. No publication source was modified by this auditor. A separate fresh subagent independently reconstructed the support-pattern and preorder arguments from the raw source.

## Exact artifacts and scope

Expanded source:

`/workspace/scratch/a478a5fc4884/release/Komorebi_Papers_I-XII_2026-10-05/supplements/Paper_I/readable/PSC_I_FINAL_MACHINE_RELEASE_v1.0.0/PSC_I_MACHINE_v1.0.0/source/PSC_I_authoritative_source.tex`

SHA-256: `e91239446e2e149bbf571c5bbc7e71a76a6f9a351d68963963cfe87f5fbf3c0f`.

Corrected journal companion:

`/workspace/scratch/a478a5fc4884/release/Komorebi_Papers_I-XII_2026-10-05/baseline/Komorebi_Complete/journal/updates/Paper_I_v1.3.1/paper/Projector_Resolved_Seed_Calculus_I.tex`

SHA-256: `b4ce2f9eecfb96d8c414de858e5e27dabdf4851ef8bbfab46feb68d07aaa85b4`.

The claim cards below are pinned to these source hashes and original labels. Their original line locators may change during editorial finalization. Applicable `AGENTS.md` files were checked on the ancestors of the supplied release root; none were found. No prior research ledger was supplied or initialized.

## Claim cards and verdicts

| Label / record | Normalized claim and exact domain | Verdict on raw source |
|---|---|---|
| `thm:module-top` / `PSC-I-T-MODULE-TOP`, lines 974–994 | For a unital ring A, J=Jac(A), finitely generated unital left A-module M, and S contained in M, S generates M iff its image generates M/JM over A/J; hence the generator numbers agree. No semisimplicity assumption is needed. | **Proved as written.** |
| `cor:local-algebra-formula` / `PSC-I-C-LOCAL-ALGEBRA-FORMULA`, lines 1008–1023 | For a local ring A with division-ring quotient D=A/J and finitely generated left module M, seed rank equals the left D-dimension of M/JM. | **Proved as written.** |
| `lem:regular-multiplicities` / `PSC-I-L-REGULAR-MODULE-MULTIPLICITIES`, lines 1037–1057 | For A a finite product of M_di(D_i), the left regular module is the direct sum of d_i copies of the natural simple column module for each factor. | **Proved as written**, with the usual positive matrix sizes. |
| `thm:semisimple-seed-rank` / `PSC-I-T-SEMISIMPLE-SEED-RANK`, lines 1059–1094 | Given the displayed semisimple product decomposition and finite simple multiplicities m_i, the minimum number of generators is max_i ceil(m_i/d_i). For a finite-dimensional algebra and finitely generated M, apply this to the radical quotient. | **Proved as written for a nonempty decomposition with positive matrix sizes.** If the zero ring is admitted through an empty product, explicitly set the empty maximum to 0 or isolate that case. This is a convention omission, not a nonzero-ring counterexample. |
| `thm:source-component-rank` / `PSC-I-T-SOURCE-COMPONENT-SEED-RANK`, lines 2344–2376 | A finite packet system with every packet nonzero, all projectors in A, a declared algebra-generating family, and a surjective pure A-block for every graph edge has packet-pure generator rank equal to the sum of the corresponding corner-module ranks over source strongly connected components. | **Proved as written.** |
| `cor:source-component-count` / `PSC-I-C-SOURCE-COMPONENT-COUNT`, lines 2392–2406 | The printed corollary assumes only packet-propagation: edge-surjectivity and cyclicity of every diagonal corner module. It asserts packet-pure rank equals the number of all source strongly connected components. | **Refuted as printed** if zero packets are retained. Correct after explicitly requiring every packet to be nonzero. |
| `thm:support-pattern` / `PSC-I-T-SUPPORT-PATTERN-ALGEBRA`, lines 2092–2122 | For a finite packet system over a field with all packet spaces nonzero, its algebraic support space contains the identity iff the relation is reflexive and is closed under products iff it is transitive. | **Proved as written.** |
| `cor:star-support` / `PSC-I-C-SUPPORT-PATTERN-STAR`, lines 2124–2137 | For orthogonal Hilbert packet projectors, the printed corollary asserts bounded support space is adjoint closed iff the relation is symmetric, and is a unital star algebra iff the relation is an equivalence relation. | **Refuted as printed** if zero packets are retained. Correct after explicitly requiring every packet to be nonzero. |
| `thm:preorder-decomposition` / `PSC-I-T-PREORDER-ALGEBRA-DECOMPOSITION`, lines 2139–2186 | For a preorder on finite I, strict transfers between equivalence classes form a nilpotent ideal, its (h+1)-st power vanishes, and the quotient is the product of endomorphism algebras of class packets. | **Proved as written for nonempty I.** The same result includes empty I after specifying h=0 for the empty quotient poset. |
| Expanded `thm:dense-realization` / `PSC-I-T-DENSE-REALIZATION`, lines 2734–2759 | A continuous surjective linear intertwiner between Hausdorff topological vector spaces transports a dense algebraic generated hull to a dense generated hull; exact aggregate packet compatibility yields exact packet-range equality. | **Proved as written in the established operator-module context.** |
| Companion `thm:dense-realization`, lines 1331–1370 | A surjective continuous linear map between normed spaces over a nontrivially normed field, intertwining bounded operator families, transports dense word-hull generation. Separately, intertwining bounded P,Q gives Φ(PX)=QY without idempotence. | **Proved as written; compatible with the expanded packet specialization.** |

## Reconstruction and dependency graph

The raw coefficient convention (`def:coefficient-regime`) uses unital left modules over arbitrary unital rings for module theory, fields when dimensions or block coordinates occur, and an explicitly declared topological regime. The packet definition (`def:packet-system`, lines 1306–1322) is a finite family of pairwise annihilating idempotents summing to the identity. It expressly permits zero packet spaces. No blanket nonzero-packet assumption can therefore be imported into the two affected corollaries.

The relevant arrows are:

1. Finite generation of M → finite generation of M/AS → Nakayama for Jac(A) → lifting a generating family from M/JM → module-top rank equality. The external input is noncommutative Nakayama, not merely the commutative determinant version.
2. Evaluation from A^r → generator number as minimum free-cover size → decomposition of A by its columns as a left module → multiplicities r d_i → a quotient with multiplicities m_i exists exactly when m_i≤r d_i. The finite-dimensional extension additionally uses semisimplicity of A/J(A), followed by module-top reduction.
3. Algebra generation by packet projectors and the declared family → expansion of words into blocks → unreachable blocks vanish → every source component must receive its own packet-pure generators. Pure corner blocks lie in A because the projectors do. Source corner generation plus edge-surjectivity → generation propagates through the finite condensation graph → the reverse inequality.
4. Finite packet coordinates → arbitrary block assembly and block multiplication → transitive support sufficiency. Nonzero packet spaces → rank-one witnesses → reflexivity and transitivity necessity. Orthogonal Hilbert projectors → adjoint reversal, and bounded rank-one witnesses → symmetry necessity, provided source and target packets are nonzero.
5. Preorder quotient by mutual reachability → a partial order → strict-class transfer ideal → no product longer than a strict chain. A return C→D→C forces C=D, so the diagonal-class map is multiplicative; arbitrary diagonal-class endomorphisms prove surjectivity and its kernel is the strict ideal.
6. Continuity plus intertwining → image of the source hull lies in the target hull and image of its closure lies in the closure of that image. Surjectivity supplies all of Y. Exact range equality uses surjectivity independently of density. Quotient-topology/completion conclusions require their separately stated hypotheses.

No circular dependency was found in these arrows. No numerical computation is a dependency of the reviewed proofs.

## Obligation matrix

| Obligation | Status | Evidence / boundary |
|---|---|---|
| Module handedness and coefficients | Passed | The regular module is decomposed into left ideals A e_jj, each a natural column module. No commutative row-rank argument is used. |
| General rather than semisimple module top | Passed | Nakayama applies to the finitely generated quotient M/AS even when A/J is not Artinian. |
| Zero module in the module-top formula | Passed | Both ranks are 0, and the empty family is allowed. |
| Positive matrix sizes and empty semisimple index | Convention needed | d_i must be positive. For the zero ring / empty product, max of an empty family requires the explicit value 0. |
| Multiplicity necessity and sufficiency | Passed | A^r contains r d_i simple copies; quotient multiplicities are bounded by these, and coordinate projections realize every permitted tuple of smaller multiplicities. |
| Pure blocks act inside the global algebra | Passed | P_beta B P_alpha belongs to A because every projector does. |
| Source lower bound | Passed | No path enters a source component from outside; projecting an orbit of an internal seed gives a corner orbit. Zero seeds can be discarded and do not affect minima. |
| Propagation upper bound | Passed | Whole packet spaces, not just individual nonzero vectors, propagate under the stipulated surjective edge blocks. |
| Infinite-dimensional packet spaces | Passed | No finite vector-space dimension is used in source propagation or algebraic support. Hilbert rank-one witnesses remain bounded. |
| Zero packets in weighted source theorem | Excluded explicitly | This theorem's hypotheses are adequate. |
| Zero packets in unweighted source corollary | Failed | Its local r_C=1 inference fails for a zero source component. |
| Zero packets in support theorem | Excluded explicitly | Rank-one necessity witnesses are valid. |
| Zero packets in star corollary | Failed | Asymmetric relation pairs can involve identically zero blocks. |
| Empty packet family | Convention needed only for height | I empty implies X=0. Algebraic identities remain valid; define the empty-poset strict-chain height as 0. |
| Dense versus surjective realization | Passed | Both expanded and corrected companion statements explicitly require surjectivity for exact range equality. |
| Quotient and completion topologies | Passed within compatibility check | The expanded quotient theorem separately assumes a quotient map, and its completion uses topology transported from Y. The companion completion clause instead assumes an isometric dense embedding into a Banach target. |
| Cross-version formal coverage | Out of scope of this audit | The companion's supplied split-field equivalences do not by themselves certify the expanded arbitrary-division-ring and radical statements. This distinction must remain explicit in the machine guide. |
| Global theorem status / novelty | Out of scope | No conclusion about all other Paper I statements or historical priority is made. |

## Decisive counterexamples and least local corrections

### A. Bounded support star classification

Take X=C, I={1,2}, P_1=I_X, P_2=0, and R={(1,1),(2,1)}. These are orthogonal packet projectors under the actual definition. For every bounded T, the only possibly nonzero packet block is P_1 T P_1, which is allowed. Thus M_R^b=B(C). It is adjoint closed and a unital star algebra. But R is not symmetric, because (1,2) is absent, and is not an equivalence relation.

The failure is exactly the corollary's choice of a nonzero rank-one map in an allowed asymmetric block: that block can have a zero endpoint. Two indices are minimal for an asymmetric relation, and ambient dimension one is minimal when requiring X nonzero.

Least correction to `cor:star-support`: add **“Assume X_alpha is nonzero for every alpha in I.”** It is also useful to say “real or complex Hilbert space” to align the coefficient convention with the companion. With this change every required witness exists and is bounded, so the printed proof establishes the corrected assertion. An alternative mathematically complete statement tests the restriction of R to I_+×I_+, where I_+ consists of the nonzero packets; that alternative is not necessary for editorial repair.

### B. Unweighted source-component count

Take X=k, A=k I_X, I={1,2}, P_1=I_X, P_2=0, and an empty generating family G. The unital algebra generated by the projectors and G is exactly A. The transfer graph has two isolated vertices, hence two source strongly connected components. Edge-surjectivity is vacuous. Both corner modules are cyclic: X_1=A·1 and X_2={0}={0}·0. The whole module has packet-pure rank 1, but c_0=2.

The failure is exactly the assertion r_C=1 for each source component; the zero component has r_C=0. The earlier cyclic-characterization proposition correctly excludes M=0, so it cannot justify the unqualified inference here.

Least correction to `cor:source-component-count`: add **“Assume every packet space is nonzero.”** Under that condition each source component needs at least one seed, and local cyclicity plus strong connectivity and edge-surjectivity provides one. The existing proof then establishes the assertion. Alternatively one could first remove zero packets, but that changes the graph's vertex set and must be stated.

## Coefficient and companion compatibility

The companion explicitly works over a nontrivially normed field for normed-space statements and R or C for Hilbert-space statements. Its dense-realization proof uses only continuity, linearity, finite word intertwining, and surjectivity; it does not infer openness or a quotient topology. Its range identity Φ(PX)=QY follows by lifting z in the representation y=Qz. This proves the claimed generality without any idempotence assumption.

The expanded packet range identity is a valid specialization: aggregate source projectors and target projectors are idempotents and obey exact intertwining, and surjectivity lifts every vector in the target range. Its use of nets correctly handles general Hausdorff topological vector spaces. The expanded generality and the companion's stricter normed coefficient domain are compatible, but they are different theorem contracts and should not be silently identified as a single formal statement.

The arbitrary-division-ring multiplicity argument belongs to the ring/module regime. The companion semisimple theorem instead begins with a nonempty finite index set and chosen split matrix-algebra and module equivalences over a field. Specializing D_i=k yields the companion formula; the converse scope extension needs the expanded mathematical argument and its classical inputs. In particular, no claim of Lean coverage of radical reduction or arbitrary division rings follows merely from the companion theorem name.

The expanded completed-presentation theorem uses the topology transported from its realized dense image. The companion uses a supplied norm making that image map isometric. These are compatible ways of fixing the essential topology; neither licenses an arbitrary quotient norm or identifies a continuous surjection with a quotient map.

## Exact-source checks for classical inputs

The proof-audit workflow's source check was confined to the exact noncommutative Nakayama and semisimple structure inputs. Official mathlib documentation and its linked immutable source were inspected on 2026-10-05. This is a source check, not a new build of those files and not a claim that Paper I imports them.

1. Junyan Xu / mathlib community, `Mathlib.RingTheory.Jacobson.Radical`, commit `c7eec1400d29a52e5944bd5aa31e999195854dfe`: `Submodule.FG.eq_bot_of_le_jacobson_smul` is stated under `[Ring R]`, not `[CommRing R]`. It makes a finitely generated submodule zero when contained in its Jacobson-radical multiple. Apply it to the whole quotient M/AS. Since M=AS+JM, that quotient equals J times itself and is finitely generated. The source's exact application is valid. [Immutable source](https://github.com/leanprover-community/mathlib4/blob/c7eec1400d29a52e5944bd5aa31e999195854dfe/Mathlib/RingTheory/Jacobson/Radical.lean).
2. Mathlib community, `Mathlib.RingTheory.SimpleModule.WedderburnArtin`, commit `25730c7c759d108ef87ab70af2342a196760f79d`: `IsSemisimpleRing.exists_ringEquiv_pi_matrix_divisionRing` supplies a finite product of matrix rings over division rings with positive sizes. The companion split-field data are a specialization. The arbitrary division rings can equivalently be presented as opposites of endomorphism rings; the expanded proof avoids confusing that side convention by using the chosen matrix-ring decomposition. [Immutable source](https://github.com/leanprover-community/mathlib4/blob/25730c7c759d108ef87ab70af2342a196760f79d/Mathlib/RingTheory/SimpleModule/WedderburnArtin.lean).
3. Mathlib community, `Mathlib.RingTheory.Artinian.Module`, commit `25730c7c759d108ef87ab70af2342a196760f79d`: `IsArtinianRing.of_finite` and `IsArtinianRing.instIsSemiprimaryRing` support the passage from a finite-dimensional algebra to an Artinian ring whose radical quotient is semisimple. A field is Artinian and the algebra is finite over it. [Immutable source](https://github.com/leanprover-community/mathlib4/blob/25730c7c759d108ef87ab70af2342a196760f79d/Mathlib/RingTheory/Artinian/Module.lean).

Only theorem signatures, relevant source proofs, and their application were inspected. No external source file was added to the publication or used to replace its proof. The source question was verification of exact algebraic implications; historical novelty was not searched.

## Commands, verification limits, and remaining work

Raw source was examined with targeted `rg -n` and `sed -n` reads. SHA-256 values were obtained with `sha256sum`. The support audit was independently reconstructed by a fresh subagent that read the same raw source and supplied the same zero-packet counterexample. No numerical experiment, random check, or finite-range enumeration was used to infer a universal statement.

The remaining substantive editorial work within this bounded audit is to restore the nonzero-packet hypothesis in the two named corollaries and record those changes as source-to-final hypothesis corrections. The least further convention clarifications are an empty-maximum value of 0 for a zero semisimple ring, and h=0 for an empty quotient poset. After those changes, the reviewed arguments require no new theorem route. Final corrected-source verification is to be appended with the resulting artifact hash rather than overwriting this raw-source record.

## Corrected-source verification, 2026-10-05

Artifact inspected:

`/workspace/scratch/a478a5fc4884/finalization/Paper_I/traditional/Paper_I_Traditional_Final.tex`

SHA-256 at this check: `cdf1bbded618d9d89f0f4df2cbf6141fbc488eabee96af578fd156c0e67106cb`.

**Corrected scoped verdict: proved as written for the reviewed nonempty semisimple / nonempty-height contracts; both substantive counterexamples have been excluded by explicit hypotheses.**

The exact authorized changes in the two affected statement/proof blocks are:

| Label | Raw source wording | Corrected wording | Recheck |
|---|---|---|---|
| `cor:star-support` | “Let X be Hilbert, let the packet projectors be orthogonal, and put” | “Let X be Hilbert, let the packet projectors be orthogonal, assume X_alpha≠0 for every alpha in I, and put” | Passed: every nonsymmetric allowed pair now admits a bounded nonzero rank-one witness. |
| `cor:source-component-count` | “Assume the packet-resolved module is packet-propagating.” | “Assume the packet-resolved module is packet-propagating and X_alpha≠0 for every alpha in I.” | Passed: source corner ranks are exactly 1 and the weighted theorem applies. |

Each proof is otherwise unchanged. A label-anchored Python comparison against the pinned raw source found identical statement/proof blocks for `thm:module-top`, `lem:regular-multiplicities`, `thm:semisimple-seed-rank`, `thm:support-pattern`, `thm:preorder-decomposition`, `thm:source-component-rank`, and `thm:dense-realization`. The coefficient-regime definition and the expanded dense packet-range contract were inspected again. No claim is made about newly integrated worked-model sections by this bounded recheck.

The empty-product maximum and empty-poset height conventions remain as in the raw source at this hash. They have been reported to the lead editor for disposition. This append-only verification records the actual corrected artifact rather than silently attributing its hypotheses to the original machine-release source.

## Final cross-version verification, 2026-10-05

**Final scoped verdict: proved as written.** The two necessary hypothesis corrections are present, and the remaining empty-case conventions are now explicit in both operative sources. No mathematical obstruction remains in the four audited areas or in their reviewed dense-realization/coefficient compatibility.

Final checked traditional source:

`/workspace/scratch/a478a5fc4884/finalization/Paper_I/traditional/Paper_I_Traditional_Final.tex`

SHA-256: `b23949b0695ef73b064ade9e5c158bf075489824542e5c65fd876236cf81acc8`.

Final checked machine source:

`/workspace/scratch/a478a5fc4884/finalization/Paper_I/machine/source/machine_v1.0.1/source/PSC_I_authoritative_source.tex`

SHA-256: `37bf8f03dbbf66ce41f8b07a8e7be8fa5fca44176bdd56dd25b483f72736ff77`.

The comparison passed for the complete statement/dependency/proof blocks at `cor:star-support` and `cor:source-component-count`. Both versions have exactly the same nonzero-packet hypotheses and the same proofs. This is a check of actual source bodies, not solely record labels or an agent's report.

Both sources also contain the identical unnumbered preliminary paragraph immediately after the coefficient-regime record:

> For finite families of nonnegative integers we use max(empty)=0. The height of an empty finite partially ordered set is 0, as is the height of a nonempty poset with no strict comparable pair. Thus the height in the support-preorder theorem counts strict steps.

This makes the empty semisimple maximum agree with seed rank 0 for the zero ring/module and makes the empty-preorder nilpotence bound N^1=0 well-defined. It is an **ambient convention clarification**, distinct from the **two substantive nonzero-packet hypothesis corrections**. The record statements and proof bodies were not otherwise changed by this clarification.

Machine-readable final provenance and equality checks are saved in `final_scoped_verification.json` in this audit directory. This auditor did not run the machine package's proof gate or regression suite; those separate validations belong to the machine agent's report. This final conclusion remains limited to the original four target areas and the specified companion compatibility checks.

## Frozen-typography receipt refresh, 2026-10-05

The final traditional source is now pinned to SHA-256 `7e71a29a18dc79058bafb0037a09de79457a75178360ea9d404bf15ad5997cb8`; the machine source remains pinned to `37bf8f03dbbf66ce41f8b07a8e7be8fa5fca44176bdd56dd25b483f72736ff77`. A fresh label-anchored equality check passed for the complete statement/dependency/proof blocks at `cor:star-support` and `cor:source-component-count`, and for the exact empty-family convention paragraph. `final_scoped_verification.json` has been refreshed to these current hashes. This supersedes the earlier traditional-source receipt at `b23949b0695ef73b064ade9e5c158bf075489824542e5c65fd876236cf81acc8`; it does not expand the audit scope or change its mathematical verdict.
