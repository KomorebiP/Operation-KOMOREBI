# Block 04 contract delta

The original 35-row contract is preserved byte-for-byte. Its older conditional interfaces remain valid and are still audited. New unconditional results live in the completion extension rather than silently changing the types of those older declarations.

## Row 13 and the printed single-operator theorem

Block 03 supplied the actual arbitrary-field primary decomposition, CRT generators and residue-field lower bounds, proving the primary-block count formula. Block 04 supplies the missing literal primary submodule, exact kernel, residue-linear quotient equivalence, individual multiplicity invariance and the maximum over all monic irreducibles. It also identifies the grouped factors with the actual primary component and counts any positive primary decomposition of that component.

Thus PSC-I-T-SINGLE-OPERATOR is now covered at its full printed scope. The public declaration

    Komorebi.PaperICompletion4.OperatorIntrinsicFormula.operator_seedRank_eq_intrinsicSeedMaximum

takes the operator over a field and finite-dimensionality. It does not require a caller-supplied decomposition, a kernel certificate, a dimension equality or the desired seed rank. Its natural-valued companion is operator_seedFinrank_eq_intrinsicSeedMaximum.

The old row-13 certificate-taking theorem is not deleted or reclassified as a different Lean type. The new extension is the stronger interface that discharges the earlier missing mathematics.

## The five originally identified certificate boundaries

| Original row | Position after Block 04 |
|---|---|
| 10: Semisimple multiplicity formula | The concrete split model and transport remain proved. Abstract decomposition construction and the nonsplit division-algebra case remain separate work. |
| 13: Single-operator seed rank | The full printed intrinsic-primary formula is now covered over arbitrary fields. |
| 14: Cyclic matrix criterion | The cyclic/minpoly bridge, primary-label criterion, conditional invariant-factor count and literal intrinsic-primary interpretation are proved. The full rational-canonical/scalar-extension/eigenspace assembly remains partial. |
| 32: General graph seed rank | Block 02's self-adjoint construction supplies the spectral certificates for real symmetric and complex Hermitian operators. No executable eigensolver is supplied. |
| 35: Exact graph-rank algorithm | The exact mathematical specification remains noncomputable. A verified executable certificate-producing procedure is still outside the completed work. |

## Publication correspondence

Exactly one proof-level record changes status in this block: PSC-I-T-SINGLE-OPERATOR. The 108 records and their current statement/proof source fields are unchanged. Among the 69 proof-level records, 17 are covered, 32 partial and 20 not mapped. The proof-level count is not the 35-row contract denominator and is not an estimate of mathematical effort remaining.

The new Lean proof uses stabilized images to establish the intrinsic quotient bridge. The printed prose proof's separate local-module/Nakayama lemmas are not marked complete merely because this alternate proof closes the single-operator result.
