import CrossRadixWidthOperatorBasis
import Mathlib.Data.Fintype.Powerset

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Primitive divisor shell: the coordinate delta-vector at `c`. -/
def shellVec (c : DivIdx T) : DivCoord T :=
  fun x => if x = c then 1 else 0

/-- Primitive divisor-shell endomorphism. -/
def shellEnd (c : DivIdx T) : Module.End ℂ (DivCoord T) :=
  diagOp (shellVec c)

lemma shellVec_mul_self (c x : DivIdx T) :
    shellVec c x * shellVec c x = shellVec c x := by
  by_cases h : x = c <;> simp [shellVec, h]

lemma shellVec_mul_ne {c e : DivIdx T} (hce : c ≠ e) (x : DivIdx T) :
    shellVec c x * shellVec e x = 0 := by
  by_cases hc : x = c
  · subst x
    simp [shellVec, hce]
  · simp [shellVec, hc]

lemma shellEnd_idempotent (c : DivIdx T) :
    (shellEnd c).comp (shellEnd c) = shellEnd c := by
  ext x y
  by_cases h : y = c <;> simp [shellEnd, diagOp, shellVec, h]

lemma shellEnd_orthogonal {c e : DivIdx T} (hce : c ≠ e) :
    (shellEnd c).comp (shellEnd e) = 0 := by
  apply LinearMap.ext
  intro v
  funext y
  by_cases hye : y = e
  · subst y
    have hec : e ≠ c := hce.symm
    simp [shellEnd, diagOp, shellVec, hec]
  · simp [shellEnd, diagOp, shellVec, hye]

lemma shellVec_sum_eq_one :
    (∑ c : DivIdx T, shellVec c) = (fun _ => (1 : ℂ)) := by
  funext x
  rw [Finset.sum_apply]
  rw [Finset.sum_eq_single x]
  · simp [shellVec]
  · intro c hc hcx
    have hne : x ≠ c := fun hxc : x = c => hcx hxc.symm
    simp [shellVec, hne]
  · intro hx
    exact (hx (Finset.mem_univ x)).elim

lemma shellEnd_sum_eq_id :
    (∑ c : DivIdx T, shellEnd c) = LinearMap.id := by
  ext x y
  simp [shellEnd, diagOp, shellVec]

/-- Width `g` is exactly the sum of primitive shells whose labels are multiples of `g`. -/
lemma widthVec_eq_sum_shells (g : DivIdx T) :
    widthVec g = ∑ c ∈ Finset.univ.filter (fun c : DivIdx T => g.1 ∣ c.1), shellVec c := by
  funext x
  by_cases hg : g.1 ∣ x.1
  · rw [widthVec]
    simp only [hg, ite_true]
    rw [Finset.sum_apply]
    rw [Finset.sum_eq_single x]
    · simp [shellVec]
    · intro c hc hcx
      have hne : x ≠ c := fun hxc : x = c => hcx hxc.symm
      simp [shellVec, hne]
    · intro hx
      have : x ∈ Finset.univ.filter (fun c : DivIdx T => g.1 ∣ c.1) := by simp [hg]
      exact (hx this).elim
  · simp [widthVec, hg, shellVec]

/-- Coordinate-level idempotence. -/
def IsCoordIdempotent (a : DivCoord T) : Prop :=
  ∀ c, a c * a c = a c

lemma isCoordIdempotent_iff_zero_or_one (a : DivCoord T) :
    IsCoordIdempotent a ↔ ∀ c, a c = 0 ∨ a c = 1 := by
  constructor
  · intro h c
    exact eq_zero_or_one_of_sq_eq_self (by simpa [pow_two] using h c)
  · intro h c
    rcases h c with hc | hc <;> simp [hc]

def indicatorVec (S : Set (DivIdx T)) : DivCoord T := by
  classical
  exact fun c => if c ∈ S then 1 else 0

lemma indicatorVec_idempotent (S : Set (DivIdx T)) :
    IsCoordIdempotent (indicatorVec S) := by
  classical
  intro c
  by_cases hc : c ∈ S <;> simp [indicatorVec, hc]

def activeSet (a : DivCoord T) : Set (DivIdx T) :=
  {c | a c = 1}

lemma idempotent_eq_indicator_activeSet {a : DivCoord T} (ha : IsCoordIdempotent a) :
    a = indicatorVec (activeSet a) := by
  classical
  funext c
  rcases (isCoordIdempotent_iff_zero_or_one a).mp ha c with hc | hc
  · simp [indicatorVec, activeSet, hc]
  · simp [indicatorVec, activeSet, hc]

abbrev IdemCoord (T : ℕ) := {a : DivCoord T // IsCoordIdempotent a}

def idemCoordEquivSet : IdemCoord T ≃ Set (DivIdx T) where
  toFun a := activeSet a.1
  invFun S := ⟨indicatorVec S, indicatorVec_idempotent S⟩
  left_inv := by
    intro a
    apply Subtype.ext
    exact (idempotent_eq_indicator_activeSet a.2).symm
  right_inv := by
    classical
    intro S
    ext c
    simp [activeSet, indicatorVec]

noncomputable instance idemCoordFintype : Fintype (IdemCoord T) :=
  Fintype.ofEquiv (Set (DivIdx T)) (idemCoordEquivSet (T := T)).symm

lemma idemCoord_card :
    Fintype.card (IdemCoord T) = 2 ^ Fintype.card (DivIdx T) := by
  rw [Fintype.card_congr (idemCoordEquivSet (T := T))]
  exact Fintype.card_set

lemma diagOp_idempotent_iff (a : DivCoord T) :
    (diagOp a).comp (diagOp a) = diagOp a ↔ IsCoordIdempotent a := by
  constructor
  · intro h c
    have hc := congrArg (fun L : Module.End ℂ (DivCoord T) => L (fun _ => 1) c) h
    simpa [diagOp] using hc
  · intro h
    rw [diagOp_comp]
    congr 1
    funext c
    exact h c

section PositivePeriod

variable (hT : 0 < T)
include hT

/-- The canonical width-projector order is reverse divisibility. -/
lemma widthEnd_absorb_iff (g h : DivIdx T) :
    (widthEnd g).comp (widthEnd h) = widthEnd g ↔ h.1 ∣ g.1 := by
  rw [widthEnd_comp_lcm hT]
  constructor
  · intro heq
    have hv : widthVec (lcmIdx hT g h) = widthVec g := by
      apply diagOp_injective
      simpa [widthEnd] using heq
    have hval := congrFun hv g
    have hl : Nat.lcm g.1 h.1 ∣ g.1 := by
      have hw : widthVec (lcmIdx hT g h) g = 1 := by
        simpa [widthVec] using hval
      by_contra hn
      have hnot : ¬ (lcmIdx hT g h).1 ∣ g.1 := by
        simpa [lcmIdx] using hn
      simp [widthVec, hnot] at hw
    exact dvd_trans (Nat.dvd_lcm_right g.1 h.1) hl
  · intro hd
    have hl : Nat.lcm g.1 h.1 = g.1 := (Nat.lcm_eq_left_iff_dvd).mpr hd
    rw [show lcmIdx hT g h = g by apply Subtype.ext; exact hl]

end PositivePeriod

end KomorebiCrossRadix

namespace KomorebiCrossRadix

variable {T : ℕ}

local instance propDecidable (p : Prop) : Decidable p := Classical.propDecidable p

lemma indicatorVec_mul (S U : Set (DivIdx T)) :
    (fun c => indicatorVec S c * indicatorVec U c) = indicatorVec (S ∩ U) := by
  classical
  funext c
  by_cases hs : c ∈ S <;> by_cases hu : c ∈ U <;> simp [indicatorVec, hs, hu]

lemma indicatorVec_eq_sum_shells (S : Set (DivIdx T)) :
    indicatorVec S = ∑ c ∈ Finset.univ.filter (fun c : DivIdx T => c ∈ S), shellVec c := by
  classical
  funext x
  by_cases hx : x ∈ S
  · rw [Finset.sum_apply, Finset.sum_eq_single x]
    · simp [indicatorVec, shellVec, hx]
    · intro c hc hcx
      have hne : x ≠ c := fun h : x = c => hcx h.symm
      simp [shellVec, hne]
    · intro h
      have : x ∈ Finset.univ.filter (fun c : DivIdx T => c ∈ S) := by simp [hx]
      exact (h this).elim
  · simp [indicatorVec, shellVec, hx]

lemma idempotent_eq_sum_active_shells {a : DivCoord T} (ha : IsCoordIdempotent a) :
    a = ∑ c ∈ Finset.univ.filter (fun c : DivIdx T => c ∈ activeSet a), shellVec c := by
  calc
    a = indicatorVec (activeSet a) := idempotent_eq_indicator_activeSet ha
    _ = ∑ c ∈ Finset.univ.filter (fun c : DivIdx T => c ∈ activeSet a), shellVec c :=
      indicatorVec_eq_sum_shells (activeSet a)

abbrev IdemAlg (T : ℕ) :=
  {P : ProjectorAlg T // P.1.comp P.1 = P.1}

private lemma diagEquiv_val (a : DivCoord T) :
    (diagEquiv (T := T) a : ProjectorAlg T).1 = diagOp a := rfl

def idemAlgEquivCoord : IdemAlg T ≃ IdemCoord T where
  toFun P := by
    let a := (diagEquiv (T := T)).symm P.1
    refine ⟨a, ?_⟩
    apply (diagOp_idempotent_iff a).mp
    have hval : diagOp a = P.1.1 := by
      have h := congrArg Subtype.val ((diagEquiv (T := T)).apply_symm_apply P.1)
      change diagOp a = P.1.1 at h
      exact h
    rw [hval]
    exact P.2
  invFun a := by
    refine ⟨diagEquiv (T := T) a.1, ?_⟩
    change (diagOp a.1).comp (diagOp a.1) = diagOp a.1
    exact (diagOp_idempotent_iff a.1).mpr a.2
  left_inv := by
    intro P
    apply Subtype.ext
    exact (diagEquiv (T := T)).apply_symm_apply P.1
  right_inv := by
    intro a
    apply Subtype.ext
    exact (diagEquiv (T := T)).symm_apply_apply a.1

def idemAlgEquivSet : IdemAlg T ≃ Set (DivIdx T) :=
  (idemAlgEquivCoord (T := T)).trans (idemCoordEquivSet (T := T))

noncomputable instance idemAlgFintype : Fintype (IdemAlg T) :=
  Fintype.ofEquiv (Set (DivIdx T)) (idemAlgEquivSet (T := T)).symm

lemma idemAlg_card :
    Fintype.card (IdemAlg T) = 2 ^ Fintype.card (DivIdx T) := by
  rw [Fintype.card_congr (idemAlgEquivSet (T := T))]
  exact Fintype.card_set

end KomorebiCrossRadix
