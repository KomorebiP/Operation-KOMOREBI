import PaperXI.TensorIntertwining107

/-! Assemble the operator proof and two-sided compact transport. The only
arithmetic inputs are support and line structure for the restricted first factor. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergReduction107
open Representation IntertwiningAlong105 TensorIntertwining107
open scoped TensorProduct
variable {k K G Q B L W U : Type*} [Field k] [Group K] [Group G] [Group Q]
  [Group B] [Group L] [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]

/-- Pull the second-factor intertwiner back to an actual embedded integral
subgroup of the centralizer, with both maps and actions checked literally. -/
theorem pullback (ι : K →* G) (b : B →* G) (a : L →* B) (j : L →* K)
    (hcompat : ∀ x, ι (j x) = b (a x))
    (ρ : Representation k K U) (τ : Representation k L U)
    (hρ : ∀ x, ρ (j x) = τ x) (y : B)
    (h : ExistsAt ι ρ (b y)) : ExistsAt a τ y := by
  obtain ⟨T, hn, ht⟩ := h
  refine ⟨T, hn, ?_⟩
  intro x z hxz u
  have he : ι (j z) = b y * ι (j x) * (b y)⁻¹ := by
    rw [hcompat, hcompat, hxz, map_mul, map_mul, map_inv]
  simpa only [hρ] using ht (j x) (j z) he u

theorem double_coset_reduction
    (ι : K →* G) (N : Subgroup K) (q : K →* Q) (hN : N ≤ q.ker)
    (κ : Representation k K W) (σ : Representation k Q U) (b : B →* G)
    (hsupport : ∀ g, ExistsAt (ι.comp N.subtype) (κ.comp N.subtype) g →
      ∃ j₁ j₂ : K, ∃ y : B, g = ι j₁ * b y * ι j₂)
    (hlines : ∀ y : B, ∃ S : W →ₗ[k] W, S ≠ 0 ∧ Along ι κ (b y) S ∧
      ∀ A : W →ₗ[k] W,
        Along (ι.comp N.subtype) (κ.comp N.subtype) (b y) A → ∃ c : k, A = c • S)
    (g : G) (hg : ExistsAt ι (κ.tprod (σ.comp q)) g) :
    ∃ j₁ j₂ : K, ∃ y : B, g = ι j₁ * b y * ι j₂ ∧
      ExistsAt ι (σ.comp q) (b y) := by
  obtain ⟨j₁, j₂, y, he⟩ := hsupport g (restrict_support ι N q hN κ σ g hg)
  have ht := existsAt_of_left_right ι (κ.tprod (σ.comp q)) j₁ j₂ (b y) (he ▸ hg)
  obtain ⟨S, hn, hs, hl⟩ := hlines y
  exact ⟨j₁, j₂, y, he, (existsAt_iff ι N q hN κ σ (b y) S hn hs hl).mp ht⟩

theorem integral_reduction
    (ι : K →* G) (N : Subgroup K) (q : K →* Q) (hN : N ≤ q.ker)
    (κ : Representation k K W) (σ : Representation k Q U)
    (b : B →* G) (a : L →* B) (j : L →* K) (r : L →* Q)
    (hcompat : ∀ x, ι (j x) = b (a x)) (hred : ∀ x, q (j x) = r x)
    (hsupport : ∀ g, ExistsAt (ι.comp N.subtype) (κ.comp N.subtype) g →
      ∃ j₁ j₂ : K, ∃ y : B, g = ι j₁ * b y * ι j₂)
    (hlines : ∀ y : B, ∃ S : W →ₗ[k] W, S ≠ 0 ∧ Along ι κ (b y) S ∧
      ∀ A : W →ₗ[k] W,
        Along (ι.comp N.subtype) (κ.comp N.subtype) (b y) A → ∃ c : k, A = c • S)
    (g : G) (hg : ExistsAt ι (κ.tprod (σ.comp q)) g) :
    ∃ j₁ j₂ : K, ∃ y : B, g = ι j₁ * b y * ι j₂ ∧ ExistsAt a (σ.comp r) y := by
  obtain ⟨j₁, j₂, y, he, hy⟩ := double_coset_reduction ι N q hN κ σ b hsupport hlines g hg
  refine ⟨j₁, j₂, y, he, pullback ι b a j hcompat (σ.comp q) (σ.comp r) ?_ y hy⟩
  intro x
  change σ (q (j x)) = σ (r x)
  rw [hred]

end PaperXI.HeisenbergReduction107
