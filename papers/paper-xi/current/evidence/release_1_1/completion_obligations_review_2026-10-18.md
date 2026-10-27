# Paper XI: terminal claim and moving-phase review

Date: 18 October 2026. Reviewed package: `/workspace/scratch/604befec1954/paperxi_work`, reading release P11-PUB-B07 / 1.0.0. This is a delegated focused source audit, not external peer review, a full-manuscript referee report, or a new compiler receipt. No package source or catalogue was edited by this reviewer.

## 1. Normalized main claim and primary verdict

**Primary verdict: incomplete, with the smallest missing implication being construction of an arithmetic realization witness for every admitted assembled H1–H4 datum.**

The current authoritative statement is `publication/source/traditional/Paper_XI_Traditional_Final.tex`, Section 16.1, lines 1828–1877. For every admitted irreducible wild Weil atom rho over the fixed local field and its supplied finite datum d_rho, Conjecture 66 asks for an actual admissible supercuspidal pi of GL_(dim rho)(K), with actual inducing data and comparison/recovery maps. Those maps must preserve the declared stabilizer action, prescribed character values, extension and phase data, and transports, and recover that same pi with its central character and noncompact completion.

H1–H4 supply finite break data, separate equivariant type-side bridges, extension/phase data, and compatible transports. They do not supply a common arithmetic inducing carrier. The text expressly permits an enlarged carrier and does not require every assembled packet to be the original maximal-simple-type quotient. The open construction must therefore be judged against this exact contract, not a stronger inner-normalizer or native-marking contract that was never supplied.

The separate comparison proposition, lines 1879–1904, is valid conditional reasoning: if one realized pi has the required normalized factors on a genuinely characterizing twist family, its class is the LLC class of rho. Its characterizing-family and normalization inputs remain essential. It does not imply the required arithmetic existence.

## 2. Dependency structure and obligations

| Step | Evidence actually inspected | Audit status |
|---|---|---|
| Supplied finite break extensions give factor intertwiners and their tensor product | `FiniteBreakAssembly.lean`, `Data`, `factor`, `tensorBridge`, `tensor_intertwines` | Passed at source/interface level. The actual extensions, center-preserving group lifts, irreducible representations, and central characters are inputs. |
| Honest stabilizer discrepancy is a character and phase equality closes it | `FiniteBreakAssembly.discrepancy`, `equivOfPhase`; `BreakBridge.lean` | Passed at source/interface level. Specified actual actions and their covariance are inputs. |
| Compatible matrix holonomy gives a gauge and a global section equivalence | `ConditionalAtomicComparison.lean`, `Holonomy`, `glue`, `holonomy_iff_gauge`, `finiteComparison` | Passed at source/interface level. This constructs finite comparisons, not arithmetic atoms. |
| Every admitted target diagram has an arithmetic atom | `LocalFactorIdentification.lean`, lines 23–35 | **Not supplied by those finite theorems.** `Realization.exists_atom` is an input field, and `chosenAtom` chooses from that field. |
| Tested normalized local factors agree for the same realized candidate | `ConditionalAtomicComparison.source`, lines 127–137 | **Conditional.** `hfactors` is a named hypothesis, separate from finite phase and holonomy data. |
| Equality of normalized profiles implies equality of isomorphism classes | `LocalFactorIdentification.FactorSystem`, lines 12–18, and `class_eq_iff`, lines 39–46 | Conditional on the concrete external converse theorem encoded by `separates`. The finite-character example later in the module is not a local-Weil converse theorem. |

An interface-level negative control makes the logical distinction exact: a one-point finite datum and an empty atom type admit trivial finite actions and gluing, but no `exists_atom` witness. This is not an arithmetic counterexample to Conjecture 66. It shows why an abstract finite interface cannot supply an unrelated atom-existence field by itself.

### Four genuinely separate research obligations

1. **P11-OPEN-016: general realization.** Construct a common actual inducing carrier with the admitted action/transport data, all full character values, and same-candidate recovery. The restricted constructors do this for their specified families with one vertex and trivial stabilizer, not for arbitrary admitted input.
2. **P11-OPEN-017: H5 on the same realizer.** Verify the stated normalized pair-factor family for that candidate. Conductors and finite Gauss phases do not supply it.
3. **P11-OPEN-021: corrected-character occurrence.** In the characteristic-zero continuation, prove `Hom_(H^1)(theta', pi_F^0) != 0`, where `pi_F^0 = AI_(L/F)(chi_0)` is independently fixed. Then identify the full noncompact extension. Source: Block03 continuation, equation (18.8), lines 432–443. The full correction uses `nu(varpi)=zeta_9`, not 1, to preserve the central character. Correcting a scalar obstruction does not select the source-defined central type.
4. **P11-OPEN-022: independently required native dyadic certificate.** For the fixed rank-eight candidate and actual specified finite extension, supply six actual symplectic basis lifts, their squares under the full character, section products, prescribed transports, and honest phases. Source: Block04 `block04/30_register.tex`, certificate subsection, and `27_capacity.tex`. At equal capacity, the actual Arf invariant must match; for a fixed embedding the whole pulled-back quadratic refinement must match. A freely transported marking has a different, already positive contract.

These are not four parts of one known final elementary lemma. The root ledger already separates them correctly.

## 3. ActualMonomialLocalGlobal: what compiler recovery would establish

The preserved file is under the B01 inherited `source/working_handoff_2026-10-04/preserved_workspace/pxi45_work/Paper_XI_Actual_Monomial_Local_Global_v0.45.0/formalization/lean/PaperXI/` directory. Its header explicitly excludes automorphic representations, class field theory, and automorphic induction from the Lean data.

The actual parameter is degree-subgroup induction on the residue–Frobenius pullback. Required data include a cyclic inertia homomorphism whose image is exactly the actual degree-zero kernel, an actual degree-one Frobenius lift, its stated conjugation relation, a full character on the degree-n subgroup, and a hypothesis that the first positive lower group acts trivially.

The resulting source derivation identifies actual inertia-fixed spaces and depth-projector ranges; proves vanishing tame Swan conductor; identifies the Artin conductor with 0 or n according to the inertia label; transports the literal induced Frobenius to the actual fixed space; characterizes descent to the inertia-free model by the zero inertia label; and applies the existing unramified field-tower restriction laws. The packaged theorem is `actual_comparison_package`; the terminal declarations are `descended_actual_baseChange_polynomial` and `descended_actual_baseChange_localFactor` at lines 441 and 455.

This is a substantive tame attachment result. It does not construct an automorphic candidate or assert general wild occurrence. It does not even assert irreducibility of every supplied induced parameter: n is positive but not required in this file to be the minimal inertia-orbit length. For example, zero inertia with n greater than 1 is permitted and yields a reducible complex cyclic induction. No irreducibility claim should be added to a replay receipt.

The companion `GLOBAL_MONOMIAL_INTEGRATION_COROLLARY.md` is explicitly non-Lean and conditional on imported global automorphic induction and local compatibility. It also excludes epsilon/gamma identification without actual additive-character and measure normalization. Successful replay can close P11-VERIFY-020 in its declared scope. It cannot discharge P11-OPEN-016 or P11-OPEN-017.

## 4. Concrete repair: the breakwise phase statement

**Focused subaudit verdict: ill-typed as written.** Current `cor:break_phase`, main manuscript lines 1776–1791, allows fixed vectors in V while displaying `Phi_p(g,V)` and `Phi_p(g,V_s)`. `def:odd_phase` defines those expressions for fixed-point-free full spaces. Its fixed-point-free hypothesis applies only to the moving image.

The smallest permitted example is a symplectic plane over F_3 with g=I. Its moving image is zero, so g is fixed-point-free there, but `Phi_3(I,V)` is outside the declared domain. The correct moving phase is 1. Extending the quadratic character to zero would give a full determinant expression equal to zero and would not supply the intended sign.

### Exact valid correction under the original written hypothesis

For the g-stable orthogonal decomposition `V = perpendicular_sum_s V_s`, set

`M = im(g-I)` and `M_s = im(g|_(V_s)-I)`.

Assume, as the current corollary does, that g is fixed-point-free on M. Then the properly typed formula is

`Phi_p(g|_M, M) = product_s Phi_p(g|_(M_s), M_s)`.

The moving decomposition is `M = perpendicular_sum_s M_s`. Fixed-point-freeness on M gives `ker(g-I) intersect M = 0`; rank-nullity gives the complementary direct sum. Symplectic invariance makes the fixed and moving summands orthogonal, hence M and every M_s are nondegenerate symplectic spaces. The restriction on each M_s is fixed-point-free. The already stated orthogonal phase multiplicativity applies. Zero moving summands contribute 1, as does an empty family.

This correction is already supported by the retained raw Lean, rather than a newly invented research route:

- `BreakMoving.productEquiv` and `equiv` construct the actual image decomposition.
- `BreakMoving.isCompl_of_moving_fixedPointFree` and `movingForm_nondegenerate` derive the complement and domain facts without an order assumption.
- `BreakOddPhase.product` and `source` prove exactly the moving-phase product.
- `BreakOddPhase.zero_moving_factor`, `empty`, and `MovingPhase.phase_identity` cover the boundary cases.

If the manuscript instead displays `Phi_p^mov`, it must explicitly connect that notation to the direct moving condition, because the current `def:moving_phase` invokes a prime-to-p order hypothesis. Adding prime-to-p order to the corollary is a valid restriction but unnecessary. The controlling `STABILIZER_CONTRACT166.md`, Section 1, expressly warns that the original cyclic stabilizer is not generally assumed to have order prime to p.

### Downstream scope

No downstream `cref` use of `cor:break_phase` appears in the current main manuscript. The adjacent restricted-bridge proof assumes actual phase equality and tensors actual intertwiners, so its statement needs no mathematical change from this correction. The visual guide already says that the fixed-point-free formula applies to the moving part, at lines 319–323.

Historical obligation 63 / all-records row 92 maps generally to `FiniteBreakAssembly`. The exact odd-branch formal locator is `BreakOddPhase.source`; `FiniteBreakAssembly` does not import that module directly. Add the precise locator in the new evidence record, preserving the historical crosswalk as historical evidence. The dyadic product statement is unaffected.

## 5. Useful interface alignment

The manuscript comparison proposition assumes H5 for one fixed realized pi. `ConditionalAtomicComparison.source` uses the stronger hypothesis that every realizer of the selected datum has the expected profile. This is not an error, but the stronger premise should not be silently described as the exact one-candidate statement.

The existing `LocalFactorIdentification.class_eq_iff` already proves the exact one-candidate comparison when applied to that pi and the reference. A small named corollary can expose that application, assuming `R.realizes d pi`, admissibility of the reference, H5 only at pi, and the reference profile identity. This would align the formal presentation without supplying any missing arithmetic input.

## 6. External source obligation

The source-access gap is explicit in root `FAILURES_AND_LIMITATIONS.md` and predecessor Block04 `evidence/block04/SOURCE_INPUT_AUDIT.md`. The inherited `ARITHMETIC_CONSTRUCTOR_AUDIT.md`, lines 37–58, identifies the detailed Henniart–Lemaire inputs and the characteristic extension required for the rank-nine F_3((t)) candidate. Root has recovered the official source and has requested a separate bounded source verification. That verification will be recorded separately and must not be promoted to H5, arithmetic occurrence, or a new constructor proof.

## 7. Review method and next action

Read raw current mathematical and Lean source, rather than accepting ledger labels. Commands used include focused `rg`, numbered source slices, direct module reads, and comparison with the preserved native-action, occurrence, and source-input notes. This reviewer did not run a Lean compiler or arithmetic constructor. Those execution claims belong to their own receipts.

The cheapest justified completion actions are the moving-phase source correction, explicit current one-candidate formal alignment if desired, bounded HL11 primary-source verification, and an actual pinned replay of the terminal tame module. Retain the four research obligations exactly until their own evidence changes.
