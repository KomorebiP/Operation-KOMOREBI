import PaperXI.MonomialInductionTransitive

/-! Induction from a specified subgroup and its actual scalar character. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialInduction
open Representation Module
variable {G X V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

/-- A supplied character that acts on the nonzero line equals its actual scalar
character once the supplied subgroup is identified with the line stabilizer. -/
def equivalenceOfSubgroup
    (ρ : Representation ℂ G V) (v : V) (hv : v ≠ 0)
    (b : Basis X ℂ V) (r : X → G) (a : X → ℂˣ)
    (hr : ∀ i, ρ (r i) v = (a i : ℂ) • b i)
    (hmono : ∀ g : G, ∃ i : X, ∃ d : ℂˣ, ρ g v = (d : ℂ) • b i)
    (S : Subgroup G) (χ : S →* ℂˣ) (hS : S = stabilizer ρ v)
    (hχ : ∀ s : S, ρ (s : G) v = (χ s : ℂ) • v) :
    Representation.Equiv (Representation.ind S.subtype (scalarRepresentation χ)) ρ := by
  subst S
  have he : χ = character ρ v hv := by
    apply MonoidHom.ext
    intro s
    apply Units.ext
    apply LineCharacter.scalar_unique hv
    rw [← hχ s, ← LineCharacter.character_action]
  subst χ
  exact equivalence ρ v hv b r a hr hmono

/-- The transitive criterion accepts the actual scalar action on the base line. -/
def transitiveEquivalenceOfSubgroupAction
    (ρ : Representation ℂ G V) (b : Basis X ℂ V)
    (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) (x₀ : X)
    (htrans : ∀ x : X, ∃ g : G, p g x₀ = x)
    (S : Subgroup G) (χ : S →* ℂˣ)
    (hS : ∀ g : G, g ∈ S ↔ p g x₀ = x₀)
    (hχ : ∀ s : S, ρ (s : G) (b x₀) = (χ s : ℂ) • b x₀) :
    Representation.Equiv (Representation.ind S.subtype (scalarRepresentation χ)) ρ := by
  apply equivalenceOfSubgroup ρ (b x₀) (b.ne_zero x₀) b
    (representative p x₀ htrans) (fun x => c (representative p x₀ htrans x) x₀)
    (representative_action ρ b p c hρ x₀ htrans)
    (orbit_is_monomial ρ b p c hρ x₀) S χ
  · ext g
    rw [hS, mem_lineStabilizer_iff ρ b p c hρ x₀]
  · exact hχ

/-- The transitive monomial criterion with an independently specified subgroup
and character.  Subgroup equality is proved from its point-stabilizer formula. -/
def transitiveEquivalenceOfSubgroup
    (ρ : Representation ℂ G V) (b : Basis X ℂ V)
    (p : G →* Equiv.Perm X) (c : G → X → ℂˣ)
    (hρ : ∀ g x, ρ g (b x) = (c g x : ℂ) • b (p g x)) (x₀ : X)
    (htrans : ∀ x : X, ∃ g : G, p g x₀ = x)
    (S : Subgroup G) (χ : S →* ℂˣ)
    (hS : ∀ g : G, g ∈ S ↔ p g x₀ = x₀)
    (hχ : ∀ s : S, (χ s : ℂ) = c (s : G) x₀) :
    Representation.Equiv (Representation.ind S.subtype (scalarRepresentation χ)) ρ := by
  apply equivalenceOfSubgroup ρ (b x₀) (b.ne_zero x₀) b
    (representative p x₀ htrans) (fun x => c (representative p x₀ htrans x) x₀)
    (representative_action ρ b p c hρ x₀ htrans)
    (orbit_is_monomial ρ b p c hρ x₀) S χ
  · ext g
    rw [hS, mem_lineStabilizer_iff ρ b p c hρ x₀]
  · intro s
    have hs := (hS (s : G)).mp s.property
    rw [hρ, hs, hχ]

end PaperXI.MonomialInduction
