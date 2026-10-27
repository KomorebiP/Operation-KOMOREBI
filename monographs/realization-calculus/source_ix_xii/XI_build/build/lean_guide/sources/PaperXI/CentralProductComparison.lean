import PaperXI.CentralProductFactors
import Mathlib.GroupTheory.NoncommPiCoprod
import Mathlib.GroupTheory.NoncommCoprod

/-! Actual compatible factor embeddings construct the comparison with a declared
full central extension. The desired group isomorphism is derived from exactness. -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace PaperXI.CentralProductComparison

variable {S Z G : Type*} [Fintype S] [DecidableEq S] [CommGroup Z] [Group G]
variable {H A : S → Type*} [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
variable (E : CentralExtension.Datum Z G (∀ s, A s))
variable (j : ∀ s, H s →* G)
variable (hc : Pairwise fun s t => ∀ h k, Commute (j s h) (j t k))
variable (hi : ∀ s z, j s ((D s).i z) = E.i z)
variable (hq : ∀ s h, E.q (j s h) = Pi.mulSingle s ((D s).q h))

/-- The finite commuting product of the actual factor images. -/
def factors : (∀ s, H s) →* G := MonoidHom.noncommPiCoprod j hc

@[simp] theorem factors_single (s : S) (h : H s) :
    factors j hc (Pi.mulSingle s h) = j s h :=
  MonoidHom.noncommPiCoprod_mulSingle j s h

include hq in
/-- Coordinate projection of the actual factor product is the prescribed tuple. -/
theorem factors_projection (h : ∀ s, H s) :
    E.q (factors j hc h) = fun s => (D s).q (h s) := by
  have he : E.q.comp (factors j hc) = MonoidHom.pi (fun s => (D s).q.comp
      (Pi.evalMonoidHom H s)) := by
    apply MonoidHom.pi_ext
    intro s x
    change E.q (factors j hc (Pi.mulSingle s x)) = fun t => (D t).q (Pi.mulSingle s x t)
    rw [factors_single, hq]
    ext t
    by_cases ht : t = s
    · subst t; simp
    · simp [Pi.mulSingle_eq_of_ne ht]
  exact DFunLike.congr_fun he h

/-- Product of the central coordinates as a homomorphism. -/
def centerProduct : (S → Z) →* Z where
  toFun z := ∏ s, z s
  map_one' := by simp
  map_mul' x y := by simp [Finset.prod_mul_distrib]

include hi in
/-- The factor centers multiply in the single declared total center. -/
theorem factors_centers (z : S → Z) :
    factors j hc (fun s => (D s).i (z s)) = E.i (∏ s, z s) := by
  have he : (factors j hc).comp (MonoidHom.pi (fun s => (D s).i.comp
      (Pi.evalMonoidHom (fun _ : S => Z) s))) = E.i.comp (centerProduct (S := S)) := by
    apply MonoidHom.pi_ext
    intro s x
    have ht : (fun t => (D t).i (Pi.mulSingle (M := fun _ : S => Z) s x t)) =
        Pi.mulSingle s ((D s).i x) := by
      funext t
      by_cases hts : t = s
      · subst t; simp
      · simp [Pi.mulSingle_eq_of_ne hts]
    change factors j hc (fun t => (D t).i (Pi.mulSingle (M := fun _ : S => Z) s x t)) =
      E.i (centerProduct (Pi.mulSingle s x))
    rw [ht, factors_single, hi]
    congr 1
    simp [centerProduct]
  exact DFunLike.congr_fun he z

/-- Actual ambient map, retaining the center also in the empty family. -/
def ambient : CentralProduct.Ambient (Z := Z) (H := H) →* G :=
  E.i.noncommCoprod (factors j hc) (fun z h => E.central z (factors j hc h))

omit [DecidableEq S] in
@[simp] theorem ambient_apply (z : Z) (h : ∀ s, H s) :
    ambient E j hc (z,h) = E.i z * factors j hc h := rfl

include hi in
/-- The balancing relations vanish, by compatibility of the actual central inclusions. -/
theorem ambient_balanced (z : S → Z) :
    ambient E j hc (CentralProduct.balanced D z) = 1 := by
  change E.i ((∏ s, z s)⁻¹) * factors j hc (fun s => (D s).i (z s)) = 1
  rw [factors_centers D E j hc hi, ← map_mul, inv_mul_cancel, map_one]

/-- The comparison descends through the actual quotient. -/
def comparison : CentralProduct.Group D →* G :=
  CentralProduct.descend D (ambient E j hc) (ambient_balanced D E j hc hi)

@[simp] theorem comparison_mk (z : Z) (h : ∀ s, H s) :
    comparison D E j hc hi (CentralProduct.mk D (z,h)) = E.i z * factors j hc h := rfl

@[simp] theorem comparison_center (z : Z) :
    comparison D E j hc hi (CentralProduct.center D z) = E.i z := by
  simp [CentralProduct.center_apply]

include hq in
/-- The comparison induces the identity on the actual quotient coordinates. -/
theorem comparison_projection (x : CentralProduct.Group D) :
    E.q (comparison D E j hc hi x) = CentralProduct.projection D x := by
  obtain ⟨⟨z,h⟩, rfl⟩ := CentralProduct.mk_surjective D x
  simp only [comparison_mk, map_mul, CentralExtension.q_i, one_mul,
    CentralProduct.projection_mk]
  exact factors_projection D E j hc hq h

include hq in
/-- Exactness on both sides proves injectivity, without a dimension surrogate. -/
theorem comparison_injective : Function.Injective (comparison D E j hc hi) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  rw [Subgroup.eq_bot_iff_forall]
  intro x hx
  change comparison D E j hc hi x = 1 at hx
  have hxq : CentralProduct.projection D x = 1 := by
    rw [← comparison_projection D E j hc hi hq, hx, map_one]
  have hm : x ∈ (CentralProduct.center D).range := by
    rw [CentralProduct.range_center_eq_ker_projection]
    exact hxq
  obtain ⟨z, rfl⟩ := hm
  have hz : z = 1 := by
    apply E.i_injective
    simpa only [comparison_center, map_one] using hx
  rw [hz, map_one]

include hq in
/-- Surjectivity follows by matching quotient coordinates and correcting the central difference. -/
theorem comparison_surjective : Function.Surjective (comparison D E j hc hi) := by
  intro g
  obtain ⟨x, hx⟩ := CentralProduct.projection_surjective D (E.q g)
  have hk : g * (comparison D E j hc hi x)⁻¹ ∈ E.q.ker := by
    change E.q (g * (comparison D E j hc hi x)⁻¹) = 1
    rw [map_mul, map_inv, comparison_projection D E j hc hi hq, hx, mul_inv_cancel]
  rw [← E.range_i_eq_ker_q] at hk
  obtain ⟨z, hz⟩ := hk
  refine ⟨CentralProduct.center D z * x, ?_⟩
  rw [map_mul, comparison_center, hz, inv_mul_cancel_right]

/-- Actual full-envelope group comparison from compatible factor embeddings. -/
def equiv : CentralProduct.Group D ≃* G :=
  MulEquiv.ofBijective (comparison D E j hc hi)
    ⟨comparison_injective D E j hc hi hq, comparison_surjective D E j hc hi hq⟩

@[simp] theorem equiv_center (z : Z) :
    equiv D E j hc hi hq (CentralProduct.center D z) = E.i z :=
  comparison_center D E j hc hi z

@[simp] theorem equiv_mk (z : Z) (h : ∀ s, H s) :
    equiv D E j hc hi hq (CentralProduct.mk D (z,h)) = E.i z * factors j hc h := rfl

end PaperXI.CentralProductComparison
