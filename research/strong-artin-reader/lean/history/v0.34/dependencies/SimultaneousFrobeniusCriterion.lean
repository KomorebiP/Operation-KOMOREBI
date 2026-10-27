import SimultaneousPrimaryNorm
import NonsemisimpleFrobeniusLifting
import FrobeniusLocalizationCokernel

/-! The same correction x is transported through the ACTUAL square-zero kernel
coordinates. Criteria concern inherited obstruction classes and original unit roots. -/
noncomputable section
namespace Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates
open Komorebi.StrongArtin.SimultaneousNorm
open Komorebi.StrongArtin.NonsemisimpleNorm
variable {G A B k V I : Type} [Group G] [Ring A] [Ring B]
variable [Field k] [AddCommGroup V] [Module k V]
variable {D : Datum G A B} {F : Aˣ} (S : FrobeniusLinearCoordinates D F k V)

theorem matchingClass_zero_iff_linear_localization (d : I → ℕ) (U : I → Aˣ)
    (hU : ∀ i, D.q (U i) = D.q (F^d i)) :
    D.frobeniusMatchingClass F d U hU = 0 ↔
      LocalizationSolvable S.operator d
        (fun i => S.coordinates (D.unitMismatch (U i) (F^d i) (hU i))) := by
  change (Submodule.Quotient.mk _ : D.FrobeniusLocalizationCokernel F d) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨⟨x,z⟩,he⟩
    refine ⟨S.coordinates x,fun i => S.coordinates (z i),?_⟩
    intro i
    have hi := congrArg S.coordinates (congrFun he i)
    simp only [D.frobeniusLocalization_apply, map_sub, map_add,
      S.norm_coordinates, S.conjugate_pow_coordinates] at hi
    exact hi.symm
  · rintro ⟨x,z,hz⟩
    refine ⟨(S.coordinates.symm x,fun i => S.coordinates.symm (z i)),?_⟩
    funext i
    apply S.coordinates.injective
    simp only [D.frobeniusLocalization_apply, map_sub, map_add,
      S.norm_coordinates, S.conjugate_pow_coordinates, S.coordinates.apply_symm_apply]
    exact (hz i).symm

/-- Exact simultaneous ORIGINAL Frobenius-root criterion. -/
theorem simultaneous_matching_iff_linear_localization (d : I → ℕ) (U : I → Aˣ)
    (hU : ∀ i, D.q (U i) = D.q (F^d i)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ ∃ u : I → Aˣ,
      (∀ i, D.q (u i) = 1) ∧ ∀ i, u i * F'^d i * (u i)⁻¹ = U i) ↔
      LocalizationSolvable S.operator d
        (fun i => S.coordinates (D.unitMismatch (U i) (F^d i) (hU i))) := by
  rw [D.simultaneous_frobenius_matching_iff_class_zero,
    S.matchingClass_zero_iff_linear_localization]

/-- Prime-power prescriptions: exact criterion for the inherited cokernel class. -/
theorem primePower_matchingClass_zero_iff_pivot (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (a : I → ℕ) (U : I → Aˣ)
    (hU : ∀ i, D.q (U i) = D.q (F^(p^a i)))
    (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let e := fun i => S.coordinates (D.unitMismatch (U i) (F^(p^a i)) (hU i))
    D.frobeniusMatchingClass F (fun i => p^a i) U hU = 0 ↔
      e i₀ ∈ LinearMap.range ((S.operator-1)^(p^a i₀-1)) ∧
      ∀ i, e i - ((S.operator-1)^(p^a i-p^a i₀)) (e i₀) ∈
        LinearMap.range ((S.operator-1)^(p^a i)) := by
  dsimp only
  rw [S.matchingClass_zero_iff_linear_localization]
  exact primePower_localization_iff_pivot S.operator p a _ i₀ hmin

/-- Mixed positive degrees on an eigenvalue-one primary kernel block. -/
theorem unipotent_matchingClass_zero_iff_pivot
    (hN : IsNilpotent (S.operator-1)) (m a : I → ℕ) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : ∀ i, (m i : k) ≠ 0)
    (U : I → Aˣ) (hU : ∀ i, D.q (U i) = D.q (F^(m i*p^a i)))
    (i₀ : I) (hmin : ∀ i, p^a i₀ ≤ p^a i) :
    let e := fun i => S.coordinates (D.unitMismatch (U i) (F^(m i*p^a i)) (hU i))
    let f := normalizedUnipotentErrors S.operator hN m a p hm e
    D.frobeniusMatchingClass F (fun i => m i*p^a i) U hU = 0 ↔
      f i₀ ∈ LinearMap.range ((S.operator-1)^(p^a i₀-1)) ∧
      ∀ i, f i - ((S.operator-1)^(p^a i-p^a i₀)) (f i₀) ∈
        LinearMap.range ((S.operator-1)^(p^a i)) := by
  dsimp only
  rw [S.matchingClass_zero_iff_linear_localization]
  exact unipotent_localization_iff_pivot S.operator hN m a p hm _ i₀ hmin

/-- A non-one primary kernel block has only the already-classified individual obstructions. -/
theorem primary_ne_one_matchingClass_zero_iff (lam : k)
    (hN : IsNilpotent (S.operator-algebraMap k (Module.End k V) lam))
    (hl0 : lam ≠ 0) (hl1 : lam ≠ 1) (m a : I → ℕ) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : ∀ i, (m i : k) ≠ 0)
    (U : I → Aˣ) (hU : ∀ i, D.q (U i) = D.q (F^(m i*p^a i))) :
    D.frobeniusMatchingClass F (fun i => m i*p^a i) U hU = 0 ↔
      ∀ i, S.coordinates (D.unitMismatch (U i) (F^(m i*p^a i)) (hU i)) ∈
        LinearMap.range ((S.operator-algebraMap k (Module.End k V) lam)^
          resonanceExponent (m i) p (a i) lam) := by
  rw [S.matchingClass_zero_iff_linear_localization]
  exact simultaneous_primary_ne_one_iff S.operator lam hN hl0 hl1 m a p hm _

end Komorebi.StrongArtin.SquareZeroH2.FrobeniusLinearCoordinates
