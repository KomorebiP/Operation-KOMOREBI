import PaperXI.HeisenbergForm
import PaperXI.HeisenbergGeometry
import Mathlib.LinearAlgebra.Dual.Lemmas

/-! Dimension and cardinality of a maximal isotropic subspace in the standard
Heisenberg symplectic space. No cardinality or self-orthogonality conclusion is
assumed as an input. -/

set_option autoImplicit false

namespace PaperXI.HeisenbergCardinality

open Module PaperXI.HeisenbergForm PaperXI.HeisenbergGeometry

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

theorem form_isAlt : LinearMap.BilinForm.IsAlt (form (K := K) (X := X)) := form_self

theorem form_separatingLeft : (form (K := K) (X := X)).SeparatingLeft := by
  intro v hv
  apply Prod.ext
  · apply (Module.forall_dual_apply_eq_zero_iff K v.1).mp
    intro φ
    simpa using hv (0, φ)
  · apply LinearMap.ext
    intro x
    simpa using hv (x, 0)

theorem form_nondegenerate : (form (K := K) (X := X)).Nondegenerate := by
  refine ⟨form_separatingLeft, ?_⟩
  intro v hv
  apply form_separatingLeft v
  intro w
  exact form_isAlt.isRefl _ _ (hv w)

/-- Pairing with every vector vanishes precisely at zero. -/
theorem form_forall_eq_zero_iff (v : X × Module.Dual K X) :
    (∀ w, form v w = 0) ↔ v = 0 := by
  exact ⟨form_separatingLeft v, fun h => by simp [h]⟩

theorem maximal_orthogonal_eq (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) :
    LinearMap.BilinForm.orthogonal form L = L :=
  orthogonal_eq (form (K := K) (X := X)) form_isAlt L hL

variable [FiniteDimensional K X]

theorem finrank_eq (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) : finrank K L = finrank K X := by
  have h := two_mul_finrank (form (K := K) (X := X)) form_isAlt form_nondegenerate L hL
  rw [Module.finrank_prod, Subspace.dual_finrank_eq] at h
  omega

theorem natCard_eq_pow (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) :
    Nat.card L = Nat.card K ^ finrank K X := by
  rw [Module.natCard_eq_pow_finrank (K := K) (V := L), finrank_eq L hL]

theorem natCard_eq (L : Submodule K (X × Module.Dual K X))
    (hL : IsMaximalIsotropic form L) : Nat.card L = Nat.card X := by
  calc
    Nat.card L = Nat.card K ^ finrank K X := natCard_eq_pow L hL
    _ = Nat.card X := (Module.natCard_eq_pow_finrank (K := K) (V := X)).symm

end PaperXI.HeisenbergCardinality
