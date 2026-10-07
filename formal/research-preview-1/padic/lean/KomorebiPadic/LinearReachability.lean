import Mathlib.LinearAlgebra.Span.Basic
import Mathlib.LinearAlgebra.Quotient.Card
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Data.Nat.Log
import Mathlib.Data.Fintype.Card
import Lean.Elab.Tactic.Omega

/-! # Correlation-aware reachable submodules
The state object is an R-module, not a coordinate box. Reachability here means
linear span of the digit orbit. It is not the orbit set or an observable quotient.
-/
namespace KomorebiPadic
namespace LinearReachability
variable {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]

structure System (R V A : Type*) [CommRing R] [AddCommGroup V] [Module R V] where
  initial : V
  transition : A → V →ₗ[R] V

def run (M : System R V A) : List A → V → V
  | [], x => x
  | d :: ds, x => run M ds (M.transition d x)

theorem run_append (M : System R V A) (xs ys : List A) (x : V) :
    run M (xs ++ ys) x = run M ys (run M xs x) := by
  induction xs generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (M.transition d x)

def Closed (M : System R V A) (U : Submodule R V) : Prop :=
  M.initial ∈ U ∧ ∀ d x, x ∈ U → M.transition d x ∈ U

noncomputable def step (M : System R V A) (U : Submodule R V) : Submodule R V :=
  (U ⊔ Submodule.span R {M.initial}) ⊔ ⨆ d, U.map (M.transition d)

theorem le_step (M : System R V A) (U : Submodule R V) : U ≤ step M U :=
  le_sup_left.trans le_sup_left

theorem seed_mem_step (M : System R V A) (U : Submodule R V) : M.initial ∈ step M U :=
  (le_sup_right.trans le_sup_left : Submodule.span R {M.initial} ≤ step M U)
    (Submodule.subset_span (Set.mem_singleton _))

theorem transition_mem_step (M : System R V A) (U : Submodule R V)
    (d : A) (x : V) (hx : x ∈ U) : M.transition d x ∈ step M U :=
  (show (⨆ d, U.map (M.transition d)) ≤ step M U from le_sup_right)
    (Submodule.mem_iSup_of_mem d (Submodule.mem_map.mpr ⟨x,hx,rfl⟩))

theorem step_mono (M : System R V A) {U W : Submodule R V} (h : U ≤ W) :
    step M U ≤ step M W := by
  apply sup_le_sup
  · exact sup_le_sup_right h _
  · exact iSup_mono (fun d => Submodule.map_mono h)

theorem step_eq_iff (M : System R V A) (U : Submodule R V) : step M U = U ↔ Closed M U := by
  constructor
  · intro h
    exact ⟨h ▸ seed_mem_step M U, fun d x hx => h ▸ transition_mem_step M U d x hx⟩
  · rintro ⟨hi,ht⟩
    apply le_antisymm _ (le_step M U)
    apply sup_le
    · exact sup_le le_rfl (Submodule.span_le.mpr (by simpa using hi))
    · apply iSup_le
      intro d y hy
      obtain ⟨x,hx,rfl⟩ := Submodule.mem_map.mp hy
      exact ht d x hx

noncomputable def iterate (M : System R V A) : ℕ → Submodule R V
  | 0 => ⊥
  | n+1 => step M (iterate M n)

theorem iterate_le_closed (M : System R V A) (U : Submodule R V) (hU : Closed M U) (n : ℕ) :
    iterate M n ≤ U := by
  induction n with
  | zero => exact bot_le
  | succ n ih => exact (step_mono M ih).trans ((step_eq_iff M U).mpr hU).le

theorem iterate_mono (M : System R V A) : Monotone (iterate M) :=
  monotone_nat_of_le_succ (fun _ => le_step M _)

theorem run_mem_closed (M : System R V A) (U : Submodule R V) (hU : Closed M U)
    (ds : List A) {x : V} (hx : x ∈ U) : run M ds x ∈ U := by
  induction ds generalizing x with
  | nil => exact hx
  | cons d ds ih => exact ih (hU.2 d x hx)

noncomputable def reachable (M : System R V A) : Submodule R V :=
  Submodule.span R (Set.range (fun ds : List A => run M ds M.initial))

theorem orbit_mem_reachable (M : System R V A) (ds : List A) : run M ds M.initial ∈ reachable M :=
  Submodule.subset_span ⟨ds,rfl⟩

theorem initial_mem_reachable (M : System R V A) : M.initial ∈ reachable M :=
  orbit_mem_reachable M []

theorem reachable_closed (M : System R V A) : Closed M (reachable M) := by
  refine ⟨initial_mem_reachable M, ?_⟩
  intro d x hx
  induction hx using Submodule.span_induction with
  | mem y hy =>
    obtain ⟨ds,rfl⟩ := hy
    have h := orbit_mem_reachable M (ds ++ [d])
    simpa only [run_append, run] using h
  | zero => simpa only [map_zero] using (reachable M).zero_mem
  | add x y _ _ hx hy => simpa only [map_add] using (reachable M).add_mem hx hy
  | smul a x _ hx => simpa only [map_smul] using (reachable M).smul_mem a hx

theorem reachable_le (M : System R V A) (U : Submodule R V) (hU : Closed M U) : reachable M ≤ U := by
  apply Submodule.span_le.mpr
  rintro x ⟨ds,rfl⟩
  exact run_mem_closed M U hU ds hU.1

theorem reachable_unique (M : System R V A) (U : Submodule R V) (hU : Closed M U)
    (hmin : ∀ W, Closed M W → U ≤ W) : U = reachable M :=
  le_antisymm (hmin _ (reachable_closed M)) (reachable_le M U hU)

theorem iterate_eq_reachable_of_fixed (M : System R V A) (n : ℕ)
    (h : step M (iterate M n) = iterate M n) : iterate M n = reachable M :=
  le_antisymm (iterate_le_closed M _ (reachable_closed M) n)
    (reachable_le M _ ((step_eq_iff M _).mp h))

/-- Proper inclusion strictly increases the number of module elements. -/
theorem card_lt_of_lt [Finite V] {U W : Submodule R V} (h : U < W) : Nat.card U < Nat.card W := by
  classical
  let : Fintype U := Fintype.ofFinite U
  let : Fintype W := Fintype.ofFinite W
  rw [Nat.card_eq_fintype_card, Nat.card_eq_fintype_card]
  apply Fintype.card_lt_of_injective_not_surjective (Submodule.inclusion h.le)
    (Submodule.inclusion_injective h.le)
  intro hs
  apply h.not_ge
  intro x hx
  obtain ⟨y,hy⟩ := hs ⟨x,hx⟩
  have he : y.val = x := congrArg Subtype.val hy
  exact he ▸ y.property

/-- Every submodule of an additive p-group has p-power cardinality. -/
theorem submodule_card_power {p b : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b)
    (U : Submodule R V) :
    Nat.card U = p ^ Nat.log p (Nat.card U) ∧ Nat.log p (Nat.card U) ≤ b := by
  have hd : Nat.card U ∣ p^b := by
    rw [← hV]
    exact ⟨Nat.card (V ⧸ U), Submodule.card_eq_card_quotient_mul_card U⟩
  obtain ⟨k,hk,he⟩ := (Nat.dvd_prime_pow hp).mp hd
  rw [he, Nat.log_pow hp.one_lt]
  exact ⟨rfl,hk⟩

/-- Proper submodule growth spends at least one p-adic digit of cardinality. -/
theorem size_lt_of_lt [Finite V] {p b : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b)
    {U W : Submodule R V} (h : U < W) : Nat.log p (Nat.card U) < Nat.log p (Nat.card W) := by
  have hc := card_lt_of_lt h
  rw [(submodule_card_power hp hV U).1, (submodule_card_power hp hV W).1] at hc
  exact (Nat.pow_lt_pow_iff_right hp.one_lt).mp hc

theorem iterate_progress [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) (n : ℕ)
    (hn : iterate M (n+1) ≠ iterate M n) :
    n+1 ≤ Nat.log p (Nat.card (iterate M (n+1))) := by
  have hg : Nat.log p (Nat.card (iterate M n)) < Nat.log p (Nat.card (iterate M (n+1))) :=
    size_lt_of_lt hp hV (lt_of_le_of_ne (le_step M _) (Ne.symm hn))
  induction n with
  | zero => omega
  | succ n ih =>
    have hn' : iterate M (n+1) ≠ iterate M n := by
      intro he
      exact hn (congrArg (step M) he)
    have hh := ih hn' (size_lt_of_lt hp hV (lt_of_le_of_ne (le_step M _) (Ne.symm hn')))
    omega

/-- If the ambient module has p^b elements, b rounds suffice, not p^b rounds. -/
theorem iterate_stabilizes [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) : step M (iterate M b) = iterate M b := by
  by_contra hn
  have hl := iterate_progress M hp hV b hn
  have hu := (submodule_card_power hp hV (iterate M (b+1))).2
  omega

theorem iterate_eq_reachable [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) : iterate M b = reachable M :=
  iterate_eq_reachable_of_fixed M b (iterate_stabilizes M hp hV)

/-- Every later round remains literally the same canonical submodule. -/
theorem iterate_eq_reachable_of_ge [Finite V] (M : System R V A) {p b n : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) (hn : b ≤ n) : iterate M n = reachable M := by
  apply le_antisymm (iterate_le_closed M _ (reachable_closed M) n)
  rw [← iterate_eq_reachable M hp hV]
  exact iterate_mono M hn

noncomputable abbrev State (M : System R V A) := reachable M

noncomputable def initial (M : System R V A) : State M := ⟨M.initial, initial_mem_reachable M⟩
noncomputable def transition (M : System R V A) (d : A) : State M →ₗ[R] State M where
  toFun x := ⟨M.transition d x.val, (reachable_closed M).2 d x.val x.property⟩
  map_add' x y := by apply Subtype.ext; exact (M.transition d).map_add _ _
  map_smul' a x := by apply Subtype.ext; exact (M.transition d).map_smul _ _
noncomputable def runRestricted (M : System R V A) : List A → State M → State M
  | [], x => x
  | d::ds, x => runRestricted M ds (transition M d x)

theorem runRestricted_embedding (M : System R V A) (ds : List A) (x : State M) :
    (runRestricted M ds x).val = run M ds x.val := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (transition M d x)

theorem initial_embedding (M : System R V A) : (initial M).val = M.initial := rfl

theorem state_card_le [Finite V] (M : System R V A) : Nat.card (State M) ≤ Nat.card V :=
  Nat.card_le_card_of_injective Subtype.val Subtype.val_injective

section Naturality
variable {W : Type*} [AddCommGroup W] [Module R W]

theorem run_intertwines (M : System R V A) (N : System R W A) (f : V →ₗ[R] W)
    (hT : ∀ d x, f (M.transition d x) = N.transition d (f x)) (ds : List A) (x : V) :
    f (run M ds x) = run N ds (f x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => simpa only [run, hT] using ih (M.transition d x)

/-- Reachable spans commute with any exact linear simulation preserving the seed. -/
theorem map_reachable (M : System R V A) (N : System R W A) (f : V →ₗ[R] W)
    (hi : f M.initial = N.initial)
    (hT : ∀ d x, f (M.transition d x) = N.transition d (f x)) :
    (reachable M).map f = reachable N := by
  unfold reachable
  rw [Submodule.map_span]
  congr 1
  ext y
  constructor
  · rintro ⟨x,⟨ds,rfl⟩,rfl⟩
    exact ⟨ds, (run_intertwines M N f hT ds M.initial).trans (congrArg (run N ds) hi) |>.symm⟩
  · rintro ⟨ds,rfl⟩
    exact ⟨run M ds M.initial, ⟨ds,rfl⟩,
      (run_intertwines M N f hT ds M.initial).trans (congrArg (run N ds) hi)⟩
end Naturality
end LinearReachability
end KomorebiPadic
