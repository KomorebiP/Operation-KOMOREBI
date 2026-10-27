import Komorebi.GreedyPacketConvergence

set_option autoImplicit false
namespace Komorebi.CachedPosterior
open Matrix Komorebi.ExactPosterior Komorebi.AdaptivePosterior
variable {ι κ υ ω α : Type*}

structure Kernel (κ : Type*) where
  step : ℚ
  transition : Matrix κ κ ℚ
  weight : ℚ

structure State (ι κ α : Type*) where
  gain : Matrix ι κ ℚ
  residuals : α → Matrix ι κ ℚ
  energies : α → ℚ
  total : ℚ

variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α]

def prepare (M : RationalModel ι κ υ ω) : Kernel κ :=
  ⟨M.solverStep, 1-M.solverStep • M.innovation,
    (M.noiseFloor+rationalVectorEnergy M.innovationVector)/M.noiseFloor^2⟩

def initialize (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (B : Matrix ι κ ℚ) : State ι κ α :=
  let F := M.residual B
  let G := fun a => Q a * F
  let e := fun a => rationalEnergy (G a)
  ⟨B,G,e,∑ a, e a⟩

def Valid (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ) (c : State ι κ α) : Prop :=
  (∀ a, c.residuals a = Q a * M.residual c.gain) ∧
  (∀ a, c.energies a = rationalEnergy (c.residuals a)) ∧
  c.total = ∑ a, c.energies a

omit [DecidableEq ι] [DecidableEq α] in
theorem initialize_valid (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (B : Matrix ι κ ℚ) : Valid M Q (initialize M Q B) := ⟨fun _ => rfl,fun _ => rfl,rfl⟩

/-- Only the selected residual and energy are recomputed; total is updated by a difference. -/
def step (K : Kernel κ) (a : α) (c : State ι κ α) : State ι κ α :=
  let G := c.residuals a * K.transition
  let e := rationalEnergy G
  ⟨c.gain+K.step • c.residuals a,
    fun b => if b=a then G else c.residuals b,
    fun b => if b=a then e else c.energies b,
    c.total-c.energies a+e⟩

omit [Fintype υ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem step_other_residual (K : Kernel κ) (a b : α) (hba : b ≠ a) (c : State ι κ α) :
    (step K a c).residuals b = c.residuals b := by simp only [step,ite_eq_right hba]

omit [Fintype υ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem step_other_energy (K : Kernel κ) (a b : α) (hba : b ≠ a) (c : State ι κ α) :
    (step K a c).energies b = c.energies b := by simp only [step,ite_eq_right hba]

omit [DecidableEq ι] in
theorem step_gain (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (c : State ι κ α) (hc : Valid M Q c) (a : α) :
    (step (prepare M) a c).gain = packetStep M (Q a) c.gain := by
  simp only [step,prepare,packetStep,hc.1 a]

/-- The cache equations are preserved by the executed update, not assumed for future states. -/
theorem step_valid (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) (a : α) :
    Valid M Q (step (prepare M) a c) := by
  refine ⟨?_,?_,?_⟩
  · intro b
    rw [step_gain M Q c hc a]
    by_cases hb : b=a
    · subst b
      simp only [step,ite_true,prepare,hc.1 a,selected_residual M Q hQ]
    · rw [step_other_residual _ _ _ hb,unselected_residual M Q hQ a b hb,hc.1 b]
  · intro b
    by_cases hb : b=a
    · subst b; simp only [step,ite_true]
    · simpa only [step,ite_eq_right hb] using hc.2.1 b
  · change c.total-c.energies a+rationalEnergy (c.residuals a*(prepare M).transition) =
      ∑ b, if b=a then rationalEnergy (c.residuals a*(prepare M).transition) else c.energies b
    rw [hc.2.2]
    have hi : (fun b => if b=a then rationalEnergy (c.residuals a*(prepare M).transition) else c.energies b) =
        (fun b => c.energies b + if b=a then rationalEnergy (c.residuals a*(prepare M).transition)-c.energies a else 0) := by
      funext b
      split_ifs with hb
      · subst b; ring
      · ring
    rw [hi,Finset.sum_add_distrib]
    simp only [Finset.sum_ite_eq',Finset.mem_univ,ite_true]
    ring

omit [DecidableEq α] in
theorem total_eq_residual_energy (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) :
    c.total = rationalEnergy (M.residual c.gain) := by
  rw [hc.2.2]
  simp only [hc.2.1,hc.1,sum_left_energy Q hQ]

def score (K : Kernel κ) (c : State ι κ α) : ℚ := c.total*K.weight

omit [DecidableEq α] in
theorem score_eq (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (hQ : RationalPacketsValid Q) (c : State ι κ α) (hc : Valid M Q c) :
    score (prepare M) c = M.residualScore c.gain := by
  rw [score,total_eq_residual_energy M Q hQ c hc]
  simp only [prepare,RationalModel.residualScore,div_eq_mul_inv,mul_assoc]

end Komorebi.CachedPosterior
