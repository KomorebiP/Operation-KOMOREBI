import ReleaseGluingDVR
import ReleaseGluingSmith

/-!
# Finiteness of the genuine gluing module

The split submodule is proved to be a full lattice.  A finite uniform
clearing exponent also makes the actual gluing quotient finite length;
no finiteness of the residue field is required.
-/

set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {K : Type v} {V : Type w}
variable [CommRing O] [IsDomain O] [IsDiscreteValuationRing O]
variable [Field K] [Algebra O K] [IsFractionRing O K]
variable [AddCommGroup V] [Module O V] [Module K V] [IsScalarTower O K V]
variable {I : Type*} [Fintype I]

/-- The actual finite sum of packet intersections is a full lattice. -/
theorem splitLattice_isLattice
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (pi : O) (hpi : Irreducible pi)
    (P : Projectors K V I) :
    Submodule.IsLattice K (splitLattice (P.restrictScalars (O := O)) Λ) := by
  let Q := P.restrictScalars (O := O)
  let finite := full_lattice_packet_clearing_exists Λ b pi hpi P
  obtain ⟨s, hs⟩ := gluing_finite_exponent Q Λ pi finite
  have hclear := (annihilates_gluing_iff Q Λ (pi ^ s)).mp hs
  refine ⟨?_, ?_⟩
  · have : IsNoetherian O (splitLattice Q Λ) :=
      isNoetherian_of_le (splitLattice_le Q Λ)
    rw [← Module.Finite.iff_fg]
    infer_instance
  · apply eq_top_iff.mpr
    rw [← Submodule.IsLattice.span_eq_top (A := K) (M := Λ)]
    apply Submodule.span_le.mpr
    intro x hx
    have hmem : (pi ^ s) • x ∈ Submodule.span K (splitLattice Q Λ : Set V) :=
      Submodule.subset_span (hclear x hx)
    have hn : algebraMap O K (pi ^ s) ≠ 0 :=
      (map_ne_zero_iff (algebraMap O K) (IsFractionRing.injective O K)).mpr
        (pow_ne_zero s hpi.ne_zero)
    have hinv := (Submodule.span K (splitLattice Q Λ : Set V)).smul_mem
      ((algebraMap O K (pi ^ s))⁻¹) hmem
    rw [← algebraMap_smul K (pi ^ s) x, smul_smul, inv_mul_cancel₀ hn, one_smul] at hinv
    exact hinv

/-- A finite basis and a uniform annihilator give finite length of an actual quotient. -/
theorem finiteLength_quotient_of_power_annihilates
    {W : Type*} [AddCommGroup W] [Module O W]
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (S : Submodule O W) (b : Module.Basis ι O W)
    (pi : O) (hpi : Irreducible pi) (s : ℕ)
    (hann : ∀ z : W ⧸ S, (pi ^ s) • z = 0) :
    IsFiniteLength O (W ⧸ S) := by
  let f := smithCoordinateMap b pi (fun _ => s)
  have hker : LinearMap.ker f ≤ S := by
    intro x hx
    have hdiv : ∀ i, pi ^ s ∣ b.repr x i := by
      have hz : f x = 0 := hx
      intro i
      have hi := congrFun hz i
      change (Ideal.span {pi ^ s}).mkQ (b.repr x i) = 0 at hi
      rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero, Ideal.mem_span_singleton] at hi
      exact hi
    rw [← b.sum_repr x]
    apply S.sum_mem
    intro i _hi
    obtain ⟨c, hc⟩ := hdiv i
    have ha := hann (S.mkQ (b i))
    rw [← map_smul, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero] at ha
    rw [hc, mul_comm, mul_smul]
    exact S.smul_mem c ha
  have hlen : Module.length O (∀ _ : ι, O ⧸ Ideal.span {pi ^ s}) = ∑ _ : ι, (s : ℕ∞) := by
    rw [Module.length_pi_of_fintype]
    apply Finset.sum_congr rfl
    intro i _hi
    have heq : Ideal.span {pi ^ s} = IsLocalRing.maximalIdeal O ^ s := by
      rw [hpi.maximalIdeal_eq, Ideal.span_singleton_pow]
    rw [(Submodule.quotEquivOfEq _ _ heq).length_eq]
    exact IsDiscreteValuationRing.length_quotient_pow_maximalIdeal (R := O) s
  have hfinite : IsFiniteLength O (∀ _ : ι, O ⧸ Ideal.span {pi ^ s}) := by
    apply Module.length_ne_top_iff.mp
    rw [hlen, ← Nat.cast_sum]
    exact ENat.natCast_ne_top _
  have hsource : IsFiniteLength O (W ⧸ LinearMap.ker f) :=
    (f.quotKerEquivOfSurjective (smithCoordinateMap_surjective b pi (fun _ => s))).symm.isFiniteLength hfinite
  exact hsource.of_surjective (Submodule.factor_surjective hker)

/-- The manuscript's gluing module is finite length for every full DVR lattice. -/
theorem dvr_gluing_finiteLength
    {ι : Type*} [Fintype ι] (Λ : Submodule O V) [Submodule.IsLattice K Λ]
    (b : Module.Basis ι O Λ) (pi : O) (hpi : Irreducible pi)
    (P : Projectors K V I) :
    IsFiniteLength O (GluingModule (P.restrictScalars (O := O)) Λ) := by
  classical
  let finite := full_lattice_packet_clearing_exists Λ b pi hpi P
  obtain ⟨s, hs⟩ := gluing_finite_exponent (P.restrictScalars (O := O)) Λ pi finite
  exact finiteLength_quotient_of_power_annihilates _ b pi hpi s hs

end Komorebi.PaperII.ReleaseGluing
