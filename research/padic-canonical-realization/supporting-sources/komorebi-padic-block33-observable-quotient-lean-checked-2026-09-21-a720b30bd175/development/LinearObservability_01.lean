import KomorebiPadic.LinearReachability
import Mathlib.LinearAlgebra.Quotient.Basic

/-! # Unobservable states and finite observation horizons
The alphabet is arbitrary. Finite stabilization uses the cardinality p^b of the
state module, not a field dimension or a matrix rank. Iteration n checks exactly
words of length strictly less than n, including the empty word when n > 0.
-/
namespace KomorebiPadic
namespace LinearObservability
variable {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]

structure System (R V A : Type*) [CommRing R] [AddCommGroup V] [Module R V] where
  dynamics : LinearReachability.System R V A
  output : V →ₗ[R] R

def wordMap (M : System R V A) : List A → V →ₗ[R] V
  | [] => LinearMap.id
  | d :: ds => (wordMap M ds).comp (M.dynamics.transition d)

@[simp] theorem wordMap_apply (M : System R V A) (ds : List A) (x : V) :
    wordMap M ds x = LinearReachability.run M.dynamics ds x := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (M.dynamics.transition d x)

def observation (M : System R V A) (ds : List A) : V →ₗ[R] R :=
  M.output.comp (wordMap M ds)

@[simp] theorem observation_nil (M : System R V A) (x : V) : observation M [] x = M.output x := rfl
@[simp] theorem observation_cons (M : System R V A) (d : A) (ds : List A) (x : V) :
    observation M (d :: ds) x = observation M ds (M.dynamics.transition d x) := rfl

noncomputable def unobservable (M : System R V A) : Submodule R V :=
  ⨅ ds : List A, LinearMap.ker (observation M ds)

@[simp] theorem mem_unobservable (M : System R V A) (x : V) :
    x ∈ unobservable M ↔ ∀ ds, observation M ds x = 0 := by
  simp [unobservable]

def SilentInvariant (M : System R V A) (U : Submodule R V) : Prop :=
  U ≤ LinearMap.ker M.output ∧ ∀ d, U ≤ U.comap (M.dynamics.transition d)

theorem unobservable_silentInvariant (M : System R V A) :
    SilentInvariant M (unobservable M) := by
  constructor
  · intro x hx
    exact (mem_unobservable M x).mp hx []
  · intro d x hx
    exact (mem_unobservable M _).mpr (fun ds => (mem_unobservable M x).mp hx (d :: ds))

theorem unobservable_le_ker (M : System R V A) :
    unobservable M ≤ LinearMap.ker M.output := (unobservable_silentInvariant M).1

theorem le_unobservable (M : System R V A) (U : Submodule R V) (hU : SilentInvariant M U) :
    U ≤ unobservable M := by
  intro x hx
  apply (mem_unobservable M x).mpr
  intro ds
  induction ds generalizing x with
  | nil => exact hU.1 hx
  | cons d ds ih => exact ih (hU.2 d hx)

/-- Greatest invariant submodule contained in the immediate-output kernel. -/
theorem unobservable_greatest (M : System R V A) (U : Submodule R V)
    (hU : SilentInvariant M U) : U ≤ unobservable M := le_unobservable M U hU

noncomputable def step (M : System R V A) (U : Submodule R V) : Submodule R V :=
  (U ⊓ LinearMap.ker M.output) ⊓ ⨅ d, U.comap (M.dynamics.transition d)

@[simp] theorem mem_step (M : System R V A) (U : Submodule R V) (x : V) :
    x ∈ step M U ↔ x ∈ U ∧ M.output x = 0 ∧ ∀ d, M.dynamics.transition d x ∈ U := by
  simp [step, and_assoc]

theorem step_le (M : System R V A) (U : Submodule R V) : step M U ≤ U :=
  inf_le_left.trans inf_le_left

theorem step_mono (M : System R V A) {U W : Submodule R V} (h : U ≤ W) :
    step M U ≤ step M W := by
  intro x hx
  rcases (mem_step M U x).mp hx with ⟨hu,ho,ht⟩
  exact (mem_step M W x).mpr ⟨h hu,ho,fun d => h (ht d)⟩

theorem step_eq_iff (M : System R V A) (U : Submodule R V) :
    step M U = U ↔ SilentInvariant M U := by
  constructor
  · intro h
    constructor
    · intro x hx
      exact ((mem_step M U x).mp (h.symm ▸ hx)).2.1
    · intro d x hx
      exact ((mem_step M U x).mp (h.symm ▸ hx)).2.2 d
  · rintro ⟨ho,ht⟩
    apply le_antisymm (step_le M U)
    intro x hx
    exact (mem_step M U x).mpr ⟨hx,ho hx,fun d => ht d hx⟩

noncomputable def iterate (M : System R V A) : ℕ → Submodule R V
  | 0 => ⊤
  | n+1 => step M (iterate M n)

theorem iterate_antitone (M : System R V A) : Antitone (iterate M) :=
  antitone_nat_of_succ_le (fun _ => step_le M _)

/-- At round n, all and only observation words of length < n are imposed. -/
theorem mem_iterate_iff (M : System R V A) (n : ℕ) (x : V) :
    x ∈ iterate M n ↔ ∀ ds : List A, ds.length < n → observation M ds x = 0 := by
  induction n generalizing x with
  | zero => simp [iterate]
  | succ n ih =>
    rw [iterate, mem_step]
    constructor
    · rintro ⟨hu,ho,ht⟩ ds hlen
      cases ds with
      | nil => exact ho
      | cons d ds =>
        apply (ih (M.dynamics.transition d x)).mp (ht d) ds
        simpa using hlen
    · intro hall
      refine ⟨(ih x).mpr (fun ds hlen => hall ds (by omega)), hall [] (by simp), ?_⟩
      intro d
      apply (ih _).mpr
      intro ds hlen
      exact hall (d :: ds) (by simpa using Nat.succ_lt_succ hlen)

theorem unobservable_le_iterate (M : System R V A) (n : ℕ) :
    unobservable M ≤ iterate M n := by
  intro x hx
  exact (mem_iterate_iff M n x).mpr (fun ds _ => (mem_unobservable M x).mp hx ds)

theorem iterate_eq_unobservable_of_fixed (M : System R V A) (n : ℕ)
    (h : step M (iterate M n) = iterate M n) : iterate M n = unobservable M :=
  le_antisymm (le_unobservable M _ ((step_eq_iff M _).mp h)) (unobservable_le_iterate M n)

/-- Each strict descent spends at least one p-power cardinality exponent. -/
theorem iterate_loss [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) (n : ℕ)
    (hn : iterate M (n+1) ≠ iterate M n) :
    Nat.log p (Nat.card (iterate M (n+1))) + (n+1) ≤ b := by
  have hg : Nat.log p (Nat.card (iterate M (n+1))) < Nat.log p (Nat.card (iterate M n)) :=
    LinearReachability.size_lt_of_lt hp hV (lt_of_le_of_ne (step_le M _) hn)
  induction n with
  | zero =>
    have hu := (LinearReachability.submodule_card_power hp hV (iterate M 0)).2
    omega
  | succ n ih =>
    have hn' : iterate M (n+1) ≠ iterate M n := by
      intro he
      exact hn (congrArg (step M) he)
    have hh := ih hn' (LinearReachability.size_lt_of_lt hp hV
      (lt_of_le_of_ne (step_le M _) hn'))
    omega

/-- b rounds suffice when the ambient module has p^b elements. -/
theorem iterate_stabilizes [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) : step M (iterate M b) = iterate M b := by
  by_contra hn
  have hl := iterate_loss M hp hV b hn
  omega

theorem iterate_eq_unobservable [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) : iterate M b = unobservable M :=
  iterate_eq_unobservable_of_fixed M b (iterate_stabilizes M hp hV)

theorem unobservable_iff_finite_words [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) (x : V) :
    x ∈ unobservable M ↔ ∀ ds : List A, ds.length < b → observation M ds x = 0 := by
  rw [← iterate_eq_unobservable M hp hV, mem_iterate_iff]

/-- Any observable difference has a distinguishing word shorter than b. -/
theorem exists_short_distinguishing_word [Finite V] (M : System R V A) {p b : ℕ}
    (hp : p.Prime) (hV : Nat.card V = p^b) {x : V} (hx : x ∉ unobservable M) :
    ∃ ds : List A, ds.length < b ∧ observation M ds x ≠ 0 := by
  classical
  have hn := mt (unobservable_iff_finite_words M hp hV x).mpr hx
  push_neg at hn
  exact hn

end LinearObservability
end KomorebiPadic
