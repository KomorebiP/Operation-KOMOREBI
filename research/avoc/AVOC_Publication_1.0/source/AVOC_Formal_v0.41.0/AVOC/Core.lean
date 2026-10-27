import Mathlib.Data.Finset.Card

namespace Komorebi.AVOC

universe u v w z

/-- `fine` refines `coarse` when the coarse representation can be decoded
from the fine representation.  This is the information preorder used by AVOC. -/
def Refines {X : Type u} {A : Type v} {B : Type w}
    (fine : X → A) (coarse : X → B) : Prop :=
  ∃ decode : A → B, ∀ x, decode (fine x) = coarse x

/-- Two encodings carry the same task-relevant information when each factors
through the other. -/
def EncodingEquiv {X : Type u} {A : Type v} {B : Type w}
    (φ : X → A) (ψ : X → B) : Prop :=
  Refines φ ψ ∧ Refines ψ φ

/-- An encoding is sufficient for target `T` when `T` can be recovered from it. -/
def TaskSufficient {X : Type u} {Z : Type v} {Y : Type w}
    (φ : X → Z) (T : X → Y) : Prop :=
  Refines φ T

/-- Fiber relation induced by a representation. -/
def SameFiber {X : Type u} {Z : Type v} (φ : X → Z) (x y : X) : Prop :=
  φ x = φ y

@[refl] theorem refines_refl {X : Type u} {A : Type v} (φ : X → A) :
    Refines φ φ := by
  exact ⟨id, by intro x; rfl⟩

@[trans] theorem refines_trans {X : Type u} {A : Type v} {B : Type w} {C : Type z}
    {φ : X → A} {ψ : X → B} {χ : X → C}
    (hφψ : Refines φ ψ) (hψχ : Refines ψ χ) : Refines φ χ := by
  rcases hφψ with ⟨d₁, hd₁⟩
  rcases hψχ with ⟨d₂, hd₂⟩
  refine ⟨d₂ ∘ d₁, ?_⟩
  intro x
  simp only [Function.comp_apply, hd₁ x, hd₂ x]

@[refl] theorem encodingEquiv_refl {X : Type u} {A : Type v} (φ : X → A) :
    EncodingEquiv φ φ := by
  exact ⟨refines_refl φ, refines_refl φ⟩

@[symm] theorem encodingEquiv_symm {X : Type u} {A : Type v} {B : Type w}
    {φ : X → A} {ψ : X → B} (h : EncodingEquiv φ ψ) : EncodingEquiv ψ φ := by
  exact ⟨h.2, h.1⟩

@[trans] theorem encodingEquiv_trans {X : Type u} {A : Type v} {B : Type w} {C : Type z}
    {φ : X → A} {ψ : X → B} {χ : X → C}
    (hφψ : EncodingEquiv φ ψ) (hψχ : EncodingEquiv ψ χ) : EncodingEquiv φ χ := by
  exact ⟨refines_trans hφψ.1 hψχ.1, refines_trans hψχ.2 hφψ.2⟩

/-- The target itself is always a sufficient representation for the target. -/
theorem target_is_sufficient {X : Type u} {Y : Type v} (T : X → Y) :
    TaskSufficient T T := by
  exact refines_refl T

/-- Sufficiency is monotone under refinement: adding information cannot destroy
recoverability of a target. -/
theorem sufficient_of_refines {X : Type u} {A : Type v} {B : Type w} {Y : Type z}
    {fine : X → A} {coarse : X → B} {T : X → Y}
    (hfc : Refines fine coarse) (hc : TaskSufficient coarse T) :
    TaskSufficient fine T := by
  exact refines_trans hfc hc

/-- Every task-sufficient encoding is above the target in the information preorder.
Thus the target is a canonical coarsest sufficient representation, modulo
`EncodingEquiv`. -/
theorem target_is_coarsest_sufficient {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y} (h : TaskSufficient φ T) : Refines φ T := by
  exact h

/-- A sufficient representation cannot merge two states that the target distinguishes. -/
theorem sufficient_preserves_target_distinctions
    {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y} (h : TaskSufficient φ T) {x y : X}
    (hxy : φ x = φ y) : T x = T y := by
  rcases h with ⟨decode, hdecode⟩
  calc
    T x = decode (φ x) := (hdecode x).symm
    _ = decode (φ y) := congrArg decode hxy
    _ = T y := hdecode y

/-- No-free-compression theorem: one task-relevant collision certifies
insufficiency of the representation. -/
theorem collision_obstructs_sufficiency
    {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y} {x y : X}
    (hφ : φ x = φ y) (hT : T x ≠ T y) : ¬ TaskSufficient φ T := by
  intro hs
  exact hT (sufficient_preserves_target_distinctions hs hφ)

/-- One direction of the fiber criterion: task sufficiency forces every fiber
of the encoding to lie inside a target fiber. -/
theorem sufficient_implies_fiber_refinement
    {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y} (h : TaskSufficient φ T) :
    ∀ x y, SameFiber φ x y → SameFiber T x y := by
  intro x y hxy
  exact sufficient_preserves_target_distinctions h hxy

/-- Conversely, if every encoding fiber lies inside a target fiber, then a
decoder exists. The `Nonempty Y` assumption supplies an arbitrary value on
encoding states that are never reached. -/
theorem fiber_refinement_implies_sufficient
    {X : Type u} {Z : Type v} {Y : Type w} [Nonempty Y]
    {φ : X → Z} {T : X → Y}
    (h : ∀ x y, SameFiber φ x y → SameFiber T x y) :
    TaskSufficient φ T := by
  classical
  let y₀ : Y := Classical.choice (inferInstance : Nonempty Y)
  let decode : Z → Y := fun z =>
    if hz : ∃ x, φ x = z then T (Classical.choose hz) else y₀
  refine ⟨decode, ?_⟩
  intro x
  have hx : ∃ x', φ x' = φ x := ⟨x, rfl⟩
  simp only [decode, dite_eq_left hx]
  apply h (Classical.choose hx) x
  exact Classical.choose_spec hx

/-- Fiber criterion for exact task sufficiency. This characterizes sufficient
representations entirely by which input distinctions they preserve. -/
theorem sufficient_iff_fiber_refinement
    {X : Type u} {Z : Type v} {Y : Type w} [Nonempty Y]
    {φ : X → Z} {T : X → Y} :
    TaskSufficient φ T ↔ ∀ x y, SameFiber φ x y → SameFiber T x y := by
  constructor
  · exact sufficient_implies_fiber_refinement
  · exact fiber_refinement_implies_sufficient





/-- General kernel-pair characterization of the information preorder.  Under an
inhabited coarse codomain, `fine` refines `coarse` exactly when every fiber of
`fine` is contained in a fiber of `coarse`. -/
theorem refines_iff_fiber_inclusion
    {X : Type u} {A : Type v} {B : Type w} [Nonempty B]
    {fine : X → A} {coarse : X → B} :
    Refines fine coarse ↔
      ∀ x y, SameFiber fine x y → SameFiber coarse x y := by
  exact sufficient_iff_fiber_refinement

/-- Number of representation states actually reached on a finite sample. -/
def reachableCard {X : Type u} {A : Type v} [DecidableEq A]
    (sample : Finset X) (φ : X → A) : ℕ :=
  (sample.image φ).card

/-- Finite data-processing theorem: a deterministic decoding cannot increase
the number of reachable representation states.  Therefore a refining
representation has at least as many reachable cells as the representation it
decodes onto. -/
theorem reachableCard_mono_of_refines
    {X : Type u} {A : Type v} {B : Type w}
    [DecidableEq X] [DecidableEq A] [DecidableEq B]
    (sample : Finset X) {fine : X → A} {coarse : X → B}
    (h : Refines fine coarse) :
    reachableCard sample coarse ≤ reachableCard sample fine := by
  rcases h with ⟨decode, hdecode⟩
  unfold reachableCard
  have himage : sample.image coarse = (sample.image fine).image decode := by
    ext b
    simp only [Finset.mem_image]
    constructor
    · rintro ⟨x, hx, rfl⟩
      refine ⟨fine x, ⟨x, hx, rfl⟩, ?_⟩
      exact hdecode x
    · rintro ⟨a, ⟨x, hx, rfl⟩, rfl⟩
      refine ⟨x, hx, ?_⟩
      exact (hdecode x).symm
  rw [himage]
  exact Finset.card_image_le

/-- A representation is task-minimal when it is sufficient and contains no
more task-relevant information than the target itself. -/
def TaskMinimal {X : Type u} {Z : Type v} {Y : Type w}
    (φ : X → Z) (T : X → Y) : Prop :=
  TaskSufficient φ T ∧ Refines T φ

/-- Task-minimality is exactly mutual factorization with the target.  Thus the
minimal sufficient representation is unique up to `EncodingEquiv`. -/
theorem taskMinimal_iff_encodingEquiv
    {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y} :
    TaskMinimal φ T ↔ EncodingEquiv φ T := by
  rfl

/-- The target representation is task-minimal. -/
theorem target_is_taskMinimal {X : Type u} {Y : Type v} (T : X → Y) :
    TaskMinimal T T := by
  exact ⟨target_is_sufficient T, refines_refl T⟩

/-- A family of queries can be compiled into one joint target.  The codomain
`Q → Y` is the vector of all answers requested from the raw state. -/
def JointTarget {Q : Type z} {X : Type u} {Y : Type w}
    (tasks : Q → X → Y) : X → (Q → Y) :=
  fun x q => tasks q x

/-- Sufficiency for the joint query family implies sufficiency for every
individual query. -/
theorem joint_sufficient_implies_each
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y}
    (h : TaskSufficient φ (JointTarget tasks)) :
    ∀ q, TaskSufficient φ (tasks q) := by
  intro q
  rcases h with ⟨decode, hdecode⟩
  refine ⟨fun z => decode z q, ?_⟩
  intro x
  simpa [JointTarget] using congrFun (hdecode x) q

/-- If one representation is sufficient for every query in a family, then it
is sufficient for their joint answer vector.  Classical choice selects the
per-query decoders. -/
theorem each_sufficient_implies_joint
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y}
    (h : ∀ q, TaskSufficient φ (tasks q)) :
    TaskSufficient φ (JointTarget tasks) := by
  classical
  let decodeFor : Q → (Z → Y) := fun q => Classical.choose (h q)
  refine ⟨fun z q => decodeFor q z, ?_⟩
  intro x
  funext q
  have hq := Classical.choose_spec (h q)
  simpa [decodeFor, JointTarget] using hq x

/-- Exact family criterion: a context is sufficient for a query family exactly
when it is sufficient for every member of that family. -/
theorem sufficient_joint_iff_each
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y} :
    TaskSufficient φ (JointTarget tasks) ↔ ∀ q, TaskSufficient φ (tasks q) := by
  constructor
  · exact joint_sufficient_implies_each
  · exact each_sufficient_implies_joint

/-- The joint target is the canonical coarsest representation sufficient for
all declared queries: every jointly sufficient context factors onto it. -/
theorem joint_target_is_coarsest_sufficient
    {Q : Type z} {X : Type u} {Z : Type v} {Y : Type w}
    {φ : X → Z} {tasks : Q → X → Y}
    (h : ∀ q, TaskSufficient φ (tasks q)) :
    Refines φ (JointTarget tasks) := by
  exact each_sufficient_implies_joint h

/-- Accepted candidates are bounded by both generation capacity and verification
capacity when admission requires membership in both sets. -/
theorem verified_yield_ceiling
    {α : Type u} [DecidableEq α]
    {accepted generated verified : Finset α}
    (hg : accepted ⊆ generated) (hv : accepted ⊆ verified) :
    accepted.card ≤ min generated.card verified.card := by
  exact le_min (Finset.card_le_card hg) (Finset.card_le_card hv)

/-- Counterexample filtering never increases a finite hypothesis class. -/
theorem counterexample_pruning_nonexpansive
    {H : Type u} [DecidableEq H] (S : Finset H) (survives : H → Prop)
    [DecidablePred survives] :
    (S.filter survives).card ≤ S.card := by
  exact Finset.card_le_card (Finset.filter_subset survives S)

/-- A witness that rejects at least one currently admitted hypothesis strictly
compresses the finite hypothesis class. -/
theorem counterexample_pruning_strict
    {H : Type u} [DecidableEq H] (S : Finset H) (survives : H → Prop)
    [DecidablePred survives] {h : H}
    (hh : h ∈ S) (hreject : ¬ survives h) :
    (S.filter survives).card < S.card := by
  apply Finset.card_lt_card
  apply Finset.ssubset_iff_subset_ne.mpr
  refine ⟨Finset.filter_subset survives S, ?_⟩
  intro heq
  have hmem : h ∈ S.filter survives := by
    rw [heq]
    exact hh
  exact hreject (Finset.mem_filter.mp hmem).2

end Komorebi.AVOC
