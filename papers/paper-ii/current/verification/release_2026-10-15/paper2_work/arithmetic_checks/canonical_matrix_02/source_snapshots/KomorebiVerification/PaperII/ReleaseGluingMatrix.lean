import KomorebiVerification.PaperII.ReleaseGluingSmith
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs

/-! Actual invertible matrix changes give Smith bases of an inclusion. -/

set_option autoImplicit false
open scoped Matrix

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {W : Type v} {I : Type w}
variable [CommRing O] [AddCommGroup W] [Module O W]
variable [Fintype I] [DecidableEq I]

/-- The matrix Smith equation for the actual inclusion yields actual Smith bases. -/
theorem smith_bases_of_inclusion_matrix
    (S : Submodule O W) (b : Module.Basis I O W) (c : Module.Basis I O S)
    (U V : Matrix.GeneralLinearGroup I O) (d : I → O)
    (hmat : (U : Matrix I I O) * LinearMap.toMatrix c b S.subtype *
      (V : Matrix I I O) = Matrix.diagonal d) :
    ∃ (b' : Module.Basis I O W) (c' : Module.Basis I O S),
      ∀ i, (c' i : W) = d i • b' i := by
  let eU := (Matrix.GeneralLinearGroup.toLin U).toLinearEquiv
  let eV := (Matrix.GeneralLinearGroup.toLin V).toLinearEquiv
  let b' := Module.Basis.ofEquivFun (b.equivFun.trans eU)
  let c' := Module.Basis.ofEquivFun (c.equivFun.trans eV.symm)
  refine ⟨b', c', ?_⟩
  intro i
  have hc : c.equivFun (c' i) = eV (Pi.single i 1) := by
    have hci : c' i = c.equivFun.symm (eV (Pi.single i 1)) := by
      change (Module.Basis.ofEquivFun (c.equivFun.trans eV.symm)) i = _
      rw [Module.Basis.coe_ofEquivFun]
      rfl
    rw [hci, c.equivFun.apply_symm_apply]
  have hb : LinearMap.toMatrix c b S.subtype *ᵥ c.equivFun (c' i) =
      b.equivFun (c' i : W) := by
    exact LinearMap.toMatrix_mulVec_repr c b S.subtype (c' i)
  have hcalc : eU (b.equivFun (c' i : W)) = (Matrix.diagonal d) *ᵥ Pi.single i 1 := by
    rw [← hb, hc]
    change (U : Matrix I I O) *ᵥ
      (LinearMap.toMatrix c b S.subtype *ᵥ ((V : Matrix I I O) *ᵥ Pi.single i 1)) = _
    rw [Matrix.mulVec_mulVec, Matrix.mulVec_mulVec, hmat]
  apply b'.repr.injective
  ext j
  change eU (b.equivFun (c' i : W)) j = b'.repr (d i • b' i) j
  rw [hcalc]
  simp [Matrix.mulVec_diagonal, Pi.single_apply, Finsupp.single_apply, eq_comm]

variable [IsDomain O]

omit [IsDomain O] in
/-- Smith form of the original inclusion matrix gives the actual quotient decomposition. -/
theorem inclusion_matrix_smith_quotient
    (S : Submodule O W) (b : Module.Basis I O W) (c : Module.Basis I O S)
    (U V : Matrix.GeneralLinearGroup I O) (pi : O) (a : I → ℕ)
    (hmat : (U : Matrix I I O) * LinearMap.toMatrix c b S.subtype *
      (V : Matrix I I O) = Matrix.diagonal (fun i => pi ^ a i)) :
    Nonempty ((W ⧸ S) ≃ₗ[O] (∀ i, O ⧸ Ideal.span {pi ^ a i})) := by
  obtain ⟨b', c', hc⟩ := smith_bases_of_inclusion_matrix S b c U V (fun i => pi ^ a i) hmat
  exact ⟨smithInclusionQuotientEquiv S b' c' pi a hc⟩

/-- Exact weight from the Smith form of an arbitrary chosen inclusion matrix. -/
theorem globalWeight_eq_smith_max_of_inclusion_matrix
    {X : Type*} [AddCommGroup X] [Module O X]
    {J : Type*} [Fintype J] (P : Projectors O X J) (Λ : Submodule O X)
    (b : Module.Basis I O Λ) (c : Module.Basis I O (splitInside P Λ))
    (U V : Matrix.GeneralLinearGroup I O) (pi : O) (hpi : pi ≠ 0)
    (hunit : ¬ IsUnit pi) (a : I → ℕ)
    (hmat : (U : Matrix I I O) * LinearMap.toMatrix c b (splitInside P Λ).subtype *
      (V : Matrix I I O) = Matrix.diagonal (fun i => pi ^ a i))
    (finite : ∀ j, ∃ s, ClearsPacket P Λ pi j s) :
    globalWeight P Λ pi finite = Finset.univ.sup a := by
  obtain ⟨b', c', hc⟩ := smith_bases_of_inclusion_matrix _ b c U V (fun i => pi ^ a i) hmat
  exact globalWeight_eq_smith_max P Λ b' c' pi hpi hunit a hc finite

end Komorebi.PaperII.ReleaseGluing
