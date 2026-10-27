import PaperXI.QuotientRepresentation
import Mathlib.RepresentationTheory.Invariants
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! Normal-inertia fixed spaces and abelian quotient descent.
No cyclic finite-inertia generator, Frobenius orbit basis, or tame hypothesis
is required for the fixed-space vanishing theorem. -/
set_option autoImplicit false
noncomputable section
open scoped Classical
namespace PaperXI.NormalInertia

variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

/-- The fixed space of a normal subgroup is a genuine ambient subrepresentation. -/
def fixedSubrepresentation (ρ : Representation ℂ G V) (I : Subgroup G) [I.Normal] :
    Subrepresentation ρ where
  toSubmodule := Representation.invariants (ρ.comp I.subtype)
  apply_mem_toSubmodule g := Representation.le_comap_invariants ρ I g

/-- Irreducibility gives the normal-subgroup invariant dichotomy. -/
theorem fixed_eq_bot_or_top (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (I : Subgroup G) [I.Normal] :
    Representation.invariants (ρ.comp I.subtype) = ⊥ ∨ Representation.invariants (ρ.comp I.subtype) = ⊤ := by
  rcases eq_bot_or_eq_top (fixedSubrepresentation ρ I) with h | h
  · exact Or.inl (congrArg Subrepresentation.toSubmodule h)
  · exact Or.inr (congrArg Subrepresentation.toSubmodule h)

/-- Full inertia-fixed space is equivalent to the literal kernel containment. -/
theorem fixed_top_iff_le_kernel (ρ : Representation ℂ G V) (I : Subgroup G) :
    Representation.invariants (ρ.comp I.subtype) = ⊤ ↔ I ≤ ρ.ker := by
  constructor
  · intro h g hg
    apply LinearMap.ext
    intro v
    have hv : v ∈ Representation.invariants (ρ.comp I.subtype) := by rw [h]; trivial
    exact hv ⟨g, hg⟩
  · intro h
    apply top_unique
    intro v _ g
    have hg := h g.property
    exact LinearMap.congr_fun hg v

/-- If the quotient by inertia is commutative, an irreducible representation
trivial on inertia is one-dimensional. -/
theorem dimension_one_of_inertia_trivial [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (I : Subgroup G) [I.Normal] [IsMulCommutative (G ⧸ I)]
    (hI : I ≤ ρ.ker) : Module.finrank ℂ V = 1 := by
  let σ := PaperXI.QuotientRepresentation.descend I ρ hI
  let : Representation.IsIrreducible σ :=
    PaperXI.QuotientRepresentation.descend_irreducible I ρ hI
  exact Representation.IsIrreducible.finrank_eq_one_of_isMulCommutative σ

/-- The original invariant-space argument needs abelian residual quotient,
not finite cyclic inertia or the tame induction theorem. -/
theorem fixed_eq_bot_of_dimension_gt_one [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (I : Subgroup G) [I.Normal] [IsMulCommutative (G ⧸ I)]
    (hdim : 1 < Module.finrank ℂ V) : Representation.invariants (ρ.comp I.subtype) = ⊥ := by
  rcases fixed_eq_bot_or_top ρ I with h | h
  · exact h
  · have hd := dimension_one_of_inertia_trivial ρ I ((fixed_top_iff_le_kernel ρ I).mp h)
    omega

/-- Nontrivial normal inertia acts without fixed vectors in an irreducible,
including one-dimensional ramified characters. -/
theorem fixed_eq_bot_of_not_le_kernel
    (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (I : Subgroup G) [I.Normal] (hI : ¬ I ≤ ρ.ker) :
    Representation.invariants (ρ.comp I.subtype) = ⊥ :=
  (fixed_eq_bot_or_top ρ I).resolve_right
    (fun h => hI ((fixed_top_iff_le_kernel ρ I).mp h))

/-- Exact codimension dichotomy, preserving the unramified one-dimensional case. -/
theorem fixed_codimension [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V) [Representation.IsIrreducible ρ]
    (I : Subgroup G) [I.Normal] :
    Module.finrank ℂ V - Module.finrank ℂ (Representation.invariants (ρ.comp I.subtype)) =
      if I ≤ ρ.ker then 0 else Module.finrank ℂ V := by
  split_ifs with hI
  · rw [(fixed_top_iff_le_kernel ρ I).mpr hI]; simp
  · rw [fixed_eq_bot_of_not_le_kernel ρ I hI]; simp

end PaperXI.NormalInertia
