import PaperX.QuadraticAlgebra
import PaperX.Reconstruction
import PaperX.Compactness
import Mathlib.Data.Fintype.EquivFin

/-! Actual quadratic roots and allowed root sets commute with adic completion.
The finite-level existence theorem uses positive precisions and does not assume
surjective reduction maps or a previously chosen compatible root family. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.QuadraticRootCompletion
open PaperX.QuadraticAlgebra
variable {R : Type} [CommRing R] (I : Ideal R)

/-- Roots in all quotient rings, with actual quotient reduction compatibility. -/
@[ext] structure Family where
  values : (n : ℕ) → Root (R ⧸ I ^ n)
  compatible : ∀ {m n : ℕ} (h : m ≤ n),
    mapRoot (Ideal.Quotient.factorPow I h) (values n) = values m

def reduce (x : Root R) : Family I where
  values n := mapRoot (Ideal.Quotient.mk (I ^ n)) x
  compatible := by
    intro m n h
    apply Subtype.ext
    simp

/-- The compatible roots give actual points of the integer quadratic ring. -/
def pointFamily (x : Family I) : PaperX.Reconstruction.RingFamily (CoordinateRing ℤ) I where
  maps n := (rootPoint ℤ (x.values n)).toRingHom
  compatible := by
    intro m n h
    apply AdjoinRoot.ringHom_ext
    · exact Subsingleton.elim _ _
    · have hc := congrArg Subtype.val (x.compatible h)
      change (Ideal.Quotient.factorPow I h)
        ((rootPoint ℤ (x.values n)) (coordinate ℤ)) =
          (rootPoint ℤ (x.values m)) (coordinate ℤ)
      simpa only [rootPoint_coordinate, mapRoot_val] using hc

/-- Reconstruction uses the checked ring-map reconstruction universal property. -/
def reconstruct [IsAdicComplete I R] (x : Family I) : Root R :=
  let f := PaperX.Reconstruction.reconstruct I (pointFamily I x)
  ⟨f (coordinate ℤ), by simpa only [map_pow, map_one] using congrArg f (coordinate_sq ℤ)⟩

theorem reconstruct_reduces [IsAdicComplete I R] (x : Family I) (n : ℕ) :
    mapRoot (Ideal.Quotient.mk (I ^ n)) (reconstruct I x) = x.values n := by
  apply Subtype.ext
  have h := congrArg (fun f : CoordinateRing ℤ →+* R ⧸ I ^ n => f (coordinate ℤ))
    (PaperX.Reconstruction.reconstruct_reduces I (pointFamily I x) n)
  simpa only [mapRoot_val, reconstruct, RingHom.comp_apply, pointFamily,
    AlgHom.toRingHom_eq_coe, AlgHom.coe_toRingHom, rootPoint_coordinate] using h

theorem root_ext [IsHausdorff I R] {x y : Root R}
    (h : ∀ n, mapRoot (Ideal.Quotient.mk (I ^ n)) x =
      mapRoot (Ideal.Quotient.mk (I ^ n)) y) : x = y := by
  apply Subtype.ext
  have H := IsHausdorff.funext' I (f := fun _ : Unit => x.val)
    (g := fun _ : Unit => y.val) (fun n _ => congrArg Subtype.val (h n))
  exact congrFun H ()

theorem reconstruct_unique [IsAdicComplete I R] (x : Family I) (y : Root R)
    (h : ∀ n, mapRoot (Ideal.Quotient.mk (I ^ n)) y = x.values n) :
    y = reconstruct I x := by
  apply root_ext I
  intro n
  rw [h n, reconstruct_reduces]

theorem reconstruct_reduce [IsAdicComplete I R] (x : Root R) :
    reconstruct I (reduce I x) = x :=
  (reconstruct_unique I (reduce I x) x (fun _ => rfl)).symm

theorem reduce_reconstruct [IsAdicComplete I R] (x : Family I) :
    reduce I (reconstruct I x) = x := by
  ext n
  exact congrArg Subtype.val (reconstruct_reduces I x n)

/-- Root-valued form of the universal property, with uniqueness. -/
def reconstructionEquiv [IsAdicComplete I R] : Root R ≃ Family I where
  toFun := reduce I
  invFun := reconstruct I
  left_inv := reconstruct_reduce I
  right_inv := reduce_reconstruct I

/-- Only positive precisions are constrained. -/
structure Conditions where
  allowed : (k : ℕ) → Root (R ⧸ I ^ (k + 1)) → Prop
  downward : ∀ {j k : ℕ} (h : j ≤ k) x, allowed k x →
    allowed j (mapRoot (Ideal.Quotient.factorPow I (Nat.add_le_add_right h 1)) x)

def tower (C : Conditions I) : PaperX.Compactness.Tower where
  Level k := {x : Root (R ⧸ I ^ (k + 1)) // C.allowed k x}
  parent k x := ⟨mapRoot (Ideal.Quotient.factorPow I
    (Nat.add_le_add_right (Nat.le_succ k) 1)) x.val, C.downward (Nat.le_succ k) _ x.property⟩

def branchValue (C : Conditions I) (b : PaperX.Compactness.Branch (tower I C)) :
    (n : ℕ) → Root (R ⧸ I ^ n)
  | 0 => ⟨1, by simp⟩
  | n + 1 => (b.value n).val

theorem branchValue_compatible (C : Conditions I)
    (b : PaperX.Compactness.Branch (tower I C)) {j k : ℕ} (h : j ≤ k) :
    mapRoot (Ideal.Quotient.factorPow I h) (branchValue I C b k) =
      branchValue I C b j := by
  apply Subtype.ext
  apply (Ideal.Quotient.eq_factor_of_eq_factor_succ
    (fun _ _ h => Ideal.pow_le_pow_right h)
    (fun m => (branchValue I C b m).val) ?_ h).symm
  intro m
  cases m with
  | zero =>
    have : Subsingleton (R ⧸ I ^ 0) := by
      simpa only [pow_zero, Ideal.one_eq_top] using (inferInstance : Subsingleton (R ⧸ (⊤ : Ideal R)))
    exact Subsingleton.elim _ _
  | succ m =>
    exact (congrArg (fun x => x.val.val) (b.compatible m)).symm

def branchFamily (C : Conditions I) (b : PaperX.Compactness.Branch (tower I C)) :
    Family I where
  values := branchValue I C b
  compatible := branchValue_compatible I C b

theorem finite_levels (C : Conditions I)
    (finite : ∀ k, Finite {x : Root (R ⧸ I ^ (k + 1)) // C.allowed k x}) :
    PaperX.Compactness.FiniteLevels (tower I C) := by
  intro k
  let : Finite ((tower I C).Level k) := finite k
  let : Fintype ((tower I C).Level k) := Fintype.ofFinite _
  classical
  exact ⟨Finset.univ.toList, by simp⟩

/-- The actual root has every required finite reduction. -/
def Realizes (C : Conditions I) (x : Root R) : Prop :=
  ∀ k, C.allowed k (mapRoot (Ideal.Quotient.mk (I ^ (k + 1))) x)

/-- Finite, nonempty, downward-closed positive levels suffice. -/
theorem exists_realization [IsAdicComplete I R] (C : Conditions I)
    (finite : ∀ k, Finite {x : Root (R ⧸ I ^ (k + 1)) // C.allowed k x})
    (occupied : ∀ k, ∃ x, C.allowed k x) :
    ∃ x : Root R, Realizes I C x := by
  obtain ⟨b⟩ := PaperX.Compactness.finite_branch_compactness (tower I C)
    (finite_levels I C finite) (fun k => let ⟨x,h⟩ := occupied k; ⟨x,h⟩)
  refine ⟨reconstruct I (branchFamily I C b), ?_⟩
  intro k
  rw [reconstruct_reduces]
  exact (b.value k).property

/-- Necessity does not need completeness or finiteness. -/
theorem levels_of_realization (C : Conditions I) (x : Root R) (h : Realizes I C x) :
    ∀ k, ∃ y, C.allowed k y :=
  fun k => ⟨mapRoot (Ideal.Quotient.mk (I ^ (k + 1))) x, h k⟩

theorem realization_iff [IsAdicComplete I R] (C : Conditions I)
    (finite : ∀ k, Finite {x : Root (R ⧸ I ^ (k + 1)) // C.allowed k x}) :
    (∃ x : Root R, Realizes I C x) ↔ ∀ k, ∃ y, C.allowed k y :=
  ⟨fun ⟨x,h⟩ => levels_of_realization I C x h, exists_realization I C finite⟩

/-- Here finite quotient rings really do imply finite root levels. -/
theorem realization_iff_of_finite_quotients [IsAdicComplete I R] (C : Conditions I)
    (finite : ∀ k, Finite (R ⧸ I ^ (k + 1))) :
    (∃ x : Root R, Realizes I C x) ↔ ∀ k, ∃ y, C.allowed k y := by
  apply realization_iff I C
  intro k
  let : Finite (R ⧸ I ^ (k + 1)) := finite k
  infer_instance

end PaperX.QuadraticRootCompletion
