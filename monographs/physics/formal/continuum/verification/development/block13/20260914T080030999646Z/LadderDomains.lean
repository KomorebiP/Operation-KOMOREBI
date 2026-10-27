module
public import KomorebiPhysics.SpectralGraph
public import KomorebiPhysics.BoundedSpectral

/-! Actual oscillator ladders on their common maximal first-moment domain.
The two sequence formulas are converted to Hilbert-space outputs only after
proving square summability. No ladder is declared bounded on all l2. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace LadderDomains
open scoped BigOperators lp
open BoundedSpectral

/-- The number-operator square-root domain. -/
def domain : Submodule ℂ Space := DiagonalDomain.domain (fun n : ℕ => Real.sqrt n)

theorem domain_iff (x : Space) : x ∈ domain ↔
    Summable (fun n : ℕ => (n : ℝ) * ‖x n‖ ^ 2) := by
  rw [domain, SpectralGraph.domain_iff]
  simp only [Real.sq_sqrt (Nat.cast_nonneg _)]

def lowerSeq : (ℕ → ℂ) →ₗ[ℂ] (ℕ → ℂ) where
  toFun x n := (Real.sqrt (n+1 : ℕ) : ℂ) * x (n+1)
  map_add' x y := by funext n; exact mul_add _ _ _
  map_smul' c x := by funext n; exact mul_left_comm _ _ _

def raiseSeq : (ℕ → ℂ) →ₗ[ℂ] (ℕ → ℂ) where
  toFun x n := match n with
    | 0 => 0
    | n+1 => (Real.sqrt (n+1 : ℕ) : ℂ) * x n
  map_add' x y := by funext n; cases n <;> simp [mul_add]
  map_smul' c x := by
    funext n
    cases n with
    | zero => simp
    | succ n => exact mul_left_comm _ _ _

theorem lowerSeq_apply (x : ℕ → ℂ) (n : ℕ) :
    lowerSeq x n = (Real.sqrt (n+1 : ℕ) : ℂ) * x (n+1) := rfl

theorem raiseSeq_zero (x : ℕ → ℂ) : raiseSeq x 0 = 0 := rfl

theorem raiseSeq_succ (x : ℕ → ℂ) (n : ℕ) :
    raiseSeq x (n+1) = (Real.sqrt (n+1 : ℕ) : ℂ) * x n := rfl

theorem lower_norm_sq (x : ℕ → ℂ) (n : ℕ) :
    ‖lowerSeq x n‖ ^ 2 = ((n+1 : ℕ) : ℝ) * ‖x (n+1)‖ ^ 2 := by
  rw [lowerSeq_apply, SpectralGraph.weighted_norm_sq,
    Real.sq_sqrt (Nat.cast_nonneg _)]

theorem raise_norm_sq (x : ℕ → ℂ) (n : ℕ) :
    ‖raiseSeq x (n+1)‖ ^ 2 = ((n+1 : ℕ) : ℝ) * ‖x n‖ ^ 2 := by
  rw [raiseSeq_succ, SpectralGraph.weighted_norm_sq,
    Real.sq_sqrt (Nat.cast_nonneg _)]

/-- Exact maximality, not just a sufficient dense core. -/
theorem lower_mem_iff (x : Space) : Memℓp (lowerSeq x) 2 ↔ x ∈ domain := by
  rw [memℓp_gen_iff (by norm_num), domain_iff]
  simp only [ENNReal.toReal_ofNat, Real.rpow_two, lower_norm_sq]
  exact summable_nat_add_iff 1

/-- Raising has the same maximal domain because the original vector is in l2. -/
theorem raise_mem_iff (x : Space) : Memℓp (raiseSeq x) 2 ↔ x ∈ domain := by
  rw [memℓp_gen_iff (by norm_num), domain_iff]
  simp only [ENNReal.toReal_ofNat, Real.rpow_two]
  rw [← summable_nat_add_iff 1]
  simp only [raise_norm_sq, Nat.cast_add, Nat.cast_one, add_mul, one_mul]
  exact summable_add_iff_right (SpectralGraph.norm_sq_summable x)

/-- Actual unbounded lowering partial linear map. -/
def lower : Space →ₗ.[ℂ] Space where
  domain := domain
  toFun := {
    toFun := fun x => ⟨lowerSeq (x : Space), (lower_mem_iff (x : Space)).mpr x.property⟩
    map_add' := fun x y => lp.ext (lowerSeq.map_add (x : Space) (y : Space))
    map_smul' := fun c x => lp.ext (lowerSeq.map_smul c (x : Space)) }

/-- Actual unbounded raising partial linear map, on the proved same domain. -/
def raise : Space →ₗ.[ℂ] Space where
  domain := domain
  toFun := {
    toFun := fun x => ⟨raiseSeq (x : Space), (raise_mem_iff (x : Space)).mpr x.property⟩
    map_add' := fun x y => lp.ext (raiseSeq.map_add (x : Space) (y : Space))
    map_smul' := fun c x => lp.ext (raiseSeq.map_smul c (x : Space)) }

theorem lower_apply (x : domain) (n : ℕ) :
    lower x n = (Real.sqrt (n+1 : ℕ) : ℂ) * (x : Space) (n+1) := rfl

theorem raise_zero (x : domain) : raise x 0 = 0 := rfl

theorem raise_succ (x : domain) (n : ℕ) :
    raise x (n+1) = (Real.sqrt (n+1 : ℕ) : ℂ) * (x : Space) n := rfl

theorem single_mem (n : ℕ) (c : ℂ) : lp.single 2 n c ∈ domain :=
  DiagonalDomain.single_mem (fun n : ℕ => Real.sqrt n) n c

def single (n : ℕ) (c : ℂ) : domain := ⟨lp.single 2 n c, single_mem n c⟩

theorem dense_domain : Dense (domain : Set Space) :=
  DiagonalDomain.dense_domain (fun n : ℕ => Real.sqrt n)

/-- Lowering annihilates the vacuum exactly. -/
theorem lower_single_zero (c : ℂ) : lower (single 0 c) = 0 := by
  apply lp.ext
  funext n
  simp [lower_apply, single]

theorem lower_single_succ (n : ℕ) (c : ℂ) :
    lower (single (n+1) c) = lp.single 2 n ((Real.sqrt (n+1 : ℕ) : ℂ) * c) := by
  apply lp.ext
  funext k
  by_cases h : k = n
  · subst k; simp [lower_apply, single]
  · have hh : k+1 ≠ n+1 := by omega
    simp [lower_apply, single, h, hh]

theorem raise_single (n : ℕ) (c : ℂ) :
    raise (single n c) = lp.single 2 (n+1) ((Real.sqrt (n+1 : ℕ) : ℂ) * c) := by
  apply lp.ext
  funext k
  cases k with
  | zero => simp [raise_zero]
  | succ k =>
    by_cases h : k = n
    · subst k; simp [raise_succ, single]
    · have hh : k+1 ≠ n+1 := by omega
      simp [raise_succ, single, h, hh]

end LadderDomains
end KomorebiPhysics
