import H1RestrictionInjective
import PreChebotarevSelector

namespace Komorebi.StrongArtin.CyclotomicDepthSurvival

open Komorebi.StrongArtin.H1RestrictionInjective
open Komorebi.StrongArtin.PreChebotarevSelector

noncomputable section

universe u w

variable {k G : Type u} [Field k] [Group G]

/-- If `n` acts trivially on the coefficient representation, a one-cocycle is
equivariant under conjugation of `n`. -/
theorem cocycle_conjugate_of_action_eq_one
    (A : Rep.{w} k G)
    (f : groupCohomology.cocycles₁ A)
    (g n : G)
    (hn : A.ρ n = 1) :
    f (g * n * g⁻¹) = A.ρ g (f n) := by
  rw [mul_assoc]
  rw [(groupCohomology.mem_cocycles₁_iff f).1 f.2 g (n * g⁻¹)]
  rw [(groupCohomology.mem_cocycles₁_iff f).1 f.2 n g⁻¹]
  rw [hn]
  simp only [Module.End.one_apply, map_add]
  rw [groupCohomology.cocycles₁_map_inv]
  abel

/-- **Central-quotient survival for cocycle values.** Let `T ≤ S ≤ G`. Assume
`S` acts trivially on the coefficient module, conjugation by `G` is trivial on
`S/T`, and the coefficient representation has no nonzero `G`-fixed vector.
Then a one-cocycle which is nonzero somewhere on `S` must already be nonzero
somewhere on `T`.

This is the abstract group-theoretic core of survival down a deeper cyclotomic
subgroup: if the cocycle vanished on `T`, its values on `S` would factor through
a quotient with trivial conjugation action and hence would be fixed vectors. -/
theorem exists_deeper_nonzero_value_of_central_quotient
    (A : Rep.{w} k G)
    (f : groupCohomology.cocycles₁ A)
    (S T : Subgroup G)
    (hTS : T ≤ S)
    (hSact : ∀ s : S, A.ρ s = 1)
    (hcentral : ∀ g : G, ∀ s : S,
      g * (s : G) * g⁻¹ * (s : G)⁻¹ ∈ T)
    (hfixed : ∀ x : A, (∀ g : G, A.ρ g x = x) → x = 0)
    (hnonzero : ∃ s : S, f s ≠ 0) :
    ∃ t : T, f t ≠ 0 := by
  obtain ⟨s, hs⟩ := hnonzero
  by_contra h
  push Not at h
  have hfs_fixed : ∀ g : G, A.ρ g (f s) = f s := by
    intro g
    let t : T :=
      ⟨g * (s : G) * g⁻¹ * (s : G)⁻¹, hcentral g s⟩
    let ts : S := ⟨(t : G), hTS t.property⟩
    have hrel : (t : G) * (s : G) = g * (s : G) * g⁻¹ := by
      dsimp [t]
      simp [mul_assoc]
    have hconj : f (g * (s : G) * g⁻¹) = A.ρ g (f s) :=
      cocycle_conjugate_of_action_eq_one A f g s (hSact s)
    have hprod : f ((t : G) * (s : G)) = f t + f s :=
      cocycle_mul_of_action_eq_one A f t s (hSact ts)
    rw [← hconj, ← hrel, hprod, h t, zero_add]
  exact hs (hfixed (f s) hfs_fixed)


/-- Combine prime-to-characteristic restriction injectivity with central-quotient
survival. A nonzero `H¹` class has a representative value nonzero on `S`, and
under the central quotient/no-fixed-vector hypotheses that value survives on
`T`. -/
theorem exists_deeper_nonzero_value_from_nonzero_H1
    (A : Rep.{u} k G)
    (f : groupCohomology.cocycles₁ A)
    (S T : Subgroup G) [S.Normal]
    [Fintype (G ⧸ S)]
    (hcard : (Fintype.card (G ⧸ S) : k) ≠ 0)
    (hclass : groupCohomology.H1π A f ≠ 0)
    (hTS : T ≤ S)
    (hSact : ∀ s : S, A.ρ s = 1)
    (hcentral : ∀ g : G, ∀ s : S,
      g * (s : G) * g⁻¹ * (s : G)⁻¹ ∈ T)
    (hfixed : ∀ x : A, (∀ g : G, A.ρ g x = x) → x = 0) :
    ∃ t : T, f t ≠ 0 := by
  have hnonzero : ∃ s : S, f s ≠ 0 :=
    exists_subgroup_element_with_nonzero_cocycle_value
      A S hcard f hclass
  exact exists_deeper_nonzero_value_of_central_quotient
    A f S T hTS hSact hcentral hfixed hnonzero


end
end Komorebi.StrongArtin.CyclotomicDepthSurvival

#print axioms Komorebi.StrongArtin.CyclotomicDepthSurvival.cocycle_conjugate_of_action_eq_one
#print axioms Komorebi.StrongArtin.CyclotomicDepthSurvival.exists_deeper_nonzero_value_of_central_quotient
#print axioms Komorebi.StrongArtin.CyclotomicDepthSurvival.exists_deeper_nonzero_value_from_nonzero_H1
