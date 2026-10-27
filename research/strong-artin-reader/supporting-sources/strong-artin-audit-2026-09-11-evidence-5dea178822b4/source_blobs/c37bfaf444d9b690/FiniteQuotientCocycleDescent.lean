import FiniteGroupCocycleAveraging

namespace Komorebi.StrongArtin.FiniteQuotientCocycleDescent

open Komorebi.StrongArtin.FiniteGroupCocycleAveraging

noncomputable section

variable {k G Γ V : Type*}
  [Field k] [Group G] [Group Γ] [Fintype Γ]
  [AddCommGroup V] [Module k V]

omit [Fintype Γ] in
/-- If a cocycle vanishes on the kernel of a quotient map, then its value
is determined by the image in the quotient. -/
theorem cocycle_eq_of_quotient_eq
    (ρG : Representation k G V)
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (q : G →* Γ)
    (hker : ∀ g : G, q g = 1 → f g = 0)
    {g h : G} (hqh : q g = q h) :
    f g = f h := by
  have hk : q (g⁻¹ * h) = 1 := by
    simp [hqh]
  have hc := hf g (g⁻¹ * h)
  have hmul : g * (g⁻¹ * h) = h := by
    simp [← mul_assoc]
  have hc' : f h = f g := by
    simpa [hmul, hker (g⁻¹ * h) hk] using hc
  exact hc'.symm

/-- **Finite-quotient cocycle descent.** Let the action of `G` factor through a
surjective finite quotient `Γ`. If a one-cocycle vanishes on the kernel, then it
descends to `Γ`; if `|Γ|` is invertible in the coefficient field, averaging on
`Γ` makes the cocycle a coboundary upstairs. -/
theorem cocycle_coboundary_of_vanishes_on_kernel
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ) (hq : Function.Surjective q)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (hker : ∀ g : G, q g = 1 → f g = 0)
    (hcard : (Fintype.card Γ : k) ≠ 0) :
    IsRepresentationCoboundary ρG f := by
  let s : Γ → G := Function.surjInv hq
  have hs : Function.RightInverse s q := Function.rightInverse_surjInv hq
  let φ : Γ → V := fun a => f (s a)
  have hφ : IsRepresentationCocycle ρΓ φ := by
    intro a b
    have hab : q (s (a * b)) = q (s a * s b) := by
      rw [map_mul, hs (a * b), hs a, hs b]
    calc
      φ (a * b) = f (s (a * b)) := rfl
      _ = f (s a * s b) :=
        cocycle_eq_of_quotient_eq ρG f hf q hker hab
      _ = f (s a) + ρG (s a) (f (s b)) := hf (s a) (s b)
      _ = φ a + ρΓ a (φ b) := by
        change f (s a) + ρG (s a) (f (s b)) =
          f (s a) + ρΓ a (f (s b))
        rw [haction (s a), hs a]
  obtain ⟨x, hx⟩ := cocycle_is_coboundary ρΓ φ hφ hcard
  refine ⟨x, ?_⟩
  intro g
  have hqsg : q (s (q g)) = q g := hs (q g)
  calc
    f g = f (s (q g)) :=
      cocycle_eq_of_quotient_eq ρG f hf q hker hqsg.symm
    _ = φ (q g) := rfl
    _ = ρΓ (q g) x - x := hx (q g)
    _ = ρG g x - x := by rw [haction]


/-- The principal one-cocycle attached to a coefficient vector. -/
def principalCocycle (ρ : Representation k G V) (x : V) : G → V :=
  fun g => ρ g x - x

omit [Fintype Γ] in
/-- Principal cocycles satisfy the cocycle equation. -/
theorem principalCocycle_is_cocycle
    (ρ : Representation k G V) (x : V) :
    IsRepresentationCocycle ρ (principalCocycle ρ x) := by
  intro g h
  change ρ (g * h) x - x =
    (ρ g x - x) + ρ g (ρ h x - x)
  rw [map_mul, Module.End.mul_apply, map_sub]
  abel

omit [Fintype Γ] in
/-- The pointwise difference of two one-cocycles is a one-cocycle. -/
theorem sub_cocycle
    (ρ : Representation k G V)
    (f₁ f₂ : G → V)
    (h₁ : IsRepresentationCocycle ρ f₁)
    (h₂ : IsRepresentationCocycle ρ f₂) :
    IsRepresentationCocycle ρ (fun g => f₁ g - f₂ g) := by
  intro g h
  change f₁ (g * h) - f₂ (g * h) =
    (f₁ g - f₂ g) + ρ g (f₁ h - f₂ h)
  rw [h₁ g h, h₂ g h, map_sub]
  abel

/-- **Restriction-injectivity at the cocycle level.** Let the action of `G`
factor through a finite quotient `Γ` of order invertible in the coefficient
field. If the restriction of a one-cocycle to the kernel of `q` is a
coboundary, then the original cocycle is a coboundary.

This is a direct cocycle-level proof of the low-degree
inflation--restriction injectivity needed in the clean Strong Artin route. -/
theorem cocycle_coboundary_of_kernel_restriction_coboundary
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ) (hq : Function.Surjective q)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (hres : ∃ x : V, ∀ g : G, q g = 1 →
      f g = principalCocycle ρG x g)
    (hcard : (Fintype.card Γ : k) ≠ 0) :
    IsRepresentationCoboundary ρG f := by
  obtain ⟨x, hx⟩ := hres
  let f₀ : G → V := fun g => f g - principalCocycle ρG x g
  have hf₀ : IsRepresentationCocycle ρG f₀ := by
    exact sub_cocycle ρG f (principalCocycle ρG x) hf
      (principalCocycle_is_cocycle ρG x)
  have hker₀ : ∀ g : G, q g = 1 → f₀ g = 0 := by
    intro g hg
    change f g - principalCocycle ρG x g = 0
    rw [hx g hg]
    abel
  obtain ⟨y, hy⟩ :=
    cocycle_coboundary_of_vanishes_on_kernel
      ρG ρΓ q hq haction f₀ hf₀ hker₀ hcard
  refine ⟨x + y, ?_⟩
  intro g
  have h := hy g
  change f g - (ρG g x - x) = ρG g y - y at h
  calc
    f g = (f g - (ρG g x - x)) + (ρG g x - x) := by abel
    _ = (ρG g y - y) + (ρG g x - x) := by rw [h]
    _ = ρG g (x + y) - (x + y) := by
      rw [map_add]
      abel


/-- Contrapositive cohomological form: a nontrivial cocycle class remains
nontrivial after restriction to the quotient kernel. -/
theorem nontrivial_class_restricts_nontrivially
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ) (hq : Function.Surjective q)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρG f) :
    ¬ ∃ x : V, ∀ g : G, q g = 1 →
      f g = principalCocycle ρG x g := by
  intro hres
  exact hnontrivial
    (cocycle_coboundary_of_kernel_restriction_coboundary
      ρG ρΓ q hq haction f hf hres hcard)

/-- **Operational residual-kernel survival.** Under the same hypotheses, a
nontrivial cocycle class has an actual nonzero value at some element of the
kernel of the residual finite quotient. -/
theorem exists_nonzero_value_in_quotient_kernel
    (ρG : Representation k G V)
    (ρΓ : Representation k Γ V)
    (q : G →* Γ) (hq : Function.Surjective q)
    (haction : ∀ g : G, ρG g = ρΓ (q g))
    (f : G → V) (hf : IsRepresentationCocycle ρG f)
    (hcard : (Fintype.card Γ : k) ≠ 0)
    (hnontrivial : ¬ IsRepresentationCoboundary ρG f) :
    ∃ sigma : G, q sigma = 1 ∧ f sigma ≠ 0 := by
  by_contra hnone
  have hker : ∀ g : G, q g = 1 → f g = 0 := by
    intro g hg
    by_contra hfg
    exact hnone ⟨g, hg, hfg⟩
  exact hnontrivial
    (cocycle_coboundary_of_vanishes_on_kernel
      ρG ρΓ q hq haction f hf hker hcard)

end

end Komorebi.StrongArtin.FiniteQuotientCocycleDescent
