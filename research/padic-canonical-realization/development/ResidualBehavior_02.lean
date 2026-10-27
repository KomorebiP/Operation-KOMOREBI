import KomorebiPadic.ObservableQuotient

/-! # Intrinsic prefix residuals of an all-word behavior
A prefix is consumed first: f_u(w) = f(u ++ w). Residual span uses arbitrary
R-linear combinations, not only the set of residual functions themselves.
-/
namespace KomorebiPadic
namespace ResidualRealization
variable {R A V : Type*} [CommRing R] [AddCommGroup V] [Module R V]
noncomputable section

abbrev Behavior (R A : Type*) := List A → R

def residual (f : Behavior R A) (u : List A) : Behavior R A := fun w => f (u ++ w)

omit [CommRing R] in
@[simp] theorem residual_nil (f : Behavior R A) : residual f [] = f := rfl
omit [CommRing R] in
@[simp] theorem residual_append (f : Behavior R A) (u v : List A) :
    residual (residual f u) v = residual f (u ++ v) := by
  funext w
  simp [residual, List.append_assoc]

def derivative (d : A) : Behavior R A →ₗ[R] Behavior R A where
  toFun f := fun w => f (d :: w)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

@[simp] theorem derivative_residual (f : Behavior R A) (u : List A) (d : A) :
    derivative d (residual f u) = residual f (u ++ [d]) := by
  funext w
  simp [derivative, residual, List.append_assoc]

def residualModule (f : Behavior R A) : Submodule R (Behavior R A) :=
  Submodule.span R (Set.range (residual f))

abbrev ResidualState (f : Behavior R A) := residualModule f

theorem residual_mem (f : Behavior R A) (u : List A) : residual f u ∈ residualModule f :=
  Submodule.subset_span ⟨u, rfl⟩

theorem derivative_mem (f : Behavior R A) (d : A) (x : Behavior R A)
    (hx : x ∈ residualModule f) : derivative d x ∈ residualModule f := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
    obtain ⟨u,rfl⟩ := hx
    rw [derivative_residual]
    exact residual_mem f _
  | zero => simpa only [map_zero] using (residualModule f).zero_mem
  | add x y _ _ hx hy => simpa only [map_add] using (residualModule f).add_mem hx hy
  | smul a x _ hx => simpa only [map_smul] using (residualModule f).smul_mem a hx

def residualInitial (f : Behavior R A) : ResidualState f := ⟨f, residual_mem f []⟩

def residualTransition (f : Behavior R A) (d : A) : ResidualState f →ₗ[R] ResidualState f where
  toFun x := ⟨derivative d x.val, derivative_mem f d x.val x.property⟩
  map_add' x y := by apply Subtype.ext; rfl
  map_smul' a x := by apply Subtype.ext; rfl

def residualOutput (f : Behavior R A) : ResidualState f →ₗ[R] R where
  toFun x := x.val []
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

def residualSystem (f : Behavior R A) : LinearObservability.System R (ResidualState f) A where
  dynamics := ⟨residualInitial f, residualTransition f⟩
  output := residualOutput f

theorem residual_run (f : Behavior R A) (u : List A) (x : ResidualState f) :
    (LinearReachability.run (residualSystem f).dynamics u x).val = residual x.val u := by
  induction u generalizing x with
  | nil => rfl
  | cons d ds ih =>
    rw [LinearReachability.run, ih]
    rfl

@[simp] theorem residual_observation (f : Behavior R A) (u : List A) (x : ResidualState f) :
    LinearObservability.observation (residualSystem f) u x = x.val u := by
  simp only [LinearObservability.observation, LinearMap.comp_apply, LinearObservability.wordMap_apply]
  change (LinearReachability.run (residualSystem f).dynamics u x).val [] = _
  rw [residual_run]
  simp [residual]

theorem residual_observable (f : Behavior R A) (x y : ResidualState f)
    (h : ∀ u, LinearObservability.observation (residualSystem f) u x =
      LinearObservability.observation (residualSystem f) u y) : x = y := by
  apply Subtype.ext
  funext u
  simpa only [residual_observation] using h u

theorem residual_reachable (f : Behavior R A) :
    LinearReachability.reachable (residualSystem f).dynamics = ⊤ := by
  let U := LinearReachability.reachable (residualSystem f).dynamics
  have hg : residualModule f ≤ U.map (residualModule f).subtype := by
    apply Submodule.span_le.mpr
    rintro x ⟨u,rfl⟩
    apply Submodule.mem_map.mpr
    refine ⟨LinearReachability.run (residualSystem f).dynamics u (residualInitial f),
      LinearReachability.orbit_mem_reachable _ u, ?_⟩
    exact residual_run f u (residualInitial f)
  apply top_unique
  intro x _
  obtain ⟨y,hy,he⟩ := Submodule.mem_map.mp (hg x.property)
  have hxy : y = x := Subtype.ext he
  exact hxy ▸ hy

/-- Read the behavior of the distinguished seed on every word, not only numeral encodings. -/
def behavior (M : LinearObservability.System R V A) : Behavior R A :=
  fun u => LinearObservability.observation M u M.dynamics.initial

/-- Future-output functions form a linear observation map. -/
def behaviorMap (M : LinearObservability.System R V A) : V →ₗ[R] Behavior R A where
  toFun x := fun u => LinearObservability.observation M u x
  map_add' x y := by funext u; exact (LinearObservability.observation M u).map_add x y
  map_smul' a x := by funext u; exact (LinearObservability.observation M u).map_smul a x

theorem observation_append (M : LinearObservability.System R V A) (u w : List A) (x : V) :
    LinearObservability.observation M (u ++ w) x =
      LinearObservability.observation M w (LinearReachability.run M.dynamics u x) := by
  simp only [LinearObservability.observation, LinearMap.comp_apply,
    LinearObservability.wordMap_apply, LinearReachability.run_append]

theorem behaviorMap_run (M : LinearObservability.System R V A) (u : List A) (x : V) :
    behaviorMap M (LinearReachability.run M.dynamics u x) = residual (behaviorMap M x) u := by
  funext w
  exact (observation_append M u w x).symm

theorem behaviorMap_ker (M : LinearObservability.System R V A) :
    LinearMap.ker (behaviorMap M) = LinearObservability.unobservable M := by
  ext x
  simp [behaviorMap, LinearObservability.mem_unobservable, funext_iff]

/-- The image of the reachable span depends only on the word behavior. -/
theorem behaviorMap_reachable (M : LinearObservability.System R V A) :
    (LinearReachability.reachable M.dynamics).map (behaviorMap M) = residualModule (behavior M) := by
  unfold LinearReachability.reachable residualModule
  rw [Submodule.map_span]
  congr 1
  ext x
  constructor
  · rintro ⟨y, ⟨u, rfl⟩, rfl⟩
    exact ⟨u, (behaviorMap_run M u M.dynamics.initial).symm⟩
  · rintro ⟨u, rfl⟩
    exact ⟨LinearReachability.run M.dynamics u M.dynamics.initial,
      ⟨u,rfl⟩, behaviorMap_run M u M.dynamics.initial⟩

theorem behaviorMap_range (M : LinearObservability.System R V A)
    (hR : LinearReachability.reachable M.dynamics = ⊤) :
    LinearMap.range (behaviorMap M) = residualModule (behavior M) := by
  have h := behaviorMap_reachable M
  simpa only [hR, Submodule.map_top] using h

/-- The intrinsic residual machine realizes its defining all-word function. -/
@[simp] theorem residualSystem_behavior (f : Behavior R A) : behavior (residualSystem f) = f := by
  funext u
  exact residual_observation f u (residualInitial f)

end
end ResidualRealization
end KomorebiPadic
