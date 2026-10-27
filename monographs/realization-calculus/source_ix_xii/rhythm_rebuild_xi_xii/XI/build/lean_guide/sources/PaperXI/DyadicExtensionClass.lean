import PaperXI.DyadicHeisenbergLift
import Mathlib.LinearAlgebra.Basis.Defs

/-! A prescribed square profile determines the bilinear F2-extension up to an
actual center- and quotient-preserving isomorphism. We construct the coboundary
with the upper-triangular part in an ordinary basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DyadicExtensionClass
open BilinearHeisenberg
variable {V : Type*} [AddCommGroup V] [Module (ZMod 2) V]

/-- Upper-triangular half of an alternating F2-bilinear form in a chosen basis. -/
def upper {n : ℕ} (e : Module.Basis (Fin n) (ZMod 2) V)
    (d : LinearMap.BilinForm (ZMod 2) V) : LinearMap.BilinForm (ZMod 2) V :=
  e.constr (ZMod 2) (fun i => e.constr (ZMod 2) (fun j => if i < j then d (e i) (e j) else 0))

@[simp] theorem upper_basis {n : ℕ} (e : Module.Basis (Fin n) (ZMod 2) V)
    (d : LinearMap.BilinForm (ZMod 2) V) (i j : Fin n) :
    upper e d (e i) (e j) = if i < j then d (e i) (e j) else 0 := by
  simp only [upper, Module.Basis.constr_basis]

/-- The triangular construction recovers the entire alternating form. -/
theorem upper_symmetrization {n : ℕ} (e : Module.Basis (Fin n) (ZMod 2) V)
    (d : LinearMap.BilinForm (ZMod 2) V) (ha : d.IsAlt) :
    upper e d + (upper e d).flip = d := by
  apply e.ext
  intro i
  apply e.ext
  intro j
  change upper e d (e i) (e j) + upper e d (e j) (e i) = d (e i) (e j)
  rw [upper_basis, upper_basis]
  rcases lt_trichotomy i j with h | h | h
  · rw [ite_eq_left h, ite_eq_right (not_lt_of_ge (le_of_lt h)), add_zero]
  · subst j
    simp only [lt_irrefl, ite_false, zero_add]
    exact (ha (e i)).symm
  · rw [ite_eq_right (not_lt_of_ge (le_of_lt h)), ite_eq_left h, zero_add]
    exact SymplecticSplit.alternating_symmetric d ha (e j) (e i)

variable [FiniteDimensional (ZMod 2) V]

/-- Every alternating bilinear form, even degenerate, is a normalized
quadratic coboundary. This is constructed rather than supplied as extension data. -/
theorem exists_coboundary (d : LinearMap.BilinForm (ZMod 2) V) (ha : d.IsAlt) :
    ∃ f : V → ZMod 2, f 0 = 0 ∧
      ∀ x y, d x y = f (x + y) - f x - f y := by
  let e := Module.finBasis (ZMod 2) V
  let u := upper e d
  have hu : u + u.flip = d := upper_symmetrization e d ha
  refine ⟨fun x => u x x, by simp, ?_⟩
  intro x y
  have hxy := LinearMap.congr_fun (LinearMap.congr_fun hu x) y
  change u x y + u y x = d x y at hxy
  simp only [map_add, LinearMap.add_apply]
  linear_combination -hxy

/-- Matching diagonal factor sets give a genuine isomorphism over both the
central group and the quotient, without an isomorphism/coboundary hypothesis. -/
theorem exists_equiv_of_diagonal (c d : LinearMap.BilinForm (ZMod 2) V)
    (hd : ∀ v, c v v = d v v) :
    ∃ e : Element c ≃* Element d,
      (∀ z, e (i c z) = i d z) ∧ (∀ h, (e h).vector = h.vector) := by
  have ha : (d - c).IsAlt := by
    intro v
    change d v v - c v v = 0
    rw [hd, sub_self]
  obtain ⟨f, h0, hf⟩ := exists_coboundary (d - c) ha
  exact ⟨HeisenbergCochain.equiv c d f h0 hf,
    HeisenbergCochain.equiv_center c d f h0 hf,
    HeisenbergCochain.equiv_vector c d f h0 hf⟩

/-- Complete equivalence criterion for these actual bilinear F2-extensions. -/
theorem exists_equiv_iff_diagonal (c d : LinearMap.BilinForm (ZMod 2) V) :
    (∃ e : Element c ≃* Element d,
      (∀ z, e (i c z) = i d z) ∧ (∀ h, (e h).vector = h.vector)) ↔
      ∀ v, c v v = d v v := by
  constructor
  · rintro ⟨e, he, hq⟩ v
    exact HeisenbergCochain.diagonal_preserved c d e he hq v
  · exact exists_equiv_of_diagonal c d

/-- Different coordinate constructions for the same declared refinement give
isomorphic middle groups. No arbitrary form-preserving map is assumed to lift. -/
theorem refinement_model_independent
    (b : LinearMap.BilinForm (ZMod 2) V) (Q : DyadicAffine.Refinement b)
    (c d : LinearMap.BilinForm (ZMod 2) V)
    (hc : ∀ v, c v v = Q.value v) (hd : ∀ v, d v v = Q.value v) :
    ∃ e : Element c ≃* Element d,
      (∀ z, e (i c z) = i d z) ∧ (∀ h, (e h).vector = h.vector) :=
  exists_equiv_of_diagonal c d (fun v => (hc v).trans (hd v).symm)

end PaperXI.DyadicExtensionClass
