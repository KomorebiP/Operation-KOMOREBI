# Proof ledger — v0.28

All declarations below are checked as written in the fresh direct replay. Counts include helper definitions and finite examples. Arithmetic instantiation and Strong Artin remain open.

## ContinuousLocalConstraintComplex.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localOneCochains` (line 15)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.restrictOne` (line 22)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraintPairs` (line 28)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraintDifferential` (line 52)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.LocalConstraintH2` (line 67)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraintClass` (line 71)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraintClass_zero_iff` (line 76)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraintClass_eq_of_boundary` (line 94)

## LocalLiftMismatch.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.pullbackDatum` (line 11)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.pullback_action` (line 19)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localCorrection` (line 23)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localCorrection_val` (line 28)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localCorrection_boundary` (line 33)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.correctedLift_at_local_iff` (line 62)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localCorrection_continuous` (line 88)

## SimultaneousLocalLiftCriterion.lean

- `def Komorebi.StrongArtin.SquareZeroH2.Datum.prescribedLocalPair` (line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneousLocalObstruction` (line 23)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneousLocalObstruction_zero_iff` (line 29)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.continuous_simultaneous_local_lifts_iff` (line 56)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneous_zero_implies_absolute_zero` (line 92)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_local_family_lifts_iff_constructed_obstruction_zero` (line 111)

## ContinuousLocalGluingCokernel.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.globalOneCocycles` (line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localOneCocycles` (line 17)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.restrictOneCocycles` (line 37)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.Datum.StrictLocalGluingCokernel` (line 50)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.localMismatchAfterPrimitive` (line 54)
- `def Komorebi.StrongArtin.SquareZeroH2.Datum.strictGluingObstruction` (line 74)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strictGluingObstruction_zero_iff` (line 81)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraint_zero_iff_gluing_zero` (line 93)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.strictGluingObstruction_independent_primitive` (line 115)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.localConstraint_zero_of_surjective_restriction` (line 134)

## FiniteKernelConjugacy.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.kernelUnit_conjugation` (line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.same_residue_representations_kernel_conjugate` (line 30)

## FiniteLocalFamilyUpToConjugacy.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.finite_quotient_lift_matching_local_family_up_to_conjugacy` (line 11)
- `theorem Komorebi.StrongArtin.SquareZeroH2.continuous_finite_quotient_local_family_up_to_conjugacy` (line 28)

## LocalGluingCapstone.lean

- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneous_lifts_iff_gluing_obstruction_zero` (line 14)
- `theorem Komorebi.StrongArtin.SquareZeroH2.Datum.simultaneous_lifts_of_absolute_zero_and_surjective_restriction` (line 30)
- `theorem Komorebi.StrongArtin.SquareZeroH2.finite_matrix_lift_matching_local_family_up_to_conjugacy` (line 53)

## LocalGluingCounterexample.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.C2` (line 12)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.G` (line 13)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.A` (line 14)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.B` (line 15)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.q` (line 25)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.q_surjective` (line 27)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.q_squareZero` (line 29)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.axisOne` (line 31)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.axisTwo` (line 36)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.diagonal` (line 41)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.sign` (line 46)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.firstSign` (line 51)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.secondSign` (line 56)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.loc` (line 61)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.prescribed` (line 62)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.candidate` (line 63)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.rho` (line 64)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.prescribed_residue` (line 66)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.prescriptions_agree_on_overlaps` (line 68)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.every_pair_has_global_lift` (line 72)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.generator` (line 78)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.no_simultaneous_representation` (line 80)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.datum` (line 94)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.datum_continuous` (line 96)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.absolute_obstruction_zero` (line 99)
- `def Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.simultaneousClass` (line 106)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.simultaneous_obstruction_nonzero` (line 110)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.absolute_primitive_exists_with_nonzero_gluing_class` (line 120)
- `theorem Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample.no_simultaneous_lift_even_up_to_local_conjugacy` (line 144)

## TameStrictVersusConjugateExample.lean

- `abbrev Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.C2` (line 11)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.G` (line 12)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.M9` (line 13)
- `abbrev Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.M3` (line 14)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.reduction` (line 16)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.matrixReduction` (line 17)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.a` (line 19)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.b` (line 25)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.conjugator` (line 31)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.conjugator_reduces_to_one` (line 37)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.local_involutions_same_residue` (line 39)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.local_involutions_kernel_conjugate` (line 41)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.local_involutions_do_not_commute` (line 43)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.group_order_isUnit` (line 45)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.signA` (line 47)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.signB` (line 52)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.globalCandidate` (line 57)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.explicit_simultaneous_local_conjugacy` (line 65)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.explicit_local_residue_compatibility` (line 69)
- `def Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.generator` (line 72)
- `theorem Komorebi.StrongArtin.SquareZeroH2.TameGluingExample.no_literal_global_lift` (line 74)

## Evidence scope

41 theorem declarations, 36 definitions, 11 abbreviations: 88 named constants audited. 899 new source lines. 12 unchanged direct dependency sources and 9 new sources replayed, plus AxiomAudit.lean. No custom axioms, sorry, admit, unsafe, native_decide, or custom opaque declarations in active sources.

Finite examples use kernel-checked `decide`. The allowed axiom set is `propext`, `Classical.choice`, `Quot.sound`. The general theorems preserve the source topology and make no discrete-source assumption.
