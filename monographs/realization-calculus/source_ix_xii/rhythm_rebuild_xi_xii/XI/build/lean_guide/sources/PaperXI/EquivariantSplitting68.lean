import PaperXI.SmoothHomOrbit68
import PaperXI.FiniteOrbitAverage68

/-! A compact-mod-scalar equivariant splitting, constructed by a finite orbit sum. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.EquivariantSplitting68

open Representation PaperXI.SmoothDegreeQuotient

variable {k G V W : Type*} [Field k] [CharZero k] [Group G]
  [TopologicalSpace G] [IsTopologicalGroup G]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]
  [FiniteDimensional k V]

/-- Every smooth surjective intertwiner onto a finite-dimensional source splits
equivariantly when a normal subgroup has compact quotient and acts by the same
scalars on both representations. Neither equivariant splitting nor orbit
finiteness is a premise. -/
theorem exists_equivariant_section
    (N : Subgroup G) [N.Normal] [CompactSpace (G ⧸ N)] (χ : N →* kˣ)
    (ρ : Representation k G V) (τ : Representation k G W)
    (hρ : IsSmooth ρ) (hτ : IsSmooth τ)
    (hcρ : ∀ z : N, ∀ v, ρ (z : G) v = (χ z : k) • v)
    (hcτ : ∀ z : N, ∀ w, τ (z : G) w = (χ z : k) • w)
    (p : IntertwiningMap τ ρ) (hp : Function.Surjective p) :
    ∃ a : IntertwiningMap ρ τ, ∀ v, p (a v) = v := by
  obtain ⟨s, hs⟩ := p.toLinearMap.exists_rightInverse_of_surjective
    (LinearMap.range_eq_top.mpr hp)
  apply FiniteOrbitAverage68.equivariant_section_of_finite_orbit ρ τ p s
  · intro v
    exact LinearMap.congr_fun hs v
  · exact SmoothHomOrbit68.linHom_orbit_finite N χ ρ τ hρ hτ hcρ hcτ s

end PaperXI.EquivariantSplitting68
