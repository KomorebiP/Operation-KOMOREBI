# Lean verification report — Realization Boundaries v0.4.0

## Accepted result

**PASS: complete diagonal homomorphism classification, endomorphism rings and rational quotient scalars, automorphism criterion, and reflection for a supplied map on canonical profinite completions.** This is an incremental checkpoint, not full-book completion.

Authoritative evidence: `verification/accepted_v0.4.0/run.json`. Six new production modules extend the actual infinite groups. All twenty inherited production modules are byte-for-byte unchanged from `Realization_Boundaries_Lean_v0.3.0_Checked.zip`; the provenance receipt and a final parent-archive comparison check that fact. The printed monograph is unchanged.

| Verification measure | v0.3.0 | v0.4.0 |
|---|---:|---:|
| Production modules rebuilt cleanly | 20 | **26** |
| Root import entrypoints rebuilt | 1 | **1** |
| Explicit source theorem/lemma declarations | 193 | **260** |
| All audited declarations, including definitions and generated helpers | 459 | **628** |
| Positive contract declarations | 66 | **101** |
| Intended rejection controls | 20 | **26** |
| Production modules passing kernel replay | 20 | **26** |
| Passing compiler/audit/control/replay command gates | 65 | **83** |

There are 3196 production source lines. The 67 newly named theorem/lemma declarations are not presented as 67 independent discoveries or 67 completed book theorems. The exact source inventory and all exported types and axiom dependencies are retained. Five additional numbered book statements are now COMPLETE.

## New mathematical content

### Arbitrary homomorphisms are derived to be diagonal

For every pair of rational subspaces U,V of the actual quotient P/D and every additive homomorphism f:H_U -> H_V, the theorem `hom_coordinate_formula` proves `(f x)_p = c_p*x_p`, where c_p is recovered from f applied to the actual prime seed. No continuity or diagonal hypothesis occurs in the theorem. Uniqueness of c and automatic continuity are proved. The induced quotient map is constructed and its rational linearity follows from unique division.

For selector groups, the exact admissibility criterion is `exists r:Q, diagonal(c)(u_S) - s_T(r) in D`. The converse constructs the actual homomorphism on the original subgroups. `selectorHomEquiv` is an equivalence for the entire homomorphism set, not merely a family of constructed examples.

### Endomorphism rings and the rational scalar

`endomorphismRingEquiv` identifies the genuine endomorphism ring with the admissible coordinate subring. For an infinite selected set S its elements are exactly the coordinate families eventually equal, on S, to reduction of one rational. The rational is unique. `quotientScalar` and `endomorphismQuotientScalar` are actual ring homomorphisms; their laws and surjectivity are proved. The zero-scalar kernel is precisely finite nonzero support on the selected coordinates, with complementary coordinates unrestricted.

`finiteSupportEndomorphismRingEquiv` separately proves End(D) is isomorphic as a ring to the full prime-coordinate product. These are actual rings with composition multiplication, not merely bijections of sets. The endomorphism rings of all rational preimages are consequently proved commutative in this setting.

The chosen rational-section multipliers supply preimages of every rational but are not asserted to be a ring-homomorphic section. A positive contract checks that the chosen lift of one half plus itself differs from the chosen lift of one at the selected prime two.

### Automorphisms of the original groups

An endomorphism of an infinite-selector group is an automorphism exactly when every diagonal coordinate is nonzero. The quotient scalar is then proved nonzero, and the reciprocal coordinate family is proved to preserve the original group. The proof constructs an actual additive equivalence agreeing with the supplied map, with the exact reciprocal formula for its inverse at every prime.

More generally, between these rank-one groups a supplied injective map is automatically bijective, as is a supplied surjective map. This is not extended to arbitrary rational-subspace preimages. The source-selector infinitude hypothesis remains explicit.

A nonzero rational quotient scalar alone is insufficient. The selected-coordinate projection has quotient scalar one but kills every complementary-prime seed. Its noninjectivity is a checked positive counterexample, and a separate negative control rejects the false implication.

### The actual induced completion map and reflection

`completionHom` is a continuous additive map between Mathlib's canonical profinite completions. It is built using the earlier checked comparison equivalences and the newly derived diagonal family. It agrees with the supplied original f on every canonical eta image. Density proves uniqueness, identifying it as the induced extension. Its coordinate action on the whole completion, its composition law, and its injectivity on original homomorphism sets are checked.

The pinned dependency version lacks some convenient additive completion-functor/lift API names tested during development. No such missing implementation is assumed. The unique extension and its defining equations are proved directly.

`paired_completion_reflects_isomorphisms` proves book Proposition 9.4: for a supplied f:G_A -> G_B, the induced completion map is a continuous additive isomorphism exactly when an actual original-group additive isomorphism agrees with f. This does not infer original isomorphism from an arbitrary isomorphism of completion objects.

The proper D -> G_A inclusion remains a counterexample outside the paired rank-one source family. Both its non-surjectivity and bijectivity of its induced completion map are rechecked in the new positive contracts.

## Monograph mapping

New COMPLETE entries are **2.2, 7.5, 7.7, 7.8 and 9.4**. All 45 original numbered records remain in `docs/MONOGRAPH_COVERAGE.json` with declaration links. The actual types and hypotheses were inspected against the corresponding original LaTeX theorem statements; `docs/EXACT_STATEMENT_REVIEW.md` records the main interfaces.

Entry 9.3 remains PARTIAL. Family-level faithfulness, map composition, and no-lift witnesses are checked, but the global category of all residually finite groups is not newly formalized. Entry 9.1 retains its canonical-completion no-decoder proof and its still-unimplemented exact Pro-object interface. No pending seed-rank, computability or grammar theorem is promoted by analogy.

## Accepted run and dependency identities

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
```

Mathlib remains pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine locked package revisions matched. The restored five-part runtime archive again had SHA-256 `f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.

The run started at `2026-10-23T19:21:06.121376+00:00` and ended at `2026-10-23T19:25:31.765997+00:00`. Its measured duration was 265.645 seconds. These are receipt timestamps, not an estimate. The audit recorded 3,484 imported modules and compared 17,290 compiler/imported-cache files at the endpoints.

The verifier took its source and dependency baseline before deleting all project compiled output, then rebuilt production serially. The final source identity and compiler/dependency identity checks passed. A post-run packaging check again compared every accepted proof input against `source_after.json`.

## Audit and diagnostic policy

All 628 project declarations have transitive axiom dependencies confined to `propext`, `Classical.choice`, and `Quot.sound`. No production declaration is an axiom or unsafe. No proof depends on `sorryAx`, a project-specific axiom, or a native-decision trust axiom. Automatic implicit parameters are disabled and warnings are errors.

The 35 additional positive contracts and six additional negative controls protect diagonal uniqueness, admissibility, inverse hypotheses, rational-scalar insufficiency, scope of completion reflection and nonadditivity of chosen lifts. The negative controls require their designated diagnostics and nonzero exits without timeout. Corresponding positive proofs establish the mathematical obstructions independently of the compiler failures.

## Failures and corrections

Development drafts encountered parser, scalar-coercion, type-inference, rewrite and warnings-as-errors failures. They were corrected without weakening the printed mathematical conclusions. Missing additive completion API names led to the direct unique-extension construction described above. One root-entrypoint attempt followed a failed dependency compilation and therefore failed on a missing module; the accepted clean rebuild supersedes that attempt. Logs and the diagnostic API probe are preserved separately from the accepted run.

Documentation validation also found eight inherited theorem-location entries pointing to blank lines immediately before their declarations. The current index now records the actual declaration-name line and validates all 260 entries against source and the audited environment. Previous indexes remain in history. A LaTeX excerpt helper's nonexistent-heading error was corrected by locating the actual theorem label. These were documentation/tooling errors, not mathematical counterexamples.

No accepted gate failed. The detailed incident record distinguishes failed drafts from the deliberately rejected controls. No external peer review or historical-priority certification is claimed.

## Trust and remaining scope

Kernel replay uses Lean's own kernel, not an independent second implementation. The restored compiler and imported compiled caches were not rebuilt from source or independently authenticated against upstream. Standard logical principles, those binaries and caches, the runtime and hardware remain trusted. Equal endpoint hashes do not exclude a transient alteration restored between snapshots.

The next formal targets are the exact finite-seed obstruction and cardinal seed ranks, including closure in the actual topology, plus root-fiber cardinalities and Chinese-remainder cyclic identifications. Topological cyclicity of P, dimension-language refinements, oracle-presentation semantics, the nonuniform decoding boundary, and grammar diagonalization remain separate unfinished work. Noncomputable definitions are not proofs of computability claims. The finite Python certificate implementation has not been proved equivalent by Lean extraction.

## Reproduce

```bash
export KOMOREBI_LEAN_KIT=/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-fresh-verification
```

Choose a new evidence directory. The source ZIP excludes the large compiler and dependency cache, but retains their version/hash records and the recovery instructions. The finalized publication, original source package, all historical ledgers and earlier accepted verification directories remain preserved.
