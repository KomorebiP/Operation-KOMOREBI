import PaperXI.HeisenbergCochain
import PaperXI.SymplecticCoordinates

/-! A given quadratic refinement on an intrinsic finite F2-space supplies an
actual bilinear factor set, hence a finite Heisenberg extension. Coordinates are
constructed from the form; its square profile is the given refinement, not erased. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicHeisenbergLift
open scoped BigOperators Classical
open PaperXI.Dyadic PaperXI.DyadicAffine PaperXI.DyadicCoordinates PaperXI.BilinearHeisenberg
variable {ι : Type*} [Fintype ι]

/-- The standard factor set with declared squares on both axes of every plane. -/
def coordinateFactor (a : ι → F2 × F2) :
    LinearMap.BilinForm F2 (ι → F2 × F2) where
  toFun x :=
    { toFun := fun y => ∑ i, ((x i).1 * (y i).2 +
        (a i).1 * (x i).1 * (y i).1 + (a i).2 * (x i).2 * (y i).2)
      map_add' := by
        intro y z
        simp only [Pi.add_apply, Prod.fst_add, Prod.snd_add]
        rw [← Finset.sum_add_distrib]
        apply Finset.sum_congr rfl
        intro i hi
        ring
      map_smul' := by
        intro r y
        change (∑ i, ((x i).1 * (r * (y i).2) +
          (a i).1 * (x i).1 * (r * (y i).1) + (a i).2 * (x i).2 * (r * (y i).2))) =
          r * (∑ i, ((x i).1 * (y i).2 +
          (a i).1 * (x i).1 * (y i).1 + (a i).2 * (x i).2 * (y i).2))
        rw [Finset.mul_sum]
        apply Finset.sum_congr rfl
        intro i hi
        ring }
  map_add' := by
    intro x z
    apply LinearMap.ext
    intro y
    change (∑ i, (((x + z) i).1 * (y i).2 +
      (a i).1 * ((x + z) i).1 * (y i).1 + (a i).2 * ((x + z) i).2 * (y i).2)) =
      (∑ i, ((x i).1 * (y i).2 + (a i).1 * (x i).1 * (y i).1 +
      (a i).2 * (x i).2 * (y i).2)) +
      (∑ i, ((z i).1 * (y i).2 + (a i).1 * (z i).1 * (y i).1 +
      (a i).2 * (z i).2 * (y i).2))
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i hi
    simp only [Pi.add_apply, Prod.fst_add, Prod.snd_add]
    ring
  map_smul' := by
    intro r x
    apply LinearMap.ext
    intro y
    change (∑ i, ((r * (x i).1) * (y i).2 +
      (a i).1 * (r * (x i).1) * (y i).1 + (a i).2 * (r * (x i).2) * (y i).2)) =
      r * (∑ i, ((x i).1 * (y i).2 + (a i).1 * (x i).1 * (y i).1 +
      (a i).2 * (x i).2 * (y i).2))
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro i hi
    ring

@[simp] theorem coordinateFactor_apply (a x y : ι → F2 × F2) :
    coordinateFactor a x y = ∑ i, ((x i).1 * (y i).2 +
      (a i).1 * (x i).1 * (y i).1 + (a i).2 * (x i).2 * (y i).2) := rfl

theorem coordinateFactor_commutator (a x y : ι → F2 × F2) :
    coordinateFactor a x y - coordinateFactor a y x = symplectic x y := by
  simp only [coordinateFactor_apply, symplectic_apply, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro i hi
  rw [sub_eq_add_neg, CharTwo.neg_eq]
  ring_nf
  simp only [show (2 : F2) = 0 from rfl, mul_zero, add_zero]

theorem coordinateFactor_diagonal (a x : ι → F2 × F2) :
    coordinateFactor a x x = quadratic a x := by
  simp only [coordinateFactor_apply, quadratic, plane]
  apply Finset.sum_congr rfl
  intro i hi
  have hs (t : F2) : t * t = t := by fin_cases t <;> rfl
  have hx := hs (x i).1
  have hy := hs (x i).2
  simp only [mul_assoc, hx, hy]

variable {V : Type*} [AddCommGroup V] [Module F2 V]

/-- Transport the actual quadratic refinement into the constructed coordinates. -/
def coordinateRefinementOf (b : LinearMap.BilinForm F2 V) (Q : Refinement b)
    (e : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y)) : Refinement (symplectic (ι := ι)) where
  value x := Q.value (e.symm x)
  polar x y := by
    rw [map_add, Q.polar, he]
    simp

/-- Pull back the explicit factor set; no central extension is an input. -/
def factorOfCoordinates (b : LinearMap.BilinForm F2 V) (Q : Refinement b)
    (e : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y)) : LinearMap.BilinForm F2 V :=
  (coordinateFactor (refinementCoefficients (coordinateRefinementOf b Q e he))).compl₁₂
    e.toLinearMap e.toLinearMap

theorem factorOfCoordinates_commutator (b : LinearMap.BilinForm F2 V) (Q : Refinement b)
    (e : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y)) (x y : V) :
    factorOfCoordinates b Q e he x y - factorOfCoordinates b Q e he y x = b x y := by
  change coordinateFactor _ (e x) (e y) - coordinateFactor _ (e y) (e x) = b x y
  rw [coordinateFactor_commutator, ← he]

theorem factorOfCoordinates_diagonal (b : LinearMap.BilinForm F2 V) (Q : Refinement b)
    (e : V ≃ₗ[F2] (ι → F2 × F2))
    (he : ∀ x y, b x y = symplectic (e x) (e y)) (x : V) :
    factorOfCoordinates b Q e he x x = Q.value x := by
  change coordinateFactor _ (e x) (e x) = Q.value x
  rw [coordinateFactor_diagonal, ← refinement_coordinate_formula]
  simp [coordinateRefinementOf]

variable [FiniteDimensional F2 V]

/-- Every refinement of a finite nondegenerate alternating F2-form has an actual
bilinear lift, including the supplied square data. A basis is constructed, not assumed. -/
theorem exists_factor (b : LinearMap.BilinForm F2 V) (ha : b.IsAlt)
    (hb : b.SeparatingLeft) (Q : Refinement b) :
    ∃ c : LinearMap.BilinForm F2 V,
      (∀ x y, c x y - c y x = b x y) ∧ (∀ x, c x x = Q.value x) := by
  obtain ⟨r, e, he⟩ := SymplecticCoordinates.exists_coordinates b ha hb
  exact ⟨factorOfCoordinates b Q e he,
    factorOfCoordinates_commutator b Q e he, factorOfCoordinates_diagonal b Q e he⟩

/-- A deterministic-in-the-foundations choice of bilinear lift. It is not a
claim of canonical functoriality or a normalized symplectic-group action. -/
def factor (b : LinearMap.BilinForm F2 V) (ha : b.IsAlt)
    (hb : b.SeparatingLeft) (Q : Refinement b) : LinearMap.BilinForm F2 V :=
  Classical.choose (exists_factor b ha hb Q)

theorem factor_commutator (b : LinearMap.BilinForm F2 V) (ha : b.IsAlt)
    (hb : b.SeparatingLeft) (Q : Refinement b) (x y : V) :
    factor b ha hb Q x y - factor b ha hb Q y x = b x y :=
  (Classical.choose_spec (exists_factor b ha hb Q)).1 x y

theorem factor_diagonal (b : LinearMap.BilinForm F2 V) (ha : b.IsAlt)
    (hb : b.SeparatingLeft) (Q : Refinement b) (x : V) :
    factor b ha hb Q x x = Q.value x :=
  (Classical.choose_spec (exists_factor b ha hb Q)).2 x

/-- The actual group constructed from Q has exactly Q as its lift-square map. -/
theorem square_profile (b : LinearMap.BilinForm F2 V) (ha : b.IsAlt)
    (hb : b.SeparatingLeft) (Q : Refinement b) (h : Element (factor b ha hb Q)) :
    h * h = i (factor b ha hb Q) (Multiplicative.ofAdd (Q.value h.vector)) := by
  rw [HeisenbergCochain.square, factor_diagonal]

end PaperXI.DyadicHeisenbergLift
