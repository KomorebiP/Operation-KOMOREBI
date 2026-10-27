import MachineTheory.Behavior
import Mathlib.Basic.Real.Basic
import Mathlib.Algebra.BigOperators.Field
import Mathlib.Tactic.Positivity

/-!
Reviewed Core v0.2, Theorem 3.6.
Column convention: K a o y x is the joint probability of successor y and report o
conditional on initial x and action a. Report and transition marginals are not substituted
for this joint instrument. All laws are exact real-valued finite distributions.
-/
namespace Komorebi.MachineTheory
namespace Instrument
open scoped BigOperators
noncomputable section

variable {X Z A O : Type*}

def mass [Fintype X] (p : X → ℝ) : ℝ := ∑ x, p x

def push [Fintype X] [DecidableEq Z] (π : X → Z) (p : X → ℝ) : Z → ℝ :=
  fun z => ∑ x, if π x = z then p x else 0

def applyKernel [Fintype X] (K : Z → X → ℝ) (p : X → ℝ) : Z → ℝ :=
  fun z => ∑ x, K z x * p x

def scale (c : ℝ) (p : X → ℝ) : X → ℝ := fun x => c * p x

def basis [DecidableEq X] (i : X) : X → ℝ := fun x => if x = i then 1 else 0

def normalize [Fintype X] (p : X → ℝ) : X → ℝ := fun x => p x / mass p

def IsDist [Fintype X] (p : X → ℝ) : Prop := (∀ x, 0 ≤ p x) ∧ mass p = 1

structure Law (X A O : Type*) [Fintype X] [Fintype O] where
  kernel : A → O → X → X → ℝ
  nonnegative : ∀ a o y x, 0 ≤ kernel a o y x
  normalized : ∀ a x, (∑ o, ∑ y, kernel a o y x) = 1

variable [Fintype X] [Fintype Z] [DecidableEq Z]

/-- Aggregation preserves total mass for any real vector, including unnormalized ones. -/
theorem mass_push (π : X → Z) (p : X → ℝ) : mass (push π p) = mass p := by
  unfold mass push
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro x _
  simp

omit [Fintype Z] in
theorem push_scale (π : X → Z) (c : ℝ) (p : X → ℝ) :
    push π (scale c p) = scale c (push π p) := by
  funext z
  simp only [push, scale, Finset.mul_sum, mul_ite, mul_zero]

theorem mass_scale (c : ℝ) (p : X → ℝ) : mass (scale c p) = c * mass p := by
  simp [mass, scale, Finset.mul_sum]

omit [Fintype Z] in
theorem push_nonnegative (π : X → Z) (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) :
    ∀ z, 0 ≤ push π p z := by
  intro z
  apply Finset.sum_nonneg
  intro x _
  split_ifs <;> simp_all

omit [Fintype Z] [DecidableEq Z] in
theorem apply_nonnegative (K : Z → X → ℝ) (hK : ∀ z x, 0 ≤ K z x)
    (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) : ∀ z, 0 ≤ applyKernel K p z := by
  intro z
  exact Finset.sum_nonneg (fun x _ => mul_nonneg (hK z x) (hp x))

/-- Aggregation of a normalized nonnegative prior is a prior. -/
theorem push_dist (π : X → Z) (p : X → ℝ) (hp : IsDist p) : IsDist (push π p) :=
  ⟨push_nonnegative π p hp.1, (mass_push π p).trans hp.2⟩

omit [Fintype Z] in
theorem push_apply_expansion (π : X → Z) (K : X → X → ℝ) (p : X → ℝ) (z : Z) :
    push π (applyKernel K p) z = ∑ x, (∑ y, if π y = z then K y x else 0) * p x := by
  unfold push applyKernel
  have hi : ∀ y, (if π y = z then ∑ x, K y x * p x else 0) =
      ∑ x, (if π y = z then K y x else 0) * p x := by
    intro y
    split_ifs <;> simp_all
  simp_rw [hi]
  rw [Finset.sum_comm]
  simp only [Finset.sum_mul]

theorem apply_push_expansion (π : X → Z) (L : Z → Z → ℝ) (p : X → ℝ) (z : Z) :
    applyKernel L (push π p) z = ∑ x, L z (π x) * p x := by
  unfold applyKernel push
  simp_rw [Finset.mul_sum, mul_ite, mul_zero]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro x _
  simp

omit [Fintype Z] [DecidableEq Z] in
theorem apply_basis [DecidableEq X] (K : Z → X → ℝ) (x : X) :
    applyKernel K (basis x) = fun z => K z x := by
  funext z
  simp [applyKernel, basis]

theorem basis_dist [DecidableEq X] (x : X) : IsDist (basis x) := by
  constructor
  · intro y
    simp only [basis]
    split_ifs <;> norm_num
  · simp [mass, basis]

/-- The literal column-fibre criterion, for a proposed coarse kernel. -/
def RowsMatch (π : X → Z) (K : X → X → ℝ) (L : Z → Z → ℝ) : Prop :=
  ∀ z x, (∑ y, if π y = z then K y x else 0) = L z (π x)

def Intertwines (π : X → Z) (K : X → X → ℝ) (L : Z → Z → ℝ) : Prop :=
  ∀ p, push π (applyKernel K p) = applyKernel L (push π p)

/-- Core 3.6: point-mass checking is equivalent to the full linear intertwining. -/
theorem intertwines_iff_rows (π : X → Z) (K : X → X → ℝ) (L : Z → Z → ℝ) :
    Intertwines π K L ↔ RowsMatch π K L := by
  classical
  constructor
  · intro h z x
    have he := congrFun (h (basis x)) z
    rw [push_apply_expansion, apply_push_expansion] at he
    simpa [basis] using he
  · intro h p
    funext z
    rw [push_apply_expansion, apply_push_expansion]
    apply Finset.sum_congr rfl
    intro x _
    rw [h z x]

/-- Probability priors suffice to identify the linear interface, since they include point masses. -/
theorem intertwines_of_priors (π : X → Z) (K : X → X → ℝ) (L : Z → Z → ℝ)
    (h : ∀ p, IsDist p → push π (applyKernel K p) = applyKernel L (push π p)) :
    Intertwines π K L := by
  classical
  apply (intertwines_iff_rows π K L).mpr
  intro z x
  have he := congrFun (h (basis x) (basis_dist x)) z
  rw [push_apply_expansion, apply_push_expansion] at he
  simpa [basis] using he


variable [Fintype O]

/-- Report-indexed successor masses must be constant on each *input* fibre. -/
def FiberCriterion (π : X → Z) (K : A → O → X → X → ℝ) : Prop :=
  ∀ a o z x y, π x = π y →
    (∑ u, if π u = z then K a o u x else 0) =
    (∑ u, if π u = z then K a o u y else 0)

/-- Choose attained input representatives, then aggregate the joint columns. -/
def coarseLaw (π : X → Z) (hπ : Function.Surjective π) (K : Law X A O) : Law Z A O where
  kernel a o z' z := ∑ y, if π y = z' then K.kernel a o y (Classical.choose (hπ z)) else 0
  nonnegative a o z' z := by
    apply Finset.sum_nonneg
    intro y _
    split_ifs
    · exact K.nonnegative a o y _
    · exact le_rfl
  normalized a z := by
    change (∑ o, mass (push π (fun y => K.kernel a o y (Classical.choose (hπ z))))) = 1
    simp_rw [mass_push]
    exact K.normalized a _

/-- With the fibre condition, the constructed coarse law is a true intertwiner. -/
theorem coarseLaw_intertwines (π : X → Z) (hπ : Function.Surjective π)
    (K : Law X A O) (hc : FiberCriterion π K.kernel) (a : A) (o : O) :
    Intertwines π (K.kernel a o) ((coarseLaw π hπ K).kernel a o) := by
  apply (intertwines_iff_rows _ _ _).mpr
  intro z x
  exact hc a o z x _ (Classical.choose_spec (hπ (π x))).symm

/-- Core 3.6, existence of a normalized nonnegative coarse instrument iff the fibre criterion. -/
theorem quotient_exists_iff (π : X → Z) (hπ : Function.Surjective π) (K : Law X A O) :
    (∃ L : Law Z A O, ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o)) ↔
      FiberCriterion π K.kernel := by
  constructor
  · rintro ⟨L, hL⟩ a o z x y hxy
    have hrow := (intertwines_iff_rows π (K.kernel a o) (L.kernel a o)).mp (hL a o)
    rw [hrow z x, hrow z y, hxy]
  · intro hc
    exact ⟨coarseLaw π hπ K, coarseLaw_intertwines π hπ K hc⟩

/-- Surjectivity is used here: unobserved coarse input columns would not be identified. -/
theorem quotient_kernel_unique (π : X → Z) (hπ : Function.Surjective π)
    (K : Law X A O) (L M : Law Z A O)
    (hL : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o))
    (hM : ∀ a o, Intertwines π (K.kernel a o) (M.kernel a o)) : L.kernel = M.kernel := by
  funext a o z' z
  obtain ⟨x, rfl⟩ := hπ z
  exact ((intertwines_iff_rows _ _ _).mp (hL a o) z' x).symm.trans
    ((intertwines_iff_rows _ _ _).mp (hM a o) z' x)

/-- Algebraic normalization commutes with aggregation; probability meaning needs positive mass. -/
theorem push_normalize (π : X → Z) (p : X → ℝ) :
    push π (normalize p) = normalize (push π p) := by
  funext z
  simp only [push, normalize, mass_push, Finset.sum_div]
  apply Finset.sum_congr rfl
  intro x _
  split_ifs <;> simp_all

theorem normalize_dist (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) (hm : 0 < mass p) :
    IsDist (normalize p) := by
  constructor
  · intro x
    exact div_nonneg (hp x) (le_of_lt hm)
  · change (∑ x, p x / mass p) = 1
    rw [← Finset.sum_div]
    exact div_self (ne_of_gt hm)

/-- An impossible report has no posterior at the public interface. -/
def posterior? (p : X → ℝ) : Option (X → ℝ) :=
  if 0 < mass p then some (normalize p) else none

theorem report_mass_eq (π : X → Z) {K : X → X → ℝ} {L : Z → Z → ℝ}
    (h : Intertwines π K L) (p : X → ℝ) :
    mass (applyKernel K p) = mass (applyKernel L (push π p)) := by
  rw [← mass_push π (applyKernel K p), h p]

/-- Exact Bayesian correction for every positive-probability report, represented as an Option. -/
theorem posterior_transport (π : X → Z) {K : X → X → ℝ} {L : Z → Z → ℝ}
    (h : Intertwines π K L) (p : X → ℝ) :
    Option.map (push π) (posterior? (applyKernel K p)) =
      posterior? (applyKernel L (push π p)) := by
  unfold posterior?
  rw [report_mass_eq π h p]
  split_ifs
  · simp only [Option.map_some]
    congr 1
    rw [push_normalize, h p]
  · rfl

/-- For nonnegative finite weights, zero total mass forces every weight to be zero. -/
theorem zero_of_zero_mass (p : X → ℝ) (hp : ∀ x, 0 ≤ p x) (hm : mass p = 0) :
    p = fun _ => 0 := by
  funext x
  have h := (Finset.sum_eq_zero_iff_of_nonneg (fun y (_ : y ∈ (Finset.univ : Finset X)) => hp y)).mp hm
  exact h x (Finset.mem_univ x)

/-- Reverse direction: report probabilities and positive-report posteriors determine the joint interface. -/
theorem intertwines_of_mass_and_posteriors (π : X → Z)
    (K : X → X → ℝ) (L : Z → Z → ℝ)
    (hK : ∀ y x, 0 ≤ K y x) (hL : ∀ z' z, 0 ≤ L z' z)
    (h : ∀ p, IsDist p →
      mass (applyKernel K p) = mass (applyKernel L (push π p)) ∧
      (0 < mass (applyKernel K p) →
        push π (normalize (applyKernel K p)) = normalize (applyKernel L (push π p)))) :
    Intertwines π K L := by
  apply intertwines_of_priors
  intro p hp
  obtain ⟨hm, hn⟩ := h p hp
  have hnn := apply_nonnegative K hK p hp.1
  have hnn' := apply_nonnegative L hL (push π p) (push_nonnegative π p hp.1)
  by_cases hz : mass (applyKernel K p) = 0
  · have hu := zero_of_zero_mass _ hnn hz
    have hv := zero_of_zero_mass _ hnn' (hm.symm.trans hz)
    rw [hu, hv]
    funext z
    simp [push]
  · have hmpos : 0 < mass (applyKernel K p) :=
      lt_of_le_of_ne (Finset.sum_nonneg (fun x _ => hnn x)) (Ne.symm hz)
    have he := hn hmpos
    rw [push_normalize] at he
    funext z
    have hd := congrFun he z
    simp only [normalize, mass_push] at hd
    rw [← hm] at hd
    calc
      push π (applyKernel K p) z =
          (push π (applyKernel K p) z / mass (applyKernel K p)) * mass (applyKernel K p) :=
        (div_mul_cancel₀ _ hz).symm
      _ = (applyKernel L (push π p) z / mass (applyKernel K p)) * mass (applyKernel K p) :=
        congrArg (fun v => v * mass (applyKernel K p)) hd
      _ = applyKernel L (push π p) z := div_mul_cancel₀ _ hz

/-- Proof fields carry no extra choice: uniqueness of kernels is uniqueness of instruments. -/
theorem quotient_unique (π : X → Z) (hπ : Function.Surjective π)
    (K : Law X A O) (L M : Law Z A O)
    (hL : ∀ a o, Intertwines π (K.kernel a o) (L.kernel a o))
    (hM : ∀ a o, Intertwines π (K.kernel a o) (M.kernel a o)) : L = M := by
  have he := quotient_kernel_unique π hπ K L M hL hM
  cases L
  cases M
  cases he
  rfl

/-- The report-probability / positive-posterior characterization is an iff, for actual laws. -/
theorem instrument_iff_reports_and_posteriors (π : X → Z)
    (K : Law X A O) (L : Law Z A O) :
    (∀ a o, Intertwines π (K.kernel a o) (L.kernel a o)) ↔
    (∀ a o p, IsDist p →
      mass (applyKernel (K.kernel a o) p) = mass (applyKernel (L.kernel a o) (push π p)) ∧
      (0 < mass (applyKernel (K.kernel a o) p) →
        push π (normalize (applyKernel (K.kernel a o) p)) =
          normalize (applyKernel (L.kernel a o) (push π p)))) := by
  constructor
  · intro h a o p _
    refine ⟨report_mass_eq π (h a o) p, ?_⟩
    intro _
    rw [push_normalize, h a o p]
  · intro h a o
    exact intertwines_of_mass_and_posteriors π (K.kernel a o) (L.kernel a o)
      (K.nonnegative a o) (L.nonnegative a o) (h a o)

end
end Instrument
end Komorebi.MachineTheory
