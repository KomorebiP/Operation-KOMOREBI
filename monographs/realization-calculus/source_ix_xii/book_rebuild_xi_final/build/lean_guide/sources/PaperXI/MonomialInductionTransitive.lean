import PaperXI.MonomialInduction

/-! The transitive weighted permutation criterion for actual induced representations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialInduction
open Representation Module
variable {G X V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ G V) (b : Basis X ℂ V)
  (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)
  (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) (x₀ : X)

include hρ in
/-- The actual line stabilizer equals the stabilizer of the basis index. -/
theorem mem_lineStabilizer_iff (g : G) :
    g ∈ LineCharacter.lineStabilizer ρ (b x₀) ↔ p g x₀ = x₀ := by
  constructor
  · rintro ⟨d, hd⟩
    by_contra hne
    have he : (c g x₀ : ℂ) • b (p g x₀) = d • b x₀ := (hρ g x₀).symm.trans hd
    have hc := congrArg (fun w => (b.repr w) (p g x₀)) he
    simp [hne] at hc
  · intro hg
    exact ⟨(c g x₀ : ℂ), by simpa [hg] using hρ g x₀⟩

include hρ in
/-- On that subgroup, the scalar character is the supplied actual basis weight. -/
theorem character_eq_weight (g : LineCharacter.lineStabilizer ρ (b x₀)) :
    (LineCharacter.character ρ (b x₀) (b.ne_zero x₀) g : ℂ) = c (g : G) x₀ := by
  apply LineCharacter.scalar_unique (b.ne_zero x₀)
  rw [← LineCharacter.character_action]
  have hg := (mem_lineStabilizer_iff ρ b p c hρ x₀ (g : G)).mp g.property
  simpa [hg] using hρ (g : G) x₀

variable (htrans : ∀ x : X, ∃ g : G, p g x₀ = x)

/-- Representatives are chosen from transitivity, not assumed to index cosets. -/
def representative : X → G := fun x => Classical.choose (htrans x)

theorem representative_spec (x : X) : p (representative p x₀ htrans x) x₀ = x :=
  Classical.choose_spec (htrans x)

include hρ in
theorem representative_action (x : X) :
    ρ (representative p x₀ htrans x) (b x₀) =
      (c (representative p x₀ htrans x) x₀ : ℂ) • b x := by
  rw [hρ, representative_spec]

include hρ in
theorem orbit_is_monomial (g : G) :
    ∃ x : X, ∃ d : ℂˣ, ρ g (b x₀) = (d : ℂ) • b x :=
  ⟨p g x₀, c g x₀, hρ g x₀⟩

/-- Actual Mathlib induction of the point-stabilizer line character is isomorphic
 to any representation with a transitive monomial basis. -/
def transitiveEquivalence : Representation.Equiv
    (induced ρ (b x₀) (b.ne_zero x₀)) ρ :=
  equivalence ρ (b x₀) (b.ne_zero x₀) b (representative p x₀ htrans)
    (fun x => c (representative p x₀ htrans x) x₀)
    (representative_action ρ b p c hρ x₀ htrans)
    (orbit_is_monomial ρ b p c hρ x₀)

@[simp] theorem transitiveEquivalence_mk (g : G) (z : ℂ) :
    transitiveEquivalence ρ b p c hρ x₀ htrans
      (IndV.mk (stabilizer ρ (b x₀)).subtype
        (lineRepresentation ρ (b x₀) (b.ne_zero x₀)) g z) = z • ρ g⁻¹ (b x₀) :=
  evaluation_mk ρ (b x₀) (b.ne_zero x₀) g z

end PaperXI.MonomialInduction
