import KomorebiPadic.MinimalMaskRealization
import KomorebiPadic.FiniteBehaviorComparison
import KomorebiPadic.ObservabilityExamples

/-! # Cross-realization and scope witnesses
Minimum linear cardinality differs from minimum orbit/DFA size. Isomorphic
modules with different outputs need not have the same word behavior.
-/
namespace KomorebiPadic
namespace ResidualRealization
noncomputable section

def constantOne : LinearObservability.System (ZMod 5) (ZMod 5) Unit where
  dynamics := ⟨1, fun _ => LinearMap.id⟩
  output := LinearMap.id

theorem constantOne_run (u : List Unit) (x : ZMod 5) :
    LinearReachability.run constantOne.dynamics u x = x := by
  induction u with
  | nil => rfl
  | cons _ _ ih => exact ih

theorem constantOne_observation (u : List Unit) (x : ZMod 5) :
    LinearObservability.observation constantOne u x = x := by
  change LinearObservability.wordMap constantOne u x = x
  rw [LinearObservability.wordMap_apply, constantOne_run]

theorem constantOne_reachable : IsReachable constantOne := by
  apply top_unique
  intro x _
  have hi := LinearReachability.initial_mem_reachable constantOne.dynamics
  simpa [constantOne, smul_eq_mul] using
    (LinearReachability.reachable constantOne.dynamics).smul_mem x hi

theorem constantOne_observable : IsObservable constantOne := by
  intro x y h
  exact h []

/-- The initial deterministic orbit is a singleton, despite minimum linear cardinality five. -/
theorem constantOne_orbit_singleton :
    Set.range (fun u : List Unit => LinearReachability.run constantOne.dynamics u constantOne.dynamics.initial) =
      {1} := by
  ext x
  constructor
  · rintro ⟨u,rfl⟩
    exact constantOne_run u constantOne.dynamics.initial
  · rintro rfl
    exact ⟨[],rfl⟩

theorem constantOne_global_minimum {V : Type*} [AddCommGroup V] [Module (ZMod 5) V] [Finite V]
    (N : LinearObservability.System (ZMod 5) V Unit)
    (hf : ∀ u, LinearObservability.observation N u N.dynamics.initial = 1) :
    5 ≤ Nat.card V := by
  have he : behavior N = behavior constantOne := by
    funext u
    exact (hf u).trans (constantOne_observation u 1).symm
  have h := minimal_cardinality constantOne N constantOne_reachable constantOne_observable he
  simpa using h

def scaledConstant : LinearObservability.System (ZMod 5) (ZMod 5) Unit where
  dynamics := ⟨2, fun _ => LinearMap.id⟩
  output := (3 : ZMod 5) • LinearMap.id

def doubleMap : ZMod 5 →ₗ[ZMod 5] ZMod 5 := (2 : ZMod 5) • LinearMap.id

theorem doubleMap_simulation : Simulation constantOne scaledConstant doubleMap := by
  refine ⟨?_, ?_, ?_⟩
  · norm_num [doubleMap, constantOne, scaledConstant]
  · intro d x
    rfl
  · intro x
    change (3 : ZMod 5) * (2*x) = x
    rw [← mul_assoc, show (3 : ZMod 5)*2=1 by decide, one_mul]

theorem scaledConstant_same_behavior : behavior scaledConstant = behavior constantOne :=
  simulation_behavior constantOne scaledConstant doubleMap doubleMap_simulation

theorem scaledConstant_observable : IsObservable scaledConstant := by
  intro x y h
  have he := h []
  change (3 : ZMod 5)*x = 3*y at he
  have hh := congrArg (fun z : ZMod 5 => 2*z) he
  simpa only [← mul_assoc, show (2 : ZMod 5)*3 = 1 by decide, one_mul] using hh

/-- The intertwiner is forced by behavior; it is not literal equality of coordinate values. -/
theorem scaledConstant_unique_map (g : ZMod 5 →ₗ[ZMod 5] ZMod 5)
    (hg : Simulation constantOne scaledConstant g) : g = doubleMap :=
  simulation_unique_to_observable constantOne scaledConstant scaledConstant_observable
    g doubleMap hg doubleMap_simulation

def zeroOutputSameModule : LinearObservability.System (ZMod 5) (ZMod 5) Unit where
  dynamics := constantOne.dynamics
  output := 0

theorem same_module_different_behavior : behavior zeroOutputSameModule ≠ behavior constantOne := by
  intro he
  have hh := congrFun he []
  change (0 : ZMod 5) = 1 at hh
  exact (by decide : (0 : ZMod 5) ≠ 1) hh

/-- A nonfree behavior module has the same cross-realization guarantee. -/
theorem twiceIdentity_global_minimum {V : Type*} [AddCommGroup V] [Module (ZMod 4) V] [Finite V]
    (N : LinearObservability.System (ZMod 4) V Unit)
    (hf : ∀ u, LinearObservability.observation N u N.dynamics.initial = 2) :
    2 ≤ Nat.card V := by
  let M := LinearObservability.quotientSystem LinearObservability.twiceIdentity
  have hR : IsReachable M := LinearObservability.quotient_reachable _ LinearObservability.twiceIdentity_reachable
  have hO : IsObservable M := LinearObservability.quotient_observable _
  have he : behavior N = behavior M := by
    funext u
    change _ = LinearObservability.observation M u
      (LinearObservability.projection LinearObservability.twiceIdentity 1)
    rw [LinearObservability.observation_projection, LinearObservability.twiceIdentity_observation]
    simpa only [behavior, mul_one] using hf u
  have h := minimal_cardinality M N hR hO he
  rw [LinearObservability.twiceIdentity_quotient_card] at h
  exact h

/-- Ordinary integer digit words and all words must not be confused. -/
def trailingZero : LinearObservability.System (ZMod 2) (Fin 2 → ZMod 2) (Fin 2) where
  dynamics :=
    { initial := ![1,0]
      transition d :=
        { toFun := fun x i => if d = 0 then (if i = 0 then 0 else x 0 + x 1)
            else (if i = 0 then x 0 + x 1 else 0)
          map_add' := by
            intro x y
            funext i
            simp only [Pi.add_apply]
            split_ifs <;> ring
          map_smul' := by
            intro a x
            funext i
            simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
            split_ifs <;> ring } }
  output :=
    { toFun := fun x => x 1
      map_add' _ _ := rfl
      map_smul' _ _ := rfl }

theorem trailingZero_empty : behavior trailingZero [] = 0 := rfl

theorem trailingZero_ends_one (u : List (Fin 2)) : behavior trailingZero (u ++ [1]) = 0 := by
  unfold behavior
  rw [observation_append]
  rfl

theorem trailingZero_single_zero : behavior trailingZero [0] = 1 := by
  change (1 : ZMod 2)+0 = 1
  simp

theorem trailingZero_not_zero_behavior : behavior trailingZero ≠ 0 := by
  intro he
  have h := congrFun he [0]
  rw [trailingZero_single_zero] at h
  exact (by decide : (1 : ZMod 2) ≠ 0) h

end
end ResidualRealization
end KomorebiPadic
