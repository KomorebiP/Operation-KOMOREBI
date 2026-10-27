import KomorebiPadic.ResidualBehavior

/-! # Cross-realization comparison through intrinsic residual behavior
All comparisons use the same ring, alphabet, and ALL-WORD function. Minimality
is module cardinality among finite linear realizations, not generator rank or
minimal DFA size. Source reachability means the linear span of the digit orbit.
-/
namespace KomorebiPadic
namespace ResidualRealization
variable {R A V W : Type*} [CommRing R]
variable [AddCommGroup V] [Module R V] [AddCommGroup W] [Module R W]
noncomputable section

abbrev IsReachable (M : LinearObservability.System R V A) : Prop :=
  LinearReachability.reachable M.dynamics = ⊤

def IsObservable (M : LinearObservability.System R V A) : Prop :=
  ∀ x y, (∀ u : List A, LinearObservability.observation M u x =
    LinearObservability.observation M u y) → x = y

/-- The canonical map is defined only after proving that its image is the residual span. -/
def toResidual (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) : V →ₗ[R] ResidualState f where
  toFun x := ⟨behaviorMap M x, by
    change behaviorMap M x ∈ residualModule f
    rw [← hf, ← behaviorMap_range M hR]
    exact ⟨x,rfl⟩⟩
  map_add' x y := Subtype.ext ((behaviorMap M).map_add x y)
  map_smul' a x := Subtype.ext ((behaviorMap M).map_smul a x)

@[simp] theorem toResidual_val (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) (x : V) :
    (toResidual M f hR hf x).val = behaviorMap M x := rfl

theorem toResidual_surjective (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) : Function.Surjective (toResidual M f hR hf) := by
  intro y
  have hy : y.val ∈ LinearMap.range (behaviorMap M) := by
    rw [behaviorMap_range M hR, hf]
    exact y.property
  obtain ⟨x,hx⟩ := hy
  exact ⟨x,Subtype.ext hx⟩

theorem toResidual_injective (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hO : IsObservable M) (hf : behavior M = f) :
    Function.Injective (toResidual M f hR hf) := by
  intro x y h
  apply hO x y
  intro u
  exact congrArg (fun z : ResidualState f => z.val u) h

theorem toResidual_initial (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) :
    toResidual M f hR hf M.dynamics.initial = residualInitial f := Subtype.ext hf

theorem toResidual_transition (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) (d : A) (x : V) :
    toResidual M f hR hf (M.dynamics.transition d x) =
      residualTransition f d (toResidual M f hR hf x) := by
  apply Subtype.ext
  funext u
  rfl

@[simp] theorem toResidual_output (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hf : behavior M = f) (x : V) :
    residualOutput f (toResidual M f hR hf x) = M.output x := rfl

/-- Reachability gives surjectivity; observability gives injectivity. -/
def equivResidual (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hO : IsObservable M) (hf : behavior M = f) :
    V ≃ₗ[R] ResidualState f :=
  LinearEquiv.ofBijective (toResidual M f hR hf)
    ⟨toResidual_injective M f hR hO hf, toResidual_surjective M f hR hf⟩

@[simp] theorem equivResidual_apply (M : LinearObservability.System R V A) (f : Behavior R A)
    (hR : IsReachable M) (hO : IsObservable M) (hf : behavior M = f) (x : V) :
    equivResidual M f hR hO hf x = toResidual M f hR hf x := rfl

/-- A morphism preserves the seed, all digit actions, and the output on every state. -/
def Simulation (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (g : V →ₗ[R] W) : Prop :=
  g M.dynamics.initial = N.dynamics.initial ∧
  (∀ d x, g (M.dynamics.transition d x) = N.dynamics.transition d (g x)) ∧
  (∀ x, N.output (g x) = M.output x)

theorem simulation_observation (M : LinearObservability.System R V A)
    (N : LinearObservability.System R W A) (g : V →ₗ[R] W) (hg : Simulation M N g)
    (u : List A) (x : V) :
    LinearObservability.observation N u (g x) = LinearObservability.observation M u x := by
  induction u generalizing x with
  | nil => exact hg.2.2 x
  | cons d ds ih =>
    rw [LinearObservability.observation_cons, ← hg.2.1 d x]
    exact ih (M.dynamics.transition d x)

theorem simulation_behavior (M : LinearObservability.System R V A)
    (N : LinearObservability.System R W A) (g : V →ₗ[R] W) (hg : Simulation M N g) :
    behavior N = behavior M := by
  funext u
  rw [behavior, ← hg.1]
  exact simulation_observation M N g hg u M.dynamics.initial

theorem simulation_unique_to_observable (M : LinearObservability.System R V A)
    (N : LinearObservability.System R W A) (hO : IsObservable N)
    (g h : V →ₗ[R] W) (hg : Simulation M N g) (hh : Simulation M N h) : g = h := by
  apply LinearMap.ext
  intro x
  apply hO
  intro u
  rw [simulation_observation M N g hg, simulation_observation M N h hh]

/-- Canonical comparison from any reachable realization onto a reachable-observable one. -/
def comparison (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) : V →ₗ[R] W :=
  (equivResidual N f hN hO hfN).symm.toLinearMap.comp (toResidual M f hM hfM)

theorem comparison_residual (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) (x : V) :
    toResidual N f hN hfN (comparison M N f hM hN hO hfM hfN x) = toResidual M f hM hfM x := by
  exact (equivResidual N f hN hO hfN).apply_symm_apply _

theorem comparison_surjective (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) :
    Function.Surjective (comparison M N f hM hN hO hfM hfN) :=
  (equivResidual N f hN hO hfN).symm.surjective.comp (toResidual_surjective M f hM hfM)

theorem comparison_simulation (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) :
    Simulation M N (comparison M N f hM hN hO hfM hfN) := by
  refine ⟨?_, ?_, ?_⟩
  · apply toResidual_injective N f hN hO hfN
    rw [comparison_residual, toResidual_initial, toResidual_initial]
  · intro d x
    apply toResidual_injective N f hN hO hfN
    rw [comparison_residual, toResidual_transition, toResidual_transition, comparison_residual]
  · intro x
    exact congrArg (fun y : ResidualState f => y.val [])
      (comparison_residual M N f hM hN hO hfM hfN x)

theorem existsUnique_comparison (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) :
    ∃! g : V →ₗ[R] W, Simulation M N g := by
  refine ⟨comparison M N f hM hN hO hfM hfN,
    comparison_simulation M N f hM hN hO hfM hfN, ?_⟩
  intro g hg
  exact simulation_unique_to_observable M N hO g _ hg
    (comparison_simulation M N f hM hN hO hfM hfN)

/-- A reachable-observable realization is unique up to a unique intertwining linear isomorphism. -/
def canonicalEquiv (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hoM : IsObservable M)
    (hN : IsReachable N) (hoN : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) : V ≃ₗ[R] W :=
  (equivResidual M f hM hoM hfM).trans (equivResidual N f hN hoN hfN).symm

theorem canonicalEquiv_simulation (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hoM : IsObservable M)
    (hN : IsReachable N) (hoN : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) :
    Simulation M N (canonicalEquiv M N f hM hoM hN hoN hfM hfN).toLinearMap := by
  exact comparison_simulation M N f hM hN hoN hfM hfN

theorem canonicalEquiv_unique (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (f : Behavior R A) (hM : IsReachable M) (hoM : IsObservable M)
    (hN : IsReachable N) (hoN : IsObservable N)
    (hfM : behavior M = f) (hfN : behavior N = f) (e : V ≃ₗ[R] W)
    (he : Simulation M N e.toLinearMap) :
    e = canonicalEquiv M N f hM hoM hN hoN hfM hfN := by
  have h := simulation_unique_to_observable M N hoN e.toLinearMap _ he
    (canonicalEquiv_simulation M N f hM hoM hN hoN hfM hfN)
  ext x
  exact congrArg (fun g : V →ₗ[R] W => g x) h

/-- The observation quotient of any reachable realization has the intrinsic residual coordinates. -/
def quotientEquivResidual (M : LinearObservability.System R V A) (hM : IsReachable M) :
    LinearObservability.State M ≃ₗ[R] ResidualState (behavior M) :=
  equivResidual (LinearObservability.quotientSystem M) (behavior M)
    (LinearObservability.quotient_reachable M hM) (LinearObservability.quotient_observable M)
    (by funext u; exact LinearObservability.observation_projection M u M.dynamics.initial)

/-- Restrict an arbitrary source to its reachable span without changing its behavior. -/
def reachableSystem (M : LinearObservability.System R V A) :
    LinearObservability.System R (LinearReachability.State M.dynamics) A where
  dynamics := ⟨LinearReachability.initial M.dynamics, LinearReachability.transition M.dynamics⟩
  output := M.output.comp (LinearReachability.reachable M.dynamics).subtype

theorem reachableSystem_run (M : LinearObservability.System R V A) (u : List A)
    (x : LinearReachability.State M.dynamics) :
    (LinearReachability.run (reachableSystem M).dynamics u x).val =
      LinearReachability.run M.dynamics u x.val := by
  induction u generalizing x with
  | nil => rfl
  | cons d ds ih => exact ih (LinearReachability.transition M.dynamics d x)

theorem reachableSystem_behavior (M : LinearObservability.System R V A) :
    behavior (reachableSystem M) = behavior M := by
  funext u
  simp only [behavior, LinearObservability.observation, LinearMap.comp_apply,
    LinearObservability.wordMap_apply]
  exact congrArg M.output (reachableSystem_run M u (LinearReachability.initial M.dynamics))

theorem reachableSystem_reachable (M : LinearObservability.System R V A) :
    IsReachable (reachableSystem M) := LinearObservability.restricted_reachable M.dynamics

/-- Even a nonreachable competitor surjects from its reachable part onto the intrinsic realization. -/
theorem exists_surjective_comparison_from_reachable
    (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (hM : IsReachable M) (hO : IsObservable M) (hf : behavior N = behavior M) :
    ∃ g : LinearReachability.State N.dynamics →ₗ[R] V,
      Simulation (reachableSystem N) M g ∧ Function.Surjective g := by
  let hfN : behavior (reachableSystem N) = behavior M := (reachableSystem_behavior N).trans hf
  exact ⟨comparison (reachableSystem N) M (behavior M) (reachableSystem_reachable N) hM hO hfN rfl,
    comparison_simulation (reachableSystem N) M (behavior M) (reachableSystem_reachable N) hM hO hfN rfl,
    comparison_surjective (reachableSystem N) M (behavior M) (reachableSystem_reachable N) hM hO hfN rfl⟩

/-- Global cardinality minimality among ALL finite R-linear realizations of the same word behavior. -/
theorem minimal_cardinality [Finite W]
    (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (hM : IsReachable M) (hO : IsObservable M) (hf : behavior N = behavior M) :
    Nat.card V ≤ Nat.card W := by
  obtain ⟨g,_,hg⟩ := exists_surjective_comparison_from_reachable M N hM hO hf
  exact (Nat.card_le_card_of_surjective g hg).trans (LinearReachability.state_card_le N.dynamics)

end
end ResidualRealization
end KomorebiPadic
