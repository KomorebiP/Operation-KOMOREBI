# Continuation113: same-carrier cyclic canonical extension

## Result and exact boundary

The finite cyclic phase-existence step is now proved, including existence before uniqueness. From an arbitrary invertible operator implementing the **actual full automorphism** of an irreducible finite-dimensional complex representation, the module constructs the unique operator of the prescribed finite cyclic order bound and determinant one, provided that order is coprime to the representation dimension. The output acts on the original carrier. A later endpoint constructs an honest homomorphism from the original cyclic group, with determinant one on every element and the required conjugation identity on every element of the original represented group.

For the actual finite Heisenberg situation, the initial implementer is also a conclusion. A full automorphism of the original finite group must restrict to an actual automorphism of the prescribed scalar subgroup and preserve its prescribed scalar character. The original scalar and trace profile then yields an implementer by continuation112's irreducible uniqueness theorem. The trace profile can itself be derived from the original nondegenerate commutator form. Thus neither an existing canonical cyclic extension nor a presumed target representation equivalence is an input to the strongest existence endpoint.

This proves the cyclic finite normalization obligation once its exact actual-group hypotheses are instantiated. It does **not** construct an arithmetic simple character, quotient, hereditary order, or full lifted stabilizer action. It does **not** prove that a preselected arithmetic beta-extension has the determinant-one normalization. It does **not** change H5 or its twist family. Strict Claim16.2 remains 65/66.

## Source motivation

Bushnell–Henniart, *Local tame lifting for GL(n) II: wildly ramified supercuspidals*, Astérisque 254 (1999), Appendix A2.3, printed page 100 / supplied PDF page105, gives the unique determinant-one extension under a finite coprime automorphism group. The present development proves a **cyclic** result directly, rather than importing that theorem as an axiom or claiming to formalize its general noncyclic case. Its precise numerical hypothesis is coprimality of the cyclic order and the complex dimension, together with stability represented by an implementer or derived from actual character data.

The supplied source PDF is `upload/AST_1999__254__R3_0.pdf`, SHA256 `8d93beb89572055a752b2f63f1f70b8de30403942a37ccc1de4abee28170032a`. The detailed source assessment is `Paper_XI_Papers_Assessment/ASSESS_1999.md`. No pair-epsilon identity or unrestricted local correspondence is used in this module.

The finite proof also applies to dimensions that are powers of two when the acting cyclic order is odd and the exact hypotheses hold. It does not establish an exact center-preserving dyadic lift merely from equality of associated graded forms. That is a separate attachment question.

## Construction

Let rho act irreducibly on the original complex vector space V, with d = dim(V). Let alpha be an actual automorphism of the original group, with alpha^n = 1 and n > 0. Suppose A implements alpha.

1. Powers of the implementer identity show that A^n commutes with rho. Schur's lemma gives A^n = z I for a nonzero complex scalar z.
2. Choose a nonzero complex r with r^n = z^(-1). Then A1 = r A still implements alpha and satisfies A1^n = I.
3. Write delta = det(A1). Its n-th power is one. For Bezout integers a,b with na + db = 1, put c = delta^(-b). Then c^n = 1 and c^d = delta^(-1). The operator B = c A1 has B^n = I and det(B) = 1.
4. Any other normalized implementer differs by a scalar u by Schur. Its order and determinant give u^n = u^d = 1. Coprimality gives u = 1. Thus the final operator is independent of both the initial implementer and the complex root choice.
5. With an actual cyclic group C and declared generator g, use n = orderOf(g). The corrected operator B defines a homomorphism C to GL(V). All group elements inherit the determinant and conjugation identities.

The proof never replaces the original representation carrier. Scalar multiplication changes the implementer, not rho, the prescribed subgroup, or its scalar character.

## Deriving the first implementer

Let P be the actual finite group and H its prescribed scalar subgroup. Assume rho(h) = theta(h) I and the character of rho vanishes off H. Let alpha restrict to an actual automorphism zeta of H and satisfy theta(zeta(h)) = theta(h).

The twist rho composed with alpha has the same scalar action on H. Since alpha preserves H in both directions, it has the same vanishing character profile off H. Continuation112 supplies an actual representation equivalence between rho and that twist. Its underlying linear equivalence is the required initial implementer.

`canonical_generator_of_actual_form` derives the trace condition from the original nondegenerate quotient commutator form. In particular, the input is a literal action on the original group, not solely an automorphism of its symplectic quotient.

## Strongest endpoints

| Declaration | Conclusion | Nontrivial input still required |
|---|---|---|
| `normalized_generator_existsUnique` | Unique determinant-one order-corrected generator on the original V | An arbitrary actual implementer, full automorphism and coprime order/dimension |
| `canonical_generator_of_actual_form` | Same unique generator, with initial implementer and trace profile derived | Actual finite group/subgroup, original scalar character and nondegenerate form, full theta-preserving automorphism |
| `canonical_action_of_implementer` | Unique honest action C to GL(V), determinant one everywhere | Actual cyclic group action on P, one initial implementer, finite positive generator order |
| `canonical_action_of_actual_profile` | Same honest action with initial implementer derived | Actual original scalar/trace profile and full theta-preserving action |
| `canonical_equivariant_bridge_of_actual_profile` | Both canonical actions and an equivariant actual representation bridge are constructed | Common original finite scalar/trace profile and one common full cyclic action |

The last endpoint extends continuation112's conditional equivariance result: the honest normalized actions are outputs rather than supplied premises. Identifying either output with an existing arithmetic kappa still requires the corresponding full-action and normalization check. Equality of a finite symplectic quotient action alone is insufficient.

## Verification and provenance

Authoritative source: `formalization/PaperXI/CyclicNormalization113.lean`.

- Source SHA256: `607587d94a544d2c4e014d81b21e4c9241d852feddfaa826df57f9715d396ce7`.
- Fresh successful compile: `evidence/phase/attempt05.json`, warnings treated as errors, approximately 5.74 seconds.
- Explicit named exports: 22 total, comprising 20 theorems and 2 definitions. This is a local declaration count, not an increase in the Paper XI theorem-completion count.
- Every named export was checked with `#print axioms`. The only axioms are the standard `Classical.choice`, `Quot.sound`, and `propext`. No `sorry` or new axiom was introduced.
- Independent `leanchecker --verbose PaperXI.CyclicNormalization113` passed, approximately 3.77 seconds.
- Final receipt: `evidence/phase/FINAL_PHASE_CHECK.json`; the complete declaration list and object hashes are recorded there.
- Portable Lean 4.34.0-rc2 and the continuation112 build were reused. Inherited baseline modules and external Mathlib were not rebuilt by this agent. The integrated root replay is the place to authenticate inherited archive hashes and record a fresh multi-module run.
- The continuation112 source `GlobalHeisenbergBridge112.lean` is imported and unchanged. Its expected SHA256 is `b44f5fc5e576c356e04e33a27cfbcd1d0f70946a32dafba8389de23b83d83998`; its archive baseline is SHA256 `4df3bff07c05985e302d5e9f4104de8f6374c17ca695b1e2e451432572272ae5`.

## Failed attempts retained

The first compile could not resolve the inherited PaperXI module because Lean selected the first PaperXI namespace root and did not search a second directory for missing objects. Populating the agent's isolated object directory with inherited objects repaired this environment issue.

Attempts 02 and 03 exposed local proof elaboration problems, not false mathematical statements: simplification reordered Bezout exponents before using the torsion identity, the determinant coercion required its explicit lemma, and an assumed `LinearEquiv.one_apply` lemma name did not exist. The proofs were corrected using explicit exponent equalities and the available coercion lemmas. Attempt 04 compiled the generator and actual-form endpoints. Attempt 05 added the complete cyclic action and compatible bridge and compiled successfully.

The first `leanchecker` attempt failed because it launches `lean` by name and the subprocess PATH did not include the portable toolchain. Its log is preserved as `leanchecker_attempt01_PATH_failure.log`, with an explanatory JSON record. Adding the portable toolchain to PATH and rerunning the same module passed. No proof or mathematical premise was changed to resolve that launcher failure.

No arithmetic existence claim failed in this module because none was asserted. The outstanding arithmetic realization and original-kappa attachment obligations remain explicit.
