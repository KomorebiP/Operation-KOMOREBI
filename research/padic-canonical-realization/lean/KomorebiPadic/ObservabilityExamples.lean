import KomorebiPadic.ObservableMaskAutomaton
import Mathlib.Tactic.FinCases

/-! # Observation restrictions witnessed over finite rings
Immediate output equality is not future equality. Even a linearly reachable
module can have a nonzero unobservable submodule. Nonfield coefficients are
handled without rank or division arguments.
-/
namespace KomorebiPadic
namespace LinearObservability
noncomputable section

/-- Reachable scalar module over Z/4 whose output sees only parity. -/
def twiceIdentity : System (ZMod 4) (ZMod 4) Unit where
  dynamics := ⟨1, fun _ => LinearMap.id⟩
  output :=
    { toFun := fun x => 2*x
      map_add' := by intro x y; ring
      map_smul' := by intro a x; simp only [smul_eq_mul, RingHom.id_apply]; ring }

theorem twiceIdentity_observation (ds : List Unit) (x : ZMod 4) :
    observation twiceIdentity ds x = 2*x := by
  induction ds with
  | nil => rfl
  | cons d ds ih => exact ih

theorem twiceIdentity_unobservable_mem (x : ZMod 4) :
    x ∈ unobservable twiceIdentity ↔ 2*x = 0 := by
  rw [mem_unobservable]
  constructor
  · intro h; exact h []
  · intro h ds; rw [twiceIdentity_observation, h]

theorem twiceIdentity_kernel_card : Nat.card (unobservable twiceIdentity) = 2 := by
  have he : unobservable twiceIdentity = LinearMap.ker twiceIdentity.output := by
    ext x
    exact twiceIdentity_unobservable_mem x
  rw [he]
  change Nat.card {x : ZMod 4 // 2*x = 0} = 2
  rw [Nat.card_eq_fintype_card]
  decide +kernel

theorem twiceIdentity_quotient_card : Nat.card (State twiceIdentity) = 2 := by
  have he := quotient_card_mul twiceIdentity
  rw [twiceIdentity_kernel_card] at he
  have hc : Nat.card (ZMod 4) = 4 := by simp
  rw [hc] at he
  omega

theorem twiceIdentity_reachable : LinearReachability.reachable twiceIdentity.dynamics = ⊤ := by
  apply top_unique
  intro x _
  have h := LinearReachability.initial_mem_reachable twiceIdentity.dynamics
  have hx := (LinearReachability.reachable twiceIdentity.dynamics).smul_mem x h
  simpa [twiceIdentity, smul_eq_mul] using hx

theorem twiceIdentity_distinct_states_merge :
    (0 : ZMod 4) ≠ 2 ∧ projection twiceIdentity 0 = projection twiceIdentity 2 ∧
      projection twiceIdentity 0 ≠ projection twiceIdentity 1 := by
  refine ⟨by decide, (projection_eq_iff _ _ _).mpr ?_, ?_⟩
  · intro ds
    simp only [twiceIdentity_observation]
    decide +kernel
  · intro h
    have hn := (projection_eq_iff _ _ _).mp h []
    change (2 : ZMod 4)*0 = 2*1 at hn
    norm_num at hn
    exact (by decide : (0 : ZMod 4) ≠ 2) hn

/-- Two outputs are necessary to observe both coordinates of a swap system. -/
def swapObserver : System (ZMod 5) (Fin 2 → ZMod 5) Unit where
  dynamics :=
    { initial := ![1,0]
      transition _ :=
        { toFun := fun x i => if i = 0 then x 1 else x 0
          map_add' := by intro x y; funext i; simp only [Pi.add_apply]; split_ifs <;> rfl
          map_smul' := by intro a x; funext i; simp only [Pi.smul_apply, RingHom.id_apply]; split_ifs <;> rfl } }
  output :=
    { toFun := fun x => x 0
      map_add' := by intro x y; rfl
      map_smul' := by intro a x; rfl }

theorem swapObserver_unobservable_bot : unobservable swapObserver = ⊥ := by
  apply le_antisymm _ bot_le
  intro x hx
  have h0 := (mem_unobservable _ _).mp hx []
  have h1 := (mem_unobservable _ _).mp hx [()]
  change x 0 = 0 at h0
  change x 1 = 0 at h1
  change x = 0
  funext i
  fin_cases i <;> assumption

theorem immediate_output_not_future_equivalence :
    swapObserver.output ![0,1] = swapObserver.output 0 ∧
      projection swapObserver ![0,1] ≠ projection swapObserver 0 := by
  constructor
  · rfl
  · intro h
    have he := (projection_eq_iff _ _ _).mp h [()]
    change (1 : ZMod 5) = 0 at he
    exact (by decide : (1 : ZMod 5) ≠ 0) he

/-- Empty word matters: no digits does not mean there is no output observation. -/
def emptyAlphabet : System (ZMod 5) (ZMod 5) (Fin 0) where
  dynamics := ⟨1, fun d => Fin.elim0 d⟩
  output := LinearMap.id

theorem emptyAlphabet_unobservable_bot : unobservable emptyAlphabet = ⊥ := by
  apply le_antisymm _ bot_le
  intro x hx
  exact (mem_unobservable _ _).mp hx []

/-- Zero output collapses the entire state module, regardless of transition dynamics. -/
theorem unobservable_top_of_zero_output {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]
    (M : System R V A) (ho : M.output = 0) : unobservable M = ⊤ := by
  apply top_unique
  intro x _
  apply (mem_unobservable M x).mpr
  intro ds
  simp [observation, ho]

end
end LinearObservability
end KomorebiPadic
