import PaperXI.ScalarHolonomy
import PaperXI.GraphTransport
import PaperXI.GraphLoopRepresentation

/-! Vertex rescaling of actual graph transport and scalar ratio characters. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.ProjectiveHolonomy

open Quiver
open PaperXI.ScalarHolonomy

attribute [local instance] GraphTransport.symmetrifyAdd GraphTransport.symmetrifyModule

variable {K α : Type*} [Field K] [Quiver α]
variable {V : α → Type*} [∀ u, AddCommGroup (V u)] [∀ u, Module K (V u)]

/-- Change the representative at each vertex by its chosen nonzero scalar. -/
def rescale (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) (a : α → Kˣ)
    {u v : α} (e : u ⟶ v) : V u ≃ₗ[K] V v :=
  ((scalarHom (a u)).symm.trans (A e)).trans (scalarHom (a v))

theorem rescale_apply (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) {u v : α} (e : u ⟶ v) (x : V u) :
    rescale A a e x = ((a v * (a u)⁻¹ : Kˣ) : K) • A e x := by
  change (a v : K) • A e ((((a u)⁻¹ : Kˣ) : K) • x) = _
  rw [map_smul, smul_smul, Units.val_mul]

/-- The rescaled edge family is related to the original by actual vertex gauges. -/
theorem rescale_gauge (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) {u v : α} (e : u ⟶ v) (x : V u) :
    scalarHom (a v) (A e x) = rescale A a e (scalarHom (a u) x) := by
  change scalarHom (a v) (A e x) =
    scalarHom (a v) (A e ((scalarHom (a u)).symm (scalarHom (a u) x)))
  rw [LinearEquiv.symm_apply_apply]

/-- Every path retains only the two endpoint rescalings. -/
theorem rescale_path (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) {u v : Symmetrify α} (p : Path u v) :
    GraphTransport.path (rescale A a) p =
      ((scalarHom (a u)).symm.trans (GraphTransport.path A p)).trans
        (scalarHom (a v)) := by
  ext x
  have h := GraphTransport.gauge_path A (rescale A a)
    (fun v => (scalarHom (a v)).toLinearMap)
    (fun e y => rescale_gauge A a e y) p ((scalarHom (a u)).symm x)
  simpa using h.symm

theorem rescale_path_apply (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) {u v : Symmetrify α} (p : Path u v) (x : V u) :
    GraphTransport.path (rescale A a) p x =
      ((a v * (a u)⁻¹ : Kˣ) : K) • GraphTransport.path A p x := by
  rw [rescale_path]
  change (a v : K) • GraphTransport.path A p ((((a u)⁻¹ : Kˣ) : K) • x) = _
  rw [map_smul, smul_smul, Units.val_mul]

/-- Vertex rescaling leaves the actual closed-path operator unchanged, at every rank. -/
theorem rescale_loop (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) {r : Symmetrify α} (p : Path r r) :
    GraphTransport.path (rescale A a) p = GraphTransport.path A p := by
  ext x
  simp [rescale_path_apply]

/-- Cancellation on represented loops gives equality of the full reduced-loop representations. -/
theorem rescale_holonomy (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) (r : α) :
    GraphLoop.holonomy (rescale A a) r = GraphLoop.holonomy A r := by
  apply MonoidHom.ext
  intro g
  obtain ⟨p, rfl⟩ := GraphLoop.loopClass_surjective r g
  rw [GraphLoop.holonomy_loopClass, GraphLoop.holonomy_loopClass]
  exact rescale_loop A a p

theorem rescale_isScalar (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) (r : α) (hA : IsScalar (GraphLoop.holonomy A r)) :
    IsScalar (GraphLoop.holonomy (rescale A a) r) := by
  rwa [rescale_holonomy]

/-- Scalarity on ordinary closed paths is exactly scalarity on their reduced quotient. -/
theorem isScalar_iff_paths (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v)) (r : α) :
    IsScalar (GraphLoop.holonomy A r) ↔
      ∀ p : @Quiver.Path (Quiver.Symmetrify α) _ r r,
        ∃ c : Kˣ, GraphTransport.path A p = scalarHom c := by
  constructor
  · intro h p
    simpa only [GraphLoop.holonomy_loopClass] using h (GraphLoop.loopClass p)
  · intro h g
    obtain ⟨p, rfl⟩ := GraphLoop.loopClass_surjective r g
    simpa only [GraphLoop.holonomy_loopClass] using h p

/-- The unique scalar character extracted from actual loop transport. -/
def loopCharacter (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (r : α) [Nontrivial (V r)] (hA : IsScalar (GraphLoop.holonomy A r)) :
    GraphLoop.Loop r →* Kˣ := character (GraphLoop.holonomy A r) hA

@[simp] theorem loopCharacter_spec
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (r : α) [Nontrivial (V r)] (hA : IsScalar (GraphLoop.holonomy A r))
    (g : GraphLoop.Loop r) :
    scalarHom (loopCharacter A r hA g) = GraphLoop.holonomy A r g :=
  character_spec _ _ _

/-- Vertex rescaling leaves the extracted scalar character unchanged. -/
theorem rescale_character (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (a : α → Kˣ) (r : α) [Nontrivial (V r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) :
    loopCharacter (rescale A a) r (rescale_isScalar A a r hA) =
      loopCharacter A r hA := by
  apply (character_unique (GraphLoop.holonomy (rescale A a) r)
    (rescale_isScalar A a r hA) (loopCharacter A r hA) ?_).symm
  intro g
  rw [loopCharacter_spec, rescale_holonomy]

/-- The ratio of two scalar loop characters factors through the actual abelianization. -/
def ratioH1 (r : α) (χ ψ : GraphLoop.Loop r →* Kˣ) : GraphLoop.H1 r →* Kˣ :=
  GraphLoop.factorCharacter r Kˣ (ratio χ ψ)

@[simp] theorem ratioH1_class (r : α) (χ ψ : GraphLoop.Loop r →* Kˣ)
    (g : GraphLoop.Loop r) :
    ratioH1 r χ ψ (GraphLoop.homologyClass r g) = ψ g * (χ g)⁻¹ := rfl

theorem ratioH1_unique (r : α) (χ ψ : GraphLoop.Loop r →* Kˣ)
    (δ : GraphLoop.H1 r →* Kˣ)
    (hδ : ∀ g, δ (GraphLoop.homologyClass r g) = ψ g * (χ g)⁻¹) :
    δ = ratioH1 r χ ψ := GraphLoop.factorCharacter_unique (ratio χ ψ) δ hδ

/-- The first-homology character is trivial exactly when the scalar holonomies agree. -/
theorem ratioH1_eq_one_iff (r : α) (χ ψ : GraphLoop.Loop r →* Kˣ) :
    ratioH1 r χ ψ = 1 ↔ χ = ψ := by
  constructor
  · intro h
    apply (ratio_eq_one_iff χ ψ).mp
    apply MonoidHom.ext
    intro g
    exact DFunLike.congr_fun h (GraphLoop.homologyClass r g)
  · intro h
    apply (GraphLoop.factorCharacter r Kˣ).symm.injective
    change ratio χ ψ = 1
    exact (ratio_eq_one_iff χ ψ).mpr h

variable {W : α → Type*} [∀ u, AddCommGroup (W u)] [∀ u, Module K (W u)]

/-- The first-homology character obtained from the two actual scalar transport systems. -/
def transportRatioH1
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (r : α) [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r)) :
    GraphLoop.H1 r →* Kˣ := ratioH1 r (loopCharacter A r hA) (loopCharacter B r hB)

@[simp] theorem transportRatioH1_class
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (r : α) [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r))
    (g : GraphLoop.Loop r) :
    transportRatioH1 A B r hA hB (GraphLoop.homologyClass r g) =
      loopCharacter B r hB g * (loopCharacter A r hA g)⁻¹ := rfl

/-- Both vertex rescalings cancel before the ratio is factored through first homology. -/
theorem transportRatioH1_rescale
    (A : ∀ {u v : α}, (u ⟶ v) → (V u ≃ₗ[K] V v))
    (B : ∀ {u v : α}, (u ⟶ v) → (W u ≃ₗ[K] W v))
    (a b : α → Kˣ) (r : α) [Nontrivial (V r)] [Nontrivial (W r)]
    (hA : IsScalar (GraphLoop.holonomy A r)) (hB : IsScalar (GraphLoop.holonomy B r)) :
    transportRatioH1 (rescale A a) (rescale B b) r
      (rescale_isScalar A a r hA) (rescale_isScalar B b r hB) =
        transportRatioH1 A B r hA hB := by
  unfold transportRatioH1
  rw [rescale_character, rescale_character]

end PaperXI.ProjectiveHolonomy
