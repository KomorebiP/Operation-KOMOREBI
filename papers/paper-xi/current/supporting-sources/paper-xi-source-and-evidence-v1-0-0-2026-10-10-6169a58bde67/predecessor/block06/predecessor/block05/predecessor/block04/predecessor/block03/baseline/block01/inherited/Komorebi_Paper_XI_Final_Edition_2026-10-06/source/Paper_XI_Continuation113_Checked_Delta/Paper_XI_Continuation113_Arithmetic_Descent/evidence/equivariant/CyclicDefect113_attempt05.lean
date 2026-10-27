import PaperXI.ScalarCocycle112
import Mathlib.Data.Int.GCD
import Mathlib.Algebra.Group.Hom.Instances
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-! Explicit coprime correction of the character defect left by scalar
cocycle comparison. Arithmetic realization is not asserted here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicDefect113
open Finset
open ScalarCocycle112

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- Norm of an arbitrary scalar function along a finite cyclic orbit. -/
def orbitNorm (β : A ≃* A) (f : A → C) (n : ℕ) (a : A) : C :=
  ∏ i ∈ range n, f ((β ^ i) a)

/-- Weighted norm, formed in the character group. -/
def weightedCharacter (β : A ≃* A) (r : A →* C) (n : ℕ) : A →* C :=
  ∏ i ∈ range n, (r.comp (β ^ i).toMonoidHom) ^ i

@[simp] theorem orbitNorm_zero (β : A ≃* A) (f : A → C) (a : A) :
    orbitNorm β f 0 a = 1 := by simp [orbitNorm]

theorem orbitNorm_succ (β : A ≃* A) (f : A → C) (n : ℕ) (a : A) :
    orbitNorm β f (n+1) a = orbitNorm β f n a * f ((β ^ n) a) := by
  simp [orbitNorm, prod_range_succ]

@[simp] theorem weightedCharacter_zero (β : A ≃* A) (r : A →* C) (a : A) :
    weightedCharacter β r 0 a = 1 := by simp [weightedCharacter]

theorem weightedCharacter_succ (β : A ≃* A) (r : A →* C) (n : ℕ) (a : A) :
    weightedCharacter β r (n+1) a =
      weightedCharacter β r n a * r ((β ^ n) a) ^ n := by
  simp [weightedCharacter, prod_range_succ]

theorem power_apply_shift (β : A ≃* A) (n : ℕ) (a : A) :
    (β ^ n) (β a) = (β ^ (n+1)) a := by
  rw [pow_succ]
  rfl

/-- The weighted norm is an explicit contracting operator for cyclic defects. -/
theorem weightedCharacter_shift (β : A ≃* A) (r : A →* C) (n : ℕ) (a : A) :
    weightedCharacter β r n (β a) * orbitNorm β r n (β a) =
      weightedCharacter β r n a * r ((β ^ n) a) ^ n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [weightedCharacter_succ, orbitNorm_succ, weightedCharacter_succ,
      power_apply_shift]
    calc
      _ = (weightedCharacter β r n (β a) * orbitNorm β r n (β a)) *
          r ((β ^ (n+1)) a) ^ (n+1) := by rw [pow_succ (r ((β ^ (n+1)) a))]; ac_rfl
      _ = _ := by rw [ih]

/-- A Bezout power inverts n-th powers on the m-torsion subgroup. -/
theorem bezout_power {n m : ℕ} (hcop : n.Coprime m) (z : C) (hm : z ^ m = 1) :
    (z ^ n) ^ (Nat.gcdA n m) = z := by
  have hbez : (1 : ℤ) = n * Nat.gcdA n m + m * Nat.gcdB n m := by
    simpa only [hcop.gcd_eq_one, Int.natCast_one] using Nat.gcd_eq_gcd_ab n m
  calc
    (z ^ n) ^ (Nat.gcdA n m) = z ^ (n * Nat.gcdA n m) := by
      rw [← zpow_natCast, ← zpow_mul]
    _ = z ^ (n * Nat.gcdA n m) * z ^ (m * Nat.gcdB n m) := by
      rw [zpow_mul z (m : ℤ), zpow_natCast, hm, one_zpow, mul_one]
    _ = z := by rw [← zpow_add, ← hbez, zpow_one]

/-- The correcting character is explicit, using a weighted norm and Bezout. -/
def correctingCharacter (β : A ≃* A) (r : A →* C) (n m : ℕ) : A →* C :=
  weightedCharacter β r n ^ (Nat.gcdA n m)

/-- Every norm-one character defect for a coprime cyclic action is a
coboundary. No correcting character is assumed. -/
theorem correctingCharacter_coboundary (β : A ≃* A) (r : A →* C)
    (n m : ℕ) (hβ : β ^ n = 1) (hm : ∀ a : A, a ^ m = 1)
    (hcop : n.Coprime m) (hnorm : ∀ a, orbitNorm β r n a = 1) (a : A) :
    correctingCharacter β r n m (β a) / correctingCharacter β r n m a = r a := by
  have ht := weightedCharacter_shift β r n a
  rw [hnorm, mul_one, hβ] at ht
  change weightedCharacter β r n (β a) = weightedCharacter β r n a * r a ^ n at ht
  have hr : r a ^ m = 1 := by rw [← map_pow, hm, map_one]
  change weightedCharacter β r n (β a) ^ (Nat.gcdA n m) /
    weightedCharacter β r n a ^ (Nat.gcdA n m) = _
  rw [ht, mul_zpow, mul_div_cancel_left]
  exact bezout_power hcop (r a) hr


/-- An actual automorphism of a scalar extension, fixing the scalars and
covering the specified quotient automorphism. Its phase is not supplied. -/
structure ScalarLift (c : Cocycle A C) (β : A ≃* A) where
  action : Extension c ≃* Extension c
  on_base : ∀ x, (action x).base = β x.base
  fixes_scalar : ∀ z, action (Extension.scalarInclusion c z) =
    Extension.scalarInclusion c z

namespace ScalarLift
variable {c : Cocycle A C} {β : A ≃* A} (L : ScalarLift c β)

/-- The phase of the given lift on the fixed section. -/
def phase (a : A) : C := (L.action (Extension.sectionOf c a)).scalar

@[simp] theorem phase_one : L.phase 1 = 1 := by
  simp [phase]

/-- The lift on every element is determined by its derived section phase. -/
theorem scalar_formula (x : Extension c) :
    (L.action x).scalar = x.scalar * L.phase x.base := by
  have hx : x = Extension.scalarInclusion c x.scalar * Extension.sectionOf c x.base := by
    apply Extension.ext <;> simp [Extension.sectionOf, c.one_left]
  calc
    (L.action x).scalar =
        (L.action (Extension.scalarInclusion c x.scalar * Extension.sectionOf c x.base)).scalar :=
      congrArg (fun y => (L.action y).scalar) hx
    _ = _ := by
      rw [map_mul, L.fixes_scalar]
      simp [phase, c.one_left]

/-- The phase law follows from the actual lifted group automorphism. -/
theorem phase_mul (a b : A) :
    L.phase (a*b) = L.phase a * L.phase b * c.coeff (β a) (β b) / c.coeff a b := by
  have h := congrArg Extension.scalar
    (L.action.map_mul (Extension.sectionOf c a) (Extension.sectionOf c b))
  rw [L.scalar_formula] at h
  simp only [Extension.mul_scalar, Extension.mul_base, Extension.sectionOf,
    one_mul, phase, L.on_base] at h
  apply (eq_div_iff_mul_eq').mpr
  simpa only [phase, mul_comm] using h

theorem power_base (n : ℕ) (x : Extension c) :
    ((L.action ^ n) x).base = (β ^ n) x.base := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [pow_succ', pow_succ']
    change (L.action ((L.action ^ n) x)).base = β ((β ^ n) x.base)
    rw [L.on_base, ih]

/-- Iteration of the full lift derives the norm of its section phases. -/
theorem power_scalar (n : ℕ) (x : Extension c) :
    ((L.action ^ n) x).scalar = x.scalar * orbitNorm β L.phase n x.base := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ']
    change (L.action ((L.action ^ n) x)).scalar = _
    rw [L.scalar_formula, L.power_base, ih, orbitNorm_succ]
    exact mul_assoc _ _ _

/-- Honest finite order of the actual lift implies its phase norm is one. -/
theorem norm_eq_one (n : ℕ) (hn : L.action ^ n = 1) (a : A) :
    orbitNorm β L.phase n a = 1 := by
  have h := L.power_scalar n (Extension.sectionOf c a)
  rw [hn] at h
  simpa [Extension.sectionOf] using h.symm

end ScalarLift


/-- A function's coboundary has telescoping cyclic norm. -/
theorem orbitNorm_coboundary (β : A ≃* A) (s : A → C) (n : ℕ) (a : A) :
    orbitNorm β (fun b => s (β b) / s b) n a = s ((β ^ n) a) / s a := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [orbitNorm_succ, ih]
    have hβ : β ((β ^ n) a) = (β ^ (n+1)) a := by rw [pow_succ']; rfl
    rw [hβ]
    simp [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

theorem orbitNorm_mul (β : A ≃* A) (f g : A → C) (n : ℕ) (a : A) :
    orbitNorm β (fun b => f b * g b) n a = orbitNorm β f n a * orbitNorm β g n a := by
  simp [orbitNorm, prod_mul_distrib]

theorem orbitNorm_div (β : A ≃* A) (f g : A → C) (n : ℕ) (a : A) :
    orbitNorm β (fun b => f b / g b) n a = orbitNorm β f n a / orbitNorm β g n a := by
  simp [orbitNorm, prod_div_distrib]

section Defect
variable (c d : Cocycle A C) (β : A ≃* A)
  (L : ScalarLift c β) (M : ScalarLift d β) (s : A → C)
  (hs1 : s 1 = 1)
  (hs : ∀ a b, c.coeff a b = (s a * s b / s (a*b)) * d.coeff a b)

/-- The label-dependent defect of the supplied honest lifted actions. -/
def actionDefect (a : A) : C := L.phase a * s (β a) / (s a * M.phase a)

include hs1 in
theorem actionDefect_one : actionDefect c d β L M s 1 = 1 := by
  simp [actionDefect, hs1]

include hs in
/-- Multiplicativity of the defect is derived, rather than postulated. -/
theorem actionDefect_mul (a b : A) :
    actionDefect c d β L M s (a*b) =
      actionDefect c d β L M s a * actionDefect c d β L M s b := by
  simp only [actionDefect, L.phase_mul, M.phase_mul, map_mul]
  rw [hs a b, hs (β a) (β b)]
  simp [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

/-- The discrepancy of the actual lifts is an actual character. -/
def defectCharacter : A →* C where
  toFun := actionDefect c d β L M s
  map_one' := actionDefect_one c d β L M s hs1
  map_mul' := actionDefect_mul c d β L M s hs

/-- Norm one follows from the full cyclic action laws and telescoping. -/
theorem actionDefect_norm (n : ℕ) (hβ : β ^ n = 1)
    (hL : L.action ^ n = 1) (hM : M.action ^ n = 1) (a : A) :
    orbitNorm β (actionDefect c d β L M s) n a = 1 := by
  have hfun : actionDefect c d β L M s =
      fun b => (L.phase b / M.phase b) * (s (β b) / s b) := by
    funext b
    simp [actionDefect, div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]
  rw [hfun, orbitNorm_mul, orbitNorm_div, orbitNorm_coboundary,
    L.norm_eq_one n hL, M.norm_eq_one n hM, hβ]
  simp

/-- The cochain corrected by the explicitly constructed defect character. -/
def correctedCochain (n m : ℕ) (a : A) : C :=
  s a / correctingCharacter β (defectCharacter c d β L M s hs1 hs) n m a

include hs1 in
theorem correctedCochain_one (n m : ℕ) :
    correctedCochain c d β L M s hs1 hs n m 1 = 1 := by
  simp [correctedCochain, hs1]

/-- Character correction preserves the original cocycle comparison. -/
theorem correctedCochain_cocycle (n m : ℕ) (a b : A) :
    c.coeff a b =
      (correctedCochain c d β L M s hs1 hs n m a *
        correctedCochain c d β L M s hs1 hs n m b /
          correctedCochain c d β L M s hs1 hs n m (a*b)) * d.coeff a b := by
  rw [hs a b]
  simp only [correctedCochain, map_mul]
  simp [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

/-- Covariance is a conclusion obtained by solving the derived character
cocycle. It is not a premise on the original scalar cochain. -/
theorem correctedCochain_covariant (n m : ℕ) (hβ : β ^ n = 1)
    (hL : L.action ^ n = 1) (hM : M.action ^ n = 1)
    (hm : ∀ a : A, a ^ m = 1) (hcop : n.Coprime m) (a : A) :
    L.phase a * correctedCochain c d β L M s hs1 hs n m (β a) =
      correctedCochain c d β L M s hs1 hs n m a * M.phase a := by
  let r := defectCharacter c d β L M s hs1 hs
  have hn : ∀ b, orbitNorm β r n b = 1 := actionDefect_norm c d β L M s n hβ hL hM
  have hc := correctingCharacter_coboundary β r n m hβ hm hcop hn a
  have hx : correctingCharacter β r n m (β a) =
      (L.phase a * s (β a) / (s a * M.phase a)) * correctingCharacter β r n m a := by
    exact (div_eq_iff_eq_mul).mp hc
  change L.phase a * (s (β a) / correctingCharacter β r n m (β a)) =
    (s a / correctingCharacter β r n m a) * M.phase a
  rw [hx]
  simp [div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]

end Defect

end PaperXI.CyclicDefect113
