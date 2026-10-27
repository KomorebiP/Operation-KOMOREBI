import Mathlib.RepresentationTheory.Character
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! The literal character element of a finite complex group algebra.
Centrality and scalar action are proved from character orthogonality. -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators MonoidAlgebra Classical
namespace PaperXI.CharacterProjector
variable {G V W : Type*} [Group G] [Fintype G]
variable [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
variable [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]

/-- The character sum, with the actual inverse and degree normalization. -/
def element (ρ : Representation ℂ G V) : MonoidAlgebra ℂ G :=
  ((Module.finrank ℂ V : ℂ) / Fintype.card G) •
    ∑ g : G, MonoidAlgebra.single g (ρ.character g⁻¹)

omit [FiniteDimensional ℂ V] in
@[simp] theorem coeff_element (ρ : Representation ℂ G V) (g : G) :
    (element ρ).coeff g =
      ((Module.finrank ℂ V : ℂ) / Fintype.card G) * ρ.character g⁻¹ := by
  simp [element, MonoidAlgebra.coeff_sum, Finsupp.single_apply]

omit [FiniteDimensional ℂ V] in
theorem central (ρ : Representation ℂ G V) :
    element ρ ∈ Submonoid.center (MonoidAlgebra ℂ G) := by
  rw [Submonoid.mem_center_iff]
  intro a
  induction a using MonoidAlgebra.induction_on with
  | of h =>
    ext g
    simp only [MonoidAlgebra.of_apply, MonoidAlgebra.coeff_single_mul_apply,
      MonoidAlgebra.coeff_mul_single_apply, one_mul, mul_one, coeff_element, mul_inv_rev,
      inv_inv]
    rw [ρ.char_mul_comm]
  | add a b ha hb => simp only [add_mul, mul_add, ha, hb]
  | smul c a ha => simp only [smul_mul_assoc, mul_smul_comm, ha]

omit [FiniteDimensional ℂ V] [FiniteDimensional ℂ W] in
/-- Expanded action of the literal group-algebra element. -/
theorem action (ρ : Representation ℂ G V) (σ : Representation ℂ G W) :
    σ.asAlgebraHom (element ρ) =
      ((Module.finrank ℂ V : ℂ) / Fintype.card G) •
        ∑ g : G, ρ.character g⁻¹ • σ g := by
  simp [element]

omit [Fintype G] in
/-- Every central element acts scalarly on an irreducible complex representation. -/
theorem central_scalar (σ : Representation ℂ G W) [Representation.IsIrreducible σ]
    {a : MonoidAlgebra ℂ G} (ha : a ∈ Submonoid.center (MonoidAlgebra ℂ G)) :
    ∃ c : ℂ, σ.asAlgebraHom a = c • (1 : Module.End ℂ W) := by
  obtain ⟨c, hc⟩ := (Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
    (ρ := σ)).surjective (Representation.IntertwiningMap.centralAlgebraMul σ ha)
  exact ⟨c, (congrArg Representation.IntertwiningMap.toLinearMap hc).symm⟩

omit [Fintype G] [FiniteDimensional ℂ V] in
theorem nontrivial_space (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    Nontrivial V := by
  by_contra h
  have : Subsingleton V := not_nontrivial_iff_subsingleton.mp h
  exact bot_ne_top (Subrepresentation.toSubmodule_injective
    (Subsingleton.elim (⊥ : Subrepresentation ρ).toSubmodule ⊤))

omit [Fintype G] in
theorem degree_ne_zero (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ] :
    (Module.finrank ℂ V : ℂ) ≠ 0 := by
  have := nontrivial_space ρ
  exact_mod_cast (Module.finrank_pos (R := ℂ) (M := V)).ne'

/-- Selection of the designated irreducible isomorphism class. -/
theorem irreducible_action (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ] :
    σ.asAlgebraHom (element ρ) =
      if Nonempty (Representation.Equiv ρ σ) then 1 else 0 := by
  have hcard : (Nat.card G : ℂ) ≠ 0 := by exact_mod_cast (Nat.card_pos (α := G)).ne'
  let : Invertible (Nat.card G : ℂ) := invertibleOfNonzero hcard
  obtain ⟨c, hc⟩ := central_scalar σ (central ρ)
  have ht := congrArg (LinearMap.trace ℂ W) hc
  rw [action ρ σ] at ht
  simp only [map_smul, map_sum, smul_eq_mul, LinearMap.trace_one] at ht
  change (Module.finrank ℂ V : ℂ) / Fintype.card G *
    (∑ g : G, ρ.character g⁻¹ * σ.character g) = c * Module.finrank ℂ W at ht
  have ho := Representation.char_orthonormal σ ρ
  rw [Fintype.card_eq_nat_card, div_eq_mul_inv, mul_assoc] at ht
  simp_rw [mul_comm (ρ.character _)] at ht
  rw [ho] at ht
  by_cases he : Nonempty (Representation.Equiv ρ σ)
  · let e := Classical.choice he
    have hd := e.toLinearEquiv.finrank_eq
    have hc1 : c = 1 := by
      simp only [ite_eq_left he, mul_one] at ht
      rw [hd] at ht
      exact (mul_right_cancel₀ (degree_ne_zero σ)) (by simpa using ht.symm)
    simp [he, hc, hc1]
  · have hc0 : c = 0 := by
      simpa [he, degree_ne_zero σ] using ht.symm
    simp [he, hc, hc0]

end PaperXI.CharacterProjector
