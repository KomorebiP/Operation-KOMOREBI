import AVOC.AdaptiveProbeControl
import AVOC.AffineRankProbe

namespace Komorebi.AVOC.Affine.AdaptiveRankProbe

set_option linter.unusedSectionVars false

open RankProbe Factorization

variable {R : Type} {Ω P : Type*} [Field R] [DecidableEq R]
  [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]
  {n m : Nat}

/-- A finite workload catalogue. The hidden world indexes a matrix instance;
a probe indexes one exact two-by-two minor. -/
structure Catalogue where
  matrix : Ω → Matrix (Fin m) (Fin n) R
  probe : P → MinorTwo m n
  fee : P → ℚ
  fee_nonneg : ∀ p, 0 ≤ fee p
  denialBenefit : ℚ
  denialBenefit_nonneg : 0 ≤ denialBenefit

/-- The abstract finite-catalogue probe model used by the adaptive planner. -/
def model (c : Catalogue (R:=R) (Ω:=Ω) (P:=P) (n:=n) (m:=m)) :
    AdaptiveProbe.Model Ω P where
  detects p w := check2 (c.matrix w) (c.probe p)
  fee := c.fee
  fee_nonneg := c.fee_nonneg
  benefit := c.denialBenefit
  benefit_nonneg := c.denialBenefit_nonneg

/-- A positive catalogue report is an actual rank-two lower-bound certificate
for the corresponding matrix. -/
theorem positive_report_rank_two (c : Catalogue (R:=R) (Ω:=Ω) (P:=P) (n:=n) (m:=m))
    (w : Ω) (p : P) (h : (model c).detects p w = true) : 2 ≤ (c.matrix w).rank :=
  check2_rank_lower (c.matrix w) (c.probe p) h

/-- If the matrix is the linear part of an affine map, a positive report bounds
every exact two-stage affine factorization. -/
theorem positive_report_bounds_every_factor
    (c : Catalogue (R:=R) (Ω:=Ω) (P:=P) (n:=n) (m:=m))
    (w : Ω) (p : P) (f : Signature R n m)
    (hm : f.linear = c.matrix w)
    (h : (model c).detects p w = true)
    {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : compose b a = f) : 2 ≤ k := by
  have hr : 2 ≤ f.linear.rank := by simpa [hm] using positive_report_rank_two c w p h
  have hu := any_factor_rank_upper a b
  rw [he] at hu
  exact hr.trans hu

/-- The planner's success probability is exactly the fraction of currently
retained catalogue matrices on which the selected minor is nonzero. -/
theorem success_probability_formula
    (c : Catalogue (R:=R) (Ω:=Ω) (P:=P) (n:=n) (m:=m))
    (s : AdaptiveProbe.State Ω P) (p : P) :
    AdaptiveProbe.successProb (model c) s p =
      (s.worlds.filter (fun w => check2 (c.matrix w) (c.probe p))).card / s.worlds.card := rfl

/-- Offset changes do not alter any probe outcome when the linear catalogue is reused. -/
theorem probe_outcome_offset_invariant
    (c : Catalogue (R:=R) (Ω:=Ω) (P:=P) (n:=n) (m:=m))
    (f g : Signature R n m) (w : Ω) (p : P)
    (hf : f.linear = c.matrix w) (hg : g.linear = c.matrix w) :
    check2 f.linear (c.probe p) = check2 g.linear (c.probe p) := by
  rw [hf,hg]

end Komorebi.AVOC.Affine.AdaptiveRankProbe
