import PaperXI.CompactSmoothSemisimple

/-!
# Finite orbits on actual linear-map spaces modulo a scalar subgroup

The subgroup and quotient are literal.  Compactness is imposed on G / N, not
on G.  Finiteness of the Hom orbit is derived from smoothness and equal scalar
actions, rather than supplied as a splitting certificate.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SmoothHomOrbit68

open Representation PaperXI.SmoothDegreeQuotient

variable {k G V W : Type*} [Field k] [Group G]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]
  [TopologicalSpace G] [IsTopologicalGroup G]

/-- A finite-dimensional smooth source makes the actual Hom action smooth,
even when its target is infinite dimensional. -/
theorem linHom_smooth [FiniteDimensional k V]
    (ρ : Representation k G V) (τ : Representation k G W)
    (hρ : IsSmooth ρ) (hτ : IsSmooth τ) : IsSmooth (linHom ρ τ) := by
  intro f
  let b := Module.finBasis k V
  let S : Subgroup G := ρ.ker ⊓ ⨅ i, vectorStabilizer τ (f (b i))
  have hopen : IsOpen (S : Set G) := by
    have he : (S : Set G) = (ρ.ker : Set G) ∩ ⋂ i, (vectorStabilizer τ (f (b i)) : Set G) := by
      ext g
      simp only [S, Subgroup.mem_inf, Subgroup.mem_iInf, Set.mem_inter_iff, Set.mem_iInter, SetLike.mem_coe]
    rw [he]
    exact (isOpen_kernel_of_smooth ρ hρ).inter
      (isOpen_iInter_of_finite fun i => hτ (f (b i)))
  apply Subgroup.isOpen_mono (H₁ := S) (H₂ := vectorStabilizer (linHom ρ τ) f) _ hopen
  intro g hg
  change linHom ρ τ g f = f
  apply b.ext
  intro i
  have hinv : ρ g⁻¹ = 1 := ρ.ker.inv_mem hg.1
  change τ g (f (ρ g⁻¹ (b i))) = f (b i)
  rw [hinv, Module.End.one_apply]
  exact Subgroup.mem_iInf.mp hg.2 i

omit [IsTopologicalGroup G] in
/-- Smoothness descends through the actual topological quotient when the
normal subgroup acts trivially. -/
theorem descend_smooth (N : Subgroup G) [N.Normal]
    (ρ : Representation k G V) (hN : N ≤ ρ.ker) (hρ : IsSmooth ρ) :
    IsSmooth (QuotientRepresentation.descend N ρ hN) := by
  intro v
  apply (QuotientGroup.isQuotientMap_mk N).isOpen_preimage.mp
  exact hρ v

/-- A smooth action with compact effective quotient has finite vector orbits. -/
theorem orbit_finite_of_compact_quotient (N : Subgroup G) [N.Normal]
    [CompactSpace (G ⧸ N)] (ρ : Representation k G V)
    (hN : N ≤ ρ.ker) (hρ : IsSmooth ρ) (v : V) :
    Set.Finite (Set.range fun g => ρ g v) := by
  have h := CompactSmoothSemisimple.orbit_finite
    (QuotientRepresentation.descend N ρ hN) (descend_smooth N ρ hN hρ) v
  apply h.subset
  rintro w ⟨g, rfl⟩
  exact ⟨QuotientGroup.mk' N g, rfl⟩

omit [TopologicalSpace G] [IsTopologicalGroup G] in
/-- Equal scalar actions cancel on Hom.  No unitarity or finite scalar image
is required. -/
theorem scalar_subgroup_le_linHom_kernel (N : Subgroup G)
    (χ : N →* kˣ) (ρ : Representation k G V) (τ : Representation k G W)
    (hρ : ∀ z : N, ∀ v, ρ (z : G) v = (χ z : k) • v)
    (hτ : ∀ z : N, ∀ w, τ (z : G) w = (χ z : k) • w) :
    N ≤ (linHom ρ τ).ker := by
  intro g hg
  change linHom ρ τ g = 1
  ext f v
  let z : N := ⟨g, hg⟩
  change τ (z : G) (f (ρ ((z⁻¹ : N) : G) v)) = f v
  rw [hρ, map_smul, map_smul, hτ, smul_smul]
  simp

/-- Every actual linear map between these representations has a finite orbit.
This is the compact-mod-scalar input needed for averaging a splitting. -/
theorem linHom_orbit_finite [FiniteDimensional k V]
    (N : Subgroup G) [N.Normal] [CompactSpace (G ⧸ N)]
    (χ : N →* kˣ) (ρ : Representation k G V) (τ : Representation k G W)
    (hρ : IsSmooth ρ) (hτ : IsSmooth τ)
    (hcρ : ∀ z : N, ∀ v, ρ (z : G) v = (χ z : k) • v)
    (hcτ : ∀ z : N, ∀ w, τ (z : G) w = (χ z : k) • w)
    (f : V →ₗ[k] W) : Set.Finite (Set.range fun g => linHom ρ τ g f) :=
  orbit_finite_of_compact_quotient N (linHom ρ τ)
    (scalar_subgroup_le_linHom_kernel N χ ρ τ hcρ hcτ)
    (linHom_smooth ρ τ hρ hτ) f

end PaperXI.SmoothHomOrbit68
