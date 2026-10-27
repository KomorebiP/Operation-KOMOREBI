import ReleaseGluing
import Mathlib.Algebra.Module.Lattice
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.RingTheory.Localization.Integer

/-!
# DVR lattices supply the finite clearing exponents

The full-lattice hypotheses are Mathlib's finite-generation and spanning
conditions.  Finite denominators are constructed from an actual extended
lattice basis and the fraction-ring localization theorem.  A DVR
uniformizer factorization then replaces the nonzero scalar denominator by
a power of pi.  Thus no clearing-existence conclusion is assumed.
-/

set_option autoImplicit false
open scoped BigOperators nonZeroDivisors

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {K : Type v} {V : Type w}
variable [CommRing O] [IsDomain O] [Field K] [Algebra O K] [IsFractionRing O K]
variable [AddCommGroup V] [Module O V] [Module K V] [IsScalarTower O K V]

theorem endomorphism_has_nonzero_integral_multiple
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (E : Module.End K V) :
    ∃ r : O, r ≠ 0 ∧ ∀ x : V, x ∈ Λ → r • E x ∈ Λ := by
  classical
  let B := b.extendOfIsLattice K
  obtain ⟨r, hr⟩ := IsLocalization.exist_integer_multiples_of_finite O⁰
    (fun ij : ι × ι => B.repr (E (b ij.1)) ij.2)
  have hb : ∀ j : ι, (r : O) • E (b j) ∈ Λ := by
    intro j
    rw [← B.sum_repr (E (b j)), Finset.smul_sum]
    apply Λ.sum_mem
    intro i _hi
    obtain ⟨c, hc⟩ := hr (j, i)
    rw [← smul_assoc, ← hc]
    simpa only [B, Module.Basis.extendOfIsLattice_apply, algebraMap_smul] using
      Λ.smul_mem c (b i).property
  refine ⟨r, nonZeroDivisors.coe_ne_zero r, ?_⟩
  intro x hx
  have hxsum : (∑ i, b.repr (⟨x, hx⟩ : Λ) i • (b i : V)) = x := by
    simpa only [Submodule.coe_sum, Submodule.coe_smul] using
      congrArg (fun y : Λ => (y : V)) (b.sum_repr ⟨x, hx⟩)
  rw [← hxsum, map_sum, Finset.smul_sum]
  apply Λ.sum_mem
  intro i _hi
  rw [E.map_smul_of_tower]
  rw [smul_comm]
  exact Λ.smul_mem _ (hb i)

theorem endomorphism_has_uniformizer_clearing_exponent
    [IsDiscreteValuationRing O]
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (pi : O) (hpi : Irreducible pi)
    (E : Module.End K V) :
    ∃ s : ℕ, ∀ x : V, x ∈ Λ → (pi ^ s) • E x ∈ Λ := by
  obtain ⟨r, hr, hclear⟩ := endomorphism_has_nonzero_integral_multiple Λ b E
  obtain ⟨s, u, hu⟩ := IsDiscreteValuationRing.eq_unit_mul_pow_irreducible hr hpi
  refine ⟨s, ?_⟩
  intro x hx
  have h := Λ.smul_mem (↑u⁻¹ : O) (hclear x hx)
  rw [hu, ← mul_smul, ← mul_assoc] at h
  simpa only [Units.inv_mul, one_mul] using h

/-- A known integral clearing scalar gives the exact normalized-valuation bound.
The conclusion uses its valuation, not an unspecified existential exponent. -/
theorem uniformizer_valuation_clears_of_scalar_clears
    [IsDiscreteValuationRing O]
    (Λ : Submodule O V) (pi : O) (hpi : Irreducible pi)
    (r : O) (hr : r ≠ 0) (E : V → V)
    (hclear : ∀ x : V, x ∈ Λ → r • E x ∈ Λ) :
    ∀ x : V, x ∈ Λ →
      (pi ^ (IsDiscreteValuationRing.addVal O r).toNat) • E x ∈ Λ := by
  obtain ⟨s, u, hu⟩ := IsDiscreteValuationRing.eq_unit_mul_pow_irreducible hr hpi
  have hv : IsDiscreteValuationRing.addVal O r = (s : ℕ∞) :=
    IsDiscreteValuationRing.addVal_def r u hpi s hu
  intro x hx
  rw [hv, ENat.toNat_coe]
  have h := Λ.smul_mem (↑u⁻¹ : O) (hclear x hx)
  rw [hu, ← mul_smul, ← mul_assoc] at h
  simpa only [Units.inv_mul, one_mul] using h

variable {I : Type*} [Fintype I]

/-- Restricting a rational projector family to O changes neither the operators nor their ranges. -/
def Projectors.restrictScalars (P : Projectors K V I) : Projectors O V I where
  proj i := (P.proj i).restrictScalars O
  idem i := by
    ext x
    exact proj_idem P i x
  orthogonal i j hij := by
    ext x
    exact proj_other P i j hij x
  complete := by
    ext x
    simpa only [LinearMap.sum_apply, LinearMap.restrictScalars_apply, Module.End.one_apply]
      using reconstruct P x

theorem full_lattice_packet_clearing_exists
    [IsDiscreteValuationRing O]
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (pi : O) (hpi : Irreducible pi)
    (P : Projectors K V I) :
    ∀ i, ∃ s, ClearsPacket (P.restrictScalars (O := O)) Λ pi i s := by
  intro i
  exact endomorphism_has_uniformizer_clearing_exponent Λ b pi hpi (P.proj i)

/-- Exact gluing exponent for a full DVR lattice and rational packet decomposition.
All least exponents here exist by the preceding denominator construction. -/
theorem dvr_gluing_exponent_eq_globalWeight
    [IsDiscreteValuationRing O]
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (pi : O) (hpi : Irreducible pi)
    (P : Projectors K V I) :
    let finite := full_lattice_packet_clearing_exists Λ b pi hpi P
    gluingExponent (P.restrictScalars (O := O)) Λ pi finite =
      globalWeight (P.restrictScalars (O := O)) Λ pi finite := by
  exact gluing_exponent_eq_globalWeight _ _ _ _

end Komorebi.PaperII.ReleaseGluing
