# Special Functions: formal sources and recorded coverage

**Recorded checkpoint: SF-LEAN-B17, 3 November 2026.**

[Inspect the Lean sources](https://KomorebiP.github.io/Operation-KOMOREBI/lean/monographs-special-functions/index.html) or [run a selected file with dependencies](https://KomorebiP.github.io/Operation-KOMOREBI/lean/run.html).
The inspector includes the coupled production modules, their axiom-audit files,
and selected controls alongside the inherited finite core. The original Block01
status file remains available as a historical checkpoint.

## Choose a production module

The existing declaration registers record 426 theorem names across the seventeen
coupled modules below. The separate inherited finite core records 39 names,
for 465 registered names at this checkpoint. These are registered names with
individual scopes; they do not measure whole-book formalization.

| Block | Production source | Registered theorem names | Declaration register |
|---|---|---:|---|
| 01 | [CoupledFormal.lean](../monographs/special-functions/lean/CoupledFormal.lean) | 29 | [Names and source lines](../monographs/special-functions/formalization/Block01/declarations.json) |
| 02 | [CoupledAnalytic.lean](../monographs/special-functions/lean/CoupledAnalytic.lean) | 21 | [Names and source lines](../monographs/special-functions/formalization/Block02/declarations.json) |
| 03 | [CoupledEntire.lean](../monographs/special-functions/lean/CoupledEntire.lean) | 19 | [Names and source lines](../monographs/special-functions/formalization/Block03/declarations.json) |
| 04 | [CoupledUniqueness.lean](../monographs/special-functions/lean/CoupledUniqueness.lean) | 16 | [Names and source lines](../monographs/special-functions/formalization/Block04/declarations.json) |
| 05 | [CoupledGermInverse.lean](../monographs/special-functions/lean/CoupledGermInverse.lean) | 13 | [Names and source lines](../monographs/special-functions/formalization/Block05/declarations.json) |
| 06 | [CoupledRescaling.lean](../monographs/special-functions/lean/CoupledRescaling.lean) | 19 | [Names and source lines](../monographs/special-functions/formalization/Block06/declarations.json) |
| 07 | [CoupledCharacteristic.lean](../monographs/special-functions/lean/CoupledCharacteristic.lean) | 23 | [Names and source lines](../monographs/special-functions/formalization/Block07/declarations.json) |
| 08 | [CoupledPositiveReal.lean](../monographs/special-functions/lean/CoupledPositiveReal.lean) | 22 | [Names and source lines](../monographs/special-functions/formalization/Block08/declarations.json) |
| 09 | [CoupledLowerGrowth.lean](../monographs/special-functions/lean/CoupledLowerGrowth.lean) | 16 | [Names and source lines](../monographs/special-functions/formalization/Block09/declarations.json) |
| 10 | [CoupledUpperGrowth.lean](../monographs/special-functions/lean/CoupledUpperGrowth.lean) | 34 | [Names and source lines](../monographs/special-functions/formalization/Block10/declarations.json) |
| 11 | [CoupledGrowthTypes.lean](../monographs/special-functions/lean/CoupledGrowthTypes.lean) | 22 | [Names and source lines](../monographs/special-functions/formalization/Block11/declarations.json) |
| 12 | [CoupledTypeProportions.lean](../monographs/special-functions/lean/CoupledTypeProportions.lean) | 26 | [Names and source lines](../monographs/special-functions/formalization/Block12/declarations.json) |
| 13 | [CoupledScalarReduction.lean](../monographs/special-functions/lean/CoupledScalarReduction.lean) | 43 | [Names and source lines](../monographs/special-functions/formalization/Block13/declarations.json) |
| 14 | [CoupledOperator.lean](../monographs/special-functions/lean/CoupledOperator.lean) | 27 | [Names and source lines](../monographs/special-functions/formalization/Block14/declarations.json) |
| 15 | [CoupledEvaluation.lean](../monographs/special-functions/lean/CoupledEvaluation.lean) | 36 | [Names and source lines](../monographs/special-functions/formalization/Block15/declarations.json) |
| 16 | [CoupledNormalization.lean](../monographs/special-functions/lean/CoupledNormalization.lean) | 30 | [Names and source lines](../monographs/special-functions/formalization/Block16/declarations.json) |
| 17 | [CoupledGuardedMajorant.lean](../monographs/special-functions/lean/CoupledGuardedMajorant.lean) | 30 | [Names and source lines](../monographs/special-functions/formalization/Block17/declarations.json) |

## Read the evidence with the source

The [Block17 report](../monographs/special-functions/formalization/Block17/REPORT.md),
[claim map](../monographs/special-functions/formalization/Block17/CLAIM_MAP.json),
[recorded execution receipt](../monographs/special-functions/formalization/Block17/evidence/receipt.json),
and [source inventory](../monographs/special-functions/formalization/Block17/SOURCE_MANIFEST.json)
identify the checkpoint's statements, assumptions, inputs, and recorded checks.
The [formal I/O inventory](../monographs/special-functions/formalization/Block17/IO_MANIFEST.json)
and [dependency pins](../monographs/special-functions/lean/dependency_pins.json)
provide the reproduction context.

Production modules contain the mathematical definitions and proofs. Files whose
names end in `Audit.lean` inspect axiom use; files in control directories test
acceptance or rejection boundaries. Their presence in the inspector does not
make them additional production theorems. Local import links open an explicitly
selected module in the same work.

The original import receipt is preserved. Later files are separately bound to
the dated Block17 publication inventory and their committed source bytes.
Adding these reading routes performs no new Lean execution or proof review.
The native runner prepares the selected source's dependencies; browser import
availability and successful compilation remain separate questions.

## Remaining scope

The recorded Block17 development proves an exact guarded-majorant algorithm
model. Full Python runtime and dictionary correspondence remains open.
Other analytic regions and ordinary type convergence retain their recorded
conditions. Consult the [remaining-work inventory](../monographs/special-functions/formalization/Block17/REMAINING_WORK.md)
and [current continuation guidance](../monographs/special-functions/current/README.md)
for subsequent work.

[Current assessment](works/monographs-special-functions.md) · [Reading volumes](SPECIAL_FUNCTIONS.md)
