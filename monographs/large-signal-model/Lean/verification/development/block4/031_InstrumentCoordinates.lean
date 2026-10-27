import KomorebiLSM.InstrumentCompletion
import KomorebiLSM.NormalizedDefect
import Mathlib.LinearAlgebra.Basis.VectorSpace

/-! Finite coordinates with the mass functional literally in coordinate zero.
The coordinate map is onto, its row space is exact, and branch maps are unique. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open Module FiniteBayes

section AnchoredBasis
variable {E : Type*} [AddCommGroup E] [Module ℝ E] [FiniteDimensional ℝ E]

/-- Extend one specified nonzero vector and place it at the first finite index. -/
theorem exists_basis_first (w : E) (hw : w ≠ 0) :
    ∃ (n : ℕ) (hn : 0 < n) (b : Basis (Fin n) ℝ E), b ⟨0,hn⟩ = w := by
  classical
  have hs : LinearIndepOn ℝ id ({w} : Set E) := linearIndepOn_singleton_iff.mpr hw
  let J := hs.extend (Set.subset_univ {w})
  let b : Basis J ℝ E := Basis.extend hs
  letI : Fintype J := FiniteDimensional.fintypeBasisIndex b
  let j0 : J := ⟨w, Basis.subset_extend hs (Set.mem_singleton w)⟩
  have hn : 0 < Fintype.card J := Fintype.card_pos_iff.mpr ⟨j0⟩
  let k0 : Fin (Fintype.card J) := ⟨0,hn⟩
  let e0 := Fintype.equivFin J
  let e := e0.trans (Equiv.swap (e0 j0) k0)
  have he : e j0 = k0 := by simp [e]
  refine ⟨Fintype.card J,hn,b.reindex e, ?_⟩
  change (b.reindex e) k0 = w
  rw [← he, Basis.reindex_apply, Equiv.symm_apply_apply]
  exact Basis.extend_apply_self hs j0

end AnchoredBasis

section RowCoordinates
variable {X : Type*} [AddCommGroup X] [Module ℝ X]
variable {J : Type*} [Fintype J] {W : Submodule ℝ (Dual ℝ X)}

/-- Basis evaluation is surjective onto the finite coordinate space. -/
theorem basis_observation_surjective [FiniteDimensional ℝ X] (b : Basis J ℝ W) :
    Function.Surjective (basisObservation b) := by
  intro z
  obtain ⟨x,hx⟩ := observableState_surjective W (b.constr ℝ z)
  refine ⟨x, ?_⟩
  funext j
  have hj := congrArg (fun f : Dual ℝ W => f (b j)) hx
  change (b j : Dual ℝ X) x = z j
  simpa only [observableState_apply, Basis.constr_basis] using hj

/-- The coordinate matrix has exactly the chosen observable row space. -/
theorem basis_observation_rowspace (b : Basis J ℝ W) :
    LinearMap.range (basisObservation b).dualMap = W := by
  classical
  apply le_antisymm
  · rintro r ⟨f,rfl⟩
    have he : (basisObservation b).dualMap f =
        ∑ j, f (pointMass j) • (b j : Dual ℝ X) := by
      ext x
      change f (basisObservation b x) = _
      rw [vector_eq_sum_pointMass (basisObservation b x), map_sum]
      simp only [map_smul, LinearMap.sum_apply, LinearMap.smul_apply, smul_eq_mul]
      apply Finset.sum_congr rfl
      intro j _
      exact mul_comm _ _
    rw [he]
    exact Submodule.sum_mem W (fun j _ => W.smul_mem _ (b j).property)
  · intro r hr
    refine ⟨basisRowReadout b ⟨r,hr⟩, ?_⟩
    ext x
    exact basisRowReadout_correct b ⟨r,hr⟩ x

/-- A full-row-rank observation map makes its reduced operator unique. -/
theorem closed_operator_unique {E : Type*} [AddCommGroup E] [Module ℝ E]
    (R : X →ₗ[ℝ] E) (hR : Function.Surjective R) (M : X →ₗ[ℝ] X)
    (B D : E →ₗ[ℝ] E) (hB : B.comp R = R.comp M) (hD : D.comp R = R.comp M) :
    D = B := by
  ext z
  obtain ⟨x,rfl⟩ := hR z
  exact congrArg (fun f : X →ₗ[ℝ] E => f x) (hD.trans hB.symm)

end RowCoordinates

section CompletionCoordinates
variable {I S : Type*} [Fintype I] [Nonempty I]

/-- P26's coordinate realization, including the first row, onto property,
exact row space and uniqueness. No supplied reduced operator is assumed. -/
theorem finite_instrument_coordinates
    (L : S → (I → ℝ) →ₗ[ℝ] (I → ℝ)) :
    ∃ (r : ℕ) (hr : 0 < r)
      (R : (I → ℝ) →ₗ[ℝ] (Fin r → ℝ))
      (B : S → (Fin r → ℝ) →ₗ[ℝ] (Fin r → ℝ)),
      r = finrank ℝ (instrumentCompletion L mass) ∧
      LinearIndependent ℝ (fun j => (LinearMap.proj j).comp R) ∧
      Function.Surjective R ∧
      LinearMap.range R.dualMap = instrumentCompletion L mass ∧
      (LinearMap.proj ⟨0,hr⟩).comp R = mass ∧
      (∀ s, (B s).comp R = R.comp (L s)) ∧
      (∀ s D, D.comp R = R.comp (L s) → D = B s) := by
  classical
  let W := instrumentCompletion L (mass : (I → ℝ) →ₗ[ℝ] ℝ)
  let w : W := ⟨mass, massRow_mem_completion L mass⟩
  have hw : w ≠ 0 := by
    intro h
    exact mass_ne_zero (congrArg (fun x : W => (x : Dual ℝ (I → ℝ))) h)
  obtain ⟨r,hr,b,hb⟩ := exists_basis_first w hw
  have hW := instrumentCompletion_invariant L (mass : (I → ℝ) →ₗ[ℝ] ℝ)
  refine ⟨r,hr,basisObservation b,basisTransition L hW b, ?_,
    basisObservation_independent b,basis_observation_surjective b,
    basis_observation_rowspace b, ?_,basisTransition_correct L hW b, ?_⟩
  · simpa only [Fintype.card_fin] using (Module.finrank_eq_card_basis b).symm
  · ext p
    change (b ⟨0,hr⟩ : Dual ℝ (I → ℝ)) p = mass p
    rw [hb]
  · intro s D hD
    exact closed_operator_unique (basisObservation b) (basis_observation_surjective b)
      (L s) (basisTransition L hW b s) D (basisTransition_correct L hW b s) hD

end CompletionCoordinates
end Komorebi.LSM.FiniteInstruments
