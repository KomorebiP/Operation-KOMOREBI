import MachineTheory.BayesianLumping
import Mathlib.SetTheory.Cardinal.Finite

/-! Core 3.5. The refinement is defined by actual block-probability sums.
The stopping bound is the number of states minus the initial number of blocks,
not the number of pairs and not a supplied termination assumption. -/
namespace Komorebi.MachineTheory
namespace Refinement
open scoped BigOperators
open Instrument Bayes BayesianLumping
noncomputable section
variable {X A O : Type*} [Fintype X]

def project (P : Setoid X) : X → Quotient P := Quotient.mk P

def coarsen {P Q : Setoid X} (h : P ≤ Q) : Quotient P → Quotient Q :=
  Quotient.map id (fun _ _ hp => h hp)

omit [Fintype X] in
@[simp] theorem coarsen_project {P Q : Setoid X} (h : P ≤ Q) (x : X) :
    coarsen h (project P x) = project Q x := rfl

omit [Fintype X] in
theorem project_surjective (P : Setoid X) : Function.Surjective (project P) := by
  intro q; induction q using Quotient.inductionOn with | _ x => exact ⟨x,rfl⟩

omit [Fintype X] in
theorem coarsen_surjective {P Q : Setoid X} (h : P ≤ Q) :
    Function.Surjective (coarsen h) := by
  intro q; induction q using Quotient.inductionOn with | _ x => exact ⟨project P x,rfl⟩

def blockCount (P : Setoid X) : ℕ := Nat.card (Quotient P)

theorem blockCount_le (P : Setoid X) : blockCount P ≤ Fintype.card X := by
  classical
  simpa [blockCount, Nat.card_eq_fintype_card] using
    Fintype.card_le_of_surjective (project P) (project_surjective P)

theorem blockCount_strict {P Q : Setoid X} (h : P ≤ Q) (hne : P ≠ Q) :
    blockCount Q < blockCount P := by
  classical
  have hni : ¬ Function.Injective (coarsen h) := by
    intro hi
    apply hne
    apply le_antisymm h
    intro x y hxy
    apply Quotient.exact
    exact hi (show coarsen h (project P x) = coarsen h (project P y) from Quotient.sound hxy)
  simpa [blockCount, Nat.card_eq_fintype_card] using
    Fintype.card_lt_of_surjective_not_injective (coarsen h) (coarsen_surjective h) hni

/-- Successor-block masses are the next refinement signature. -/
def signature (K : A → X → X → ℝ) (P : Setoid X) (x : X) : A → Quotient P → ℝ := by
  classical
  exact fun a => push (project P) (fun y => K a y x)

def step (K : A → X → X → ℝ) (P : Setoid X) : Setoid X :=
  P ⊓ Setoid.ker (signature K P)

def Stable (K : A → X → X → ℝ) (P : Setoid X) : Prop := step K P = P

theorem step_le (K : A → X → X → ℝ) (P : Setoid X) : step K P ≤ P :=
  fun _ _ h => h.1

theorem stable_iff (K : A → X → X → ℝ) (P : Setoid X) :
    Stable K P ↔ ∀ x y, P x y → signature K P x = signature K P y := by
  constructor
  · intro h x y hxy
    have hh : step K P x y := by rw [h]; exact hxy
    exact hh.2
  · intro h
    exact le_antisymm (step_le K P) (fun x y hxy => ⟨hxy,h x y hxy⟩)

/-- Aggregation along two finite quotients is literal aggregation along their composite. -/
theorem push_comp {Y Z : Type*} [Fintype Y] [DecidableEq Y] [DecidableEq Z]
    (π : X → Y) (ψ : Y → Z) (p : X → ℝ) :
    push ψ (push π p) = push (ψ ∘ π) p := by
  funext z
  unfold push
  have hi (y : Y) :
      (if ψ y = z then ∑ x, if π x = y then p x else 0 else 0) =
      ∑ x, if π x = y then (if ψ y = z then p x else 0) else 0 := by
    by_cases hy : ψ y = z <;> simp [hy]
  simp_rw [hi]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro x _
  simp

/-- A stable finer partition stays finer after each actual block-sum split. -/
theorem stable_refines_step (K : A → X → X → ℝ) {P Q : Setoid X}
    (h : Q ≤ P) (hQ : Stable K Q) : Q ≤ step K P := by
  classical
  intro x y hxy
  refine ⟨h hxy, ?_⟩
  have hs := (stable_iff K Q).mp hQ x y hxy
  funext a
  have he := congrArg (push (coarsen h)) (congrFun hs a)
  simp only [signature, push_comp] at he
  exact he

attribute [local instance] Classical.propDecidable

/-- A finite state representative suffices to name each current block.
This connects the quotient implementation to the manuscript's literal block sums. -/
theorem step_rel_iff (K : A → X → X → ℝ) (P : Setoid X) (x y : X) :
    step K P x y ↔ P x y ∧ ∀ a z,
      (∑ u, if P u z then K a u x else 0) =
      (∑ u, if P u z then K a u y else 0) := by
  constructor
  · rintro ⟨hxy,hs⟩
    refine ⟨hxy, ?_⟩
    intro a z
    have hh := congrFun (congrFun hs a) (project P z)
    simpa only [signature, push, project, Quotient.eq] using hh
  · rintro ⟨hxy,hs⟩
    refine ⟨hxy, ?_⟩
    funext a q
    induction q using Quotient.inductionOn with
    | _ z => simpa only [signature, push, project, Quotient.eq] using hs a z

/-- The first split retains both the mandatory target and every likelihood value. -/
def initial (P₀ : Setoid X) (l : O → X → ℝ) : Setoid X :=
  P₀ ⊓ Setoid.ker (fun x => fun o => l o x)

def sequence (K : A → X → X → ℝ) (I : Setoid X) : ℕ → Setoid X
  | 0 => I
  | n+1 => step K (sequence K I n)

theorem sequence_le_initial (K : A → X → X → ℝ) (I : Setoid X) (n : ℕ) :
    sequence K I n ≤ I := by
  induction n with
  | zero => exact le_rfl
  | succ n ih => exact le_trans (step_le K _) ih

theorem stable_refines_sequence (K : A → X → X → ℝ) {I Q : Setoid X}
    (h : Q ≤ I) (hq : Stable K Q) (n : ℕ) : Q ≤ sequence K I n := by
  induction n with
  | zero => exact h
  | succ n ih => exact stable_refines_step K ih hq

/-- Every strict refinement adds a block, so a fixed point is reached within
the manuscript's linear-in-state-count number of strict rounds. -/
theorem bounded_stabilization (K : A → X → X → ℝ) (I : Setoid X) :
    ∃ n ≤ Fintype.card X - blockCount I, Stable K (sequence K I n) := by
  by_contra hn
  push Not at hn
  let b := Fintype.card X - blockCount I
  have hg : ∀ n, n ≤ b+1 → blockCount I + n ≤ blockCount (sequence K I n) := by
    intro n
    induction n with
    | zero => intro _; simp [sequence]
    | succ n ih =>
      intro hnb
      have hnb' : n ≤ b := by omega
      have hs := hn n hnb'
      have hc := blockCount_strict (step_le K (sequence K I n)) hs
      have hi := ih (by omega)
      change blockCount I + (n+1) ≤ blockCount (step K (sequence K I n))
      omega
  have hb := hg (b+1) le_rfl
  have hmax := blockCount_le (sequence K I (b+1))
  have hi := blockCount_le I
  dsimp [b] at hb hmax
  omega

def stopIndex (K : A → X → X → ℝ) (I : Setoid X) : ℕ := by
  classical
  exact Nat.find (bounded_stabilization K I)

def terminal (K : A → X → X → ℝ) (I : Setoid X) : Setoid X :=
  sequence K I (stopIndex K I)

theorem stopIndex_bound (K : A → X → X → ℝ) (I : Setoid X) :
    stopIndex K I ≤ Fintype.card X - blockCount I := by
  classical
  exact (Nat.find_spec (bounded_stabilization K I)).1

theorem terminal_stable (K : A → X → X → ℝ) (I : Setoid X) :
    Stable K (terminal K I) := by
  classical
  exact (Nat.find_spec (bounded_stabilization K I)).2

theorem terminal_le (K : A → X → X → ℝ) (I : Setoid X) : terminal K I ≤ I :=
  sequence_le_initial K I _

theorem terminal_coarsest (K : A → X → X → ℝ) (I : Setoid X) {Q : Setoid X}
    (h : Q ≤ I) (hs : Stable K Q) : Q ≤ terminal K I :=
  stable_refines_sequence K h hs _

theorem terminal_unique (K : A → X → X → ℝ) (I : Setoid X) (Q : Setoid X)
    (hle : Q ≤ I) (hs : Stable K Q)
    (hgreatest : ∀ R, R ≤ I → Stable K R → R ≤ Q) : Q = terminal K I :=
  le_antisymm (terminal_coarsest K I hle hs)
    (hgreatest _ (terminal_le K I) (terminal_stable K I))

/-- A stochastic transition is represented by an instrument with one trivial report.
The successor law is still column-oriented, as in Block 01. -/
def transition (K : Law X A Unit) : A → X → X → ℝ := fun a => K.kernel a ()

def PredictionExists (K : Law X A Unit) (P : Setoid X) : Prop := by
  classical
  exact ∃ L : Law (Quotient P) A Unit,
    ∀ a o, Intertwines (project P) (K.kernel a o) (L.kernel a o)

theorem stable_iff_prediction (K : Law X A Unit) (P : Setoid X) :
    Stable (transition K) P ↔ PredictionExists K P := by
  classical
  change Stable (transition K) P ↔
    ∃ L : Law (Quotient P) A Unit,
      ∀ a o, Intertwines (project P) (K.kernel a o) (L.kernel a o)
  rw [quotient_exists_iff (project P) (project_surjective P) K]
  constructor
  · intro h a o z x y hxy
    cases o
    exact congrFun (congrFun ((stable_iff (transition K) P).mp h x y
      (Quotient.exact hxy)) a) z
  · intro h
    apply (stable_iff (transition K) P).mpr
    intro x y hxy
    funext a z
    exact h a () z x y (Quotient.sound hxy)

/-- A separate correction uses one fixed positive coarse likelihood for every prior. -/
def CorrectionsExist (l : O → X → ℝ) (P : Setoid X) : Prop := by
  classical
  exact ∀ o, ∃ g : Quotient P → ℝ, (∀ z, 0 < g z) ∧
    ∀ p, IsDist p → push (project P) (update p (l o)) =
      update (push (project P) p) g

def Admissible (K : Law X A Unit) (l : O → X → ℝ) (P₀ P : Setoid X) : Prop :=
  P ≤ P₀ ∧ PredictionExists K P ∧ CorrectionsExist l P

/-- The Bayesian necessity is proved from two-point priors, not assumed as a field
of the target partition. The likelihood split is exactly the necessary initial split. -/
theorem admissible_iff (K : Law X A Unit) (l : O → X → ℝ) (P₀ P : Setoid X)
    (hl : ∀ o x, 0 < l o x) (hnt : ∃ x y, ¬ P₀ x y) :
    Admissible K l P₀ P ↔ P ≤ initial P₀ l ∧ Stable (transition K) P := by
  classical
  constructor
  · rintro ⟨hle,hpred,hcorr⟩
    refine ⟨?_, (stable_iff_prediction K P).mpr hpred⟩
    intro x y hxy
    refine ⟨hle hxy, ?_⟩
    funext o
    have hn : ∃ u v, project P u ≠ project P v := by
      obtain ⟨u,v,h⟩ := hnt
      exact ⟨u,v, fun he => h (hle (Quotient.exact he))⟩
    exact (fixed_positive_coarse_iff (project P) (project_surjective P) (l o)
      (hl o) hn).mp (hcorr o) x y (Quotient.sound hxy)
  · rintro ⟨hle,hs⟩
    refine ⟨fun _ _ hxy => (hle hxy).1, (stable_iff_prediction K P).mp hs, ?_⟩
    intro o
    let g : Quotient P → ℝ := fun z => l o z.out
    have hf : ∀ x, l o x = g (project P x) := by
      intro x
      have hp : P x (project P x).out := Quotient.exact (Quotient.out_eq (project P x)).symm
      exact congrFun (hle hp).2 o
    exact ⟨g, fun z => hl o z.out,
      fun p _ => update_commutes_of_factored (project P) (l o) g hf p⟩

/-- Core 3.5: the specified splitting process terminates within the exact block-count
bound and returns the unique coarsest operationally admissible refinement. -/
theorem least_prediction_correction_refinement (K : Law X A Unit)
    (l : O → X → ℝ) (P₀ : Setoid X) (hl : ∀ o x, 0 < l o x)
    (hnt : ∃ x y, ¬ P₀ x y) :
    let I := initial P₀ l
    let n := stopIndex (transition K) I
    let P := sequence (transition K) I n
    n ≤ Fintype.card X - blockCount I ∧
      Admissible K l P₀ P ∧
      (∀ Q, Admissible K l P₀ Q → Q ≤ P) ∧
      (∀ Q, Admissible K l P₀ Q →
        (∀ R, Admissible K l P₀ R → R ≤ Q) → Q = P) := by
  dsimp only
  let I := initial P₀ l
  let P := terminal (transition K) I
  have hadm : Admissible K l P₀ P :=
    (admissible_iff K l P₀ P hl hnt).mpr
      ⟨terminal_le _ _, terminal_stable _ _⟩
  have hmin : ∀ Q, Admissible K l P₀ Q → Q ≤ P := by
    intro Q hq
    obtain ⟨hqI,hqS⟩ := (admissible_iff K l P₀ Q hl hnt).mp hq
    exact terminal_coarsest _ _ hqI hqS
  refine ⟨stopIndex_bound _ _, hadm, hmin, ?_⟩
  intro Q hq hbest
  exact le_antisymm (hmin Q hq) (hbest P hadm)

end
end Refinement
end Komorebi.MachineTheory
