import KomorebiSpace.GrowingTower
import KomorebiSpace.SplitTowerCanonicity

set_option autoImplicit false

/-!
# A checked counterexample to splitting-independent repair

The same dimension-growing towers admit both zero extension and extension by
the first coordinate. Both splittings have norm at most one and the same gap.
They yield different exact repairs of the identity candidate, while agreeing
at the initial level and on every already-exact candidate.
-/
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace SplittingDependence
open BanachTower GrowingTower

def skewInsertLinear (n : ℕ) : Stage n →ₗ[ℝ] Stage (n+1) where
  toFun x := Fin.snoc x (x 0)
  map_add' x y := by
    funext i
    refine Fin.lastCases ?_ (fun j => ?_) i <;> simp
  map_smul' c x := by
    funext i
    refine Fin.lastCases ?_ (fun j => ?_) i <;> simp

theorem skewInsertLinear_bound (n : ℕ) (x : Stage n) :
    ‖skewInsertLinear n x‖ ≤ ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (norm_nonneg x)).mpr
  intro i
  refine Fin.lastCases ?_ (fun j => ?_) i
  · simpa [skewInsertLinear] using norm_le_pi_norm x 0
  · simpa [skewInsertLinear] using norm_le_pi_norm x j

def skewInsert (n : ℕ) : Stage n →L[ℝ] Stage (n+1) :=
  (skewInsertLinear n).mkContinuous 1 (fun x => by simpa using skewInsertLinear_bound n x)

@[simp] theorem skewInsert_old (n : ℕ) (x : Stage n) (i : Fin (n+1)) :
    skewInsert n x i.castSucc = x i := by
  change (Fin.snoc x (x 0) : Stage (n+1)) i.castSucc = x i
  simp

@[simp] theorem skewInsert_last (n : ℕ) (x : Stage n) :
    skewInsert n x (Fin.last (n+1)) = x 0 := by
  change (Fin.snoc x (x 0) : Stage (n+1)) (Fin.last (n+1)) = x 0
  simp

theorem skewInsert_opNorm (n : ℕ) : ‖skewInsert n‖ ≤ 1 :=
  ContinuousLinearMap.opNorm_le_bound _ zero_le_one
    (fun x => by simpa only [skewInsert, LinearMap.mkContinuous_apply, one_mul]
      using skewInsertLinear_bound n x)

theorem drop_skewInsert (n : ℕ) :
    (drop n).comp (skewInsert n) = ContinuousLinearMap.id ℝ (Stage n) := by
  ext x i
  simp

def skewSplitting : Splitting target where
  up := skewInsert
  down_up := drop_skewInsert
  bound := 1
  up_bound := skewInsert_opNorm

theorem skew_gap : (skewSplitting.bound : ℝ) * source.bound < 1 := by
  norm_num [skewSplitting, source]

def skewRepair : Candidates source target →L[ℝ] Candidates source target :=
  skewSplitting.repair source skew_gap

theorem skewRepair_exact (f : Candidates source target) :
    Exact source target (skewRepair f) :=
  skewSplitting.repair_exact source skew_gap f

@[simp] theorem skewRepair_seed (f : Candidates source target) : skewRepair f 0 = f 0 :=
  skewSplitting.repair_preserves_zero source skew_gap f

theorem skew_identity_first_new (x : Stage 1) :
    skewRepair identityCandidate 1 x 1 = x 1 - (1/2 : ℝ) * x 0 := by
  change x 1 - skewInsert 0 ((differential source target identityCandidate 0 +
    (0 : Stage 0 →L[ℝ] Stage 0).comp (source.down 0)) x) (Fin.last 1) = _
  rw [skewInsert_last, identityCandidate_defect]
  simp [smul_eq_mul]

theorem skew_identity_first_old (x : Stage 1) :
    skewRepair identityCandidate 1 x 0 = (1/2 : ℝ) * x 0 := by
  change x 0 - skewInsert 0 ((differential source target identityCandidate 0 +
    (0 : Stage 0 →L[ℝ] Stage 0).comp (source.down 0)) x) 0 = _
  rw [identityCandidate_defect]
  simp [skewInsert, skewInsertLinear, drop_apply, smul_eq_mul]
  ring

/-- A concrete inequality of two exact infinite transport families. -/
theorem exact_repairs_differ : skewRepair identityCandidate ≠ exactRepair identityCandidate := by
  intro he
  have h := congrArg (fun f : Candidates source target => f 1 (fun _ => 1) 1) he
  rw [skew_identity_first_new, identityRepair_first_new] at h
  norm_num at h

theorem repair_operators_differ : skewRepair ≠ exactRepair := by
  intro he
  exact exact_repairs_differ (congrArg (fun T : Candidates source target →L[ℝ]
    Candidates source target => T identityCandidate) he)

/-- The protected-profile subspaces remain literally equal. -/
theorem profile_spaces_equal :
    skewSplitting.semanticSpace source = targetSplitting.semanticSpace source :=
  skewSplitting.semanticSpace_eq source targetSplitting

/-- But the profile values of a nonexact candidate may differ. -/
theorem protected_profiles_differ :
    skewSplitting.observable source identityCandidate ≠
      targetSplitting.observable source identityCandidate := by
  intro he
  have h := congrArg (fun f : Candidates source target => f 1 (fun _ => 1) 1) he
  change (1 : ℝ) - skewInsert 0 (drop 0 (fun _ => 1)) (Fin.last 1) =
    1 - GrowingTower.insert 0 (drop 0 (fun _ => 1)) (Fin.last 1) at h
  rw [skewInsert_last, GrowingTower.insert_last] at h
  norm_num [drop_apply] at h

/-- Different exact retractions onto this common kernel fail to commute. -/
theorem repair_operators_do_not_commute :
    skewRepair.comp exactRepair ≠ exactRepair.comp skewRepair := by
  intro he
  apply repair_operators_differ
  exact (skewSplitting.repairs_commute_iff source targetSplitting skew_gap propagation_gap).mp he

/-- The counterexample changes neither the towers nor their norms or the initial operator. -/
theorem same_seed_distinct_exact_repairs :
    Exact source target (skewRepair identityCandidate) ∧
    Exact source target (exactRepair identityCandidate) ∧
    skewRepair identityCandidate 0 = exactRepair identityCandidate 0 ∧
    skewRepair identityCandidate ≠ exactRepair identityCandidate := by
  refine ⟨skewRepair_exact _, exactRepair_exact _, ?_, exact_repairs_differ⟩
  rw [skewRepair_seed, exactRepair_seed]

end SplittingDependence
end KomorebiSpace
end
