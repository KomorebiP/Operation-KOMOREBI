# Block 22 independent proof audit

**Normalized claim.** Let `Packet B` be the characters of the actual absolute Galois group of `ℚ` that factor through its fixed action on a square root of `−1`. For every characteristic-zero field `K`, their actual field-induced restrictions are trivial exactly when `−1` is a square in `K` or the global packet is trivial. For `K = ℚ_p`, the first alternative holds exactly when `p ≡ 1 (mod 4)`. Every packet is trivial on the residue-action inertia subgroup of every valuation ring above `ℤ_p` when `p ≠ 2`. Over an adically complete coefficient ring with finite positive quotients, downward-closed nonempty finite packet conditions incorporating these actual local restrictions have a continuous global realization.

**Primary verdict: proved as written.** This verdict applies to the eight source modules and the explicitly quantified restricted packet above. It does not certify any of the five full arithmetic claims of Paper X. The final source hashes and execution evidence are recorded in `LOCAL_PROOF_AUDIT_SOURCES.json`.

## Claim card and exact scope

The authoritative statements reviewed are the raw Lean sources, particularly:

- `QuadraticLocalGalois.restriction_commutes`, `localQuotient_eq_one_iff`, `localQuotient_trivial_iff`, and `localQuotient_eq_one_iff_fixed_root`.
- `PadicQuadraticSplitting.root_iff_mod_four_eq_one`, for every natural prime, including `2`.
- `QuadraticLocalPackets.locallyTrivial_iff`, with arbitrary commutative coefficient ring `B`.
- `QuadraticGaloisInertia.packet_on_inertia`, `inertiaTrivial_of_odd`, and `exists_dominating_inertia_trivial`.
- `QuadraticLocalCompletion.local_completion_iff` and `QuadraticLocalArithmetic.arithmetic_local_completion_iff`.
- `QuadraticLocalArithmetic.dyadic_local_detection_mod_four` and its explicit residual failure example.

Here `Packet B` is the subtype of homomorphisms `G_ℚ → Bˣ` whose kernels contain the kernel of the fixed quadratic quotient. It is not the class of all quadratic characters of `G_ℚ`. The restriction map is `Field.absoluteGaloisGroup.map (algebraMap ℚ K)`, not a supplied abstract homomorphism. The coefficient ring and arithmetic field are different parameters. In particular, a dyadic coefficient ring does not imply that the arithmetic prime is `2`.

For inertia, `A.decompositionSubgroup K` is the stabilizer of the valuation subring `A` under `K`-algebra automorphisms. Its inertia subgroup is the kernel of the induced residue-field action. The statements do not identify this decomposition subgroup with the entire absolute local Galois group. A locally dominating valuation exists by an applied Mathlib theorem, so the quantified valuation construction is inhabited. No ramification or inertia-triviality assertion at `p = 2` is inferred from the odd-prime result.

Completion assumes `[IsAdicComplete I R]`, finite positive quotient rings, a `Conditions I` object whose downward property is explicit, and occupancy at every required positive precision. It does not assume a chosen compatible branch, surjective transition maps, coefficient characteristic zero, or a finite set of specified local fields. No universal occupancy result is claimed.

## Dependency graph and independent reconstruction

1. **Global arithmetic quotient.** The predecessor `ArithmeticCertificateExample` chooses an actual root `i ∈ AlgebraicClosure ℚ` with `i² = −1`, proves its nonrationality, and defines the quotient from its Galois action. The inherited `QuadraticGalois.Packet` and descent equivalence refer to this quotient.
2. **Actual local comparison.** Mathlib's field-induced Galois map is defined using a chosen `IsAlgClosed.lift` between closures and normal restriction after scalar restriction. The new `closureEmbedding` uses that same lift. `restriction_commutes` instantiates `AlgEquiv.restrictNormal_commutes`, proving that the image of the global root transforms under the actual local automorphism as asserted. Injectivity of the closure embedding gives both directions of the fixed-root comparison. This is the decisive attachment step.
3. **Triviality criterion.** In characteristic zero the algebraic closure is a Galois extension. Its common fixed elements are exactly the base field by `InfiniteGalois.mem_range_algebraMap_iff_fixed`. The image of `i` lies in `K` exactly when `K` contains some root of `X² + 1`, since any two roots differ by sign. A nontrivial map to the two-element group is surjective. Consequently restriction distinguishes every packet over a nonsplit field, even with characteristic-two or nonreduced coefficients. Over a split field every packet restricts trivially.
4. **All-prime arithmetic criterion.** A root in `ℚ_p` has norm one, hence is integral. Reduction gives the finite-field obstruction. At odd primes, a residue root has nonzero derivative `2x`, so the proved norm inequality satisfies the precise hypothesis of Mathlib's Hensel theorem. The finite-field square criterion then gives `p % 4 ≠ 3`. The separate modulo-four obstruction excludes `p = 2`; primality and parity give the final `p % 4 = 1` equivalence. No residue-root existence is supplied as an oracle in the final theorem.
5. **Actual inertia.** A square root of `−1` belongs to every valuation subring: if only its inverse is initially known integral, the identity `y⁻¹ = −y` puts `y` there too. It is a unit. A decomposition automorphism sends it to itself or its negative. An inertia element fixes its residue. The negative alternative would imply `2·res(y) = 0`, impossible because both factors are nonzero when `2` is a unit. For odd `p`, the image of `2 ∈ ℤ_p` is a unit in every containing valuation subring. The local-root comparison then makes the actual global packet trivial on these inertia elements.
6. **Coefficient reduction and closure.** Mapping coefficients commutes with the actual local character. In a separated adic ring, if every reduction is locally trivial, then either the field is split or all reductions of the packet equal the trivial packet; predecessor packet separation yields actual equality. Positive precisions suffice by further reduction. Intersecting the allowed finite levels with all specified local-triviality predicates therefore preserves downward closure and finiteness.
7. **Simultaneous completion.** The predecessor finite-branch theorem chooses an infinite branch from finite nonempty levels with total parent maps. Its proof does not assume those maps are surjective. Root/packet reconstruction then supplies a continuous global character, and the just-proved local closure gives all selected restrictions. The explicit congruence disjunction is substituted only after its equivalence to the actual local restriction has been proved. Odd-prime inertia conditions hold for every resulting packet separately.
8. **Dyadic detector.** The predecessor classification of integral dyadic roots gives exactly trivial and sign packets. Their reductions agree modulo `2` and differ modulo `4`. The detector theorem is therefore proved for integral dyadic packets, uniformly in the arithmetic prime. It is not a liftability theorem for arbitrary finite coefficient packets.

All leaves used above are existing Lean definitions/proofs or the new Lean proofs. No unverified external arithmetic comparison theorem, computation, or literature citation is used as an assumption. The exact computations accompanying the release are separate corroboration and are not premises of this audit verdict.

## Obligation matrix

| Obligation | Result | Decisive evidence |
|---|---|---|
| Fixed global quotient really comes from a Galois action | Passed | Raw predecessor root, quotient, and packet definitions inspected |
| Field restriction and closure embedding are the same construction | Passed | Pinned `absoluteGaloisGroup.map` and `restriction_commutes` |
| Both directions of splitting/triviality | Passed | Fixed-field descent and the sign classification of square roots |
| Every prime, including `2` | Passed | Separate `ℚ_2` modulo-four obstruction and final all-prime theorem |
| Hensel hypotheses and derivative bound | Passed | Integral lift, residue nonvanishing, norm-one derivative |
| Arbitrary commutative coefficient rings | Passed | No domain/characteristic assumptions in the packet equivalence; characteristic-two and zero-ring edge applications |
| Actual inertia, not a label or quotient kernel renamed inertia | Passed | Pinned stabilizer and residue-action-kernel definitions |
| Existence of an appropriate valuation | Passed | Actual local-domination theorem and instantiated existence result |
| Do not conflate inertia with whole-local-group triviality | Passed | Independent sign example at arithmetic prime `3`: inertia trivial, locally nontrivial |
| Local predicate survives all reductions and their inverse limit | Passed | Coefficient naturality, separated packet extensionality, positive-precision theorem |
| Simultaneous conditions with infinitely many specified fields | Passed | Independent application indexed by `ℕ`; only coefficient levels assumed finite |
| No transition-surjectivity/coherent-witness premise | Passed | Raw compactness and reconstruction dependencies inspected; compiler application uses only stated inputs |
| Residual detection versus modulo-four detection | Passed | Actual dyadic sign is residually locally trivial at `3` but not locally trivial; modulo-four theorem also instantiated at arithmetic prime `2` |
| Entire decomposition group equals `G_ℚp` | Out of scope | No such theorem is asserted |
| Ramification or inertia behavior at `2` | Out of scope | Odd-prime inertia theorem explicitly excludes it |
| Full Paper X arithmetic claims, HT/WD comparisons, universal occupancy | Out of scope | Restricted packet and explicit finite-level occupancy retained |

## Compiler and source checks

The independent runner verifies the supplied Block 21 archive SHA256
`fbe69e04d5e693f6f91b7af7090b04ec43a3467feea1c17cd53fbc9cd9cffbf2`, extracts its 138 predecessor proof objects, and creates a separate output directory. The author's project `build` directory is removed from `LEAN_PATH`. Every new module is compiled from its frozen raw source with warnings as errors, against archived predecessor objects and the newly generated audit objects. No author-produced Block 22 object is reused.

The final run recompiles all eight modules in dependency order and then compiles `checks/local_audit/EdgeApplications.lean`. The latter includes prime `2`, `3`, `5`, `7`, and `13` applications; `K = ℚ`; unit `2` at `3` and nonunit `2` at `2`; coefficients `ZMod 2`, `ZMod 4`, and the zero ring `ZMod 1`; actual valuation inertia; an infinite local-field index; a residual false positive; and the arithmetic-prime-two modulo-four detector.

Reproduce with:

```text
python3 checks/local_audit/run_isolated.py KIT --work AUDIT_TEMP \
  PadicQuadraticSplitting QuadraticValuationInertia QuadraticPadicInertia \
  QuadraticLocalGalois QuadraticLocalPackets QuadraticLocalCompletion \
  QuadraticGaloisInertia QuadraticLocalArithmetic --edge
```

Use the project's pinned portable Lean kit. All audit proof objects remain outside the release tree. Source hashes, inspected Mathlib source hashes, commands, logs, and final exit codes are recorded alongside this report. The root release audit separately performs the cumulative rebuild, transitive axiom audit, controls, and archive replay; this report does not substitute for those gates.

### Failed development checks and resolutions

- The initial independent harness split one `PaperX` namespace between two search roots. Lean selected the first namespace directory and could not find a predecessor import. The harness was corrected to combine archived predecessor objects and fresh new objects within one isolated namespace directory. No production source was changed to address this harness failure.
- An unfrozen `QuadraticLocalArithmetic` version left the definitional equality between `ZMod 4` and `ZMod (2^2)` after rewriting, and also ran a tactic after a preceding rewrite had already closed another goal. The author added the final reflexivity step and removed the redundant tactic. Statements and hypotheses did not change.
- One audit example similarly attempted `decide` after a rewrite had closed the concrete prime-13 goal. The redundant tactic was removed.

The failed logs are retained as development evidence. None remains a failure of the final frozen sources or final edge applications.

## Remaining gap and strongest safe statement

This block establishes a precise arithmetic local-condition bridge for the fixed `ℚ(i)` packet, including actual local absolute-Galois restriction, the all-prime splitting criterion, actual odd-prime valuation inertia, and a completion equivalence with proved local closure. That is the strongest safe statement of this audit.

It does not identify the manuscript's full intended packets or define/prove the required Hodge–Tate and Weil–Deligne comparison machinery. Those remain the substantive obligations before promoting a full partial claim. No additional hypothesis-free arithmetic existence statement follows from the conditional occupancy theorem.

The cheapest remaining release check is to compare the packaged source hashes with this audit manifest and replay the eight new modules. Optional further mathematical tests are unnecessary for the stated scope after those release gates pass.
