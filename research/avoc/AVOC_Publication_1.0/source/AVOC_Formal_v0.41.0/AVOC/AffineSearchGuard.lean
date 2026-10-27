import AVOC.AffineReuse
import Mathlib.Tactic.GCongr

namespace Komorebi.AVOC.Affine.SearchGuard

open Factorization
variable {R : Type} [Field R] {n m : Nat}

/-- A cheap certified width floor. Nonzero linear maps need at least one coordinate.
It does not compute rank and is not asserted to be tight. -/
def widthFloor [DecidableEq R] (f : Signature R n m) : Nat :=
  if f.linear = 0 then 0 else 1

theorem zero_width_linear (a : Signature R n 0) (b : Signature R 0 m) :
    (compose b a).linear = 0 := by
  ext i j
  simp [compose]

theorem widthFloor_le_factor [DecidableEq R] (f : Signature R n m)
    {k : Nat} (a : Signature R n k) (b : Signature R k m) (h : compose b a = f) :
    widthFloor f ≤ k := by
  unfold widthFloor
  split
  · exact Nat.zero_le _
  next hn =>
    by_contra hk
    have hzero : k = 0 := by omega
    subst k
    exact hn (by rw [← h]; exact zero_width_linear a b)

theorem widthFloor_le_checked [DecidableEq R] (f : Signature R n m) (c : Checked f) :
    widthFloor f ≤ c.candidate.width :=
  widthFloor_le_factor f c.candidate.first c.candidate.second c.certified.1

/-- Lower cost for the menu consisting of this incumbent, a direct dense map,
and exact two-dense-stage implementations of width at least lo. -/
def menuFloor (original n m lo : Nat) : Nat :=
  min (min original (denseCost n m)) (factorCost n m lo)

theorem menuFloor_le_original (original n m lo : Nat) :
    menuFloor original n m lo ≤ original :=
  (Nat.min_le_left _ _).trans (Nat.min_le_left _ _)

theorem menuFloor_le_dense (original n m lo : Nat) :
    menuFloor original n m lo ≤ denseCost n m :=
  (Nat.min_le_left _ _).trans (Nat.min_le_right _ _)

theorem menuFloor_le_factor (original n m lo : Nat) :
    menuFloor original n m lo ≤ factorCost n m lo := Nat.min_le_right _ _

theorem menuFloor_mono (original n m : Nat) {a b : Nat} (h : a ≤ b) :
    menuFloor original n m a ≤ menuFloor original n m b :=
  min_le_min_left _ (factorCost_mono h)

/-- A supplied lower width certificate can be stronger than the zero/nonzero floor. -/
theorem chosen_cost_ge_floor (p : DenseProgram R n m) (c : Checked (coefficients p))
    (lo : Nat) (hlo : lo ≤ c.candidate.width) :
    menuFloor (executionCost p) n m lo ≤ executionCost (choose p c) := by
  rw [Reuse.choose_cost_exact]
  exact menuFloor_mono _ _ _ hlo

/-- Prospective deployment savings, before charging any future work. -/
def opportunity (calls original floor : Nat) : Nat := calls * (original - floor)

theorem opportunity_bound (calls original floor candidate : Nat)
    (hf : floor ≤ candidate) :
    calls * (original - candidate) ≤ opportunity calls original floor := by
  exact Nat.mul_le_mul_left calls (Nat.sub_le_sub_left hf original)

/-- Compare remaining prospective costs only. Preflight work already paid is not refunded. -/
theorem no_positive_net_of_floor (calls original floor setup candidate : Nat)
    (hf : floor ≤ original) (hc : floor ≤ candidate)
    (hstop : opportunity calls original floor ≤ setup) :
    calls * original ≤ setup + calls * candidate := by
  have hs : original = (original - floor) + floor := (Nat.sub_add_cancel hf).symm
  have hm := Nat.mul_le_mul_left calls hc
  calc
    calls * original = opportunity calls original floor + calls * floor := by
      rw [hs]; simp only [opportunity, Nat.add_sub_cancel_right, Nat.mul_add]
    _ ≤ setup + calls * candidate := Nat.add_le_add hstop hm

theorem no_positive_net_of_setup_lower_bound
    (calls original floor lowerSetup actualSetup candidate : Nat)
    (hf : floor ≤ original) (hc : floor ≤ candidate)
    (hl : lowerSetup ≤ actualSetup)
    (hstop : opportunity calls original floor ≤ lowerSetup) :
    calls * original ≤ actualSetup + calls * candidate :=
  no_positive_net_of_floor _ _ _ _ _ hf hc (hstop.trans hl)

def worthExploring (calls original floor lowerSetup : Nat) : Bool :=
  decide (lowerSetup < opportunity calls original floor)

theorem worthExploring_iff (calls original floor lowerSetup : Nat) :
    worthExploring calls original floor lowerSetup = true ↔
      lowerSetup < opportunity calls original floor := by simp [worthExploring]

theorem skipped_search_no_positive_net
    (calls original floor lowerSetup actualSetup candidate : Nat)
    (hf : floor ≤ original) (hc : floor ≤ candidate)
    (hl : lowerSetup ≤ actualSetup)
    (h : worthExploring calls original floor lowerSetup = false) :
    calls * original ≤ actualSetup + calls * candidate := by
  have hb : opportunity calls original floor ≤ lowerSetup := by
    simpa [worthExploring, Nat.not_lt] using h
  exact no_positive_net_of_setup_lower_bound _ _ _ _ _ _ hf hc hl hb

/-- Concrete early stopping for every accepted minimum-width certificate, not a
claim that all affine execution strategies are represented by this menu. -/
theorem affine_skip_sound [DecidableEq R] (p : DenseProgram R n m)
    (c : Checked (coefficients p)) (calls lowerSetup actualSetup : Nat)
    (hl : lowerSetup ≤ actualSetup)
    (hskip : worthExploring calls (executionCost p)
      (menuFloor (executionCost p) n m (widthFloor (coefficients p))) lowerSetup = false) :
    calls * executionCost p ≤ actualSetup + calls * executionCost (choose p c) := by
  exact skipped_search_no_positive_net _ _ _ _ _ _
    (menuFloor_le_original _ _ _ _) (chosen_cost_ge_floor p c _ (widthFloor_le_checked _ c))
    hl hskip

/-- Exact count of factor and witness entries emitted by the reference proposer.
This is a tariff, not a universal algorithmic lower bound on all proposers. -/
def emissionCharge (n m r : Nat) : Nat := r*n + r + m*r + m + r*m + n*r

theorem emissionCharge_mono (n m : Nat) {r k : Nat} (h : r ≤ k) :
    emissionCharge n m r ≤ emissionCharge n m k := by
  unfold emissionCharge
  gcongr

theorem checkingCharge_mono (n m : Nat) {r k : Nat} (h : r ≤ k) :
    checkingCharge n m r ≤ checkingCharge n m k := by
  unfold checkingCharge composeCost denseCost
  gcongr

def coldFloor (n m lo : Nat) : Nat := emissionCharge n m lo + checkingCharge n m lo

theorem coldFloor_lower (n m lo width generation : Nat)
    (hw : lo ≤ width) (hg : emissionCharge n m width ≤ generation) :
    coldFloor n m lo ≤ generation + checkingCharge n m width :=
  Nat.add_le_add ((emissionCharge_mono n m hw).trans hg) (checkingCharge_mono n m hw)

/-- Cost to revalidate the old certificate, compare linear keys, and adjust the
new affine offset. Normalization/lookup/preflight costs are accounted separately. -/
def reuseCharge (n m r : Nat) : Nat := checkingCharge n m r + m*n + denseCost r m

theorem reuseCharge_mono (n m : Nat) {a b : Nat} (h : a ≤ b) :
    reuseCharge n m a ≤ reuseCharge n m b := by
  unfold reuseCharge
  have hc := checkingCharge_mono n m h
  have hd : denseCost a m ≤ denseCost b m := by unfold denseCost; gcongr
  omega

theorem reuseCharge_no_free_validation (n m r : Nat) :
    checkingCharge n m r ≤ reuseCharge n m r := by unfold reuseCharge; omega

/-- An explicit lifecycle boundary; it counts one validation per session. -/
def coldLifecycle (sessions callsPerSession generation validation perCall : Nat) : Nat :=
  sessions * (generation + validation + callsPerSession * perCall)

def warmLifecycle (sessions callsPerSession generation validation adaptation perCall : Nat) : Nat :=
  generation + sessions * (validation + adaptation + callsPerSession * perCall)

theorem reuse_lifecycle_break_even
    (sessions calls generation validation adaptation perCall : Nat) :
    warmLifecycle sessions calls generation validation adaptation perCall ≤
      coldLifecycle sessions calls generation validation perCall ↔
    generation + sessions * adaptation ≤ sessions * generation := by
  unfold warmLifecycle coldLifecycle
  simp only [Nat.mul_add]
  omega

/-- Transfer and import never remove the option of keeping a cheaper incumbent. -/
theorem zero_cost_incumbent_no_positive_search_net (p : DenseProgram R n m)
    (c : Checked (coefficients p)) (calls setup : Nat) (hp : executionCost p = 0) :
    calls * executionCost p ≤ setup + calls * executionCost (choose p c) := by
  rw [hp]; simp

end Komorebi.AVOC.Affine.SearchGuard
