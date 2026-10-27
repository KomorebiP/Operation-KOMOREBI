import Komorebi.PacketSelectiveAlgebra

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior
variable {α : Type*}

/-- Finite maximum scan, preserving the incumbent on ties. -/
def winner (e : α → ℚ) : α → List α → α
  | a, [] => a
  | a, b::rest => winner e (if e a < e b then b else a) rest

theorem winner_ge_initial (e : α → ℚ) (a : α) (xs : List α) : e a ≤ e (winner e a xs) := by
  induction xs generalizing a with
  | nil => exact le_rfl
  | cons b xs ih =>
    simp only [winner]
    split_ifs with h
    · exact h.le.trans (ih b)
    · exact ih a

theorem winner_ge_member (e : α → ℚ) (a b : α) (xs : List α) (hb : b ∈ xs) :
    e b ≤ e (winner e a xs) := by
  induction xs generalizing a with
  | nil => simp at hb
  | cons c xs ih =>
    simp only [winner]
    rcases List.mem_cons.mp hb with he | he
    · subst b
      split_ifs with h
      · exact winner_ge_initial e c xs
      · exact (le_of_not_gt h).trans (winner_ge_initial e a xs)
    · exact ih _ he

variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α]

def selectPacket (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (seed : α) (scan : List α) (B : Matrix ι κ ℚ) : α :=
  winner (fun a => rationalEnergy (Q a * M.residual B)) seed scan

def greedyStep (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (seed : α) (scan : List α) (B : Matrix ι κ ℚ) : Matrix ι κ ℚ :=
  packetStep M (Q (selectPacket M Q seed scan B)) B

omit [Fintype α] [DecidableEq ι] [DecidableEq α] in
theorem selectPacket_max (M : RationalModel ι κ υ ω) (Q : α → Matrix ι ι ℚ)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ) (a : α) :
    rationalEnergy (Q a*M.residual B) ≤ rationalEnergy (Q (selectPacket M Q seed scan B)*M.residual B) :=
  winner_ge_member _ seed a scan (hscan a)

/-- Pigeonhole lower bound for the actually selected packet, including repeated scan labels. -/
theorem selected_energy_share (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ) :
    rationalEnergy (M.residual B) / (Fintype.card α : ℚ) ≤
      rationalEnergy (Q (selectPacket M Q seed scan B)*M.residual B) := by
  have hc : (0 : ℚ) < Fintype.card α := by
    exact_mod_cast (Fintype.card_pos_iff.mpr ⟨seed⟩)
  have hsum := Finset.sum_le_sum (fun a (_ : a ∈ Finset.univ) => selectPacket_max M Q seed scan hscan B a)
  rw [sum_left_energy Q hQ] at hsum
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul] at hsum
  exact (div_le_iff₀ hc).mpr (by simpa only [mul_comm] using hsum)

omit [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq α] in
def adaptiveRate (q : ℚ) (count : ℕ) : ℚ := 1 - (1-q)/(count : ℚ)

omit [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq α] in
theorem adaptiveRate_bounds (q : ℚ) (count : ℕ) (hq : 0 ≤ q) (h1 : q < 1)
    (hc : 0 < count) : 0 ≤ adaptiveRate q count ∧ adaptiveRate q count < 1 := by
  have hc0 : (0 : ℚ) < count := by exact_mod_cast hc
  have hc1 : (1 : ℚ) ≤ count := by exact_mod_cast hc
  have hd : 0 < (1-q)/(count : ℚ) := div_pos (sub_pos.mpr h1) hc0
  have hu : (1-q)/(count : ℚ) ≤ 1 := (div_le_one hc0).mpr (by linarith)
  unfold adaptiveRate
  constructor <;> linarith

/-- Global geometric progress for an actual maximum-energy output-packet step. -/
theorem greedy_energy_contract (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (hscan : ∀ a, a ∈ scan) (B : Matrix ι κ ℚ) :
    rationalEnergy (M.residual (greedyStep M Q seed scan B)) ≤
      adaptiveRate M.solverRate (Fintype.card α)*rationalEnergy (M.residual B) := by
  have hd := packetStep_energy_descent M hs Q hQ (selectPacket M Q seed scan B) B
  have ha := selected_energy_share M Q hQ seed scan hscan B
  have hm := mul_le_mul_of_nonneg_left ha (sub_nonneg.mpr (M.solverRate_bounds hs).2.le)
  calc
    _ ≤ rationalEnergy (M.residual B) - (1-M.solverRate)*
        rationalEnergy (Q (selectPacket M Q seed scan B)*M.residual B) := hd
    _ ≤ rationalEnergy (M.residual B) - (1-M.solverRate)*
        (rationalEnergy (M.residual B)/(Fintype.card α : ℚ)) := sub_le_sub_left hm _
    _ = _ := by unfold adaptiveRate; ring

end Komorebi.AdaptivePosterior
