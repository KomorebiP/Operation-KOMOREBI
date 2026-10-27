import ReleaseGluingDVR
import ReleasePrecision

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {K : Type v} {V : Type w}
variable [CommRing O] [IsDomain O] [Field K] [Algebra O K] [IsFractionRing O K]
variable [AddCommGroup V] [Module O V] [Module K V] [IsScalarTower O K V]
variable {I : Type*} [Fintype I]

/-- The O-submodule clearing condition is the original additive-lattice condition after scalar restriction. -/
theorem clearsPacket_iff_original
    (P : Projectors K V I) (Λ : Submodule O V) (pi : O) (i : I) (s : ℕ) :
    ClearsPacket (P.restrictScalars (O := O)) Λ pi i s ↔
      ResultantSeparation.IsSeparationWeight (algebraMap O K pi) (P.proj i)
        Λ.toAddSubgroup s := by
  simp only [ClearsPacket, Projectors.restrictScalars,
    ResultantSeparation.IsSeparationWeight, ResultantSeparation.PreservesLattice,
    LinearMap.smul_apply, LinearMap.restrictScalars_apply,
    ← map_pow, algebraMap_smul, Submodule.mem_toAddSubgroup]

theorem original_finite_of_packet_finite
    (P : Projectors K V I) (Λ : Submodule O V) (pi : O) (i : I)
    (finite : ∃ s, ClearsPacket (P.restrictScalars (O := O)) Λ pi i s) :
    ResultantSeparation.HasFiniteSeparationWeight (algebraMap O K pi)
      (P.proj i) Λ.toAddSubgroup := by
  obtain ⟨s, hs⟩ := finite
  exact ⟨s, (clearsPacket_iff_original P Λ pi i s).mp hs⟩

/-- The new quotient theorem uses precisely the pre-existing least separation weight. -/
theorem packetWeight_eq_original_separationWeight
    (P : Projectors K V I) (Λ : Submodule O V) (pi : O) (i : I)
    (finite : ∃ s, ClearsPacket (P.restrictScalars (O := O)) Λ pi i s) :
    packetWeight (P.restrictScalars (O := O)) Λ pi i finite =
      ResultantSeparation.separationWeight
        (original_finite_of_packet_finite P Λ pi i finite) := by
  classical
  unfold packetWeight ResultantSeparation.separationWeight
  exact Nat.find_congr' (clearsPacket_iff_original P Λ pi i _)

/-- DVR valuation normalization expressed in the original separation API. -/
theorem original_clearing_weight_at_valuation
    [IsDiscreteValuationRing O]
    (Λ : Submodule O V) (pi : O) (hpi : Irreducible pi)
    (r : O) (hr : r ≠ 0) (E : Module.End K V)
    (hclear : ∀ x : V, x ∈ Λ → r • E x ∈ Λ) :
    ResultantSeparation.IsSeparationWeight (algebraMap O K pi) E Λ.toAddSubgroup
      (IsDiscreteValuationRing.addVal O r).toNat := by
  intro x hx
  change ((algebraMap O K pi) ^ (IsDiscreteValuationRing.addVal O r).toNat) • E x ∈ Λ
  rw [← map_pow, algebraMap_smul]
  exact uniformizer_valuation_clears_of_scalar_clears Λ pi hpi r hr E hclear x hx

theorem original_finite_of_scalar_clears
    [IsDiscreteValuationRing O]
    (Λ : Submodule O V) (pi : O) (hpi : Irreducible pi)
    (r : O) (hr : r ≠ 0) (E : Module.End K V)
    (hclear : ∀ x : V, x ∈ Λ → r • E x ∈ Λ) :
    ResultantSeparation.HasFiniteSeparationWeight (algebraMap O K pi) E Λ.toAddSubgroup :=
  ⟨_, original_clearing_weight_at_valuation Λ pi hpi r hr E hclear⟩

/-- In particular, setting r to the actual polynomial resultant gives cor:resultant_bound. -/
theorem original_separationWeight_le_valuation
    [IsDiscreteValuationRing O]
    (Λ : Submodule O V) (pi : O) (hpi : Irreducible pi)
    (r : O) (hr : r ≠ 0) (E : Module.End K V)
    (hclear : ∀ x : V, x ∈ Λ → r • E x ∈ Λ) :
    ResultantSeparation.separationWeight
      (original_finite_of_scalar_clears Λ pi hpi r hr E hclear) ≤
        (IsDiscreteValuationRing.addVal O r).toNat :=
  ResultantSeparation.separationWeight_le_of_clears _
    (original_clearing_weight_at_valuation Λ pi hpi r hr E hclear)

end Komorebi.PaperII.ReleaseGluing
