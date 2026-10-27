import Mathlib.RingTheory.Artinian.Ring
import Mathlib.RingTheory.Localization.AtPrime.Basic
import Mathlib.RingTheory.Idempotents

set_option autoImplicit false

/-! The exact canonical algebraic input of Paper XII, external Fact 8.1.
The supplied equivalence is a ring decomposition, not a module decomposition
or a localization equivalence for the representation. Those are outputs of
the subsequent packet theorems. The R-algebra structure fixes every canonical
localization coordinate. No new axiom is introduced. -/
namespace PaperXII.ArtinData

open scoped BigOperators

variable {R : Type*} [CommRing R]

/-- The canonical ring decomposition supplied by external Fact 8.1. -/
abbrev Decomposition (R : Type*) [CommRing R] :=
  R ≃ₐ[R] (∀ m : MaximalSpectrum R, Localization.AtPrime m.asIdeal)

/-- The actual central idempotent indexed by a maximal ideal. -/
noncomputable def idempotent (D : Decomposition R) (m : MaximalSpectrum R) : R := by
  classical
  exact D.symm (Pi.single m 1)

/-- Every coordinate is the canonical localization map, by R-algebra linearity. -/
theorem coordinate (D : Decomposition R) (r : R) (m : MaximalSpectrum R) :
    D r m = algebraMap R (Localization.AtPrime m.asIdeal) r := by
  have h := D.commutes r
  exact congrFun h m

/-- The canonical coordinate maps determine the decomposition uniquely. -/
theorem decomposition_unique (D₁ D₂ : Decomposition R) : D₁ = D₂ := by
  ext r m
  rw [coordinate, coordinate]

/-- The coordinate-vector identity determines the idempotent uniquely. -/
theorem map_idempotent [DecidableEq (MaximalSpectrum R)]
    (D : Decomposition R) (m : MaximalSpectrum R) :
    D (idempotent D m) = Pi.single m 1 := by
  simp only [idempotent, AlgEquiv.apply_symm_apply]
  congr 1
  exact Subsingleton.elim _ _

theorem idem (D : Decomposition R) (m : MaximalSpectrum R) :
    IsIdempotentElem (idempotent D m) := by
  classical
  apply D.injective
  simp only [map_mul, map_idempotent, ← Pi.single_mul, one_mul]

theorem complete [Fintype (MaximalSpectrum R)] (D : Decomposition R) :
    CompleteOrthogonalIdempotents (idempotent D) := by
  classical
  exact (CompleteOrthogonalIdempotents.single
    (fun m : MaximalSpectrum R => Localization.AtPrime m.asIdeal)).map D.symm.toRingHom

theorem algebraMap_idempotent_self (D : Decomposition R) (m : MaximalSpectrum R) :
    algebraMap R (Localization.AtPrime m.asIdeal) (idempotent D m) = 1 := by
  classical
  rw [← coordinate, map_idempotent]
  exact Pi.single_eq_same _ _

theorem algebraMap_idempotent_other (D : Decomposition R) (m n : MaximalSpectrum R)
    (h : m ≠ n) :
    algebraMap R (Localization.AtPrime n.asIdeal) (idempotent D m) = 0 := by
  classical
  rw [← coordinate, map_idempotent]
  exact Pi.single_eq_of_ne h.symm _

theorem idempotent_not_mem (D : Decomposition R) (m : MaximalSpectrum R) :
    idempotent D m ∉ m.asIdeal := by
  have h : IsUnit (algebraMap R (Localization.AtPrime m.asIdeal) (idempotent D m)) := by
    rw [algebraMap_idempotent_self]
    exact isUnit_one
  exact (IsLocalization.AtPrime.isUnit_to_map_iff
    (Localization.AtPrime m.asIdeal) m.asIdeal _).mp h

/-- Vanishing in the localized ring is exactly vanishing after multiplication
by the corresponding canonical idempotent. -/
theorem mul_idempotent_eq_zero_iff (D : Decomposition R) (m : MaximalSpectrum R) (r : R) :
    r * idempotent D m = 0 ↔
      algebraMap R (Localization.AtPrime m.asIdeal) r = 0 := by
  classical
  constructor
  · intro h
    have hh := congrArg (algebraMap R (Localization.AtPrime m.asIdeal)) h
    simpa [map_mul, algebraMap_idempotent_self] using hh
  · intro h
    apply D.injective
    ext n
    by_cases hn : m = n
    · subst n
      simp [map_mul, coordinate, algebraMap_idempotent_self, h]
    · simp [map_mul, coordinate, algebraMap_idempotent_other D m n hn]

end PaperXII.ArtinData
