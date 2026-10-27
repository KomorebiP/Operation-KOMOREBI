import Mathlib.RingTheory.HopkinsLevitzki
import Mathlib.RingTheory.Artinian.Ring
import Mathlib.RingTheory.Spectrum.Maximal.Localization
import PaperXII.PacketTrace
import PaperXII.ArtinData

set_option autoImplicit false

/-! Paper XII, Corollary 8.3. A maximal ideal specified by generators gives
simultaneous generalized eigenspaces in the actual canonical Artin packet.
The Artin product equivalence is the external input from Fact 8.1.
Nilpotence, separation of different maximal ideals, and the packet equality
are proved here, without assuming a semisimple or faithful representation. -/
namespace PaperXII.GeneralizedPackets

open scoped BigOperators
open PaperXII.ArtinData

variable {R : Type*} [CommRing R] [IsArtinianRing R]

/-- A single positive exponent kills the image of the entire maximal ideal
in its Artin localization. -/
theorem exists_local_power (m : MaximalSpectrum R) :
    ∃ N : ℕ, 1 ≤ N ∧ ∀ x ∈ m.asIdeal,
      (algebraMap R (Localization.AtPrime m.asIdeal) x) ^ N = 0 := by
  obtain ⟨n, hn⟩ := (isArtinianRing_iff_isNilpotent_maximalIdeal
    (Localization.AtPrime m.asIdeal)).mp inferInstance
  refine ⟨n + 1, Nat.le_add_left 1 n, ?_⟩
  intro x hx
  have hmem := Ideal.pow_mem_pow
    ((IsLocalization.AtPrime.to_map_mem_maximal_iff
      (Localization.AtPrime m.asIdeal) m.asIdeal x).mpr hx) n
  have hz : (algebraMap R (Localization.AtPrime m.asIdeal) x) ^ n = 0 := by
    simpa only [hn, Ideal.zero_eq_bot, Ideal.mem_bot] using hmem
  rw [pow_succ, hz, zero_mul]

omit [IsArtinianRing R] in
/-- Distinct maximal ideals cannot contain all the generators of each other.
This also handles an empty generator type: no distinct maximal ideal can exist. -/
theorem exists_generator_outside {ι : Type*} (g : ι → R)
    (m n : MaximalSpectrum R) (hg : Ideal.span (Set.range g) = m.asIdeal)
    (hne : n ≠ m) : ∃ i, g i ∉ n.asIdeal := by
  classical
  by_contra! h
  have hle : m.asIdeal ≤ n.asIdeal := by
    rw [← hg, Ideal.span_le]
    rintro _ ⟨i, rfl⟩
    exact h i
  exact hne (MaximalSpectrum.ext (m.isMaximal.eq_of_le n.isMaximal.ne_top hle).symm)

omit [IsArtinianRing R] in
/-- An element invertible in one Artin coordinate has a partial inverse whose
product with it is exactly the corresponding canonical idempotent. -/
theorem exists_partial_inverse (D : Decomposition R) (m : MaximalSpectrum R)
    (x : R) (hu : IsUnit (algebraMap R (Localization.AtPrime m.asIdeal) x)) :
    ∃ y : R, y * x = idempotent D m := by
  classical
  obtain ⟨u, hu⟩ := hu
  refine ⟨D.symm (Pi.single m (↑(u⁻¹) : Localization.AtPrime m.asIdeal)), ?_⟩
  apply D.injective
  simp only [map_mul, AlgEquiv.apply_symm_apply, map_idempotent]
  ext n
  by_cases hn : n = m
  · subst n
    simp only [Pi.mul_apply, Pi.single_eq_same, coordinate, ← hu, Units.inv_mul]
  · simp [Pi.single_eq_of_ne hn]

/-- The canonical packet is annihilated by one common positive power of every
element of its maximal ideal. This exponent is independent of the module. -/
theorem exists_packet_power (D : Decomposition R) (m : MaximalSpectrum R) :
    ∃ N : ℕ, 1 ≤ N ∧ ∀ x ∈ m.asIdeal, x ^ N * idempotent D m = 0 := by
  obtain ⟨N, hN, hn⟩ := exists_local_power m
  refine ⟨N, hN, fun x hx => (mul_idempotent_eq_zero_iff D m _).mpr ?_⟩
  simpa only [map_pow] using hn x hx

variable {V : Type*} [AddCommGroup V] [Module R V]

omit [IsArtinianRing R] in
/-- On every other Artin packet, a generator of m acts invertibly. Therefore a
vector killed by powers of all the generators has zero projection there. -/
theorem other_packet_vanishes {ι : Type*} (D : Decomposition R) (g : ι → R)
    (m n : MaximalSpectrum R) (hg : Ideal.span (Set.range g) = m.asIdeal)
    (hne : n ≠ m) (N : ℕ) (v : V) (hv : ∀ i, g i ^ N • v = 0) :
    idempotent D n • v = 0 := by
  obtain ⟨i, hi⟩ := exists_generator_outside g m n hg hne
  have hu : IsUnit (algebraMap R (Localization.AtPrime n.asIdeal) (g i ^ N)) := by
    rw [map_pow]
    exact ((IsLocalization.AtPrime.isUnit_to_map_iff
      (Localization.AtPrime n.asIdeal) n.asIdeal (g i)).mpr hi).pow N
  obtain ⟨y, hy⟩ := exists_partial_inverse D n (g i ^ N) hu
  rw [← hy, mul_smul, hv i, smul_zero]

/-- Exact equality of the actual projector image with simultaneous generalized
nilpotence conditions. No finiteness, semisimplicity, or faithfulness condition
on the representation is needed. The maximal ideal generators are explicit. -/
theorem simultaneous_packet [Fintype (MaximalSpectrum R)] {ι : Type*}
    (D : Decomposition R) (g : ι → R) (m : MaximalSpectrum R)
    (hg : Ideal.span (Set.range g) = m.asIdeal) :
    ∃ N : ℕ, 1 ≤ N ∧ ∀ v : V,
      (∃ w : V, idempotent D m • w = v) ↔ ∀ i, g i ^ N • v = 0 := by
  classical
  obtain ⟨N, hN, hn⟩ := exists_packet_power D m
  refine ⟨N, hN, fun v => ?_⟩
  constructor
  · rintro ⟨w, rfl⟩ i
    rw [← mul_smul, hn (g i) (hg ▸ Ideal.subset_span ⟨i, rfl⟩), zero_smul]
  · intro hv
    refine ⟨v, ?_⟩
    have hsum : (∑ n : MaximalSpectrum R, idempotent D n • v) = v := by
      rw [← Finset.sum_smul, (complete D).complete, one_smul]
    rw [Finset.sum_eq_single m] at hsum
    · exact hsum
    · intro n _ hne
      exact other_packet_vanishes D g m n hg hne N v hv
    · simp

omit [IsArtinianRing R] in
/-- Corollary 8.3 in the paper's operator-and-eigenvalue notation. Once the
maximal ideal is explicitly given by these differences, algebraic closure and
an additional algebra-generation hypothesis are unnecessary. The packet is
the actual E-linear image of its canonical Artin idempotent. -/
theorem simultaneous_generalized_eigenspaces {E ι : Type*} [Field E]
    [Algebra E R] [Module.Finite E R] [Module E V] [IsScalarTower E R V]
    (D : Decomposition R) (T : ι → R) (eigenvalue : ι → E) (m : MaximalSpectrum R)
    (hm : Ideal.span (Set.range (fun i => T i - algebraMap E R (eigenvalue i))) = m.asIdeal) :
    ∃ N : ℕ, 1 ≤ N ∧
      (PaperXII.PacketTrace.packet (E := E) (V := V) (idempotent D m) : Set V) =
        {v : V | ∀ i, (T i - algebraMap E R (eigenvalue i)) ^ N • v = 0} := by
  let : IsArtinianRing R := IsArtinianRing.of_finite E R
  let : Fintype (MaximalSpectrum R) := Fintype.ofFinite _
  obtain ⟨N, hN, hn⟩ := simultaneous_packet (V := V) D
    (fun i => T i - algebraMap E R (eigenvalue i)) m hm
  refine ⟨N, hN, ?_⟩
  ext v
  exact hn v

end PaperXII.GeneralizedPackets
