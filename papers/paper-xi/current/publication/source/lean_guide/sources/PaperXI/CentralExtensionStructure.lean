import PaperXI.CentralExtensionCocycle
import Mathlib.GroupTheory.Subgroup.Center
import Mathlib.SetTheory.Cardinal.Finite

/-! Coordinates, cardinality, and intrinsic scalar nondegeneracy of an actual
central extension. Faithfulness is an explicit hypothesis when a central-valued
nondegeneracy statement is transported through a central character. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtension

open CocycleCommutator
variable {Z H A : Type*} [CommGroup Z] [Group H] [CommGroup A]
variable (D : Datum Z H A)

/-- The actual normal-coordinate equivalence of underlying types. -/
def coordinates : H ≃ Z × A where
  toFun h := (coordinate D h, D.q h)
  invFun p := D.i p.1 * sectionMap D p.2
  left_inv h := (normal_form D h).symm
  right_inv p := by
    apply Prod.ext
    · exact coordinate_eq_of_eq D _ _ _ rfl
    · simp

@[simp] theorem coordinates_apply (h : H) :
    coordinates D h = (coordinate D h, D.q h) := rfl

@[simp] theorem coordinates_symm_apply (z : Z) (a : A) :
    (coordinates D).symm (z, a) = D.i z * sectionMap D a := rfl

include D in
theorem finite_middle [Finite Z] [Finite A] : Finite H :=
  Finite.of_injective (coordinates D) (coordinates D).injective

include D in
/-- The order of the middle group is the product of kernel and quotient orders. -/
theorem natCard_eq : Nat.card H = Nat.card Z * Nat.card A := by
  rw [Nat.card_congr (coordinates D), Nat.card_prod]

include D in
theorem card_eq [Fintype H] [Fintype Z] [Fintype A] :
    Fintype.card H = Fintype.card Z * Fintype.card A := by
  simpa only [Fintype.card_prod] using Fintype.card_congr (coordinates D)

/-- Scalar nondegeneracy can be stated intrinsically on all actual group lifts,
without referring to the chosen quotient section. -/
theorem radical_scalarCocycle_eq_bot_iff (ζ : Z →* ℂˣ) :
    radical (scalarCocycle D ζ) = ⊥ ↔
      ∀ h : H, (∀ k : H, ζ (centralCommutator D h k) = 1) → D.q h = 1 := by
  rw [Subgroup.eq_bot_iff_forall]
  constructor
  · intro hnd h hh
    apply hnd (D.q h)
    rw [mem_radical_iff]
    intro a
    obtain ⟨k, rfl⟩ := D.q_surjective a
    rw [scalar_commutator]
    exact hh k
  · intro hnd a ha
    obtain ⟨h, rfl⟩ := D.q_surjective a
    apply hnd h
    intro k
    rw [← scalar_commutator]
    exact (mem_radical_iff _ _).mp ha (D.q k)

/-- A faithful central character carries intrinsic central nondegeneracy to
scalar nondegeneracy. Faithfulness cannot be replaced by mere nontriviality. -/
theorem radical_scalarCocycle_eq_bot_of_faithful (ζ : Z →* ℂˣ)
    (hζ : Function.Injective ζ)
    (hcentral : ∀ h : H, (∀ k : H, centralCommutator D h k = 1) → D.q h = 1) :
    radical (scalarCocycle D ζ) = ⊥ := by
  apply (radical_scalarCocycle_eq_bot_iff D ζ).2
  intro h hh
  apply hcentral h
  intro k
  apply hζ
  simpa only [map_one] using hh k

/-- For a faithful character the scalar and central cocycle radicals coincide. -/
theorem radical_scalarCocycle_of_injective (ζ : Z →* ℂˣ)
    (hζ : Function.Injective ζ) :
    radical (scalarCocycle D ζ) = radical (centralCocycle D) := by
  ext a
  rw [mem_radical_iff, mem_radical_iff]
  constructor
  · intro h b
    apply hζ
    simpa only [CocycleCommutator.commutator, scalarCocycle_coeff,
      centralCocycle, map_div, map_one] using h b
  · intro h b
    simpa only [CocycleCommutator.commutator, scalarCocycle_coeff,
      centralCocycle, map_div, map_one] using congrArg ζ (h b)

theorem radical_scalarCocycle_eq_bot_of_central (ζ : Z →* ℂˣ)
    (hζ : Function.Injective ζ) (hcentral : radical (centralCocycle D) = ⊥) :
    radical (scalarCocycle D ζ) = ⊥ := by
  rw [radical_scalarCocycle_of_injective D ζ hζ, hcentral]

/-- Scalar nondegeneracy forces the distinguished central subgroup to be the
full center of the actual middle group. -/
theorem center_eq_range (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥) : Subgroup.center H = D.i.range := by
  apply le_antisymm
  · intro h hh
    rw [D.range_i_eq_ker_q]
    apply (radical_scalarCocycle_eq_bot_iff D ζ).1 hnd h
    intro k
    have hc : centralCommutator D h k = 1 := by
      apply D.i_injective
      rw [i_centralCommutator, map_one, ← (Subgroup.mem_center_iff.mp hh k)]
      group
    simp only [hc, map_one]
  · rintro _ ⟨z, rfl⟩
    exact Subgroup.mem_center_iff.mpr (fun h => (D.central z h).symm)

end PaperXI.CentralExtension
