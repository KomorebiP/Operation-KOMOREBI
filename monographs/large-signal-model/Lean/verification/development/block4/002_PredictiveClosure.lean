import KomorebiLSM.Realization

/-! P6 and the set-level part of P22. The codomain is onto its image.
Representative choice constructs a reduced map; fiber constancy, not a
supplied transition, establishes that the construction is well defined.
-/
set_option autoImplicit false
namespace Komorebi.LSM
universe u v w t

/-- Exactly the information-loss criterion needed for a factor map. -/
def FiberConstant {X : Type u} {Z : Type v} {Y : Type w}
    (gamma : X → Z) (eta : X → Y) : Prop :=
  ∀ x y, gamma x = gamma y → eta x = eta y

theorem factor_exists_unique_iff {X : Type u} {Z : Type v} {Y : Type w}
    (gamma : X → Z) (onto : ∀ z, ∃ x, gamma x = z) (eta : X → Y) :
    (∃ J : Z → Y, (∀ x, J (gamma x) = eta x) ∧
      (∀ K : Z → Y, (∀ x, K (gamma x) = eta x) → K = J)) ↔
    FiberConstant gamma eta := by
  constructor
  · rintro ⟨J, hj, _⟩ x y h
    exact (hj x).symm.trans ((congrArg J h).trans (hj y))
  · intro h
    classical
    let chooseX (z : Z) : X := Classical.choose (onto z)
    have hx (z : Z) : gamma (chooseX z) = z := Classical.choose_spec (onto z)
    let J : Z → Y := fun z => eta (chooseX z)
    have hj (x : X) : J (gamma x) = eta x := h _ _ (hx (gamma x))
    refine ⟨J, hj, ?_⟩
    intro K hk
    funext z
    obtain ⟨x, rfl⟩ := onto z
    exact (hk x).trans (hj x).symm

/-- The reduced transition is unique on the actual summary space. -/
theorem predictive_closure_iff {X : Type u} {Z : Type v}
    (gamma : X → Z) (onto : ∀ z, ∃ x, gamma x = z) (F : X → X) :
    (∃ f : Z → Z, (∀ x, f (gamma x) = gamma (F x)) ∧
      (∀ g : Z → Z, (∀ x, g (gamma x) = gamma (F x)) → g = f)) ↔
    FiberConstant gamma (fun x => gamma (F x)) :=
  factor_exists_unique_iff gamma onto (fun x => gamma (F x))

def SummaryState {X : Type u} {Z : Type v} (gamma : X → Z) :=
  {z : Z // ∃ x, gamma x = z}

def summarize {X : Type u} {Z : Type v} (gamma : X → Z) (x : X) :
    SummaryState gamma := ⟨gamma x, x, rfl⟩

theorem summarize_onto {X : Type u} {Z : Type v} (gamma : X → Z)
    (z : SummaryState gamma) : ∃ x, summarize gamma x = z := by
  obtain ⟨x, hx⟩ := z.property
  exact ⟨x, Subtype.ext hx⟩

theorem closure_on_image_iff {X : Type u} {Z : Type v}
    (gamma : X → Z) (F : X → X) :
    (∃ f : SummaryState gamma → SummaryState gamma,
      (∀ x, f (summarize gamma x) = summarize gamma (F x)) ∧
      (∀ g : SummaryState gamma → SummaryState gamma,
        (∀ x, g (summarize gamma x) = summarize gamma (F x)) → g = f)) ↔
    FiberConstant gamma (fun x => gamma (F x)) := by
  rw [predictive_closure_iff (summarize gamma) (summarize_onto gamma)]
  constructor
  · intro h x y hxy
    exact congrArg Subtype.val (h x y (Subtype.ext hxy))
  · intro h x y hxy
    exact Subtype.ext (h x y (congrArg Subtype.val hxy))

/-- Upward lift between the actual images, not ambient codomains. -/
theorem factor_on_images_iff {X : Type u} {Z : Type v} {Y : Type w}
    (gamma : X → Z) (eta : X → Y) :
    (∃ J : SummaryState gamma → SummaryState eta,
      (∀ x, J (summarize gamma x) = summarize eta x) ∧
      (∀ K : SummaryState gamma → SummaryState eta,
        (∀ x, K (summarize gamma x) = summarize eta x) → K = J)) ↔
    FiberConstant gamma eta := by
  rw [factor_exists_unique_iff (summarize gamma) (summarize_onto gamma)
    (summarize eta)]
  constructor
  · intro h x y hxy
    exact congrArg Subtype.val (h x y (Subtype.ext hxy))
  · intro h x y hxy
    exact Subtype.ext (h x y (congrArg Subtype.val hxy))

/-- Actions need simultaneous fiber constancy. No transition is assumed. -/
theorem controlled_closure_iff {X : Type u} {Z : Type v} {A : Type w}
    (gamma : X → Z) (onto : ∀ z, ∃ x, gamma x = z) (F : A → X → X) :
    (∃ f : A → Z → Z, ∀ a x, f a (gamma x) = gamma (F a x)) ↔
    (∀ a, FiberConstant gamma (fun x => gamma (F a x))) := by
  constructor
  · rintro ⟨f, hf⟩ a x y h
    exact (hf a x).symm.trans ((congrArg (f a) h).trans (hf a y))
  · intro h
    classical
    have ex (a : A) := (predictive_closure_iff gamma onto (F a)).mpr (h a)
    exact ⟨fun a => Classical.choose (ex a),
      fun a => (Classical.choose_spec (ex a)).1⟩

/-- Exact closure is preserved under composition of operations. -/
theorem factor_composition {X : Type u} {Z : Type v}
    (gamma : X → Z) (F G : X → X) (f g : Z → Z)
    (hf : ∀ x, f (gamma x) = gamma (F x))
    (hg : ∀ x, g (gamma x) = gamma (G x)) (x : X) :
    g (f (gamma x)) = gamma (G (F x)) := by
  rw [hf, hg]

/-- One explicit pair in a lost-information fiber refutes every proposed factor. -/
theorem no_factor_of_witness {X : Type u} {Z : Type v} {Y : Type w}
    (gamma : X → Z) (eta : X → Y) (x y : X)
    (same : gamma x = gamma y) (different : eta x ≠ eta y) :
    ¬ ∃ J : Z → Y, ∀ t, J (gamma t) = eta t := by
  rintro ⟨J, hj⟩
  exact different ((hj x).symm.trans ((congrArg J same).trans (hj y)))

end Komorebi.LSM
