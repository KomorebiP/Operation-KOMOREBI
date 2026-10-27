import PaperXI.CentralProduct
import PaperXI.CentralExtensionStructure
import Mathlib.Algebra.Group.Pi.Lemmas

/-! The actual quotient commutator is the product of the factor commutators.
Scalar nondegeneracy is inherited without assuming a faithful central character. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralProduct

open CentralExtension CocycleCommutator
variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A : S → Type*} [∀ s, _root_.Group (H s)] [∀ s, CommGroup (A s)]
variable (D : ∀ s, CentralExtension.Datum Z (H s) (A s))

theorem commutator_mk (x y : Ambient (Z := Z) (H := H)) :
    centralCommutator (datum D) (mk D x) (mk D y) =
      ∏ s, centralCommutator (D s) (x.2 s) (y.2 s) := by
  apply (datum D).i_injective
  rw [i_centralCommutator, datum_i, ← map_inv, ← map_inv,
    ← map_mul, ← map_mul, ← map_mul]
  have h : x * y * x⁻¹ * y⁻¹ = (1,
      fun s => (D s).i (centralCommutator (D s) (x.2 s) (y.2 s))) := by
    apply Prod.ext
    · change x.1 * y.1 * x.1⁻¹ * y.1⁻¹ = 1
      simp [mul_assoc]
    · funext s
      exact (i_centralCommutator (D s) _ _).symm
  rw [h, mk_centers, one_mul]

/-- The scalar commutator on the actual product quotient factors componentwise. -/
theorem scalar_commutator_product (ζ : Z →* ℂˣ) (a b : ∀ s, A s) :
    commutator (scalarCocycle (datum D) ζ) a b =
      ∏ s, commutator (scalarCocycle (D s) ζ) (a s) (b s) := by
  let x : Ambient (Z := Z) (H := H) :=
    (1, fun s => sectionMap (D s) (a s))
  let y : Ambient (Z := Z) (H := H) :=
    (1, fun s => sectionMap (D s) (b s))
  have hx : (datum D).q (mk D x) = a := by ext s; simp [x]
  have hy : (datum D).q (mk D y) = b := by ext s; simp [y]
  rw [← hx, ← hy, scalar_commutator, commutator_mk, map_prod]
  apply Finset.prod_congr rfl
  intro s _
  simpa [x, y] using (scalar_commutator (D s) ζ (sectionMap (D s) (a s))
    (sectionMap (D s) (b s))).symm

/-- Test each coordinate with a single supported quotient element. -/
theorem radical_eq_bot (ζ : Z →* ℂˣ)
    (hnd : ∀ s, radical (scalarCocycle (D s) ζ) = ⊥) :
    radical (scalarCocycle (datum D) ζ) = ⊥ := by
  classical
  rw [Subgroup.eq_bot_iff_forall]
  intro a ha
  funext s
  apply ((Subgroup.eq_bot_iff_forall _).mp (hnd s))
  rw [mem_radical_iff]
  intro b
  have hh := (mem_radical_iff _ _).mp ha (Pi.mulSingle s b)
  rw [scalar_commutator_product] at hh
  rw [Finset.prod_eq_single s] at hh
  · simpa using hh
  · intro t _ hts
    simp [Pi.mulSingle_eq_of_ne hts]
  · simp

/-- The full center is exactly the common retained center under the same hypothesis. -/
theorem full_center (ζ : Z →* ℂˣ)
    (hnd : ∀ s, radical (scalarCocycle (D s) ζ) = ⊥) :
    Subgroup.center (Group D) = (center D).range :=
  CentralExtension.center_eq_range (datum D) ζ (radical_eq_bot D ζ hnd)

end PaperXI.CentralProduct
