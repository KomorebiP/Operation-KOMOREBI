import AVOC.AffineRankProbe

namespace Komorebi.AVOC.Affine.RankProbe

open Factorization SearchGuard
variable {R : Type} [Field R] [DecidableEq R] {n m : Nat}

/-- Four coefficient reads, two multiplications, subtraction, and a zero test.
This declared tariff omits host/IO and list/plan construction overhead. -/
def probeFee : Nat := 8

structure ScanResult (m n : Nat) where
  lower : Nat
  tested : Nat
  remaining : Nat
  witness : Option (MinorTwo m n)
  deriving Repr, DecidableEq

/-- Test only funded probes, stop at the first nonzero minor. A failed or truncated
search never asserts an upper rank bound. Duplicates in a supplied plan are charged. -/
def scan (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat) :
    List (MinorTwo m n) → ScanResult m n
  | [] => ⟨lo,0,credit,none⟩
  | p :: tail =>
    if probeFee ≤ credit then
      if check2 A p then ⟨max lo 2,1,credit-probeFee,some p⟩
      else
        let r := scan A lo (credit-probeFee) tail
        ⟨r.lower,r.tested+1,r.remaining,r.witness⟩
    else ⟨lo,0,credit,none⟩

theorem scan_accounting (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) :
    probeFee * (scan A lo credit ps).tested + (scan A lo credit ps).remaining = credit := by
  induction ps generalizing credit with
  | nil => simp [scan]
  | cons p ps ih =>
    simp only [scan]
    split
    next hc =>
      split
      · simp only; omega
      · have h := ih (credit-probeFee)
        simp only [Nat.mul_add, Nat.mul_one]
        omega
    · simp

theorem scan_count (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) : (scan A lo credit ps).tested ≤ ps.length := by
  induction ps generalizing credit with
  | nil => simp [scan]
  | cons p ps ih =>
    simp only [scan]
    split
    · split
      · simp
      · have h := ih (credit-probeFee); simp only [List.length_cons]; omega
    · simp

theorem scan_lower_preserved (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) (hlo : lo ≤ A.rank) :
    (scan A lo credit ps).lower ≤ A.rank := by
  induction ps generalizing credit with
  | nil => exact hlo
  | cons p ps ih =>
    simp only [scan]
    split
    · split
      next hc => exact max_le hlo (check2_rank_lower A p hc)
      · exact ih (credit-probeFee)
    · exact hlo

theorem scan_lower_monotone (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) : lo ≤ (scan A lo credit ps).lower := by
  induction ps generalizing credit with
  | nil => exact le_rfl
  | cons p ps ih =>
    simp only [scan]; split
    · split
      · exact Nat.le_max_left _ _
      · exact ih _
    · exact le_rfl

theorem scan_witness_valid (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) (p : MinorTwo m n)
    (h : (scan A lo credit ps).witness = some p) :
    p ∈ ps ∧ check2 A p = true := by
  induction ps generalizing credit with
  | nil => simp [scan] at h
  | cons q ps ih =>
    simp only [scan] at h
    split at h
    · split at h
      next hq =>
        have he : q = p := Option.some.inj h
        subst p
        exact ⟨List.mem_cons_self, hq⟩
      · have hr := ih (credit-probeFee) h
        exact ⟨List.mem_cons_of_mem _ hr.1, hr.2⟩
    · cases h

theorem scan_no_witness_no_upgrade (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) (h : (scan A lo credit ps).witness = none) :
    (scan A lo credit ps).lower = lo := by
  induction ps generalizing credit with
  | nil => rfl
  | cons p ps ih =>
    by_cases hc : probeFee ≤ credit
    · by_cases hq : check2 A p = true
      · simp [scan,hc,hq] at h
      · have hr : (scan A lo (credit-probeFee) ps).witness = none := by
          simpa [scan,hc,hq] using h
        simpa [scan,hc,hq] using ih (credit-probeFee) hr
    · simp [scan,hc]

theorem scan_unfunded (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) (h : credit < probeFee) :
    scan A lo credit ps = ⟨lo,0,credit,none⟩ := by
  cases ps <;> simp [scan, Nat.not_le.mpr h]

theorem scan_spent_bound (A : Matrix (Fin m) (Fin n) R) (lo credit : Nat)
    (ps : List (MinorTwo m n)) : probeFee * (scan A lo credit ps).tested ≤ credit := by
  have h := scan_accounting A lo credit ps; omega

omit [DecidableEq R] in
/-- Generalized width certificate, avoiding dependence on a completed factor search. -/
theorem rank_floor_le_checked (f : Signature R n m) (lo : Nat)
    (hl : lo ≤ f.linear.rank) (c : Checked f) : lo ≤ c.candidate.width := by
  rwa [valid_rank_exact c.certified] at hl

theorem scanned_floor_le_checked (f : Signature R n m) (credit : Nat)
    (ps : List (MinorTwo m n)) (c : Checked f) :
    (scan f.linear (widthFloor f) credit ps).lower ≤ c.candidate.width :=
  rank_floor_le_checked f _
    (scan_lower_preserved f.linear _ credit ps (widthFloor_rank f)) c

/-- A larger certified floor can only shrink the opportunity upper bound. -/
theorem opportunity_antitone (calls original n m : Nat) {lo hi : Nat} (h : lo ≤ hi) :
    opportunity calls original (menuFloor original n m hi) ≤
      opportunity calls original (menuFloor original n m lo) := by
  exact Nat.mul_le_mul_left calls (Nat.sub_le_sub_left (menuFloor_mono original n m h) original)

theorem coldFloor_mono (n m : Nat) {lo hi : Nat} (h : lo ≤ hi) :
    coldFloor n m lo ≤ coldFloor n m hi :=
  Nat.add_le_add (emissionCharge_mono n m h) (checkingCharge_mono n m h)

/-- Under the two-dense-stage menu, denial is preserved as rank evidence improves. -/
theorem denial_monotone (calls original n m : Nat) {lo hi : Nat} (h : lo ≤ hi)
    (hs : worthExploring calls original (menuFloor original n m lo) (coldFloor n m lo) = false) :
    worthExploring calls original (menuFloor original n m hi) (coldFloor n m hi) = false := by
  have h1 := opportunity_antitone calls original n m h
  have h2 := coldFloor_mono n m h
  have h3 : opportunity calls original (menuFloor original n m lo) ≤ coldFloor n m lo := by
    simpa [worthExploring, Nat.not_lt] using hs
  simp only [worthExploring, decide_eq_false_iff_not, Nat.not_lt]
  omega

omit [DecidableEq R] in
/-- No positive remaining gain, not a promise that past probe costs are repaid. -/
theorem partial_rank_skip_sound (p : DenseProgram R n m) (c : Checked (coefficients p))
    (lo calls generation : Nat) (hl : lo ≤ (coefficients p).linear.rank)
    (hg : emissionCharge n m c.candidate.width ≤ generation)
    (hs : worthExploring calls (executionCost p)
      (menuFloor (executionCost p) n m lo) (coldFloor n m lo) = false) :
    calls * executionCost p ≤ generation + checkingCharge n m c.candidate.width +
      calls * executionCost (choose p c) := by
  have hw := rank_floor_le_checked (coefficients p) lo hl c
  exact skipped_search_no_positive_net _ _ _ _ _ _
    (menuFloor_le_original _ _ _ _) (chosen_cost_ge_floor p c lo hw)
    (coldFloor_lower n m lo c.candidate.width generation hw hg) hs

theorem scanned_skip_sound (p : DenseProgram R n m) (c : Checked (coefficients p))
    (probeCredit calls generation : Nat) (ps : List (MinorTwo m n))
    (hg : emissionCharge n m c.candidate.width ≤ generation)
    (hs : worthExploring calls (executionCost p)
      (menuFloor (executionCost p) n m (scan (coefficients p).linear
        (widthFloor (coefficients p)) probeCredit ps).lower)
      (coldFloor n m (scan (coefficients p).linear
        (widthFloor (coefficients p)) probeCredit ps).lower) = false) :
    calls * executionCost p ≤ generation + checkingCharge n m c.candidate.width +
      calls * executionCost (choose p c) :=
  partial_rank_skip_sound p c _ calls generation
    (scan_lower_preserved _ _ _ _ (widthFloor_rank (coefficients p))) hg hs

/-- Known-gain bound for purchasing probes: even a perfect answer cannot save more
than the current execution opportunity, absent cross-task value. -/
theorem probe_no_positive_task_net (calls original floor probeCost setup candidate : Nat)
    (hf : floor ≤ original) (hc : floor ≤ candidate)
    (hp : opportunity calls original floor ≤ probeCost) :
    calls * original ≤ probeCost + setup + calls * candidate := by
  have h := no_positive_net_of_floor calls original floor probeCost candidate hf hc hp
  omega

omit [DecidableEq R] in
/-- An inexpensive floor can prove the baseline already beats every two-stage
implementation. This does not construct a factorization or identify the full rank. -/
theorem baseline_le_every_factor (p : DenseProgram R n m) (lo : Nat)
    (hl : lo ≤ (coefficients p).linear.rank)
    (hcost : executionCost (cheaper p (fuse p)) ≤ factorCost n m lo)
    {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : compose b a = coefficients p) :
    executionCost (cheaper p (fuse p)) ≤ factorCost n m k := by
  have hr := any_factor_rank_upper a b
  rw [he] at hr
  exact hcost.trans (factorCost_mono (hl.trans hr))

def remainingMinimum (p : DenseProgram R n m) (lo : Nat) : Nat :=
  normalizationCost p + reuseCharge n m lo + emissionCharge n m lo

omit [DecidableEq R] in
theorem remainingMinimum_lower (p : DenseProgram R n m) (lo : Nat)
    (c : Checked (coefficients p)) (generation : Nat)
    (hl : lo ≤ (coefficients p).linear.rank)
    (hg : emissionCharge n m c.candidate.width ≤ generation) :
    remainingMinimum p lo ≤
      normalizationCost p + reuseCharge n m c.candidate.width + generation := by
  have hw := rank_floor_le_checked (coefficients p) lo hl c
  have he := (emissionCharge_mono n m hw).trans hg
  have hc := reuseCharge_mono n m hw
  unfold remainingMinimum
  omega

omit [DecidableEq R] in
theorem baseline_floor_le_selected (p : DenseProgram R n m) (lo : Nat)
    (c : Checked (coefficients p)) (hl : lo ≤ (coefficients p).linear.rank) :
    menuFloor (executionCost (cheaper p (fuse p))) n m lo ≤ executionCost (choose p c) := by
  have hw := rank_floor_le_checked (coefficients p) lo hl c
  have hd : executionCost (cheaper p (fuse p)) ≤ denseCost n m := cheaper_right p (fuse p)
  unfold menuFloor
  rw [Nat.min_eq_left hd, Reuse.cheaper_cost, fused_execution_cost, Reuse.choose_cost_exact]
  exact min_le_min_left _ (factorCost_mono hw)

omit [DecidableEq R] in
theorem paid_probe_denial_sound (p : DenseProgram R n m) (lo calls generation : Nat)
    (c : Checked (coefficients p)) (hl : lo ≤ (coefficients p).linear.rank)
    (hg : emissionCharge n m c.candidate.width ≤ generation)
    (hs : worthExploring calls (executionCost (cheaper p (fuse p)))
      (menuFloor (executionCost (cheaper p (fuse p))) n m lo) (remainingMinimum p lo) = false) :
    calls * executionCost (cheaper p (fuse p)) ≤
      normalizationCost p + reuseCharge n m c.candidate.width + generation +
        calls * executionCost (choose p c) :=
  skipped_search_no_positive_net _ _ _ _ _ _ (menuFloor_le_original _ _ _ _)
    (baseline_floor_le_selected p lo c hl) (remainingMinimum_lower p lo c generation hl hg) hs

end Komorebi.AVOC.Affine.RankProbe
