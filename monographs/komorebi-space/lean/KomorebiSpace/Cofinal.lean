import KomorebiSpace.Realization
import Mathlib.Order.Monotone.Basic

set_option autoImplicit false

/-!
# Cofinal invariance of realized exact information

This proves an equivalence of inverse-limit point types. It does not assert
invariance of an arbitrary weighted residual sum or of an undefined cohomology.
-/
universe u
namespace KomorebiSpace
namespace Resolution

abbrev UnboundedSchedule (φ : ℕ → ℕ) : Prop := ∀ n, ∃ j, n ≤ φ j

def reindex (X : Resolution.{u}) (φ : ℕ → ℕ) (hφ : Monotone φ) : Resolution.{u} where
  Obj := fun n => X.Obj (φ n)
  restrict := fun h => X.restrict (hφ h)
  restrict_refl := fun n x => X.restrict_refl (φ n) x
  restrict_trans := fun hij hjk x => X.restrict_trans (hφ hij) (hφ hjk) x

def sample (X : Resolution.{u}) (φ : ℕ → ℕ) (hφ : Monotone φ)
    (x : X.Point) : (X.reindex φ hφ).Point :=
  ⟨fun n => x.val (φ n), fun i j h => x.property (φ i) (φ j) (hφ h)⟩

noncomputable def pickIndex {φ : ℕ → ℕ} (hcof : UnboundedSchedule φ) (n : ℕ) : ℕ :=
  Classical.choose (hcof n)

theorem pickIndex_spec {φ : ℕ → ℕ} (hcof : UnboundedSchedule φ) (n : ℕ) :
    n ≤ φ (pickIndex hcof n) := Classical.choose_spec (hcof n)

noncomputable def recoveredCoordinate (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ)
    (y : (X.reindex φ hφ).Point) (n : ℕ) : X.Obj n :=
  X.restrict (pickIndex_spec hcof n) (y.val (pickIndex hcof n))

/-- The recovered coordinate is independent of the chosen sufficiently fine sample. -/
theorem recoveredCoordinate_eq (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ)
    (y : (X.reindex φ hφ).Point) (n j : ℕ) (h : n ≤ φ j) :
    recoveredCoordinate X φ hφ hcof y n = X.restrict h (y.val j) := by
  let p := pickIndex hcof n
  let k := max p j
  have hp : p ≤ k := Nat.le_max_left _ _
  have hj : j ≤ k := Nat.le_max_right _ _
  have yp : X.restrict (hφ hp) (y.val k) = y.val p := y.property p k hp
  have yj : X.restrict (hφ hj) (y.val k) = y.val j := y.property j k hj
  change X.restrict (pickIndex_spec hcof n) (y.val p) = X.restrict h (y.val j)
  calc
    X.restrict (pickIndex_spec hcof n) (y.val p) =
        X.restrict (pickIndex_spec hcof n) (X.restrict (hφ hp) (y.val k)) :=
      congrArg (X.restrict (pickIndex_spec hcof n)) yp.symm
    _ = X.restrict (Nat.le_trans (pickIndex_spec hcof n) (hφ hp)) (y.val k) :=
      X.restrict_trans _ _ _
    _ = X.restrict h (X.restrict (hφ hj) (y.val k)) :=
      (X.restrict_trans h (hφ hj) (y.val k)).symm
    _ = X.restrict h (y.val j) := congrArg (X.restrict h) yj

noncomputable def extend (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ)
    (y : (X.reindex φ hφ).Point) : X.Point := by
  refine ⟨recoveredCoordinate X φ hφ hcof y, ?_⟩
  intro i j hij
  let p := pickIndex hcof j
  have hj : j ≤ φ p := pickIndex_spec hcof j
  calc
    X.restrict hij (recoveredCoordinate X φ hφ hcof y j) =
        X.restrict hij (X.restrict hj (y.val p)) :=
      congrArg (X.restrict hij) (recoveredCoordinate_eq X φ hφ hcof y j p hj)
    _ = X.restrict (Nat.le_trans hij hj) (y.val p) := X.restrict_trans _ _ _
    _ = recoveredCoordinate X φ hφ hcof y i :=
      (recoveredCoordinate_eq X φ hφ hcof y i p (Nat.le_trans hij hj)).symm

@[simp] theorem extend_sample (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) (x : X.Point) :
    extend X φ hφ hcof (sample X φ hφ x) = x := by
  apply Point.ext
  intro n
  exact x.property n (φ (pickIndex hcof n)) (pickIndex_spec hcof n)

@[simp] theorem sample_extend (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ)
    (y : (X.reindex φ hφ).Point) :
    sample X φ hφ (extend X φ hφ hcof y) = y := by
  apply Point.ext
  intro n
  change recoveredCoordinate X φ hφ hcof y (φ n) = y.val n
  rw [recoveredCoordinate_eq X φ hφ hcof y (φ n) n (Nat.le_refl _)]
  exact X.restrict_refl _ _

/-- Canonical restriction equivalence; its inverse is independent of choice. -/
noncomputable def cofinalEquiv (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    X.Point ≃ (X.reindex φ hφ).Point where
  toFun := sample X φ hφ
  invFun := extend X φ hφ hcof
  left_inv := extend_sample X φ hφ hcof
  right_inv := sample_extend X φ hφ hcof

theorem sample_injective (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    Function.Injective (sample X φ hφ) := (cofinalEquiv X φ hφ hcof).injective

theorem double_monotone : Monotone (fun n : ℕ => 2*n) := by
  intro a b h; change 2*a ≤ 2*b; omega

theorem double_unbounded : UnboundedSchedule (fun n : ℕ => 2*n) := by
  intro n; exact ⟨n, by change n ≤ 2*n; omega⟩

end Resolution
end KomorebiSpace
