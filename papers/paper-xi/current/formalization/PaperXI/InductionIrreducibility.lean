import PaperXI.OpenSubgroupSmoothInduction
import PaperXI.RepresentationStability
import PaperXI.SemisimpleProjection
import PaperXI.CompactSmoothSemisimple

/-!
# Irreducibility of actual subgroup induction from a local coefficient projector

All spaces and actions below are Mathlib's actual `IndV` and `ind`, at arbitrary
subgroup index.  The projection hypothesis is a local group-algebra condition:
each vector's identity-coset coefficient can be isolated by a finite linear
combination of subgroup operators.  The conclusion is actual irreducibility,
not scalar endomorphisms or an assumed simple subrepresentation lattice.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InductionIrreducibility

open Representation PaperXI.OpenSubgroupSmoothInduction
open PaperXI.RepresentationStability

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]
variable (H : Subgroup G) (σ : Representation k H V)

/-- The actual inducing space, placed on the identity right coset. -/
def identityInclusion : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype) where
  toLinearMap := IndV.mk H.subtype σ 1
  isIntertwining' h := by
    ext v
    change IndV.mk H.subtype σ 1 (σ h v) =
      ind H.subtype σ (h : G) (IndV.mk H.subtype σ 1 v)
    rw [ind_mk, one_mul, ← mk_subgroup]
    simp

/-- Translation in the actual induced representation translates coefficients. -/
theorem evaluate_translate (t x : G) (z : IndV H.subtype σ) :
    evaluate H σ x (ind H.subtype σ t z) = evaluate H σ (x * t) z := by
  have he := LinearMap.congr_fun ((functionIntertwiner H σ).isIntertwining' t) z
  exact congrArg (fun f : coindV H.subtype σ => f.val x) he

/-- Evaluation on the identity coset is a subgroup intertwiner. -/
def identityEvaluation : IntertwiningMap ((ind H.subtype σ).comp H.subtype) σ where
  toLinearMap := evaluate H σ 1
  isIntertwining' h := by
    apply LinearMap.ext
    intro z
    change evaluate H σ 1 (ind H.subtype σ (h : G) z) = σ h (evaluate H σ 1 z)
    rw [evaluate_translate, one_mul]
    change (functionModel H σ z).val (h : G) = σ h ((functionModel H σ z).val 1)
    exact (by simpa only [Subgroup.subtype_apply, mul_one] using
      (functionModel H σ z).property h 1)

@[simp] theorem identityEvaluation_inclusion (v : V) :
    identityEvaluation H σ (identityInclusion H σ v) = v := evaluate_mk_self H σ 1 v

/-- The identity-coset projection on actual induced vectors. -/
def identityProjection : Module.End k (IndV H.subtype σ) :=
  (identityInclusion H σ).toLinearMap ∘ₗ (identityEvaluation H σ).toLinearMap

/-- A nonzero vector has a nonzero coefficient, without any finite-index assumption. -/
theorem exists_nonzero_coefficient {z : IndV H.subtype σ} (hz : z ≠ 0) :
    ∃ x : G, evaluate H σ x z ≠ 0 := by
  by_contra h
  push Not at h
  apply hz
  apply functionModel_injective H σ
  apply Subtype.ext
  funext x
  exact h x

/-- Once a stable space contains the identity copy, translations generate all induction. -/
theorem eq_top_of_contains_identity (S : Submodule k (IndV H.subtype σ))
    (hS : Stable (ind H.subtype σ) S)
    (hi : ∀ v : V, identityInclusion H σ v ∈ S) : S = ⊤ := by
  have hq : S.mkQ = 0 := by
    apply IndV.hom_ext
    intro g
    ext v
    apply (Submodule.Quotient.mk_eq_zero S).mpr
    have hv := hS g⁻¹ (identityInclusion H σ v) (hi v)
    simpa only [identityInclusion, IntertwiningMap.coe_mk, ind_mk, inv_inv, one_mul] using hv
  apply top_unique
  intro z _
  exact (Submodule.Quotient.mk_eq_zero S).mp (LinearMap.congr_fun hq z)

/-- The coefficient projector, together with irreducibility of the inducing
action, proves irreducibility of genuine induction. -/
theorem irreducible_of_projection [IsIrreducible σ]
    (hP : ∀ S : Submodule k (IndV H.subtype σ), Stable (ind H.subtype σ) S →
      ∀ z ∈ S, identityProjection H σ z ∈ S) :
    IsIrreducible (ind H.subtype σ) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space σ
  let : Nontrivial (IndV H.subtype σ) := ind_nontrivial H σ
  apply irreducible_of_stable
  intro S hS
  by_cases hSb : S = ⊥
  · exact Or.inl hSb
  right
  obtain ⟨z, hzS, hz⟩ := S.ne_bot_iff.mp hSb
  obtain ⟨x, hx⟩ := exists_nonzero_coefficient H σ hz
  let T := S.comap (identityInclusion H σ).toLinearMap
  have hT : Stable σ T := by
    intro h v hv
    change identityInclusion H σ (σ h v) ∈ S
    have he := LinearMap.congr_fun ((identityInclusion H σ).isIntertwining' h) v
    change identityInclusion H σ (σ h v) =
      ind H.subtype σ (h : G) (identityInclusion H σ v) at he
    rw [he]
    exact hS (h : G) _ hv
  have hc : evaluate H σ x z ∈ T := by
    have hm := hP S hS (ind H.subtype σ x z) (hS x z hzS)
    change identityInclusion H σ (evaluate H σ 1 (ind H.subtype σ x z)) ∈ S at hm
    rw [evaluate_translate, one_mul] at hm
    exact hm
  have hTtop : T = ⊤ := by
    rcases RepresentationStability.eq_bot_or_top σ T hT with hb | ht
    · exact (hx (by simpa only [hb, Submodule.mem_bot] using hc)).elim
    · exact ht
  apply eq_top_of_contains_identity H σ S hS
  intro v
  change v ∈ T
  rw [hTtop]
  trivial

/-- A stable subspace is invariant under every finite group-algebra operator. -/
theorem algebra_action_mem {W : Type*} [AddCommGroup W] [Module k W]
    (τ : Representation k H W) (S : Submodule k W) (hS : Stable τ S)
    (a : MonoidAlgebra k H) {w : W} (hw : w ∈ S) : τ.asAlgebraHom a w ∈ S := by
  induction a using MonoidAlgebra.induction_on with
  | of h => simpa using hS h w hw
  | add a b ha hb => simpa using S.add_mem ha hb
  | smul c a ha => simpa using S.smul_mem c ha

/-- A concrete local criterion: a finite linear combination of subgroup
translations isolates the identity coefficient of each individual vector.
The combination may depend on the vector, as for compact smooth averaging. -/
theorem irreducible_of_local_groupAlgebra [IsIrreducible σ]
    (hlocal : ∀ z : IndV H.subtype σ, ∃ a : MonoidAlgebra k H,
      Representation.asAlgebraHom ((ind H.subtype σ).comp H.subtype) a z =
        identityProjection H σ z) :
    IsIrreducible (ind H.subtype σ) := by
  apply irreducible_of_projection H σ
  intro S hS z hz
  obtain ⟨a, ha⟩ := hlocal z
  rw [← ha]
  exact algebra_action_mem H ((ind H.subtype σ).comp H.subtype) S
    (fun h w hw => hS (h : G) w hw) a hz

/-- The subgroup `H ∩ g⁻¹Hg`, viewed inside `H`. -/
def intersectionSubgroup (g : G) : Subgroup H :=
  H.comap ((MulAut.conj g).toMonoidHom.comp H.subtype)

/-- Conjugation identifies this intersection with a subgroup of the inducing group. -/
def intersectionConjugation (g : G) : intersectionSubgroup H g →* H where
  toFun h := ⟨g * ((h : H) : G) * g⁻¹, h.property⟩
  map_one' := Subtype.ext (by simp)
  map_mul' a b := Subtype.ext (by simp)

/-- Every coefficient of an `H`-intertwiner is an intertwiner over the exact
intersection subgroup appearing in Mackey's criterion. -/
def coefficientIntertwiner (g : G)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype)) :
    IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
      (σ.comp (intersectionConjugation H g)) where
  toLinearMap := evaluate H σ g ∘ₗ f.toLinearMap
  isIntertwining' h := by
    apply LinearMap.ext
    intro v
    change evaluate H σ g (f (σ (h : H) v)) =
      σ (intersectionConjugation H g h) (evaluate H σ g (f v))
    rw [f.isIntertwining]
    change evaluate H σ g (ind H.subtype σ ((h : H) : G) (f v)) = _
    rw [evaluate_translate]
    change (functionModel H σ (f v)).val (g * ((h : H) : G)) =
      σ (intersectionConjugation H g h) ((functionModel H σ (f v)).val g)
    have hc := (functionModel H σ (f v)).property (intersectionConjugation H g h) g
    simpa only [intersectionConjugation, MonoidHom.coe_mk, OneHom.coe_mk,
      Subgroup.subtype_apply, Subtype.coe_mk, mul_assoc, inv_mul_cancel, mul_one] using hc

/-- The off-identity Mackey Hom conditions force an `H`-intertwiner whose
identity coefficient vanishes to be zero.  No semisimplicity is used here. -/
theorem intertwiner_eq_zero_of_mackey
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0)
    (f : IntertwiningMap σ ((ind H.subtype σ).comp H.subtype))
    (hf : ∀ v, identityEvaluation H σ (f v) = 0) : f = 0 := by
  apply IntertwiningMap.ext
  apply LinearMap.ext
  intro v
  apply functionModel_injective H σ
  apply Subtype.ext
  funext g
  change evaluate H σ g (f v) = 0
  by_cases hg : g ∈ H
  · have hc := (functionModel H σ (f v)).property ⟨g, hg⟩ 1
    change evaluate H σ (g * 1) (f v) = σ ⟨g, hg⟩ (identityEvaluation H σ (f v)) at hc
    simpa only [mul_one, hf v, map_zero] using hc
  · have he := congrArg (fun A => A v) (hM g hg (coefficientIntertwiner H σ g f))
    exact he

/-- A Mackey irreducibility theorem for actual induction at arbitrary subgroup
index.  Semisimplicity of the restricted induced representation supplies the
coefficient projection; all off-identity intersection Hom spaces vanish. -/
theorem irreducible_of_mackey [IsIrreducible σ]
    [IsSemisimpleRepresentation ((ind H.subtype σ).comp H.subtype)]
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0) :
    IsIrreducible (ind H.subtype σ) := by
  apply irreducible_of_projection H σ
  intro S hS z hz
  exact SemisimpleProjection.projection_mem σ ((ind H.subtype σ).comp H.subtype)
    (identityInclusion H σ) (identityEvaluation H σ)
    (identityEvaluation_inclusion H σ) (intertwiner_eq_zero_of_mackey H σ hM)
    S (fun h w hw => hS (h : G) w hw) hz

/-- The compact-open Mackey criterion has no independent semisimplicity
hypothesis: compactness and smoothness prove it for the actual restricted
induced representation.  The ambient group and coset space may be infinite. -/
theorem irreducible_of_compact_open_mackey [CharZero k]
    [TopologicalSpace G] [IsTopologicalGroup G] [IsIrreducible σ]
    (hHopen : IsOpen (H : Set G)) (hHcompact : IsCompact (H : Set G))
    (hσ : SmoothDegreeQuotient.IsSmooth σ)
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0) :
    IsIrreducible (ind H.subtype σ) := by
  let : CompactSpace H := isCompact_iff_compactSpace.mp hHcompact
  have hres : SmoothDegreeQuotient.IsSmooth ((ind H.subtype σ).comp H.subtype) := by
    intro z
    exact (ind_isSmooth H σ hHopen hσ z).preimage continuous_subtype_val
  let : IsSemisimpleRepresentation ((ind H.subtype σ).comp H.subtype) :=
    CompactSmoothSemisimple.smooth_semisimple _ hres
  exact irreducible_of_mackey H σ hM

end PaperXI.InductionIrreducibility
