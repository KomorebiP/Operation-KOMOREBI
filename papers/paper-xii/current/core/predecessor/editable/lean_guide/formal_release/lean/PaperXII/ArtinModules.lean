import PaperXII.ArtinData
import PaperXII.PacketTrace
import Mathlib.RingTheory.Idempotents
import Mathlib.Algebra.DirectSum.Module
import Mathlib.RingTheory.Support

set_option autoImplicit false

open scoped DirectSum

/-! Paper XII, Theorem 8.2: actual scalar-action packets, their direct sum,
and their canonical identification with localized modules. -/
namespace PaperXII.ArtinModules

variable {R V I : Type*} [CommRing R] [AddCommGroup V] [Module R V]

/-- The actual submodule fixed by an idempotent, equal to its scalar-action image. -/
def packet (e : R) : Submodule R V where
  carrier := {v | e • v = v}
  zero_mem' := smul_zero e
  add_mem' hv hw := by simp only [Set.mem_ofPred_eq] at *; rw [smul_add, hv, hw]
  smul_mem' r v hv := by
    simp only [Set.mem_ofPred_eq] at *
    rw [smul_comm e r, hv]

theorem mem_packet_iff (e : R) (v : V) : v ∈ packet e ↔ e • v = v := Iff.rfl

theorem mem_packet_iff_image {e : R} (he : IsIdempotentElem e) (v : V) :
    v ∈ packet e ↔ ∃ w : V, e • w = v := by
  constructor
  · intro hv
    exact ⟨v, hv⟩
  · rintro ⟨w, rfl⟩
    change e • (e • w) = e • w
    rw [← mul_smul, he]

/-- Projection to the packet is multiplication by the idempotent itself. -/
def projection (e : R) (he : IsIdempotentElem e) : V →ₗ[R] packet (V := V) e where
  toFun v := ⟨e • v, by change e • (e • v) = e • v; rw [← mul_smul, he]⟩
  map_add' v w := Subtype.ext (smul_add e v w)
  map_smul' r v := Subtype.ext (smul_comm e r v)

theorem projection_apply (e : R) (he : IsIdempotentElem e) (v : V) :
    (projection e he v : V) = e • v := rfl

theorem projection_packet (e : R) (he : IsIdempotentElem e) (v : packet (V := V) e) :
    projection e he (v : V) = v := Subtype.ext v.property

variable [Fintype I] (e : I → R) (he : CompleteOrthogonalIdempotents e)

/-- The product of packet projections. -/
def toPackets : V →ₗ[R] ∀ i, packet (V := V) (e i) :=
  LinearMap.pi fun i => projection (e i) (he.idem i)

/-- Packet assembly adds their vectors in the original module. -/
def fromPackets : (∀ i, packet (V := V) (e i)) →ₗ[R] V where
  toFun v := ∑ i, (v i : V)
  map_add' v w := by simp [Finset.sum_add_distrib]
  map_smul' r v := by simp [Finset.smul_sum]

theorem from_to_packets (v : V) : fromPackets e (toPackets e he v) = v := by
  change ∑ i, e i • v = v
  rw [← Finset.sum_smul, he.complete, one_smul]

theorem to_from_packets (v : ∀ i, packet (V := V) (e i)) :
    toPackets e he (fromPackets e v) = v := by
  classical
  funext i
  apply Subtype.ext
  change e i • ∑ j, (v j : V) = (v i : V)
  rw [Finset.smul_sum, Finset.sum_eq_single i]
  · exact (v i).property
  · intro j _ hji
    calc
      e i • (v j : V) = e i • (e j • (v j : V)) := congrArg (e i • ·) (v j).property.symm
      _ = 0 := by rw [← mul_smul, he.ortho (Ne.symm hji), zero_smul]
  · simp

/-- The equivalence has the canonical projections and sum as its two maps. -/
def productEquiv : V ≃ₗ[R] ∀ i, packet (V := V) (e i) :=
  LinearEquiv.ofLinearMap (toPackets e he) (fromPackets e)
    (LinearMap.ext (to_from_packets e he)) (LinearMap.ext (from_to_packets e he))

/-- Finite product and direct sum coincide, yielding the actual direct sum of packets. -/
noncomputable def directSumEquiv : V ≃ₗ[R] ⨁ i, packet (V := V) (e i) := by
  classical
  exact (productEquiv e he).trans (DirectSum.linearEquivFunOnFintype R I _).symm

theorem directSumEquiv_apply (v : V) (i : I) :
    ((directSumEquiv e he v) i : V) = e i • v := by
  classical
  rfl

theorem directSumEquiv_symm_apply (v : ⨁ i, packet (V := V) (e i)) :
    (directSumEquiv e he).symm v = ∑ i, (v i : V) := by
  classical
  rfl

/-- Every denominator has an inverse on the corresponding idempotent summand. -/
theorem denominator_inverse (D : ArtinData.Decomposition R) (m : MaximalSpectrum R)
    (s : m.asIdeal.primeCompl) :
    ∃ t : R, (s : R) * t * ArtinData.idempotent D m = ArtinData.idempotent D m := by
  classical
  obtain ⟨u, hu⟩ := (IsLocalization.map_units (Localization.AtPrime m.asIdeal) s).exists_right_inv
  let t : R := D.symm (Pi.single m u)
  refine ⟨t, ?_⟩
  apply D.injective
  ext n
  simp only [map_mul, Pi.mul_apply, ArtinData.map_idempotent]
  by_cases hn : n = m
  · subst n
    simp only [t, AlgEquiv.apply_symm_apply, Pi.single_eq_same, mul_one]
    rw [ArtinData.coordinate]
    exact hu
  · simp [Pi.single_eq_of_ne hn]

/-- Multiplication by every denominator is invertible on the actual packet. -/
theorem denominator_unit (D : ArtinData.Decomposition R) (m : MaximalSpectrum R)
    (s : m.asIdeal.primeCompl) :
    IsUnit (algebraMap R (Module.End R (packet (V := V) (ArtinData.idempotent D m))) s) := by
  obtain ⟨t, ht⟩ := denominator_inverse D m s
  let P := packet (V := V) (ArtinData.idempotent D m)
  refine ⟨⟨algebraMap R (Module.End R P) s, algebraMap R (Module.End R P) t, ?_, ?_⟩, rfl⟩
  · ext v
    change (s : R) • (t • (v : V)) = (v : V)
    calc
      _ = ((s : R) * t) • (ArtinData.idempotent D m • (v : V)) := by
        rw [v.property, mul_smul]
      _ = v := by rw [← mul_smul, ht, v.property]
  · ext v
    change t • ((s : R) • (v : V)) = (v : V)
    rw [smul_comm t (s : R)]
    calc
      _ = ((s : R) * t) • (ArtinData.idempotent D m • (v : V)) := by
        rw [v.property, mul_smul]
      _ = v := by rw [← mul_smul, ht, v.property]

/-- The projection to the packet satisfies the complete localization specification. -/
theorem projection_isLocalizedModule (D : ArtinData.Decomposition R) (m : MaximalSpectrum R) :
    IsLocalizedModule m.asIdeal.primeCompl
      (projection (V := V) (ArtinData.idempotent D m) (ArtinData.idem D m)) where
  map_units := denominator_unit D m
  surj v := ⟨((v : V), 1), by simpa using (projection_packet _ (ArtinData.idem D m) v).symm⟩
  exists_of_eq h := ⟨⟨ArtinData.idempotent D m, ArtinData.idempotent_not_mem D m⟩,
    congrArg Subtype.val h⟩

/-- The canonical localization equivalence, derived from the ring decomposition. -/
noncomputable def localizationEquiv (D : ArtinData.Decomposition R) (m : MaximalSpectrum R) :
    packet (V := V) (ArtinData.idempotent D m) ≃ₗ[R]
      LocalizedModule m.asIdeal.primeCompl V := by
  letI := projection_isLocalizedModule (V := V) D m
  exact IsLocalizedModule.linearEquiv m.asIdeal.primeCompl
    (projection (ArtinData.idempotent D m) (ArtinData.idem D m))
    (LocalizedModule.mkLinearMap m.asIdeal.primeCompl V)

/-- This is the original localization map restricted to the packet. -/
theorem localizationEquiv_apply (D : ArtinData.Decomposition R) (m : MaximalSpectrum R)
    (v : packet (V := V) (ArtinData.idempotent D m)) :
    localizationEquiv D m v = LocalizedModule.mk (v : V) 1 := by
  let := projection_isLocalizedModule (V := V) D m
  have h := IsLocalizedModule.linearEquiv_apply m.asIdeal.primeCompl
    (projection (ArtinData.idempotent D m) (ArtinData.idem D m))
    (LocalizedModule.mkLinearMap m.asIdeal.primeCompl V) (v : V)
  simpa [localizationEquiv, projection_packet] using h

/-- Occupancy agrees exactly with the ordinary module support. -/
theorem occupied_iff_support (D : ArtinData.Decomposition R) (m : MaximalSpectrum R) :
    packet (V := V) (ArtinData.idempotent D m) ≠ ⊥ ↔
      m.toPrimeSpectrum ∈ Module.support R V := by
  rw [← Submodule.nontrivial_iff_ne_bot, Module.mem_support_iff]
  exact (localizationEquiv (V := V) D m).toEquiv.nontrivial_congr

/-- Paper XII 8.2: the actual canonical direct sum over maximal ideals. -/
noncomputable def canonicalDirectSumEquiv [Fintype (MaximalSpectrum R)]
    (D : ArtinData.Decomposition R) :
    V ≃ₗ[R] ⨁ m, packet (V := V) (ArtinData.idempotent D m) :=
  directSumEquiv (ArtinData.idempotent D) (ArtinData.complete D)

/-- The R-module packet has exactly the field-linear image used in Corollary 8.4. -/
theorem packet_restrictScalars {E : Type*} [Field E] [Algebra E R]
    [Module E V] [IsScalarTower E R V] {a : R} (ha : IsIdempotentElem a) :
    (packet (V := V) a).restrictScalars E = PacketTrace.packet (E := E) (V := V) a := by
  ext v
  exact (mem_packet_iff_image ha v).trans (PacketTrace.mem_packet_iff a v).symm

/-- The source-level Theorem 8.2, with finiteness of the maximal spectrum derived
from finite dimension. The only supplied algebraic decomposition is external
Fact 8.1; all module maps and support conclusions are constructed here. -/
theorem canonical_hecke_packet_decomposition {E : Type*} [Field E] [Algebra E R]
    [FiniteDimensional E R] [Module.Finite R V] (D : ArtinData.Decomposition R) :
    ∃ F : V ≃ₗ[R] ⨁ m, packet (V := V) (ArtinData.idempotent D m),
      (∀ (v : V) (m : MaximalSpectrum R), ((F v) m : V) = ArtinData.idempotent D m • v) ∧
      (∀ m : MaximalSpectrum R,
        ∃ L : packet (V := V) (ArtinData.idempotent D m) ≃ₗ[R]
          LocalizedModule m.asIdeal.primeCompl V,
          (∀ v, L v = LocalizedModule.mk (v : V) 1) ∧
          (packet (V := V) (ArtinData.idempotent D m) ≠ ⊥ ↔
            m.toPrimeSpectrum ∈ Module.support R V)) := by
  let : IsArtinianRing R := IsArtinianRing.of_finite E R
  let : Fintype (MaximalSpectrum R) := Fintype.ofFinite _
  refine ⟨canonicalDirectSumEquiv D, ?_, ?_⟩
  · exact directSumEquiv_apply (ArtinData.idempotent D) (ArtinData.complete D)
  · intro m
    exact ⟨localizationEquiv D m, localizationEquiv_apply D m, occupied_iff_support D m⟩

end PaperXII.ArtinModules
