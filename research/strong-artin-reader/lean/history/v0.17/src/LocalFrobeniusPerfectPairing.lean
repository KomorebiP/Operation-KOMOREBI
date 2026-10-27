import FrobeniusCocycleQuotient
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Matrix.StdBasis

namespace Komorebi.StrongArtin.LocalFrobeniusPerfectPairing

open Komorebi.StrongArtin.SpectralTraceConjugacy
open Komorebi.StrongArtin.FrobeniusCocycleQuotient

noncomputable section

variable {k n : Type*} [Field k] [Fintype n] [DecidableEq n]

/-- The perfect trace pairing on square matrices, bundled as a map to the dual. -/
def tracePairingMap :
    Matrix n n k →ₗ[k] Module.Dual k (Matrix n n k) where
  toFun P := traceProbeLinear P
  map_add' P Q := by
    ext X
    simp [traceProbeLinear_apply, traceProbe, Matrix.add_mul]
  map_smul' a P := by
    ext X
    simp [traceProbeLinear_apply, traceProbe]

@[simp]
theorem tracePairingMap_apply (P X : Matrix n n k) :
    tracePairingMap P X = traceProbe P X := rfl

/-- The matrix trace pairing is left nondegenerate. -/
theorem tracePairingMap_injective :
    Function.Injective (tracePairingMap (k := k) (n := n)) := by
  intro P Q hPQ
  rw [Matrix.ext_iff_trace_mul_right]
  intro X
  have h := congrArg (fun f : Module.Dual k (Matrix n n k) => f X) hPQ
  simpa [tracePairingMap_apply, traceProbe] using h

/-- The matrix trace pairing identifies matrices with their full linear dual. -/
def tracePairingEquiv :
    Matrix n n k ≃ₗ[k] Module.Dual k (Matrix n n k) :=
  (tracePairingMap (k := k) (n := n)).linearEquivOfInjective
    tracePairingMap_injective (by simp)

@[simp]
theorem tracePairingEquiv_apply (P X : Matrix n n k) :
    tracePairingEquiv P X = traceProbe P X := rfl

/-- Matrices fixed by residual Frobenius conjugation. -/
def frobeniusCentralizer (A : (Matrix n n k)ˣ) :
    Submodule k (Matrix n n k) :=
  LinearMap.ker (frobeniusCoboundaryMap A)

/-- Being fixed by Frobenius conjugation is exactly commuting with Frobenius. -/
theorem mem_frobeniusCentralizer_iff_commute
    (A : (Matrix n n k)ˣ) (P : Matrix n n k) :
    P ∈ frobeniusCentralizer A ↔ Commute P (A : Matrix n n k) := by
  rw [frobeniusCentralizer, LinearMap.mem_ker]
  constructor
  · intro h
    have hEq : P = (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) := by
      simpa [frobeniusCoboundaryMap_apply] using sub_eq_zero.mp h
    show P * (A : Matrix n n k) = (A : Matrix n n k) * P
    calc
      P * (A : Matrix n n k) =
          ((A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k)) *
            (A : Matrix n n k) := congrArg
              (fun X : Matrix n n k => X * (A : Matrix n n k)) hEq
      _ = (A : Matrix n n k) * P := by simp [Matrix.mul_assoc]
  · intro hcomm
    apply sub_eq_zero.mpr
    calc
      P = (A : Matrix n n k) * P * (↑A⁻¹ : Matrix n n k) := by
        rw [← hcomm.eq]
        simp

/-- A Frobenius-centralizing matrix defines an annihilator of Frobenius coboundaries. -/
def centralizerToAnnihilator (A : (Matrix n n k)ˣ) :
    frobeniusCentralizer A →ₗ[k]
      (frobeniusCoboundaries A).dualAnnihilator where
  toFun P := ⟨tracePairingMap P.1, by
    rw [Submodule.mem_dualAnnihilator]
    exact frobeniusCoboundaries_le_ker_traceProbe A P.1
      ((mem_frobeniusCentralizer_iff_commute A P.1).mp P.2)⟩
  map_add' P Q := by
    apply Subtype.ext
    ext X
    simp [tracePairingMap_apply, traceProbe]
  map_smul' a P := by
    apply Subtype.ext
    ext X
    simp [tracePairingMap_apply, traceProbe]

@[simp]
theorem centralizerToAnnihilator_apply
    (A : (Matrix n n k)ˣ) (P : frobeniusCentralizer A)
    (X : Matrix n n k) :
    (centralizerToAnnihilator A P).1 X = traceProbe P.1 X := rfl

/-- The centralizer injects into the annihilator of the coboundary space. -/
theorem centralizerToAnnihilator_injective (A : (Matrix n n k)ˣ) :
    Function.Injective (centralizerToAnnihilator A) := by
  intro P Q h
  apply Subtype.ext
  apply tracePairingMap_injective
  exact congrArg Subtype.val h

/-- The Frobenius centralizer and the annihilator of Frobenius coboundaries have
exactly the same dimension. -/
theorem finrank_centralizer_eq_finrank_annihilator
    (A : (Matrix n n k)ˣ) :
    Module.finrank k (frobeniusCentralizer A) =
      Module.finrank k (frobeniusCoboundaries A).dualAnnihilator := by
  have hkerRange :
      Module.finrank k (LinearMap.range (frobeniusCoboundaryMap A)) +
          Module.finrank k (frobeniusCentralizer A) =
        Module.finrank k (Matrix n n k) := by
    change
      Module.finrank k (LinearMap.range (frobeniusCoboundaryMap A)) +
          Module.finrank k (LinearMap.ker (frobeniusCoboundaryMap A)) =
        Module.finrank k (Matrix n n k)
    exact LinearMap.finrank_range_add_finrank_ker (frobeniusCoboundaryMap A)
  have hann :
      Module.finrank k (LinearMap.range (frobeniusCoboundaryMap A)) +
          Module.finrank k (frobeniusCoboundaries A).dualAnnihilator =
        Module.finrank k (Matrix n n k) := by
    change
      Module.finrank k (LinearMap.range (frobeniusCoboundaryMap A)) +
          Module.finrank k (LinearMap.range (frobeniusCoboundaryMap A)).dualAnnihilator =
        Module.finrank k (Matrix n n k)
    exact Subspace.finrank_add_finrank_dualAnnihilator_eq
      (LinearMap.range (frobeniusCoboundaryMap A))
  exact Nat.add_left_cancel (hkerRange.trans hann.symm)

/-- The trace pairing identifies the Frobenius centralizer with the complete
annihilator of local Frobenius coboundaries. -/
def centralizerEquivAnnihilator (A : (Matrix n n k)ˣ) :
    frobeniusCentralizer A ≃ₗ[k]
      (frobeniusCoboundaries A).dualAnnihilator :=
  LinearMap.linearEquivOfInjective
    (K := k)
    (V := frobeniusCentralizer A)
    (V₂ := (frobeniusCoboundaries A).dualAnnihilator)
    (centralizerToAnnihilator A)
    (centralizerToAnnihilator_injective A)
    (finrank_centralizer_eq_finrank_annihilator A)

@[simp]
theorem centralizerEquivAnnihilator_apply
    (A : (Matrix n n k)ˣ) (P : frobeniusCentralizer A)
    (X : Matrix n n k) :
    (centralizerEquivAnnihilator A P).1 X = traceProbe P.1 X := by
  change (centralizerToAnnihilator A P).1 X = traceProbe P.1 X
  rfl

/-- **Perfect local Frobenius pairing.** The Frobenius centralizer is canonically
identified with the dual of tangent representatives modulo Frobenius coboundaries. -/
def centralizerEquivQuotientDual (A : (Matrix n n k)ˣ) :
    frobeniusCentralizer A ≃ₗ[k]
      Module.Dual k (Matrix n n k ⧸ frobeniusCoboundaries A) :=
  (centralizerEquivAnnihilator A).trans
    (Submodule.dualQuotEquivDualAnnihilator
      (frobeniusCoboundaries A)).symm

@[simp]
theorem centralizerEquivQuotientDual_apply_mkQ
    (A : (Matrix n n k)ˣ) (P : frobeniusCentralizer A)
    (X : Matrix n n k) :
    centralizerEquivQuotientDual A P
        ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
  change
    ((Submodule.dualQuotEquivDualAnnihilator
      (frobeniusCoboundaries A)).symm
      (centralizerEquivAnnihilator A P))
      (Submodule.Quotient.mk X) = traceProbe P.1 X
  rw [Submodule.dualQuotEquivDualAnnihilator_symm_apply_mk]
  exact centralizerEquivAnnihilator_apply A P X

/-- Every linear functional on the local Frobenius quotient is represented by a
unique Frobenius-centralizing matrix through the trace pairing. -/
theorem exists_unique_centralizer_representative
    (A : (Matrix n n k)ˣ)
    (φ : Module.Dual k (Matrix n n k ⧸ frobeniusCoboundaries A)) :
    ∃! P : frobeniusCentralizer A,
      ∀ X : Matrix n n k,
        φ ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
  let P := (centralizerEquivQuotientDual A).symm φ
  have hP : ∀ X : Matrix n n k,
      φ ((frobeniusCoboundaries A).mkQ X) = traceProbe P.1 X := by
    intro X
    calc
      φ ((frobeniusCoboundaries A).mkQ X) =
          centralizerEquivQuotientDual A P
            ((frobeniusCoboundaries A).mkQ X) := by
              rw [show centralizerEquivQuotientDual A P = φ by
                exact (centralizerEquivQuotientDual A).apply_symm_apply φ]
      _ = traceProbe P.1 X :=
        centralizerEquivQuotientDual_apply_mkQ A P X
  refine ⟨P, hP, ?_⟩
  intro Q hQ
  apply (centralizerEquivQuotientDual A).injective
  apply Submodule.quot_hom_ext
  intro X
  change
    centralizerEquivQuotientDual A Q
        ((frobeniusCoboundaries A).mkQ X) =
      centralizerEquivQuotientDual A P
        ((frobeniusCoboundaries A).mkQ X)
  rw [centralizerEquivQuotientDual_apply_mkQ,
    centralizerEquivQuotientDual_apply_mkQ]
  exact (hQ X).symm.trans (hP X)

end
end Komorebi.StrongArtin.LocalFrobeniusPerfectPairing

#print axioms Komorebi.StrongArtin.LocalFrobeniusPerfectPairing.tracePairingMap_injective
#print axioms Komorebi.StrongArtin.LocalFrobeniusPerfectPairing.centralizerEquivQuotientDual
#print axioms Komorebi.StrongArtin.LocalFrobeniusPerfectPairing.exists_unique_centralizer_representative
