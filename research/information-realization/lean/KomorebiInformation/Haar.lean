module
public import KomorebiInformation.Predictive
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Algebra.Field.ZMod
public import Mathlib.Data.Fin.VecNotation
public import Mathlib.Tactic
@[expose] public section

namespace KomorebiInformation.Haar
variable {K : Type*} [Field K]
abbrev Source (K : Type*) := Fin 4 → K
abbrev Coarse (K : Type*) := Fin 2 → K
abbrev Closed (K : Type*) := Fin 3 → K

def shift (x : Source K) : Source K := ![x 1, x 2, x 3, x 0]
def coarse (x : Source K) : Coarse K := ![x 0+x 1, x 2+x 3]
def detail (x : Source K) : Coarse K := ![x 0-x 1, x 2-x 3]
def supplement (d : Coarse K) : K := d 1-d 0

def decoder (o : Coarse K) (c : K) : Coarse K :=
  ![(o 0+o 1+c)/2, (o 0+o 1-c)/2]

def closed (x : Source K) : Closed K :=
  ![coarse x 0, coarse x 1, supplement (detail x)]

def closedStep (s : Closed K) : Closed K :=
  ![(s 0+s 1+s 2)/2, (s 0+s 1-s 2)/2, s 1-s 0]

def closedOutput (s : Closed K) : Coarse K := ![s 0, s 1]

/-- Symbolic field proof: not a 625-state Python test. -/
theorem next_output_repair (htwo : (2 : K) ≠ 0) (x : Source K) :
    decoder (coarse x) (supplement (detail x)) = coarse (shift x) := by
  funext i
  fin_cases i <;> simp [decoder, coarse, detail, supplement, shift] <;>
    (try field_simp) <;> ring

/-- The helper uses only its two detail coordinates. -/
theorem helper_repair_correct (htwo : (2 : K) ≠ 0) :
    Repair (coarse (K := K)) (coarse ∘ shift) detail supplement
      (fun p => decoder p.1 p.2) := by
  intro x
  exact next_output_repair htwo x

/-- The augmented three-coordinate state closes under the four-state shift. -/
theorem closed_semiconjugacy (htwo : (2 : K) ≠ 0) (x : Source K) :
    closed (shift x) = closedStep (closed x) := by
  funext i
  fin_cases i <;> simp [closed, closedStep, coarse, detail, supplement, shift] <;>
    (try field_simp) <;> ring

theorem closed_preserves_observation (x : Source K) :
    closedOutput (closed x) = coarse x := by
  funext i
  fin_cases i <;> rfl

/-- All horizons are proved by induction, not bounded by the earlier replay. -/
theorem closed_predicts_all_times (htwo : (2 : K) ≠ 0) (n : Nat) (x : Source K) :
    closed (shift^[n] x) = closedStep^[n] (closed x) :=
  Predictive.simulation_all_times shift closedStep closed
    (closed_semiconjugacy htwo) n x

theorem coarse_predicts_all_times (htwo : (2 : K) ≠ 0) (n : Nat) (x : Source K) :
    coarse (shift^[n] x) = closedOutput (closedStep^[n] (closed x)) := by
  rw [← closed_predicts_all_times htwo, closed_preserves_observation]

/-- A nonzero source direction invisible to the predictive representation. -/
def invisible : Source K := ![1,-1,1,-1]

theorem invisible_has_zero_closed_state : closed (invisible : Source K) = closed 0 := by
  funext i
  fin_cases i <;> simp [closed, coarse, detail, supplement, invisible]

theorem invisible_ne_zero : (invisible : Source K) ≠ 0 := by
  intro h
  have := congrFun h 0
  simp [invisible] at this

theorem predictive_is_not_source_reconstruction :
    ¬ Sufficient (closed : Source K → Closed K) id := by
  intro h
  exact invisible_ne_zero (h invisible 0 invisible_has_zero_closed_state)

/-- Two shifts exchange the observations; endpoint information can disappear. -/
theorem two_shift_endpoint (x : Source K) :
    coarse (shift (shift x)) = ![coarse x 1, coarse x 0] := by
  funext i
  fin_cases i <;> rfl

/-- The helper seeing only the first detail cannot resolve this witness. -/
def inaccessible : Source K := ![0,0,-1,1]

theorem inaccessible_observation : coarse (inaccessible : Source K) = coarse 0 := by
  funext i
  fin_cases i <;> simp [coarse, inaccessible]

theorem inaccessible_first_detail :
    detail (inaccessible : Source K) 0 = detail 0 0 := by
  simp [detail, inaccessible]

theorem inaccessible_next_output :
    coarse (shift (inaccessible : Source K)) ≠ coarse (shift 0) := by
  intro h
  have h0 := congrFun h 0
  simp [coarse, shift, inaccessible] at h0

theorem first_detail_rejects_every_code {Message : Type*}
    (h : K → Message) (g : Coarse K × Message → Coarse K) :
    ¬ Repair coarse (coarse ∘ shift) (fun x => detail x 0) h g := by
  exact inaccessible_pair_rejects_every_code
    inaccessible_observation inaccessible_first_detail inaccessible_next_output h g

/-- Any correct helper alphabet needs at least one field coordinate's worth
of symbols, even for nonlinear encoders. -/
theorem next_output_alphabet_lower_bound [Fintype K]
    {Message : Type*} [Fintype Message]
    (h : Coarse K → Message) (g : Coarse K × Message → Coarse K)
    (hrep : Repair coarse (coarse ∘ shift) detail h g) :
    Fintype.card K ≤ Fintype.card Message := by
  let s : K → Source K := fun t => ![0,0,t,-t]
  have hr : ∀ t, coarse (s t) = 0 := by
    intro t
    funext i
    fin_cases i <;> simp [coarse,s]
  have hf : Function.Injective ((coarse ∘ shift) ∘ s) := by
    intro a b hab
    have h0 := congrFun hab 0
    simpa [coarse, shift, s] using h0
  exact repair_alphabet_lower_bound hrep s 0 hr hf

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
local instance : Fact (Nat.Prime 2) := ⟨by decide⟩

/-- Concrete application over the declared five-element field. -/
theorem concrete_five_state :
    let x : Source (ZMod 5) := ![4,1,3,2]
    coarse (shift x) = ![4,1] := by decide

/-- Characteristic two is an explicitly rejected boundary for the inverse. -/
theorem characteristic_two_collision :
    let x : Source (ZMod 2) := ![1,0,0,0]
    let y : Source (ZMod 2) := ![0,1,0,0]
    coarse x = coarse y ∧ detail x = detail y ∧ x ≠ y := by decide
end KomorebiInformation.Haar
