import Komorebi.RationalPacketCertificates

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix

/-- Exact model data. Positivity is checked, not silently assumed by this record. -/
structure RationalModel (ι κ υ ω : Type*) where
  observationMatrix : Matrix κ ι ℚ
  priorFactor : Matrix ι υ ℚ
  noiseFactor : Matrix κ ω ℚ
  noiseFloor : ℚ
  mean : ι → ℚ
  observation : κ → ℚ

/-- Proposed gain and optional conservative rational local upper bounds. -/
structure RationalCandidate (ι κ α β : Type*) where
  gain : Matrix ι κ ℚ
  packetUpper : α → β → ℚ
  innovationUpper : ℚ

variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

namespace RationalModel

def prior (M : RationalModel ι κ υ ω) : Matrix ι ι ℚ :=
  M.priorFactor * M.priorFactor.transpose

def noise (M : RationalModel ι κ υ ω) : Matrix κ κ ℚ :=
  M.noiseFactor * M.noiseFactor.transpose + M.noiseFloor • 1

def innovation (M : RationalModel ι κ υ ω) : Matrix κ κ ℚ :=
  M.observationMatrix * M.prior * M.observationMatrix.transpose + M.noise

def residual (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Matrix ι κ ℚ :=
  M.prior * M.observationMatrix.transpose - B * M.innovation

def innovationVector (M : RationalModel ι κ υ ω) : κ → ℚ :=
  M.observation - M.observationMatrix *ᵥ M.mean

end RationalModel

def totalUpper (c : RationalCandidate ι κ α β) : ℚ := ∑ a, ∑ b, c.packetUpper a b

/-- An upper bound on squared transport error, expressed entirely in rational arithmetic. -/
def candidateScore (M : RationalModel ι κ υ ω) (c : RationalCandidate ι κ α β) : ℚ :=
  totalUpper c * (M.noiseFloor + c.innovationUpper) / M.noiseFloor^2

abbrev ValidCandidate (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (c : RationalCandidate ι κ α β) : Prop :=
  0 < M.noiseFloor ∧ RationalPacketsValid Q ∧ RationalPacketsValid D ∧
  (∀ a b, rationalEnergy (Q a * M.residual c.gain * D b) ≤ c.packetUpper a b) ∧
  rationalVectorEnergy M.innovationVector ≤ c.innovationUpper

/-- Recomputes every finite obligation. A producer's claimed success is not trusted. -/
def checkCandidate (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (c : RationalCandidate ι κ α β) : Bool := decide (ValidCandidate M Q D c)

@[simp] theorem checkCandidate_eq_true (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (c : RationalCandidate ι κ α β) :
    checkCandidate M Q D c = true ↔ ValidCandidate M Q D c := by
  simp [checkCandidate]

/-- The tolerance test avoids square roots and divisions. -/
def checkTolerance (M : RationalModel ι κ υ ω)
    (c : RationalCandidate ι κ α β) (ε : ℚ) : Bool :=
  decide (0 ≤ ε ∧ totalUpper c * (M.noiseFloor+c.innovationUpper) ≤ ε^2*M.noiseFloor^2)

omit [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
  [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β] in
@[simp] theorem checkTolerance_eq_true (M : RationalModel ι κ υ ω)
    (c : RationalCandidate ι κ α β) (ε : ℚ) :
    checkTolerance M c ε = true ↔
      0 ≤ ε ∧ totalUpper c*(M.noiseFloor+c.innovationUpper) ≤ ε^2*M.noiseFloor^2 := by
  simp [checkTolerance]

/-- A computable producer with exact rather than inflated upper bounds. -/
def exactCandidate (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    RationalCandidate ι κ α β where
  gain := B
  packetUpper a b := rationalEnergy (Q a * M.residual B * D b)
  innovationUpper := rationalVectorEnergy M.innovationVector

omit [DecidableEq α] [DecidableEq β] in
theorem exactCandidate_valid (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) :
    ValidCandidate M Q D (exactCandidate M Q D B) :=
  ⟨hs, hQ, hD, fun _ _ => le_rfl, le_rfl⟩

omit [DecidableEq α] [DecidableEq β] in
theorem valid_totalUpper_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) : 0 ≤ totalUpper c := by
  exact Finset.sum_nonneg fun a _ => Finset.sum_nonneg fun b _ =>
    (rationalEnergy_nonneg _).trans (h.2.2.2.1 a b)

omit [DecidableEq α] [DecidableEq β] in
theorem valid_innovationUpper_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) : 0 ≤ c.innovationUpper :=
  (rationalVectorEnergy_nonneg _).trans h.2.2.2.2

omit [DecidableEq α] [DecidableEq β] in
theorem valid_candidateScore_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) : 0 ≤ candidateScore M c := by
  exact div_nonneg (mul_nonneg (valid_totalUpper_nonneg M Q D c h)
    (add_nonneg h.1.le (valid_innovationUpper_nonneg M Q D c h))) (sq_nonneg _)

end Komorebi.ExactPosterior
