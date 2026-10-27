import PaperXI.EquivariantSplitting68
import PaperXI.InducedTypeSpace68

/-!
# Full-subgroup Mackey irreducibility for compact-mod-central induction

The ambient induction and its coefficient maps are the actual Mathlib carriers.
No compact-restriction intertwining criterion is substituted for the given
full-subgroup criterion. Smoothness, scalar cancellation and compact quotient
supply the needed equivariant section by a finite orbit average.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CompactModCenterInduction68

open Representation PaperXI.SmoothDegreeQuotient
open PaperXI.InductionIrreducibility PaperXI.OpenSubgroupSmoothInduction
open PaperXI.RepresentationStability

variable {k G V : Type*} [Field k] [Group G] [AddCommGroup V] [Module k V]
variable (H : Subgroup G) (σ : Representation k H V)

/-- Central scalars on the inducing space act by exactly the same scalar on
all actual induced vectors. -/
theorem induced_central_scalar (z : H) (hz : ∀ g : G, Commute (z : G) g)
    (c : k) (hc : ∀ v, σ z v = c • v) (w : IndV H.subtype σ) :
    ind H.subtype σ (z : G) w = c • w := by
  apply functionModel_injective H σ
  apply Subtype.ext
  funext x
  change evaluate H σ x (ind H.subtype σ (z : G) w) = evaluate H σ x (c • w)
  rw [evaluate_translate, map_smul]
  calc
    evaluate H σ (x * (z : G)) w = evaluate H σ ((z : G) * x) w :=
      congrArg (fun t => evaluate H σ t w) (hz x).eq.symm
    _ = σ z (evaluate H σ x w) := (functionModel H σ w).property z x
    _ = c • evaluate H σ x w := hc _

/-- The literal inclusion of a subrepresentation as an intertwiner. -/
def subInclusion {A W : Type*} [Group A] [AddCommGroup W] [Module k W]
    (τ : Representation k A W) (S : Subrepresentation τ) :
    IntertwiningMap S.toRepresentation τ where
  toLinearMap := S.toSubmodule.subtype
  isIntertwining' _ := rfl

variable [CharZero k] [TopologicalSpace G] [IsTopologicalGroup G]
  [FiniteDimensional k V] [IsIrreducible σ]

/-- Actual induction from an open subgroup compact modulo an ambient-central
subgroup is irreducible under the FULL off-H Mackey criterion. The compact
quotient is H / Z; no compactness of H or finite subgroup index is required. -/
theorem irreducible_of_compact_mod_center_mackey
    (Z : Subgroup H) [Z.Normal] [CompactSpace (H ⧸ Z)]
    (χ : Z →* kˣ)
    (hcentral : ∀ z : Z, ∀ g : G, Commute (((z : H) : G)) g)
    (hscalar : ∀ z : Z, ∀ v, σ (z : H) v = (χ z : k) • v)
    (hHopen : IsOpen (H : Set G)) (hσ : IsSmooth σ)
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0) :
    IsIrreducible (ind H.subtype σ) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space σ
  let : Nontrivial (IndV H.subtype σ) := ind_nontrivial H σ
  let τ := (ind H.subtype σ).comp H.subtype
  have hτ : IsSmooth τ := by
    intro w
    exact (ind_isSmooth H σ hHopen hσ w).preimage continuous_subtype_val
  have hcτ : ∀ z : Z, ∀ w, τ (z : H) w = (χ z : k) • w := by
    intro z w
    exact induced_central_scalar H σ (z : H) (hcentral z) (χ z : k) (hscalar z) w
  apply irreducible_of_stable
  intro S hS
  by_cases hbot : S = ⊥
  · exact Or.inl hbot
  right
  obtain ⟨w, hwS, hw⟩ := S.ne_bot_iff.mp hbot
  obtain ⟨g, hg⟩ := exists_nonzero_coefficient H σ hw
  let T : Subrepresentation τ := ⟨S, fun h v hv => hS (h : G) v hv⟩
  let p : IntertwiningMap T.toRepresentation σ :=
    (identityEvaluation H σ).comp (subInclusion τ T)
  have hpne : p ≠ 0 := by
    intro hp
    have he := congrArg (fun f => f ⟨ind H.subtype σ g w, hS g w hwS⟩) hp
    have he' : evaluate H σ 1 (ind H.subtype σ g w) = 0 := he
    rw [evaluate_translate, one_mul] at he'
    exact hg he'
  have hpsurj := (IsIrreducible.surjective_or_eq_zero p).resolve_right hpne
  have hT : IsSmooth T.toRepresentation :=
    CompactSmoothSemisimple.subrepresentation_smooth τ hτ T
  have hcT : ∀ z : Z, ∀ t, T.toRepresentation (z : H) t = (χ z : k) • t := by
    intro z t
    apply Subtype.ext
    exact hcτ z t
  obtain ⟨a, ha⟩ := EquivariantSplitting68.exists_equivariant_section
    Z χ σ T.toRepresentation hσ hT hscalar hcT p hpsurj
  let A : IntertwiningMap σ τ := (subInclusion τ T).comp a
  have hA : A = identityInclusion H σ := by
    apply sub_eq_zero.mp
    apply intertwiner_eq_zero_of_mackey H σ hM
    intro v
    change identityEvaluation H σ ((a v : IndV H.subtype σ) - identityInclusion H σ v) = 0
    rw [map_sub, identityEvaluation_inclusion]
    exact sub_eq_zero.mpr (ha v)
  apply eq_top_of_contains_identity H σ S hS
  intro v
  rw [← hA]
  exact (a v).property

/-- The complete general source package keeps nonzeroness, smoothness and
irreducibility distinct from later arithmetic admissibility claims. -/
theorem induction_package
    (Z : Subgroup H) [Z.Normal] [CompactSpace (H ⧸ Z)]
    (χ : Z →* kˣ)
    (hcentral : ∀ z : Z, ∀ g : G, Commute (((z : H) : G)) g)
    (hscalar : ∀ z : Z, ∀ v, σ (z : H) v = (χ z : k) • v)
    (hHopen : IsOpen (H : Set G)) (hσ : IsSmooth σ)
    (hM : ∀ g : G, g ∉ H →
      ∀ A : IntertwiningMap (σ.comp (intersectionSubgroup H g).subtype)
        (σ.comp (intersectionConjugation H g)), A = 0) :
    Nontrivial (IndV H.subtype σ) ∧ IsSmooth (ind H.subtype σ) ∧
      IsIrreducible (ind H.subtype σ) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space σ
  exact ⟨ind_nontrivial H σ, ind_isSmooth H σ hHopen hσ,
    irreducible_of_compact_mod_center_mackey H σ Z χ hcentral hscalar hHopen hσ hM⟩

end PaperXI.CompactModCenterInduction68
