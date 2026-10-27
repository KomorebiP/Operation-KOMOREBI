import KomorebiSpace.RealizationFaithfulness

set_option autoImplicit false

/-!
# The exact image of realization for projection-surjective sources

An output level must factor through some finite input level. The input level
may depend on the output level. A common monotone schedule is constructed.
No topology or numerical complexity bound is implicit in this condition.
-/

universe u v
namespace KomorebiSpace
namespace Resolution
variable {X : Resolution.{u}} {Y : Resolution.{v}}

/-- Finite-level factorization for every output coordinate. -/
def FinitelyObserved (F : X.Point → Y.Point) : Prop :=
  ∀ n, ∃ k, ∃ a : X.Obj k → Y.Obj n,
    ∀ x : X.Point, (F x).val n = a (x.val k)

def levelEnvelope (k : ℕ → ℕ) : ℕ → ℕ
  | 0 => k 0
  | n+1 => max (levelEnvelope k n) (k (n+1))

theorem levelEnvelope_ge (k : ℕ → ℕ) (n : ℕ) : k n ≤ levelEnvelope k n := by
  cases n with
  | zero => exact le_refl _
  | succ n => exact Nat.le_max_right _ _

theorem levelEnvelope_monotone (k : ℕ → ℕ) : Monotone (levelEnvelope k) := by
  intro i j h
  induction j, h using Nat.le_induction with
  | base => exact le_refl _
  | succ j hj ih => exact ih.trans (Nat.le_max_left _ _)

def observedApp (k : ℕ → ℕ) (a : ∀ n, X.Obj (k n) → Y.Obj n) (n : ℕ) :
    X.Obj (levelEnvelope k n) → Y.Obj n :=
  fun x => a n (X.restrict (levelEnvelope_ge k n) x)

theorem observedApp_on_point (F : X.Point → Y.Point) (k : ℕ → ℕ)
    (a : ∀ n, X.Obj (k n) → Y.Obj n)
    (ha : ∀ n x, (F x).val n = a n (x.val (k n))) (n : ℕ) (x : X.Point) :
    observedApp k a n (x.val (levelEnvelope k n)) = (F x).val n := by
  exact (congrArg (a n) (x.property (k n) (levelEnvelope k n)
    (levelEnvelope_ge k n))).trans (ha n x).symm

/-- Compatibility is derived from the realized output and source projection surjectivity. -/
def observedPresentation (hX : ProjectionSurjective X) (F : X.Point → Y.Point)
    (k : ℕ → ℕ) (a : ∀ n, X.Obj (k n) → Y.Obj n)
    (ha : ∀ n x, (F x).val n = a n (x.val (k n))) : ReindexedMap X Y where
  level := levelEnvelope k
  monotone := levelEnvelope_monotone k
  app := observedApp k a
  naturality := by
    intro i j hij y
    obtain ⟨x, hx⟩ := hX (levelEnvelope k j) y
    change x.val (levelEnvelope k j) = y at hx
    subst y
    rw [observedApp_on_point F k a ha j x, (F x).property i j hij,
      x.property _ _ (levelEnvelope_monotone k hij), observedApp_on_point F k a ha i x]

theorem observedPresentation_onLimit (hX : ProjectionSurjective X)
    (F : X.Point → Y.Point) (k : ℕ → ℕ) (a : ∀ n, X.Obj (k n) → Y.Obj n)
    (ha : ∀ n x, (F x).val n = a n (x.val (k n))) :
    (observedPresentation hX F k a ha).onLimit = F := by
  funext x
  exact Point.ext (fun n => observedApp_on_point F k a ha n x)

theorem exists_presentation_of_finitelyObserved (hX : ProjectionSurjective X)
    (F : X.Point → Y.Point) (hF : FinitelyObserved F) :
    ∃ f : ReindexedMap X Y, f.onLimit = F := by
  classical
  let k : ℕ → ℕ := fun n => Classical.choose (hF n)
  let a : ∀ n, X.Obj (k n) → Y.Obj n :=
    fun n => Classical.choose (Classical.choose_spec (hF n))
  have ha : ∀ n x, (F x).val n = a n (x.val (k n)) :=
    fun n => Classical.choose_spec (Classical.choose_spec (hF n))
  exact ⟨observedPresentation hX F k a ha, observedPresentation_onLimit hX F k a ha⟩

theorem reindexed_finitelyObserved (f : ReindexedMap X Y) :
    FinitelyObserved f.onLimit := by
  intro n
  exact ⟨f.level n, f.app n, fun _ => rfl⟩

theorem eventual_finitelyObserved (f : EventualHom X Y) :
    FinitelyObserved f.onLimit := by
  induction f using Quotient.inductionOn with
  | _ f => exact reindexed_finitelyObserved f

theorem realization_image_iff (hX : ProjectionSurjective X) (F : X.Point → Y.Point) :
    (∃ f : EventualHom X Y, f.onLimit = F) ↔ FinitelyObserved F := by
  constructor
  · rintro ⟨f, rfl⟩; exact eventual_finitelyObserved f
  · intro hF
    obtain ⟨f, hf⟩ := exists_presentation_of_finitelyObserved hX F hF
    exact ⟨EventualHom.mk f, hf⟩

/-- Presentation-independent coordinates on the morphism set, under an explicit hypothesis. -/
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

@[simp] theorem finiteObservationEquiv_apply (hX : ProjectionSurjective X)
    (f : EventualHom X Y) : (finiteObservationEquiv hX f).val = f.onLimit := rfl

end Resolution
end KomorebiSpace
