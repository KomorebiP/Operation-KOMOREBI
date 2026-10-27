import FiniteBranchCompactness
import PadicMatrixTowerLimit

/-! Predicate-preserving compactness for the actual inherited matrix-unit tower.
No norm invertibility or uniqueness assumptions occur. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open ResonantBranch
variable (p : ℕ)
variable (n : Type) [Fintype n] [DecidableEq n]

/-- Reduction between arbitrary positive coefficient levels. -/
def coefficientProject {i j : ℕ} (h : i ≤ j) : Coeff p j →+* Coeff p i :=
  ZMod.castHom (by
    rw [modulus_eq_pow, modulus_eq_pow]
    exact pow_dvd_pow p (Nat.add_le_add_right h 1)) _

/-- Actual matrix-unit reduction, not an abstract branch label. -/
def project {i j : ℕ} (h : i ≤ j) : MatrixUnits p n j →* MatrixUnits p n i :=
  Units.map (coefficientProject p h).mapMatrix.toMonoidHom

@[simp] theorem project_refl (i : ℕ) (a : MatrixUnits p n i) :
    project p n (le_refl i) a = a := by
  apply Units.ext
  ext u v
  change coefficientProject p (le_refl i) (a.val u v) = _
  rw [show coefficientProject p (le_refl i) = RingHom.id _ from Subsingleton.elim _ _]
  rfl

@[simp] theorem project_trans {i j k : ℕ} (hij : i ≤ j) (hjk : j ≤ k)
    (a : MatrixUnits p n k) :
    project p n hij (project p n hjk a) = project p n (hij.trans hjk) a := by
  apply Units.ext
  ext u v
  exact congrArg (fun f : Coeff p k →+* Coeff p i => f (a.val u v))
    (Subsingleton.elim ((coefficientProject p hij).comp (coefficientProject p hjk))
      (coefficientProject p (hij.trans hjk)))

@[simp] theorem project_succ (i : ℕ) (a : MatrixUnits p n (i+1)) :
    project p n (Nat.le_succ i) a = down p n i a := by
  apply Units.ext
  ext u v
  exact congrArg (fun f : Coeff p (i+1) →+* Coeff p i => f (a.val u v))
    (Subsingleton.elim (coefficientProject p (Nat.le_succ i)) (coefficientDown p i))

variable [Fact (Nat.Prime p)]

@[simp] theorem project_padicReduction {i j : ℕ} (h : i ≤ j)
    (a : (Matrix n n ℤ_[p])ˣ) :
    project p n h (padicUnitReduction p n j a) = padicUnitReduction p n i a := by
  induction j, h using Nat.le_induction with
  | base => exact project_refl p n i _
  | succ j hij ih =>
    rw [← project_trans p n hij (Nat.le_succ j), project_succ,
      padicUnitReduction_compatible]
    exact ih

/-- Finite tuples include a Frobenius and any finite family of local conjugators. -/
def finiteTupleTower (I : Type) : FiniteTower (fun r => I → MatrixUnits p n r) where
  project h a := fun i => project p n h (a i)
  project_refl a := funext fun i => project_refl p n _ (a i)
  project_trans hij hjk a := funext fun i => project_trans p n hij hjk (a i)

/-- Every downward-closed finite-level condition lifts exactly iff every level is occupied. -/
theorem padic_tuple_exists_iff_every_level (I : Type) [Fintype I]
    (P : ∀ r, (I → MatrixUnits p n r) → Prop)
    (hP : DownwardClosed (finiteTupleTower p n I) P) :
    (∃ a : I → (Matrix n n ℤ_[p])ˣ,
      ∀ r, P r (fun i => padicUnitReduction p n r (a i))) ↔
    ∀ r, ∃ a, P r a := by
  constructor
  · rintro ⟨a, ha⟩ r
    exact ⟨_, ha r⟩
  · intro hne
    obtain ⟨f, hf, hc⟩ := exists_compatible_branch (finiteTupleTower p n I) P hP hne
    have hfc : ∀ i, Compatible p n (fun r => f r i) := by
      intro i r
      have h := congrFun (hc (Nat.le_succ r)) i
      exact (project_succ p n r _).symm.trans h
    refine ⟨fun i => unitLimit p n (fun r => f r i) (hfc i), ?_⟩
    intro r
    simpa only [unitLimit_spec] using hf r

/-- A failure of any such finite tuple problem is witnessed by a finite coefficient level. -/
theorem no_padic_tuple_iff_empty_level (I : Type) [Fintype I]
    (P : ∀ r, (I → MatrixUnits p n r) → Prop)
    (hP : DownwardClosed (finiteTupleTower p n I) P) :
    (¬ ∃ a : I → (Matrix n n ℤ_[p])ˣ,
      ∀ r, P r (fun i => padicUnitReduction p n r (a i))) ↔
    ∃ r, ∀ a, ¬ P r a := by
  rw [padic_tuple_exists_iff_every_level p n I P hP]
  simp only [not_forall, not_exists]

end Komorebi.StrongArtin.FrobeniusTower
