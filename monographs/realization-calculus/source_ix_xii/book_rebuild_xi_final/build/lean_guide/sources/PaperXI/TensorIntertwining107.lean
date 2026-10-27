import PaperXI.TensorSlices107
import PaperXI.IntertwiningAlong105

/-! The operator argument underlying BK 5.3.2. The arithmetic support and
one-dimensional Heisenberg-intertwining results are kept as explicit inputs. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorIntertwining107
open Representation IntertwiningAlong105 TensorSlices107
open scoped TensorProduct
variable {k K G Q W U : Type*} [Field k] [Group K] [Group G] [Group Q]
  [AddCommGroup W] [Module k W] [AddCommGroup U] [Module k U]
  (ι : K →* G) (N : Subgroup K) (q : K →* Q) (hN : N ≤ q.ker)
  (κ : Representation k K W) (σ : Representation k Q U)

include hN

/-- Every coefficient of a tensor intertwiner intertwines the actual restricted
first-factor action; the quotient factor is trivial on the subgroup. -/
theorem slice_along (g : G) (T : W ⊗[k] U →ₗ[k] W ⊗[k] U)
    (hT : Along ι (κ.tprod (σ.comp q)) g T) (u : U) (φ : Module.Dual k U) :
    Along (ι.comp N.subtype) (κ.comp N.subtype) g (slice T u φ) := by
  intro x y hxy w
  have hx : q x = 1 := hN x.property
  have hy : q y = 1 := hN y.property
  have h := hT x y hxy (w ⊗ₜ[k] u)
  change T (TensorProduct.map (κ x) (σ (q x)) (w ⊗ₜ[k] u)) =
    TensorProduct.map (κ y) (σ (q y)) (T (w ⊗ₜ[k] u)) at h
  rw [hx, hy, map_one] at h
  change T (κ x w ⊗ₜ[k] u) =
    TensorProduct.map (κ y) LinearMap.id (T (w ⊗ₜ[k] u)) at h
  change right φ (T (κ x w ⊗ₜ[k] u)) = κ y (right φ (T (w ⊗ₜ[k] u)))
  rw [← right_map]
  exact congrArg (right φ) h

theorem restrict_support (g : G) (h : ExistsAt ι (κ.tprod (σ.comp q)) g) :
    ExistsAt (ι.comp N.subtype) (κ.comp N.subtype) g := by
  obtain ⟨T, hT, ht⟩ := h
  obtain ⟨u, φ, hn⟩ := exists_nonzero_slice T hT
  exact ⟨slice T u φ, hn, slice_along ι N q hN κ σ g T ht u φ⟩

omit N hN in
/-- Cancel a nonzero first-factor intertwiner using a separating functional,
without assuming the intertwiner is invertible. -/
theorem second_along (g : G) (S : W →ₗ[k] W) (hS : S ≠ 0)
    (hs : Along ι κ g S) (R : U →ₗ[k] U)
    (hT : Along ι (κ.tprod (σ.comp q)) g (TensorProduct.map S R)) :
    Along ι (σ.comp q) g R := by
  obtain ⟨w₀, hw₀⟩ : ∃ w₀, S w₀ ≠ 0 := by
    by_contra h
    push Not at h
    exact hS (LinearMap.ext h)
  intro x y hxy u
  apply tmul_left_injective (k := k) (S w₀) hw₀
  have h := hT x y hxy (κ x⁻¹ w₀ ⊗ₜ[k] u)
  have he := hs x y hxy (κ x⁻¹ w₀)
  simp only [act_mul_inv_cancel] at he
  simpa only [Representation.tprod_apply, MonoidHom.comp_apply,
    TensorProduct.map_tmul, act_mul_inv_cancel, ← he] using h

omit N hN in
theorem map_along (g : G) (S : W →ₗ[k] W) (hs : Along ι κ g S)
    (R : U →ₗ[k] U) (hr : Along ι (σ.comp q) g R) :
    Along ι (κ.tprod (σ.comp q)) g (TensorProduct.map S R) := by
  intro x y hxy t
  induction t using TensorProduct.induction_on with
  | zero => simp
  | add a b ha hb => simp only [map_add, ha, hb]
  | tmul w u =>
    simpa only [Representation.tprod_apply, TensorProduct.map_tmul,
      MonoidHom.comp_apply] using congrArg₂ (TensorProduct.tmul k)
        (hs x y hxy w) (hr x y hxy u)

/-- An exact factorization of every tensor intertwiner, given the restricted
Heisenberg intertwining line and its extension to the full first factor. -/
theorem factor_along (g : G) (S : W →ₗ[k] W) (hS : S ≠ 0)
    (hs : Along ι κ g S)
    (hline : ∀ A : W →ₗ[k] W,
      Along (ι.comp N.subtype) (κ.comp N.subtype) g A → ∃ c : k, A = c • S)
    (T : W ⊗[k] U →ₗ[k] W ⊗[k] U)
    (hT : Along ι (κ.tprod (σ.comp q)) g T) :
    ∃ R : U →ₗ[k] U, T = TensorProduct.map S R ∧ Along ι (σ.comp q) g R := by
  obtain ⟨R, hr⟩ := factor_of_slice_line T S hS (fun u φ =>
    hline _ (slice_along ι N q hN κ σ g T hT u φ))
  exact ⟨R, hr, second_along ι q κ σ g S hS hs R (hr ▸ hT)⟩

/-- Both directions of tensor-to-residue intertwining at a fixed element. -/
theorem existsAt_iff (g : G) (S : W →ₗ[k] W) (hS : S ≠ 0)
    (hs : Along ι κ g S)
    (hline : ∀ A : W →ₗ[k] W,
      Along (ι.comp N.subtype) (κ.comp N.subtype) g A → ∃ c : k, A = c • S) :
    ExistsAt ι (κ.tprod (σ.comp q)) g ↔ ExistsAt ι (σ.comp q) g := by
  constructor
  · rintro ⟨T, hT, ht⟩
    obtain ⟨R, rfl, hr⟩ := factor_along ι N q hN κ σ g S hS hs hline T ht
    refine ⟨R, ?_, hr⟩
    intro hR
    exact hT (by simp [hR])
  · rintro ⟨R, hR, hr⟩
    refine ⟨TensorProduct.map S R, ?_, map_along ι q κ σ g S hs R hr⟩
    intro h
    apply hR
    apply map_left_injective S hS
    simpa using h

end PaperXI.TensorIntertwining107
