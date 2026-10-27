import PaperICompletion8.SemisimpleFormula

/-! Coherent multiplicity presentations for actual modules over a product
of matrix rings. Simple summands are identified with natural factors by a
nonzero column projection and Schur's lemma, then grouped by their factor.
No multiplicity equality or module decomposition is supplied by the caller. -/
set_option autoImplicit false
set_option linter.unusedSectionVars false

namespace Komorebi.PaperICompletion8.ProductPresentation

open scoped DirectSum
open Komorebi.PaperICompletion8.DivisionProduct
open Komorebi.PaperICompletion8.RegularMultiplicity
open Komorebi.PaperICompletion8.SemisimpleFormula

universe u v w
variable {I : Type v} [Fintype I] [DecidableEq I]
variable {D : I → Type u} [∀ i, DivisionRing (D i)]
variable (d : I → ℕ)

/-- Every actual simple module is isomorphic to a natural factor, without choosing it as an input. -/
theorem simple_equiv_natural (S : Type w) [AddCommGroup S]
    [Module (DivisionProductAlgebra (D := D) d) S]
    [IsSimpleModule (DivisionProductAlgebra (D := D) d) S]
    (hd : ∀ i, 0 < d i) :
    ∃ i : I, Nonempty (S ≃ₗ[DivisionProductAlgebra (D := D) d] Simple (D := D) d i) := by
  classical
  let A := DivisionProductAlgebra (D := D) d
  let : Nontrivial S := IsSimpleModule.nontrivial A S
  obtain ⟨J, ⟨e⟩⟩ := IsSemisimpleRing.exists_linearEquiv_ideal_of_isSimpleModule A S
  let f : S →ₗ[A] MultiplicityModule (D := D) d d :=
    (regularColumnsEquiv d).toLinearMap ∘ₗ J.subtype ∘ₗ e.toLinearMap
  have hf : Function.Injective f :=
    (regularColumnsEquiv d).injective.comp (J.subtype_injective.comp e.injective)
  obtain ⟨x, hx⟩ := exists_ne (0 : S)
  have hfx : f x ≠ 0 := by
    intro h
    exact hx (hf (h.trans f.map_zero.symm))
  obtain ⟨i, hi⟩ : ∃ i : I, f x i ≠ 0 := by
    by_contra h
    apply hfx
    funext i
    by_contra hh
    exact h ⟨i, hh⟩
  obtain ⟨j, hj⟩ : ∃ j : Fin (d i), f x i j ≠ 0 := by
    by_contra h
    apply hi
    funext j
    by_contra hh
    exact h ⟨j, hh⟩
  let g : S →ₗ[A] Simple (D := D) d i :=
    LinearMap.proj j ∘ₗ LinearMap.proj i ∘ₗ f
  have hg : g ≠ 0 := by
    intro h
    exact hj (congrArg (fun h : S →ₗ[A] Simple (D := D) d i ↦ h x) h)
  let := simple_isSimple (D := D) d i (hd i)
  exact ⟨i, ⟨LinearEquiv.ofBijective g (LinearMap.bijective_of_ne_zero hg)⟩⟩

/-- Grouping a finite family of simple factors is a genuine A-linear reindexing. -/
noncomputable def regroupSimpleFactors {J : Type w} [Fintype J] (f : J → I) :
    (∀ j : J, Simple (D := D) d (f j)) ≃ₗ[DivisionProductAlgebra (D := D) d]
      MultiplicityModule (D := D) d (fun i ↦ Fintype.card {j : J // f j = i}) := by
  classical
  let A := DivisionProductAlgebra (D := D) d
  let e (i : I) :
      (∀ j : {j : J // f j = i}, Simple (D := D) d (f j.1)) ≃ₗ[A]
        (Fin (Fintype.card {j : J // f j = i}) → Simple (D := D) d i) :=
    (LinearEquiv.piCongrRight fun j ↦ by
      rcases j with ⟨j, hj⟩
      subst i
      exact LinearEquiv.refl A _).trans
    (LinearEquiv.piCongrLeft A (fun _ : Fin (Fintype.card {j : J // f j = i}) ↦
      Simple (D := D) d i) (Fintype.equivFin {j : J // f j = i}))
  refine { __ := Equiv.piCongrFiberwise (fun i ↦ (e i).toEquiv)
           map_add' := ?_, map_smul' := ?_ }
  · intro x y
    funext i
    exact (e i).map_add _ _
  · intro a x
    funext i
    exact (e i).map_smul a _

/-- Every finitely generated module over the actual matrix product has a compatible multiplicity presentation. -/
theorem exists_multiplicity_presentation (M : Type w) [AddCommGroup M]
    [Module (DivisionProductAlgebra (D := D) d) M]
    [Module.Finite (DivisionProductAlgebra (D := D) d) M]
    (hd : ∀ i, 0 < d i) :
    ∃ m : I → ℕ,
      Nonempty (M ≃ₗ[DivisionProductAlgebra (D := D) d] MultiplicityModule (D := D) d m) := by
  classical
  let A := DivisionProductAlgebra (D := D) d
  obtain ⟨n, S, e, hS⟩ := IsSemisimpleModule.exists_linearEquiv_fin_dfinsupp A M
  letI (j : Fin n) : IsSimpleModule A (S j) := hS j
  choose f ef using fun j : Fin n ↦ simple_equiv_natural d (S j) hd
  exact ⟨fun i ↦ Fintype.card {j : Fin n // f j = i}, ⟨e.trans
    (DirectSum.linearEquivFunOnFintype A (Fin n) (fun j ↦ S j)) |>.trans
    (LinearEquiv.piCongrRight fun j ↦ (ef j).some) |>.trans
    (regroupSimpleFactors d f)⟩⟩

end Komorebi.PaperICompletion8.ProductPresentation
