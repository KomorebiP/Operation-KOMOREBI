import KomorebiSpace.SplitTowerCoordinates
import Mathlib.Data.Fin.Tuple.Basic

set_option autoImplicit false

/-!
# An explicit, dimension-growing tower model

Stage n is real coordinate space of dimension n+1 with its sup norm.
The source coarse-graining is half the coordinate truncation; the target
coarse-graining is unscaled truncation. Zero extension supplies the target
splitting. Every hypothesis of the split-tower repair theorem is verified.
-/
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace GrowingTower
open BanachTower

abbrev Stage (n : ℕ) := Fin (n+1) → ℝ

def dropLinear (n : ℕ) : Stage (n+1) →ₗ[ℝ] Stage n where
  toFun x i := x i.castSucc
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem dropLinear_bound (n : ℕ) (x : Stage (n+1)) : ‖dropLinear n x‖ ≤ ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (norm_nonneg x)).mpr
  intro i
  exact norm_le_pi_norm x i.castSucc

def drop (n : ℕ) : Stage (n+1) →L[ℝ] Stage n :=
  (dropLinear n).mkContinuous 1 (fun x => by simpa using dropLinear_bound n x)

@[simp] theorem drop_apply (n : ℕ) (x : Stage (n+1)) (i : Fin (n+1)) :
    drop n x i = x i.castSucc := rfl

theorem drop_opNorm (n : ℕ) : ‖drop n‖ ≤ 1 :=
  ContinuousLinearMap.opNorm_le_bound _ zero_le_one
    (fun x => by simpa only [drop, LinearMap.mkContinuous_apply, one_mul] using dropLinear_bound n x)

def insertLinear (n : ℕ) : Stage n →ₗ[ℝ] Stage (n+1) where
  toFun x := Fin.snoc x 0
  map_add' x y := by
    funext i
    refine Fin.lastCases ?_ (fun j => ?_) i <;> simp
  map_smul' c x := by
    funext i
    refine Fin.lastCases ?_ (fun j => ?_) i <;> simp

theorem insertLinear_bound (n : ℕ) (x : Stage n) : ‖insertLinear n x‖ ≤ ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (norm_nonneg x)).mpr
  intro i
  refine Fin.lastCases ?_ (fun j => ?_) i
  · simp [insertLinear]
  · simpa [insertLinear] using norm_le_pi_norm x j

def insert (n : ℕ) : Stage n →L[ℝ] Stage (n+1) :=
  (insertLinear n).mkContinuous 1 (fun x => by simpa using insertLinear_bound n x)

@[simp] theorem insert_old (n : ℕ) (x : Stage n) (i : Fin (n+1)) :
    insert n x i.castSucc = x i := by
  change (Fin.snoc x 0 : Stage (n+1)) i.castSucc = x i
  simp

@[simp] theorem insert_last (n : ℕ) (x : Stage n) :
    insert n x (Fin.last (n+1)) = 0 := by
  change (Fin.snoc x 0 : Stage (n+1)) (Fin.last (n+1)) = 0
  simp

theorem insert_opNorm (n : ℕ) : ‖insert n‖ ≤ 1 :=
  ContinuousLinearMap.opNorm_le_bound _ zero_le_one
    (fun x => by simpa only [insert, LinearMap.mkContinuous_apply, one_mul] using insertLinear_bound n x)

theorem drop_insert (n : ℕ) : (drop n).comp (insert n) = ContinuousLinearMap.id ℝ (Stage n) := by
  ext x i
  simp

/-- Both objects and bonding maps are genuinely level-dependent. -/
abbrev source : BanachTower ℝ where
  Obj := Stage
  down n := (1/2 : ℝ) • drop n
  bound := 1/2
  down_bound n := by
    rw [norm_smul]
    norm_num
    nlinarith [drop_opNorm n]

abbrev target : BanachTower ℝ where
  Obj := Stage
  down := drop
  bound := 1
  down_bound := drop_opNorm

def targetSplitting : Splitting target where
  up := insert
  down_up := drop_insert
  bound := 1
  up_bound := insert_opNorm

theorem propagation_gap :
    (targetSplitting.bound : ℝ) * source.bound < 1 := by
  norm_num [targetSplitting, source]

theorem gain_eq_two : targetSplitting.gain source = 2 := by
  norm_num [Splitting.gain, targetSplitting, source]

def correction : Residuals source target →L[ℝ] Candidates source target :=
  targetSplitting.correction source propagation_gap

def exactRepair : Candidates source target →L[ℝ] Candidates source target :=
  targetSplitting.repair source propagation_gap

@[simp] theorem differential_correction (r : Residuals source target) :
    differential source target (correction r) = r :=
  targetSplitting.differential_correction source propagation_gap r

theorem correction_bound (r : Residuals source target) : ‖correction r‖ ≤ 2 * ‖r‖ := by
  simpa only [gain_eq_two, correction] using targetSplitting.correction_bound source propagation_gap r

theorem exactRepair_exact (f : Candidates source target) : Exact source target (exactRepair f) :=
  targetSplitting.repair_exact source propagation_gap f

theorem exactRepair_error (f : Candidates source target) :
    ‖f - exactRepair f‖ ≤ 2 * ‖differential source target f‖ := by
  simpa only [gain_eq_two, exactRepair] using targetSplitting.repair_error source propagation_gap f

@[simp] theorem exactRepair_seed (f : Candidates source target) : exactRepair f 0 = f 0 :=
  targetSplitting.repair_preserves_zero source propagation_gap f

/-- The correction never erases the newly added target row. -/
@[simp] theorem correction_last (r : Residuals source target) (n : ℕ) (x : Stage (n+1)) :
    correction r (n+1) x (Fin.last (n+1)) = 0 := by
  change insert n _ (Fin.last (n+1)) = 0
  exact insert_last n _

/-- Every newly exposed output row is preserved by the repair. -/
theorem exactRepair_last (f : Candidates source target) (n : ℕ) (x : Stage (n+1)) :
    exactRepair f (n+1) x (Fin.last (n+1)) = f (n+1) x (Fin.last (n+1)) := by
  change f (n+1) x (Fin.last (n+1)) -
    correction (differential source target f) (n+1) x (Fin.last (n+1)) = _
  rw [correction_last, sub_zero]

/-- A non-exact input with nonzero protected seed and nonzero innovation at every stage. -/
def identityCandidate : Candidates source target :=
  ⟨fun n => ContinuousLinearMap.id ℝ (Stage n), memℓp_infty ⟨1, by
    rintro _ ⟨n, rfl⟩
    exact ContinuousLinearMap.norm_id_le⟩⟩

@[simp] theorem identityCandidate_apply (n : ℕ) (x : Stage n) : identityCandidate n x = x := rfl

theorem identityCandidate_defect (n : ℕ) :
    differential source target identityCandidate n = (1/2 : ℝ) • drop n := by
  ext x i
  change x i.castSucc - (1/2 : ℝ) * x i.castSucc = (1/2 : ℝ) * x i.castSucc
  ring

theorem identityCandidate_not_exact : ¬ Exact source target identityCandidate := by
  intro he
  have hz := (exact_iff_differential_zero source target identityCandidate).mp he
  have h := congrArg (fun r : Residuals source target => r 0 (fun _ => 1) 0) hz
  change (1 : ℝ) - (1/2 : ℝ) * 1 = 0 at h
  norm_num at h

theorem identityRepair_nonzero : exactRepair identityCandidate ≠ 0 := by
  intro hz
  have h := congrArg (fun f : Candidates source target => f 0 (fun _ => 1) 0) hz
  rw [exactRepair_seed] at h
  change (1 : ℝ) = 0 at h
  norm_num at h

/-- The first repair already changes inherited data while retaining new data. -/
theorem identityRepair_first_old (x : Stage 1) :
    exactRepair identityCandidate 1 x 0 = (1/2 : ℝ) * x 0 := by
  change x 0 - insert 0 ((differential source target identityCandidate 0 +
    (0 : Stage 0 →L[ℝ] Stage 0).comp (source.down 0)) x) 0 = _
  rw [identityCandidate_defect]
  simp [insert, insertLinear, drop_apply, smul_eq_mul]
  ring

theorem identityRepair_first_new (x : Stage 1) : exactRepair identityCandidate 1 x 1 = x 1 :=
  exactRepair_last identityCandidate 0 x

/-- Exact compatibility transports every inherited row by the source contraction. -/
theorem exactRepair_old (f : Candidates source target) (n : ℕ)
    (x : Stage (n+1)) (i : Fin (n+1)) :
    exactRepair f (n+1) x i.castSucc = (1/2 : ℝ) * exactRepair f n (drop n x) i := by
  have h := congrArg (fun T : Stage (n+1) →L[ℝ] Stage n => T x i)
    (exactRepair_exact f n)
  change exactRepair f (n+1) x i.castSucc = exactRepair f n ((1/2 : ℝ) • drop n x) i at h
  rw [map_smul] at h
  exact h

/-- An all-level closed formula for the repair of the initially incompatible identities. -/
theorem identityRepair_formula (n : ℕ) : ∀ (x : Stage n) (i : Fin (n+1)),
    exactRepair identityCandidate n x i = (1/2 : ℝ) ^ (n-i.val) * x i := by
  induction n with
  | zero =>
    intro x i
    simp only [Nat.zero_sub, pow_zero, one_mul]
    rw [exactRepair_seed]
    rfl
  | succ n ih =>
    intro x i
    refine Fin.lastCases ?_ (fun j => ?_) i
    · simp only [Fin.val_last, Nat.sub_self, pow_zero, one_mul]
      exact exactRepair_last identityCandidate n x
    · rw [exactRepair_old, ih]
      have hn : n+1-j.val = (n-j.val)+1 := by omega
      rw [Fin.val_castSucc, hn, pow_succ, drop_apply]
      ring

/-- Realization is a map of the actual inverse-limit point types. -/
def realizedIdentity : source.Point → target.Point :=
  onLimit source target (exactRepair identityCandidate) (exactRepair_exact identityCandidate)

@[simp] theorem realizedIdentity_coordinate (x : source.Point) (n : ℕ) (i : Fin (n+1)) :
    (realizedIdentity x).val n i = (1/2 : ℝ) ^ (n-i.val) * x.val n i :=
  identityRepair_formula n (x.val n) i

end GrowingTower
end KomorebiSpace
end
