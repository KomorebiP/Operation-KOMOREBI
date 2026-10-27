import AVOC.TypedAffineProgram

namespace Komorebi.AVOC.Affine

/-- Dense dot products: n multiplies, n accumulations and one bias addition per row.
This is a declared scalar-operation tariff, not wall time or bit complexity. -/
def denseCost (n m : Nat) : Nat := m * (2*n + 1)

/-- Dense coefficient-composition tariff: product matrix and affine offset. -/
def composeCost (n m k : Nat) : Nat := 2*k*n*m + denseCost m k

variable {R : Type} [Ring R]

abbrev DenseProgram (R : Type) := Program (Signature R)

def coefficients {n m} (p : DenseProgram R n m) : Signature R n m := normalize (fun x => x) p

def execute {n m} (p : DenseProgram R n m) (x : Fin n → R) : Fin m → R := run (fun x => x) p x

def executionCost {n m} (p : DenseProgram R n m) : Nat := cost (fun {n m} _ => denseCost n m) p

/-- Arithmetic charged while forming coefficients; copies and allocations are excluded. -/
def normalizationCost : {n m : Nat} → DenseProgram R n m → Nat
  | _, _, .atom _ => 0
  | _, _, .ident => 0
  | n, k, .seq (m:=m) f g => normalizationCost f + normalizationCost g + composeCost n m k
  | n, m, .plus f g => normalizationCost f + normalizationCost g + m*(n+1)

def fuse {n m} (p : DenseProgram R n m) : DenseProgram R n m := .atom (coefficients p)

@[simp] theorem coefficients_correct {n m} (p : DenseProgram R n m) (x : Fin n → R) :
    eval (coefficients p) x = execute p x := normalize_correct (fun x => x) p x

@[simp] theorem fuse_correct {n m} (p : DenseProgram R n m) (x : Fin n → R) :
    execute (fuse p) x = execute p x := coefficients_correct p x

@[simp] theorem fused_execution_cost {n m} (p : DenseProgram R n m) :
    executionCost (fuse p) = denseCost n m := rfl

def chooseNoSlower {n m} (p : DenseProgram R n m) : DenseProgram R n m :=
  if denseCost n m ≤ executionCost p then fuse p else p

theorem chooseNoSlower_correct {n m} (p : DenseProgram R n m) (x : Fin n → R) :
    execute (chooseNoSlower p) x = execute p x := by
  unfold chooseNoSlower; split
  · exact fuse_correct p x
  · rfl

theorem chooseNoSlower_cost {n m} (p : DenseProgram R n m) :
    executionCost (chooseNoSlower p) ≤ executionCost p := by
  unfold chooseNoSlower; split
  · simpa using ‹denseCost n m ≤ executionCost p›
  · exact Nat.le_refl _

/-- Compile-once plus deployment arithmetic. Validation/IO are not free claims. -/
def fusedLifecycle {n m} (p : DenseProgram R n m) (calls : Nat) : Nat :=
  normalizationCost p + calls * denseCost n m

def baselineLifecycle {n m} (p : DenseProgram R n m) (calls : Nat) : Nat :=
  calls * executionCost p

def WorthFusing {n m} (p : DenseProgram R n m) (calls : Nat) : Prop :=
  fusedLifecycle p calls ≤ baselineLifecycle p calls

instance {n m} (p : DenseProgram R n m) (calls : Nat) : Decidable (WorthFusing p calls) :=
  inferInstanceAs (Decidable (_ ≤ _))

theorem worthwhile_certificate {n m} (p : DenseProgram R n m) (calls : Nat)
    (h : WorthFusing p calls) :
    (∀ x, execute (fuse p) x = execute p x) ∧
    normalizationCost p + calls * executionCost (fuse p) ≤ calls * executionCost p := by
  exact ⟨fuse_correct p, h⟩

/-- A correct coefficient normal form need not be a cheap evaluation schedule. -/
theorem bottleneck_fusion_cost_increases :
    denseCost 4 1 + denseCost 1 4 = 21 ∧ denseCost 4 4 = 36 ∧
    denseCost 4 1 + denseCost 1 4 < denseCost 4 4 := by decide

theorem beneficial_fusion_costs :
    denseCost 2 3 + denseCost 3 2 = 29 ∧ denseCost 2 2 = 10 ∧ composeCost 2 3 2 = 38 := by decide

theorem beneficial_fusion_break_even (calls : Nat) :
    38 + calls * denseCost 2 2 ≤ calls * (denseCost 2 3 + denseCost 3 2) ↔ 2 ≤ calls := by
  simp only [denseCost]; omega

theorem beneficial_fusion_strict_gain (calls : Nat) :
    38 + calls * denseCost 2 2 < calls * (denseCost 2 3 + denseCost 3 2) ↔ 3 ≤ calls := by
  simp only [denseCost]; omega

/-- Zero is a valid lower certificate. It is generally not tight for nonidentity maps. -/
theorem zero_lower_valid :
    LowerValid (fun {n m} (f : Signature R n m) => f)
      (fun {n m} _ => denseCost n m) (fun {_ _} _ => 0) := by
  constructor
  · intro n m f; exact Nat.zero_le _
  · intro n; exact Nat.le_refl _
  · intro n m k f g; exact Nat.le_refl _
  · intro n m f g; exact Nat.zero_le _

omit [Ring R] in
theorem identity_global_minimum (n : Nat) (p : DenseProgram R n n) :
    executionCost (Program.ident : DenseProgram R n n) ≤ executionCost p := by
  exact Nat.zero_le _

end Komorebi.AVOC.Affine
