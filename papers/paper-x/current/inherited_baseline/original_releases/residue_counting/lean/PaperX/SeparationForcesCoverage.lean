import Mathlib.Algebra.Group.ConjFinite
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.RepresentationTheory.Character

/-! A necessary coverage condition for square trace separation.
This is an obstruction theorem: it does not establish arithmetic prime coverage.
The row count is the number of conjugacy classes. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SeparationForcesCoverage

section FiniteClasses
variable {C X R : Type*} [Fintype C] [DecidableEq C] [CommRing R]

/-- A square nonsingular evaluation matrix of functions constant on fibers
must sample every fiber label when the label set is the row index set. -/
theorem surjective_labels_of_det_ne_zero (label : X → C) (f : C → X → R)
    (hf : ∀ i x y, label x = label y → f i x = f i y) (points : C → X)
    (hdet : Matrix.det (fun i j : C => f j (points i)) ≠ 0) :
    Function.Surjective (fun i => label (points i)) := by
  apply Finite.surjective_of_injective
  intro i j hij
  by_contra hne
  exact hdet (Matrix.det_zero_of_row_eq hne (funext fun k => hf k _ _ hij))

/-- Missing even one label rules out every square nonsingular evaluation matrix
of the indicated size. Repeating the available samples does not help. -/
theorem det_eq_zero_of_missing_label (label : X → C) (f : C → X → R)
    (hf : ∀ i x y, label x = label y → f i x = f i y)
    (missing : C) (hmiss : ∀ x, label x ≠ missing) (points : C → X) :
    Matrix.det (fun i j : C => f j (points i)) = 0 := by
  by_contra hdet
  obtain ⟨i, hi⟩ := surjective_labels_of_det_ne_zero label f hf points hdet missing
  exact hmiss (points i) hi
end FiniteClasses

section Groups
variable {G X K : Type*} [Group G] [Fintype G] [Field K]
local instance : Fintype (ConjClasses G) := Fintype.ofFinite _
local instance : DecidableEq (ConjClasses G) := Classical.decEq _

/-- When the matrix has one row for every conjugacy class, its invertibility
forces the sample family to meet every conjugacy class. -/
theorem conjugacy_coverage_of_det_ne_zero
    (s : X → G) (χ : ConjClasses G → G → K)
    (hχ : ∀ i g h, IsConj g h → χ i g = χ i h)
    (points : ConjClasses G → X)
    (hdet : Matrix.det (fun i j : ConjClasses G => χ j (s (points i))) ≠ 0) :
    ∀ g : G, ∃ i : ConjClasses G, IsConj (s (points i)) g := by
  classical
  have hs := surjective_labels_of_det_ne_zero
    (fun x => ConjClasses.mk (s x)) (fun j x => χ j (s x))
    (fun i x y h => hχ i _ _ (ConjClasses.mk_eq_mk_iff_isConj.mp h)) points hdet
  intro g
  obtain ⟨i, hi⟩ := hs (ConjClasses.mk g)
  exact ⟨i, ConjClasses.mk_eq_mk_iff_isConj.mp hi⟩

/-- Finite-deletion square separation for a complete-size class-function family
already forces finite-deletion conjugacy coverage. -/
theorem cofinite_coverage_of_square_separation
    (s : X → G) (χ : ConjClasses G → G → K)
    (hχ : ∀ i g h, IsConj g h → χ i g = χ i h)
    (hsep : ∀ bad : Finset X, ∃ points : ConjClasses G → X,
      (∀ i, points i ∉ bad) ∧
      Matrix.det (fun i j : ConjClasses G => χ j (s (points i))) ≠ 0) :
    ∀ (bad : Finset X) (g : G), ∃ x : X, x ∉ bad ∧ IsConj (s x) g := by
  classical
  intro bad g
  obtain ⟨points, hp, hd⟩ := hsep bad
  obtain ⟨i, hi⟩ := conjugacy_coverage_of_det_ne_zero s χ hχ points hd g
  exact ⟨points i, hp i, hi⟩

/-- The obstruction applies to actual representation characters, even with
varying representation spaces. It assumes the number of rows equals the
number of finite conjugacy classes, but does not assume character completeness. -/
theorem representation_coverage_of_square_separation
    (V : ConjClasses G → Type*) [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]
    (ρ : (i : ConjClasses G) → Representation K G (V i)) (s : X → G)
    (hsep : ∀ bad : Finset X, ∃ points : ConjClasses G → X,
      (∀ i, points i ∉ bad) ∧
      Matrix.det (fun i j : ConjClasses G =>
        Representation.character (ρ j) (s (points i))) ≠ 0) :
    ∀ (bad : Finset X) (g : G), ∃ x : X, x ∉ bad ∧ IsConj (s x) g := by
  apply cofinite_coverage_of_square_separation s
    (fun i g => Representation.character (ρ i) g) ?_ hsep
  intro i g h hgh
  obtain ⟨a, ha⟩ := isConj_iff.mp hgh
  rw [← ha, Representation.char_conj]
end Groups
end PaperX.SeparationForcesCoverage
