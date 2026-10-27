# Source excerpts for expanded exposition KS59–KS70

These are verbatim source excerpts from the unchanged canonical tree. Extraction is not a compiler run or a proof of English-to-Lean equivalence.

## KS59 — Obstructions under stronger prescription

Additive view systems and nested prescribed domains. The forgetful quotient maps are surjective, not generally injective. Both quotient naturality and persistence refer to the actual extension class.

### KomorebiSpace.AdditiveViewSystem.boundaries_antitone

Source: `formal/KomorebiSpace/ObstructionRestriction.lean`, line 21. SHA-256 `3a99be42c1d3bbbe834e209251754ccc68c398b834c703cc7a179be96871d2a0`.

```lean
theorem boundaries_antitone {U W : Set V} (h : U ⊆ W) :
    (F.problem W).boundaries ≤ (F.problem U).boundaries := by
  rintro r ⟨x,hx,hr⟩
  refine ⟨x,?_,hr⟩
  change F.observation U x = 0
  funext a
  exact congrFun hx (⟨a.val,h a.property⟩ : W)

/-- The canonical quotient homomorphism forgetting some protected views. -/
```

### KomorebiSpace.AdditiveViewSystem.forgetObstruction_surjective

Source: `formal/KomorebiSpace/ObstructionRestriction.lean`, line 54. SHA-256 `3a99be42c1d3bbbe834e209251754ccc68c398b834c703cc7a179be96871d2a0`.

```lean
theorem forgetObstruction_surjective {U W : Set V} (h : U ⊆ W) :
    Function.Surjective (F.forgetObstruction h) := by
  intro x
  induction x using QuotientAddGroup.induction_on with
  | H r => exact ⟨(r : (F.problem W).Obstruction),rfl⟩

/-- Restriction of a partial realization transports its actual extension class. -/
```

### KomorebiSpace.AdditiveViewSystem.forgetObstruction_comp

Source: `formal/KomorebiSpace/ObstructionRestriction.lean`, line 46. SHA-256 `3a99be42c1d3bbbe834e209251754ccc68c398b834c703cc7a179be96871d2a0`.

```lean
theorem forgetObstruction_comp {U W Z : Set V} (h : U ⊆ W) (k : W ⊆ Z)
    (x : (F.problem Z).Obstruction) :
    F.forgetObstruction h (F.forgetObstruction k x) =
      F.forgetObstruction (h.trans k) x := by
  induction x using QuotientAddGroup.induction_on with
  | H x => rfl

/-- The map is onto as a map of obstruction groups. It need not be injective. -/
```

### KomorebiSpace.AdditiveViewSystem.extensionClass_restrict

Source: `formal/KomorebiSpace/ObstructionRestriction.lean`, line 61. SHA-256 `3a99be42c1d3bbbe834e209251754ccc68c398b834c703cc7a179be96871d2a0`.

```lean
theorem extensionClass_restrict {U W : Set V} (h : U ⊆ W)
    (s : F.views.Partial W) :
    F.forgetObstruction h (F.extensionClass W s) =
      F.extensionClass U (F.views.restrictPartial h s) := by
  change (F.problem U).obstruction (F.rawExtension W s) = _
  apply F.extensionClass_independent
  intro a
  exact F.rawExtension_observed W s ⟨a.val,h a.property⟩

/-- A genuinely obstructed restriction cannot be cured while preserving more data. -/
```

### KomorebiSpace.AdditiveViewSystem.obstruction_persists_under_prescription

Source: `formal/KomorebiSpace/ObstructionRestriction.lean`, line 71. SHA-256 `3a99be42c1d3bbbe834e209251754ccc68c398b834c703cc7a179be96871d2a0`.

```lean
theorem obstruction_persists_under_prescription {U W : Set V} (h : U ⊆ W)
    (s : F.views.Partial W)
    (ho : F.extensionClass U (F.views.restrictPartial h s) ≠ 0) :
    F.extensionClass W s ≠ 0 := by
  intro hz
  apply ho
  rw [← F.extensionClass_restrict h s,hz,map_zero]

/-- Compatible extension to W implies compatible extension to every smaller U. -/
```

## KS60 — Prescribed choices and obstructed intermediate steps

The concrete three-view integer model retains its original restriction maps. The initial extension fiber is parametrized by integers, while a prescribed middle value extends precisely when even.

### KomorebiSpace.ExtensionChoiceExample.initialExtensionsEquiv

Source: `formal/KomorebiSpace/ExtensionChoiceExample.lean`, line 166. SHA-256 `02e8b9542fe55cbce45c2fb821140c652a88b573a7b1432817d92cc22aa976dd`.

```lean
def initialExtensionsEquiv (k : ℤ) :
    ℤ ≃ threeViews.views.Extensions initialDomain (initialSeed k) where
  toFun n := ⟨globalSection k n,global_restrict_initial k n⟩
  invFun x := (x.val.val 2).2
  left_inv _ := rfl
  right_inv x := Subtype.ext (initial_extension_formula k x).symm

```

### KomorebiSpace.ExtensionChoiceExample.middle_obstruction_iff_even

Source: `formal/KomorebiSpace/ExtensionChoiceExample.lean`, line 110. SHA-256 `02e8b9542fe55cbce45c2fb821140c652a88b573a7b1432817d92cc22aa976dd`.

```lean
theorem middle_obstruction_iff_even (k m : ℤ) :
    threeViews.extensionClass middleDomain (middleSeed k m) = 0 ↔
      ∃ n : ℤ, m = 2*n := by
  rw [threeViews.extensionClass_zero_iff]
  constructor
  · rintro ⟨⟨x,hx⟩⟩
    have hv : x.val 1 = (k,m) :=
      congrArg (fun t : threeViews.views.Partial middleDomain => t.val ⟨1,Or.inr rfl⟩) hx
    have hc := x.property 1 2 (homOfLE (by decide))
    change doubleTail (show Pair from x.val 2) = x.val 1 at hc
    have hh := congrArg Prod.snd (hc.trans hv)
    exact ⟨(x.val 2).2,hh.symm⟩
  · rintro ⟨n,rfl⟩
    exact ⟨⟨globalSection k n,global_restrict_middle k n⟩⟩

```

### KomorebiSpace.ExtensionChoiceExample.nonzero_seed_dead_end

Source: `formal/KomorebiSpace/ExtensionChoiceExample.lean`, line 184. SHA-256 `02e8b9542fe55cbce45c2fb821140c652a88b573a7b1432817d92cc22aa976dd`.

```lean
theorem nonzero_seed_dead_end :
    Nonempty (threeViews.views.Extensions initialDomain (initialSeed 7)) ∧
    threeViews.views.restrictPartial initial_subset_middle (middleSeed 7 1) = initialSeed 7 ∧
    ¬ Nonempty (threeViews.views.Extensions middleDomain (middleSeed 7 1)) := by
  refine ⟨initial_extends 7,middle_restrict_initial 7 1,?_⟩
  intro h
  exact odd_middle_obstructed 7 ((threeViews.extensionClass_zero_iff _ _).mpr h)

end ExtensionChoiceExample
end KomorebiSpace
```

## KS61 — Scheduled transports and eventual equality

Set-valued sequential resolutions, monotone schedules, and finite-stage eventual equality. The realized action respects the quotient and composition. This is not an identification with every general pro-category.

### KomorebiSpace.Resolution.ReindexedMap.comp_congr

Source: `formal/KomorebiSpace/ReindexedTransports.lean`, line 96. SHA-256 `eb3472ee08977cea95f1cb8b56b36ecd6508454bce908491718f26a07509e204`.

```lean
theorem comp_congr {f f' : ReindexedMap X Y} {g g' : ReindexedMap Y Z}
    (hf : EventuallyEq f f') (hg : EventuallyEq g g') :
    EventuallyEq (comp f g) (comp f' g') := by
  intro n
  obtain ⟨j, hgj, hgj', hj⟩ := hg n
  obtain ⟨k, hfk, hfk', hk⟩ := hf j
  refine ⟨k, (f.monotone hgj).trans hfk,
    (f'.monotone hgj').trans hfk', ?_⟩
  intro x
  change g.app n (f.app (g.level n) (X.restrict _ x)) =
    g'.app n (f'.app (g'.level n) (X.restrict _ x))
  calc
    g.app n (f.app (g.level n) (X.restrict _ x)) =
        g.app n (Y.restrict hgj (f.app j (X.restrict hfk x))) := by
      rw [f.naturality, X.restrict_trans]
    _ = g.app n (Y.restrict hgj (f'.app j (X.restrict hfk' x))) := by rw [hk x]
    _ = g'.app n (Y.restrict hgj' (f'.app j (X.restrict hfk' x))) :=
      hj (f'.app j (X.restrict hfk' x))
    _ = g'.app n (f'.app (g'.level n) (X.restrict _ x)) := by
      rw [f'.naturality, X.restrict_trans]

instance eventualSetoid (X : Resolution.{u}) (Y : Resolution.{v}) :
    Setoid (ReindexedMap X Y) where
  r := EventuallyEq
  iseqv := ⟨eventuallyEq_refl, eventuallyEq_symm, eventuallyEq_trans⟩

/-- Realization only uses coherent input coordinates at the selected stages. -/
```

### KomorebiSpace.Resolution.ReindexedMap.onLimit_congr

Source: `formal/KomorebiSpace/ReindexedTransports.lean`, line 139. SHA-256 `eb3472ee08977cea95f1cb8b56b36ecd6508454bce908491718f26a07509e204`.

```lean
theorem onLimit_congr {f g : ReindexedMap X Y} (h : EventuallyEq f g) :
    f.onLimit = g.onLimit := by
  funext x
  apply Point.ext
  intro n
  obtain ⟨k, hf, hg, hk⟩ := h n
  have hx := hk (x.val k)
  rw [x.property _ _ hf, x.property _ _ hg] at hx
  exact hx

end ReindexedMap
end Resolution
end KomorebiSpace
```

### KomorebiSpace.Resolution.ReindexedMap.onLimit_comp

Source: `formal/KomorebiSpace/ReindexedTransports.lean`, line 133. SHA-256 `eb3472ee08977cea95f1cb8b56b36ecd6508454bce908491718f26a07509e204`.

```lean
@[simp] theorem onLimit_comp (f : ReindexedMap X Y) (g : ReindexedMap Y Z)
    (x : X.Point) : (comp f g).onLimit x = g.onLimit (f.onLimit x) := rfl

```

### KomorebiSpace.Resolution.realizationFunctor

Source: `formal/KomorebiSpace/EventualCategory.lean`, line 93. SHA-256 `8e5b5dd147c996046e5c703d242d915fd0eaf268aecb94ae6a116cc93ca4dc69`.

```lean
def realizationFunctor : Resolution.{u} ⥤ Type u where
  obj := Point
  map := fun f => ↾f.onLimit
  map_id := by intro X; rfl
  map_comp := by
    intro X Y Z f g
    apply ConcreteCategory.hom_ext
    intro x
    exact EventualHom.onLimit_comp f g x

end Resolution
end KomorebiSpace
```

## KS62 — Faithfulness from observable finite stages

Faithfulness assumes surjectivity of every source projection from the limit. Surjective bonding maps give a sufficient condition. Without it equality on global points can conceal a finite-stage difference.

### KomorebiSpace.Resolution.ReindexedMap.eventuallyEq_iff_onLimit_eq

Source: `formal/KomorebiSpace/RealizationFaithfulness.lean`, line 39. SHA-256 `f8527cf96665e6652c541d5874a2a52917848db5bca3dd77205319ead3d27f3a`.

```lean
theorem eventuallyEq_iff_onLimit_eq (hX : ProjectionSurjective X)
    (f g : ReindexedMap X Y) : EventuallyEq f g ↔ f.onLimit = g.onLimit :=
  ⟨onLimit_congr, eventuallyEq_of_onLimit_eq hX f g⟩

end ReindexedMap

namespace EventualHom
variable {X : Resolution.{u}} {Y : Resolution.{v}}

```

### KomorebiSpace.Resolution.projectionSurjective_of_surjective_bonding

Source: `formal/KomorebiSpace/RealizationFaithfulness.lean`, line 110. SHA-256 `f8527cf96665e6652c541d5874a2a52917848db5bca3dd77205319ead3d27f3a`.

```lean
theorem projectionSurjective_of_surjective_bonding
    (hsurj : ∀ n, Function.Surjective (X.restrict (Nat.le_succ n))) :
    ProjectionSurjective X := by
  classical
  let lift : ∀ n, X.Obj n → X.Obj (n+1) :=
    fun n x => Classical.choose (hsurj n x)
  have hlift : ∀ n x, X.restrict (Nat.le_succ n) (lift n x) = x :=
    fun n x => Classical.choose_spec (hsurj n x)
  exact projectionSurjective_of_sections X lift hlift

end Resolution
end KomorebiSpace
```

## KS63 — Finite observation characterizes realized transport

Every source limit projection is surjective. For each target coordinate one finite source stage must work uniformly for all source points. The theorem does not assert that arbitrary functions have finite observation.

### KomorebiSpace.Resolution.realization_image_iff

Source: `formal/KomorebiSpace/FiniteObservation.lean`, line 92. SHA-256 `ad7f071a6cc0553484ba4a2df6c7caab6e1baa15ed618b98f8b30491036965ca`.

```lean
theorem realization_image_iff (hX : ProjectionSurjective X) (F : X.Point → Y.Point) :
    (∃ f : EventualHom X Y, f.onLimit = F) ↔ FinitelyObserved F := by
  constructor
  · rintro ⟨f, rfl⟩; exact eventual_finitelyObserved f
  · intro hF
    obtain ⟨f, hf⟩ := exists_presentation_of_finitelyObserved hX F hF
    exact ⟨EventualHom.mk f, hf⟩

/-- Presentation-independent coordinates on the morphism set, under an explicit hypothesis. -/
```

### KomorebiSpace.Resolution.finiteObservationEquiv

Source: `formal/KomorebiSpace/FiniteObservation.lean`, line 101. SHA-256 `ad7f071a6cc0553484ba4a2df6c7caab6e1baa15ed618b98f8b30491036965ca`.

```lean
noncomputable def finiteObservationEquiv (hX : ProjectionSurjective X) :
    EventualHom X Y ≃ {F : X.Point → Y.Point // FinitelyObserved F} :=
  Equiv.ofBijective (fun f => ⟨f.onLimit, eventual_finitelyObserved f⟩)
    ⟨by
      intro f g h
      exact EventualHom.onLimit_injective hX (congrArg Subtype.val h),
     by
      intro F
      obtain ⟨f, hf⟩ := (realization_image_iff hX F.val).mpr F.property
      exact ⟨f, Subtype.ext hf⟩⟩

```

### KomorebiSpace.Resolution.observedPresentation_onLimit

Source: `formal/KomorebiSpace/FiniteObservation.lean`, line 64. SHA-256 `ad7f071a6cc0553484ba4a2df6c7caab6e1baa15ed618b98f8b30491036965ca`.

```lean
theorem observedPresentation_onLimit (hX : ProjectionSurjective X)
    (F : X.Point → Y.Point) (k : ℕ → ℕ) (a : ∀ n, X.Obj (k n) → Y.Obj n)
    (ha : ∀ n x, (F x).val n = a n (x.val (k n))) :
    (observedPresentation hX F k a ha).onLimit = F := by
  funext x
  exact Point.ext (fun n => observedApp_on_point F k a ha n x)

```

## KS64 — Cofinal transport equivalence

Increasing cofinal schedules give explicit isomorphisms in the eventual transport category and Hom equivalences. This does not assert equality of quantitative residual norms.

### KomorebiSpace.Resolution.cofinalIso

Source: `formal/KomorebiSpace/CofinalTransports.lean`, line 80. SHA-256 `78e7fe892911c3aced04c1c9da8e819ca8674f0d9d7beb228b3d0da0bab4c7b1`.

```lean
noncomputable def cofinalIso (X : Resolution.{u}) (φ : ℕ → ℕ)
    (hφ : Monotone φ) (hcof : UnboundedSchedule φ) :
    X ≅ X.reindex φ hφ where
  hom := EventualHom.mk (sampleTransport X φ hφ)
  inv := EventualHom.mk (recoverTransport X φ hφ hcof)
  hom_inv_id := Quotient.sound (sample_recover_eventually X φ hφ hcof)
  inv_hom_id := Quotient.sound (recover_sample_eventually X φ hφ hcof)

```

### KomorebiSpace.Resolution.cofinalHomEquiv

Source: `formal/KomorebiSpace/CofinalTransports.lean`, line 112. SHA-256 `78e7fe892911c3aced04c1c9da8e819ca8674f0d9d7beb228b3d0da0bab4c7b1`.

```lean
noncomputable def cofinalHomEquiv (X Y : Resolution.{u})
    (φ ψ : ℕ → ℕ) (hφ : Monotone φ) (hψ : Monotone ψ)
    (hφcof : UnboundedSchedule φ) (hψcof : UnboundedSchedule ψ) :
    (X ⟶ Y) ≃ (X.reindex φ hφ ⟶ Y.reindex ψ hψ) where
  toFun := fun f => (cofinalIso X φ hφ hφcof).inv ≫ f ≫
    (cofinalIso Y ψ hψ hψcof).hom
  invFun := fun f => (cofinalIso X φ hφ hφcof).hom ≫ f ≫
    (cofinalIso Y ψ hψ hψcof).inv
  left_inv := by intro f; simp [Category.assoc]
  right_inv := by intro f; simp [Category.assoc]

```

### KomorebiSpace.Resolution.cofinalHomEquiv_onLimit

Source: `formal/KomorebiSpace/CofinalTransports.lean`, line 123. SHA-256 `78e7fe892911c3aced04c1c9da8e819ca8674f0d9d7beb228b3d0da0bab4c7b1`.

```lean
theorem cofinalHomEquiv_onLimit (X Y : Resolution.{u})
    (φ ψ : ℕ → ℕ) (hφ : Monotone φ) (hψ : Monotone ψ)
    (hφcof : UnboundedSchedule φ) (hψcof : UnboundedSchedule ψ)
    (f : X ⟶ Y) (x : (X.reindex φ hφ).Point) :
    (cofinalHomEquiv X Y φ ψ hφ hψ hφcof hψcof f).onLimit x =
    cofinalEquiv Y ψ hψ hψcof
      (f.onLimit ((cofinalEquiv X φ hφ hφcof).symm x)) := by
  change EventualHom.onLimit
    (EventualHom.comp (cofinalIso X φ hφ hφcof).inv
      (EventualHom.comp f (cofinalIso Y ψ hψ hψcof).hom)) x = _
  simp only [EventualHom.onLimit_comp, cofinalIso_inv_onLimit, cofinalIso_hom_onLimit]

namespace Map
variable {X Y : Resolution.{u}}

```

## KS65 — Split repair coordinates and choice dependence

Continuous linear right inverses of a fixed defect operator determine exact/residual coordinates. Projectors with this common kernel image commute exactly when equal, and equality reflects equality of the right inverses.

### KomorebiSpace.SplitDefect.Section.chart

Source: `formal/KomorebiSpace/SplitDefectCharts.lean`, line 169. SHA-256 `6fdf5a5cba4d307ab56ccbb7cac773b925a0c3a1cbb7818f7213e65300f559b8`.

```lean
def chart : E ≃L[𝕜] (Core d × R) :=
  A.chartLinear.toContinuousLinearEquivOfBounds
    (max ‖A.project‖ ‖d‖) (1 + ‖A.lift‖) A.chart_bound A.chart_inverse_bound

```

### KomorebiSpace.SplitDefect.Section.project_change

Source: `formal/KomorebiSpace/SplitDefectCharts.lean`, line 81. SHA-256 `6fdf5a5cba4d307ab56ccbb7cac773b925a0c3a1cbb7818f7213e65300f559b8`.

```lean
theorem project_change (f : E) :
    B.project f - A.project f = (A.difference B (d f) : E) := by
  simp only [project_apply, difference_apply]
  abel

```

### KomorebiSpace.SplitDefect.Section.projects_commute_iff

Source: `formal/KomorebiSpace/SplitDefectCharts.lean`, line 96. SHA-256 `6fdf5a5cba4d307ab56ccbb7cac773b925a0c3a1cbb7818f7213e65300f559b8`.

```lean
theorem projects_commute_iff :
    A.project.comp B.project = B.project.comp A.project ↔ A.project = B.project := by
  constructor
  · intro h
    ext f
    have hx := congrArg (fun T : E →L[𝕜] E => T f) h
    simpa only [ContinuousLinearMap.comp_apply, project_other] using hx.symm
  · intro h
    rw [h]

/-- Surjectivity of the differential makes the chosen section recoverable from its retraction. -/
```

### KomorebiSpace.SplitDefect.Section.projects_equal_iff_lifts_equal

Source: `formal/KomorebiSpace/SplitDefectCharts.lean`, line 107. SHA-256 `6fdf5a5cba4d307ab56ccbb7cac773b925a0c3a1cbb7818f7213e65300f559b8`.

```lean
theorem projects_equal_iff_lifts_equal : A.project = B.project ↔ A.lift = B.lift := by
  constructor
  · intro h
    ext r
    have h0 : B.project (A.lift r) = 0 := by
      rw [← h]
      exact A.project_lift r
    have hx : A.lift r - B.lift r = 0 := by
      simpa only [project_apply, A.right_inv] using h0
    exact sub_eq_zero.mp hx
  · intro h
    unfold project
    rw [h]

/-- Explicit linear coordinates: exact component and unchanged residual. -/
```

## KS66 — Triangular representation change and repair mismatch

The square of defect operators commutes exactly. The mismatch depends on chosen bounded right inverses. Its composition law uses the declared residual map in the second term. Norm convergence requires the supplied bounded maps and vanishing residuals.

### KomorebiSpace.SplitDefect.DefectMap.chart_formula

Source: `formal/KomorebiSpace/ResidualNaturality.lean`, line 123. SHA-256 `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8`.

```lean
theorem chart_formula (z : Core d × R) :
    B.chart (S.candidate (A.chart.symm z)) =
      (S.coreMap z.1 + S.coreMismatch A B z.2, S.residual z.2) := by
  apply Prod.ext
  · apply Subtype.ext
    change B.project (S.candidate (z.1.val + A.lift z.2)) =
      S.candidate z.1.val + (S.candidate (A.lift z.2) - B.lift (S.residual z.2))
    rw [map_add, map_add, B.project_fixes _ (S.preserves_exact z.1.val z.1.property),
      Section.project_apply, S.commutes, A.right_inv]
  · change D (S.candidate (z.1.val + A.lift z.2)) = S.residual z.2
    have hz : d z.1.val = 0 := z.1.property
    rw [S.commutes, map_add, hz, A.right_inv, zero_add]

/-- The mismatch satisfies an exact composition law for two presentation changes. -/
```

### KomorebiSpace.SplitDefect.DefectMap.repair_change

Source: `formal/KomorebiSpace/ResidualNaturality.lean`, line 77. SHA-256 `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8`.

```lean
theorem repair_change (f : E) :
    B.project (S.candidate f) - S.candidate (A.project f) = S.mismatch A B (d f) := by
  simp only [Section.project_apply, mismatch_apply, map_sub, S.commutes]
  abel

```

### KomorebiSpace.SplitDefect.DefectMap.repair_natural_iff

Source: `formal/KomorebiSpace/ResidualNaturality.lean`, line 105. SHA-256 `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8`.

```lean
theorem repair_natural_iff :
    (∀ f, B.project (S.candidate f) = S.candidate (A.project f)) ↔
      S.candidate.comp A.lift = B.lift.comp S.residual := by
  constructor
  · intro h
    ext r
    have hz : S.mismatch A B r = 0 := by
      have hm := S.repair_change A B (A.lift r)
      rw [A.right_inv, h, sub_self] at hm
      exact hm.symm
    exact sub_eq_zero.mp hz
  · intro h f
    apply sub_eq_zero.mp
    rw [S.repair_change]
    change (S.candidate.comp A.lift) (d f) - (B.lift.comp S.residual) (d f) = 0
    rw [h, sub_self]

/-- In coordinates, a cochain map is block triangular, not necessarily block diagonal. -/
```

### KomorebiSpace.SplitDefect.DefectMap.mismatch_comp

Source: `formal/KomorebiSpace/ResidualNaturality.lean`, line 137. SHA-256 `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8`.

```lean
theorem mismatch_comp {d' : G →L[𝕜] U} (V : DefectMap D d')
    (C : Section d') (r : R) :
    (S.comp V).mismatch A C r =
      V.candidate (S.mismatch A B r) + V.mismatch B C (S.residual r) := by
  simp only [mismatch_apply, comp_candidate, comp_residual, map_sub]
  abel

/-- If residuals vanish along a sequence, the two repair routes approach one another. -/
```

### KomorebiSpace.SplitDefect.DefectMap.repair_discrepancy_tendsto_zero

Source: `formal/KomorebiSpace/ResidualNaturality.lean`, line 145. SHA-256 `accf1d105c612e673fcd508847d023f56d7939490a5416202873d7bde803b8e8`.

```lean
theorem repair_discrepancy_tendsto_zero (f : ℕ → E)
    (hf : Filter.Tendsto (fun n => d (f n)) Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun n => B.project (S.candidate (f n)) - S.candidate (A.project (f n)))
      Filter.atTop (nhds 0) := by
  have hc := ((S.mismatch A B).continuous.tendsto (0 : R)).comp hf
  simpa only [map_zero, Function.comp_def, ← S.repair_change A B] using hc

end DefectMap
end SplitDefect
end KomorebiSpace
end
```

## KS67 — Residual sampling and repair across scales

Actual operator-valued tower residuals with contractive bonding maps. A uniform bound on sampling gaps is required for the stated residual operator and repair norm estimates, but not for qualitative preservation of exactness.

### KomorebiSpace.BanachTower.resampling_chain

Source: `formal/KomorebiSpace/ResidualSampling.lean`, line 113. SHA-256 `01c4bf790c0ac8e55f1fe38c60b88d42e044a2ea85fa26651b87a370a0024985`.

```lean
theorem resampling_chain (f : Candidates X Y) :
    differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ f) =
      residualSampleCLM X Y hX hY φ hφ M hgap (differential X Y f) := by
  apply lp.ext
  funext n
  exact (blockSum_differential X Y f (hφ (Nat.le_succ n))).symm

include hgap in
```

### KomorebiSpace.BanachTower.residualSampleCLM_opNorm

Source: `formal/KomorebiSpace/ResidualSampling.lean`, line 107. SHA-256 `01c4bf790c0ac8e55f1fe38c60b88d42e044a2ea85fa26651b87a370a0024985`.

```lean
theorem residualSampleCLM_opNorm :
    ‖residualSampleCLM X Y hX hY φ hφ M hgap‖ ≤ (M : ℝ) :=
  ContinuousLinearMap.opNorm_le_bound _ (by positivity)
    (residualSampleCLM_bound X Y hX hY φ hφ M hgap)

/-- The central commuting square, with both operators already constructed. -/
```

### KomorebiSpace.BanachTower.sample_exact

Source: `formal/KomorebiSpace/ResidualSampling.lean`, line 129. SHA-256 `01c4bf790c0ac8e55f1fe38c60b88d42e044a2ea85fa26651b87a370a0024985`.

```lean
theorem sample_exact (f : Candidates X Y) (hf : Exact X Y f) :
    Exact (resample X hX φ hφ) (resample Y hY φ hφ) (sampleCLM X Y hX hY φ hφ f) := by
  intro n
  apply ContinuousLinearMap.ext
  intro x
  change restriction Y (hφ (Nat.le_succ n)) (f (φ (n+1)) x) =
    f (φ n) (restriction X (hφ (Nat.le_succ n)) x)
  rw [restriction_underlying Y, restriction_underlying X]
  exact Resolution.Adjacent.map_all (fun n => f n)
    (fun k y => congrArg (fun T : X.Obj (k+1) →L[𝕜] Y.Obj k => T y) (hf k))
    (hφ (Nat.le_succ n)) x

include hgap in
/-- Vanishing residual in candidate-sequence norm survives bounded-gap resampling. -/
```

### KomorebiSpace.BanachTower.sampling_repair_bound

Source: `formal/KomorebiSpace/SamplingRepair.lean`, line 68. SHA-256 `314018aefc244c41bb591d37611d27157df2677cf02769d78e1b258a9a29ccc5`.

```lean
theorem sampling_repair_bound (f : Candidates X Y) :
    ‖B.project (sampleCLM X Y hX hY φ hφ f) -
      sampleCLM X Y hX hY φ hφ (A.project f)‖ ≤
        (‖A.lift‖ + (M : ℝ)*‖B.lift‖) * ‖differential X Y f‖ := by
  rw [sampling_repair_formula X Y hX hY φ hφ M hgap]
  exact ((samplingMismatch X Y hX hY φ hφ M hgap A B).le_opNorm _).trans
    (mul_le_mul_of_nonneg_right (samplingMismatch_opNorm X Y hX hY φ hφ M hgap A B)
      (norm_nonneg _))

include hgap in
/-- The discrepancy tends to zero, though equality at each finite stage is not automatic. -/
```

## KS68 — Why literal full framing is presentation dependent

The two-copy equivalent-view model compares actual fully framed gauge groupoids. Failure concerns freezing every representative, not the invariant identified-boundary realization construction.

### KomorebiSpace.FramingBoundaryExamples.full_framing_not_equivalence

Source: `formal/KomorebiSpace/FramingBoundaryExamples.lean`, line 115. SHA-256 `c55a4b3576aa167aa828f0b1ae0ce9e2a65c2ae6ae1fb8ff89445a052108f885`.

```lean
theorem full_framing_not_equivalence (v : V) (g : H) (hg : g ≠ 1) :
    ¬ ((ViewDuplication.constantGroups V H).reindexFramedFunctor
      (ViewDuplication.embed V) Set.univ).IsEquivalence := by
  intro h
  let := h
  exact full_framing_not_full V v g hg inferInstance

end FramingBoundaryExamples
end KomorebiSpace
```

### KomorebiSpace.GroupViewSystem.fully_framed_equivalent_iff

Source: `formal/KomorebiSpace/FramingBoundaryExamples.lean`, line 43. SHA-256 `c55a4b3576aa167aa828f0b1ae0ce9e2a65c2ae6ae1fb8ff89445a052108f885`.

```lean
theorem fully_framed_equivalent_iff (c d : F.Cocycle) :
    F.GaugeEquivalent Set.univ c d ↔ c = d := by
  constructor
  · rintro ⟨a,ha⟩
    rw [F.fully_framed_gauge a, F.gauge_one] at ha
    exact ha
  · intro h
    exact ⟨1, (F.gauge_one c).trans h⟩

end GroupViewSystem

namespace FramingBoundaryExamples
variable (V : Type u₁) [Category.{v₁} V]
variable {H : Type w} [Group H]

/-- Give the redundant copy a different trivialization. -/
```

### KomorebiSpace.FramingBoundaryExamples.copyCocycle_pullback

Source: `formal/KomorebiSpace/FramingBoundaryExamples.lean`, line 75. SHA-256 `c55a4b3576aa167aa828f0b1ae0ce9e2a65c2ae6ae1fb8ff89445a052108f885`.

```lean
@[simp] theorem copyCocycle_pullback (g : H) :
    (ViewDuplication.constantGroups V H).reindexCocycle (ViewDuplication.embed V)
      (copyCocycle V g) =
    ((ViewDuplication.constantGroups V H).reindex (ViewDuplication.embed V)).trivial := by
  apply GroupViewSystem.Cocycle.ext
  intro v w f
  change (1 : H) * 1 * 1⁻¹ = 1
  simp

/-- Both framing domains in the counterexample are saturated. -/
```

## KS69 — Measured and uncertain residual certificates

A supplied residual bound for the reference operator. Measurement error and operator error have separate terms. Proximity is to the reference exact space, not automatically to the changed kernel.

### KomorebiSpace.ResidualRobustness.Bound.measured

Source: `formal/KomorebiSpace/ResidualPerturbation.lean`, line 33. SHA-256 `5ceeb960fcb6fb6318829a9b13a4f12c08c5afd86048c750ff8bbb5a03011bfd`.

```lean
theorem measured (x : E) (y : R) (η : ℝ) (hy : ‖d x-y‖≤η) :
    ‖x-projection d x‖≤B.constant*(‖y‖+η) := by
  apply (B.estimate x).trans
  apply mul_le_mul_of_nonneg_left _ B.nonneg
  calc
    ‖d x‖ ≤ ‖d x-y‖+‖y‖ := by
      simpa only [sub_add_cancel] using norm_add_le (d x-y) y
    _ ≤ ‖y‖+η := by linarith

/-- With no kernel-preservation assumption, operator error costs epsilon times
input size. The conclusion still concerns the reference exact space. -/
```

### KomorebiSpace.ResidualRobustness.Bound.uncertain_operator_opNorm

Source: `formal/KomorebiSpace/ResidualPerturbation.lean`, line 59. SHA-256 `5ceeb960fcb6fb6318829a9b13a4f12c08c5afd86048c750ff8bbb5a03011bfd`.

```lean
theorem uncertain_operator_opNorm (e : E →L[ℝ] R) (ε η : ℝ)
    (he : ‖d-e‖≤ε) (x : E) (y : R) (hy : ‖e x-y‖≤η) :
    ‖x-projection d x‖≤B.constant*(‖y‖+η+ε*‖x‖) :=
  B.uncertain_operator e ε η (fun z => ((d-e).le_opNorm z).trans
    (mul_le_mul_of_nonneg_right he (norm_nonneg z))) x y hy

/-- The direction of exact-space comparison that needs no preservation premise. -/
```

## KS70 — Stable repair when the old exact space is preserved

The changed operator annihilates the old kernel and the product of reference gain and perturbation radius is strictly less than one. Kernel equality and the new bound are derived, not assumed from norm closeness alone.

### KomorebiSpace.ResidualRobustness.Bound.preserved_kernel_bound

Source: `formal/KomorebiSpace/ResidualPerturbation.lean`, line 73. SHA-256 `5ceeb960fcb6fb6318829a9b13a4f12c08c5afd86048c750ff8bbb5a03011bfd`.

```lean
theorem preserved_kernel_bound (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) (x : E) :
    ‖x-projection d x‖≤(B.constant/(1-B.constant*ε))*‖e x‖ := by
  let u := x-projection d x
  have hdu : d u=d x := defect_error d x
  have heu : e u=e x := by simp only [u,map_sub,hpres,sub_zero]
  have htri : ‖d x‖≤‖e x‖+ε*‖u‖ := by
    calc
      ‖d x‖ = ‖(d-e) u+e u‖ := by simp only [sub_apply,sub_add_cancel,hdu]
      _ ≤ ‖(d-e) u‖+‖e u‖ := norm_add_le _ _
      _ ≤ ‖e x‖+ε*‖u‖ := by rw [heu]; linarith [he u]
  have hb := (B.estimate x).trans (mul_le_mul_of_nonneg_left htri B.nonneg)
  have hp : 0<1-B.constant*ε := sub_pos.mpr hradius
  have hh : (1-B.constant*ε)*‖x-projection d x‖≤B.constant*‖e x‖ := by
    dsimp only [u] at hb
    nlinarith
  calc
    _ ≤ (B.constant*‖e x‖)/(1-B.constant*ε) :=
      (le_div_iff₀ hp).mpr (by nlinarith [hh])
    _ = _ := by ring

/-- Equality of kernels is a conclusion, not an input field. -/
```

### KomorebiSpace.ResidualRobustness.Bound.kernels_equal

Source: `formal/KomorebiSpace/ResidualPerturbation.lean`, line 96. SHA-256 `5ceeb960fcb6fb6318829a9b13a4f12c08c5afd86048c750ff8bbb5a03011bfd`.

```lean
theorem kernels_equal (e : E →L[ℝ] R) (ε : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1) : d.ker=e.ker := by
  ext x
  change d x=0 ↔ e x=0
  constructor
  · intro hx
    simpa only [projection_fixes d x hx] using hpres x
  · intro hx
    have hb := B.preserved_kernel_bound e ε he hpres hradius x
    rw [hx,norm_zero,mul_zero] at hb
    have hz : x=projection d x := sub_eq_zero.mp (norm_eq_zero.mp
      (le_antisymm hb (norm_nonneg _)))
    rw [hz]
    exact projection_exact d x

/-- The same canonical exact repair works for every admitted perturbation. -/
```

### KomorebiSpace.ResidualRobustness.Bound.perturbed_measured

Source: `formal/KomorebiSpace/ResidualPerturbation.lean`, line 139. SHA-256 `5ceeb960fcb6fb6318829a9b13a4f12c08c5afd86048c750ff8bbb5a03011bfd`.

```lean
theorem perturbed_measured (e : E →L[ℝ] R) (ε η : ℝ)
    (he : ∀ x, ‖(d-e) x‖≤ε*‖x‖)
    (hpres : ∀ x, e (projection d x)=0) (hradius : B.constant*ε<1)
    (x : E) (y : R) (hy : ‖e x-y‖≤η) :
    ‖x-projection d x‖≤(B.constant/(1-B.constant*ε))*(‖y‖+η) := by
  have h := (B.perturb e ε he hpres hradius).measured x y η hy
  simpa only [perturb,← B.projections_equal e ε he hpres hradius] using h

end Bound
end ResidualRobustness
end KomorebiSpace
end
```
