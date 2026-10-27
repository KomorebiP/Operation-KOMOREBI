import CrossRadixInvariantShellJetHull
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

noncomputable section
namespace KomorebiCrossRadix

/-- Finite coordinates for the refined common hull: the full transient prefix together with the
absolute minimal positive-affine orbit hull of the declared quasi-polynomial tail profile. -/
abbrev OrbitCommonHullCoordinates (N T d : ℕ) (P : DegreeBoundedProfile T d) :=
  PrefixData N × ProfileOrbitHull T d P

/-- Synthesis from transient coordinates and the minimal tail orbit hull. -/
def orbitCommonHullSynthesize (N T d : ℕ) (P : DegreeBoundedProfile T d) :
    OrbitCommonHullCoordinates N T d P →ₗ[ℂ] (ℕ → ℂ) where
  toFun c n := prefixSynthesize N c.1 n + quasiPolynomialEval T d c.2.1 n
  map_add' c e := by
    funext n
    change prefixSynthesize N (c.1 + e.1) n +
        quasiPolynomialEval T d (c.2.1 + e.2.1) n = _
    simp only [map_add, Pi.add_apply]
    ring
  map_smul' x c := by
    funext n
    change prefixSynthesize N (x • c.1) n +
        quasiPolynomialEval T d (x • c.2.1) n = _
    rw [map_smul, map_smul]
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    ring

/-- Refined transient-plus-tail common hull.  The transient `N`-prefix remains fully retained,
while the tail is reduced from the whole `T(d+1)` profile space to its absolute affine orbit hull. -/
def OrbitCommonHull (N T d : ℕ) (P : DegreeBoundedProfile T d) :
    Submodule ℂ (ℕ → ℂ) :=
  LinearMap.range (orbitCommonHullSynthesize N T d P)

/-- Any sequence agreeing from `N` with a tail profile already in the affine orbit hull belongs
to the refined common hull. -/
theorem mem_OrbitCommonHull_of_agrees_orbit_profile
    (f : ℕ → ℂ) (N T d : ℕ) (P Q : DegreeBoundedProfile T d)
    (hQ : Q ∈ ProfileOrbitHull T d P)
    (h : AgreesFromQP N f (quasiPolynomialEval T d Q)) :
    f ∈ OrbitCommonHull N T d P := by
  refine ⟨(prefixCorrection N T d f Q, ⟨Q, hQ⟩), ?_⟩
  funext n
  by_cases hn : n < N
  · simp [orbitCommonHullSynthesize, prefixSynthesize, prefixCorrection, hn]
  · have hN : N ≤ n := Nat.le_of_not_gt hn
    have heq := h n hN
    simp [orbitCommonHullSynthesize, prefixSynthesize, hn, heq]

/-- Every member of the refined common hull has a tail profile in the minimal affine orbit hull. -/
theorem exists_orbit_profile_agrees_of_mem_OrbitCommonHull
    (N T d : ℕ) (P : DegreeBoundedProfile T d) {f : ℕ → ℂ}
    (hf : f ∈ OrbitCommonHull N T d P) :
    ∃ Q : DegreeBoundedProfile T d,
      Q ∈ ProfileOrbitHull T d P ∧ AgreesFromQP N f (quasiPolynomialEval T d Q) := by
  rcases hf with ⟨c, hc⟩
  rcases c with ⟨pref, Q⟩
  refine ⟨Q.1, Q.2, ?_⟩
  intro n hn
  have hnot : ¬ n < N := Nat.not_lt_of_ge hn
  calc
    f n = orbitCommonHullSynthesize N T d P (pref, Q) n := by rw [hc]
    _ = quasiPolynomialEval T d Q.1 n := by
      simp [orbitCommonHullSynthesize, prefixSynthesize, hnot]

/-- The refined common hull is invariant under every positive affine section. -/
theorem OrbitCommonHull_closed_under_positive_section
    (N T d m r : ℕ) (hm : 0 < m) (P : DegreeBoundedProfile T d)
    {f : ℕ → ℂ} (hf : f ∈ OrbitCommonHull N T d P) :
    coeffSection m r f ∈ OrbitCommonHull N T d P := by
  obtain ⟨Q, hQ, htail⟩ := exists_orbit_profile_agrees_of_mem_OrbitCommonHull N T d P hf
  let Q' := quasiPolynomialSectionProfile T d m r hm Q
  have hQ' : Q' ∈ ProfileOrbitHull T d P :=
    ProfileOrbitHull_section_closed T d m r hm P hQ
  apply mem_OrbitCommonHull_of_agrees_orbit_profile
    (coeffSection m r f) N T d P Q' hQ'
  exact eventualQuasiPolynomial_section_closed f N T d m r hm Q htail

/-- Every positive affine section supplied by the Bell downstream interface lands in the refined
common hull determined by the single original tail profile. -/
theorem bellDownstream_uniform_all_positive_affine_OrbitCommonHull
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    ∀ m r : ℕ, 0 < m →
      coeffSection m r a ∈ OrbitCommonHull B.N B.T B.d B.profile := by
  intro m r hm
  let Q := quasiPolynomialSectionProfile B.T B.d m r hm B.profile
  have hQorbit : Q ∈ ProfileOrbitHull B.T B.d B.profile := by
    apply Submodule.subset_span
    exact ⟨m, r, hm, rfl⟩
  apply mem_OrbitCommonHull_of_agrees_orbit_profile
    (coeffSection m r a) B.N B.T B.d B.profile Q hQorbit
  exact eventualQuasiPolynomial_section_closed
    a B.N B.T B.d m r hm B.profile B.agrees

/-- The original sequence itself belongs to the refined common hull. -/
theorem bellDownstream_original_mem_OrbitCommonHull
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    a ∈ OrbitCommonHull B.N B.T B.d B.profile := by
  have h := bellDownstream_uniform_all_positive_affine_OrbitCommonHull a B 1 0 (by omega)
  have heq : coeffSection 1 0 a = a := by
    funext n
    simp [coeffSection]
  rw [heq] at h
  exact h

/-- Uniform positive-radix specialization of the refined common-hull theorem. -/
theorem bellDownstream_uniform_all_positive_radix_OrbitCommonHull
    (a : ℕ → ℂ) (B : BellDownstreamInterface a) :
    ∀ b e s : ℕ, 0 < b →
      coeffSection (b ^ e) s a ∈ OrbitCommonHull B.N B.T B.d B.profile := by
  intro b e s hb
  exact bellDownstream_uniform_all_positive_affine_OrbitCommonHull
    a B (b ^ e) s (Nat.pow_pos hb)

/-- Vector-space freeness for the minimal profile orbit hull, made explicit so product-finrank
lemmas do not depend on low-priority global instance search. -/
local instance profileOrbitHullFree (T d : ℕ) (P : DegreeBoundedProfile T d) :
    Module.Free ℂ (ProfileOrbitHull T d P) :=
  Module.Free.of_divisionRing ℂ (ProfileOrbitHull T d P)

/-- Exact dimension of the refined finite coordinate source. -/
theorem OrbitCommonHullCoordinates_finrank
    (N T d : ℕ) [NeZero T] (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (OrbitCommonHullCoordinates N T d P) =
      N + Module.finrank ℂ (ProfileOrbitHull T d P) := by
  rw [Module.finrank_prod]
  rw [Module.finrank_fin_fun]

/-- First sharpening of the v0.7 coarse bound: use the exact finrank of the absolute minimal
affine orbit hull of the tail rather than all `T(d+1)` bounded-profile coordinates. -/
theorem OrbitCommonHull_finrank_le_orbit
    (N T d : ℕ) [NeZero T] (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (OrbitCommonHull N T d P) ≤
      N + Module.finrank ℂ (ProfileOrbitHull T d P) := by
  calc
    Module.finrank ℂ (OrbitCommonHull N T d P) ≤
        Module.finrank ℂ (OrbitCommonHullCoordinates N T d P) :=
      LinearMap.finrank_range_le (orbitCommonHullSynthesize N T d P)
    _ = N + Module.finrank ℂ (ProfileOrbitHull T d P) :=
      OrbitCommonHullCoordinates_finrank N T d P

/-- Shell/jet quantitative sharpening: the refined sequence hull is bounded by the number of
active Fourier-frequency/jet coordinates in the minimal shell/jet-saturated tail envelope. -/
theorem OrbitCommonHull_finrank_le_activeShellJet
    (N T d : ℕ) [NeZero T] (hT : 0 < T) (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (OrbitCommonHull N T d P) ≤
      N + (allowedFreqJetFinset hT
        (ActiveShellJetSet hT (ProfileOrbitHull T d P))).card := by
  calc
    Module.finrank ℂ (OrbitCommonHull N T d P) ≤
        N + Module.finrank ℂ (ProfileOrbitHull T d P) :=
      OrbitCommonHull_finrank_le_orbit N T d P
    _ ≤ N + (allowedFreqJetFinset hT
        (ActiveShellJetSet hT (ProfileOrbitHull T d P))).card :=
      Nat.add_le_add_left (ProfileOrbitHull_finrank_le_activeShellJet hT P) N

/-- The new active shell/jet bound recovers the v0.7 coarse bound as a formal consequence. -/
theorem OrbitCommonHull_finrank_le_coarse
    (N T d : ℕ) [NeZero T] (hT : 0 < T) (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (OrbitCommonHull N T d P) ≤ N + T * (d + 1) := by
  exact (OrbitCommonHull_finrank_le_activeShellJet N T d hT P).trans
    (Nat.add_le_add_left
      (allowedFreqJetFinset_card_le_full hT
        (ActiveShellJetSet hT (ProfileOrbitHull T d P))) N)

/-- Whenever the active shell/jet coordinate count is genuinely smaller than `T(d+1)`, the
refined common hull has a strictly smaller certified dimension bound than v0.7's coarse bound. -/
theorem OrbitCommonHull_finrank_lt_coarse_of_active_lt
    (N T d : ℕ) [NeZero T] (hT : 0 < T) (P : DegreeBoundedProfile T d)
    (hactive : (allowedFreqJetFinset hT
      (ActiveShellJetSet hT (ProfileOrbitHull T d P))).card < T * (d + 1)) :
    Module.finrank ℂ (OrbitCommonHull N T d P) < N + T * (d + 1) := by
  exact lt_of_le_of_lt (OrbitCommonHull_finrank_le_activeShellJet N T d hT P)
    (Nat.add_lt_add_left hactive N)

/-- The refined hull lies inside the original v0.7 common hull. -/
theorem OrbitCommonHull_le_CommonHull
    (N T d : ℕ) (P : DegreeBoundedProfile T d) :
    OrbitCommonHull N T d P ≤ CommonHull N T d := by
  rintro f ⟨c, rfl⟩
  refine ⟨(c.1, c.2.1), ?_⟩
  rfl

/-- **Minimal refined common-hull theorem.**  Once the full transient prefix space is retained,
`OrbitCommonHull` is the smallest linear sequence space that contains the declared tail seed and
is invariant under every positive affine section.  This is an absolute minimality theorem under
the stated prefix-retention convention. -/
theorem OrbitCommonHull_minimal
    (N T d : ℕ) (P : DegreeBoundedProfile T d)
    (K : Submodule ℂ (ℕ → ℂ))
    (hprefix : LinearMap.range (prefixSynthesize N) ≤ K)
    (hP : quasiPolynomialEval T d P ∈ K)
    (hclosed : ∀ m r : ℕ, ∀ _hm : 0 < m, ∀ f ∈ K, coeffSection m r f ∈ K) :
    OrbitCommonHull N T d P ≤ K := by
  have hprofile : ProfileOrbitHull T d P ≤ K.comap (quasiPolynomialEval T d) := by
    apply ProfileOrbitHull_minimal T d P (K.comap (quasiPolynomialEval T d))
    · exact hP
    · intro m r hm Q hQ
      change quasiPolynomialEval T d (quasiPolynomialSectionProfile T d m r hm Q) ∈ K
      rw [← quasiPolynomialEval_coeffSection T d m r hm Q]
      exact hclosed m r hm (quasiPolynomialEval T d Q) hQ
  rintro f ⟨c, rfl⟩
  change prefixSynthesize N c.1 + quasiPolynomialEval T d c.2.1 ∈ K
  apply K.add_mem
  · exact hprefix ⟨c.1, rfl⟩
  · exact hprofile c.2.2

/-- Bell-specialized minimality. Under the retained full-prefix convention, the refined hull is
the smallest positive-affine-invariant linear sequence space containing the original sequence. -/
theorem bellDownstream_OrbitCommonHull_minimal
    (a : ℕ → ℂ) (B : BellDownstreamInterface a)
    (K : Submodule ℂ (ℕ → ℂ))
    (hprefix : LinearMap.range (prefixSynthesize B.N) ≤ K)
    (ha : a ∈ K)
    (hclosed : ∀ m r : ℕ, ∀ _hm : 0 < m, ∀ f ∈ K, coeffSection m r f ∈ K) :
    OrbitCommonHull B.N B.T B.d B.profile ≤ K := by
  apply OrbitCommonHull_minimal B.N B.T B.d B.profile K hprefix ?_ hclosed
  let c := prefixCorrection B.N B.T B.d a B.profile
  have hc : prefixSynthesize B.N c ∈ K := hprefix ⟨c, rfl⟩
  have htail : a - prefixSynthesize B.N c ∈ K := K.sub_mem ha hc
  have heq : a - prefixSynthesize B.N c = quasiPolynomialEval B.T B.d B.profile := by
    funext n
    by_cases hn : n < B.N
    · simp [c, prefixCorrection, prefixSynthesize, hn]
    · have hN : B.N ≤ n := Nat.le_of_not_gt hn
      have hagree := B.agrees n hN
      simp [c, prefixCorrection, prefixSynthesize, hn, hagree]
  rwa [heq] at htail

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.OrbitCommonHull_closed_under_positive_section
#print axioms KomorebiCrossRadix.bellDownstream_uniform_all_positive_radix_OrbitCommonHull
#print axioms KomorebiCrossRadix.OrbitCommonHull_finrank_le_activeShellJet
#print axioms KomorebiCrossRadix.OrbitCommonHull_minimal
#print axioms KomorebiCrossRadix.bellDownstream_OrbitCommonHull_minimal
