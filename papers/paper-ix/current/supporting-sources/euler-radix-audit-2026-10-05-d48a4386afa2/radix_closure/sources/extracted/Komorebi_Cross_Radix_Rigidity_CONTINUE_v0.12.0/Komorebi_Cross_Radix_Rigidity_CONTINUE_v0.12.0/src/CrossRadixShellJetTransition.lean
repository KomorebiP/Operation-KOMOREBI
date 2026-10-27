import CrossRadixExplicitShellJetClosure
import Mathlib.Algebra.EuclideanDomain.Basic

noncomputable section
open Polynomial
open scoped BigOperators

namespace KomorebiCrossRadix

local instance propDecidableShellJetTransition (p : Prop) : Decidable p := Classical.propDecidable p

variable {T d : ℕ}

/-- Multiplication of a Fourier frequency can only move upward in the divisor-shell lattice. -/
lemma frequencyShellIdx_dvd_mul [NeZero T] (hT : 0 < T) (m : ZMod T) (ξ : ZMod T) :
    (frequencyShellIdx hT ξ).1 ∣ (frequencyShellIdx hT (m * ξ)).1 := by
  apply Nat.dvd_gcd
  · exact Nat.gcd_dvd_left T ξ.val
  · rw [frequencyShellIdx_val, ZMod.val_mul]
    apply (Nat.dvd_mod_iff (Nat.gcd_dvd_left T ξ.val)).2
    exact dvd_mul_of_dvd_right (Nat.gcd_dvd_right T ξ.val) m.val

/-- Explicit divisor-upward / jet-downward closure of a shell/jet support. -/
def ExplicitShellJetClosure (S : Set (ShellJetIdx T d)) : Set (ShellJetIdx T d) :=
  {t | ∃ s ∈ S, s.1.1 ∣ t.1.1 ∧ t.2.val ≤ s.2.val}

lemma subset_ExplicitShellJetClosure (S : Set (ShellJetIdx T d)) :
    S ⊆ ExplicitShellJetClosure S := by
  intro s hs
  exact ⟨s, hs, dvd_rfl, le_rfl⟩

lemma ExplicitShellJetClosure_mono {S U : Set (ShellJetIdx T d)} (hSU : S ⊆ U) :
    ExplicitShellJetClosure S ⊆ ExplicitShellJetClosure U := by
  rintro t ⟨s, hs, hdiv, hjet⟩
  exact ⟨s, hSU hs, hdiv, hjet⟩

lemma ExplicitShellJetClosure_trans
    {S : Set (ShellJetIdx T d)} {u t : ShellJetIdx T d}
    (hu : u ∈ ExplicitShellJetClosure S)
    (hut : u.1.1 ∣ t.1.1) (hjet : t.2.val ≤ u.2.val) :
    t ∈ ExplicitShellJetClosure S := by
  rcases hu with ⟨s, hs, hsu, hju⟩
  exact ⟨s, hs, dvd_trans hsu hut, hjet.trans hju⟩

/-- **Support transition theorem.** Any nonzero Fourier/jet coordinate created by a positive
affine section comes from a nonzero input coordinate whose frequency maps to the output frequency
and whose jet order is at least the output jet order. -/
theorem nonzero_section_coord_has_source
    [NeZero T] (hT : 0 < T) (S : Set (ShellJetIdx T d))
    (m r : ℕ) (hm : 0 < m) (Q : DegreeBoundedProfile T d)
    (hQ : Q ∈ ShellJetMaskSubmodule hT S)
    (zout : FreqJetIdx T d)
    (hout : profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d m r hm Q) zout ≠ 0) :
    ∃ zin : FreqJetIdx T d,
      freqJetShellLabel hT zin ∈ S ∧
      (m : ZMod T) * zin.1 = zout.1 ∧
      zout.2.val ≤ zin.2.val := by
  rw [profileFourierJetEquiv_apply, dft_quasiPolynomialSectionProfile] at hout
  let R : DegreeBoundedPolynomial d :=
    ∑ ξ : ZMod T, if (m : ZMod T) * ξ = zout.1 then
      ZMod.stdAddChar ((r : ZMod T) * ξ) • ZMod.dft Q ξ else 0
  have houtR :
      (boundedAffinePolynomialEquiv d (m : ℂ) (r : ℂ)
        (natCast_complex_ne_zero_of_pos hm) R).1.coeff zout.2 ≠ 0 := by
    simpa [R] using hout
  have hj : ∃ j : ℕ, zout.2.val ≤ j ∧ R.1.coeff j ≠ 0 := by
    by_contra hn
    push Not at hn
    exact houtR (boundedAffinePolynomialEquiv_coeff_eq_zero_of_tail_zero
      d zout.2.val (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm) R hn)
  rcases hj with ⟨j, hqj, hRj⟩
  have hRcoeff :
      R.1.coeff j =
        ∑ ξ : ZMod T, if (m : ZMod T) * ξ = zout.1 then
          ZMod.stdAddChar ((r : ZMod T) * ξ) * (ZMod.dft Q ξ).1.coeff j else 0 := by
    let f : ZMod T → DegreeBoundedPolynomial d := fun ξ =>
      if (m : ZMod T) * ξ = zout.1 then
        ZMod.stdAddChar ((r : ZMod T) * ξ) • ZMod.dft Q ξ else 0
    have hcoe :
        (↑(∑ ξ : ZMod T, f ξ) : Polynomial ℂ) =
          ∑ ξ : ZMod T, (↑(f ξ) : Polynomial ℂ) := by
      simp
    change (↑R : Polynomial ℂ).coeff j = _
    rw [show R = ∑ ξ : ZMod T, f ξ by rfl, hcoe]
    change Polynomial.lcoeff ℂ j (∑ ξ : ZMod T, (↑(f ξ) : Polynomial ℂ)) = _
    rw [map_sum]
    apply Finset.sum_congr rfl
    intro ξ _
    dsimp [f]
    by_cases hf : (m : ZMod T) * ξ = zout.1
    · simp [hf]
    · simp [hf]
  have hsum :
      (∑ ξ : ZMod T, if (m : ZMod T) * ξ = zout.1 then
          ZMod.stdAddChar ((r : ZMod T) * ξ) * (ZMod.dft Q ξ).1.coeff j else 0) ≠ 0 := by
    intro hz
    exact hRj (hRcoeff.trans hz)
  have hex : ∃ ξ : ZMod T,
      (if (m : ZMod T) * ξ = zout.1 then
          ZMod.stdAddChar ((r : ZMod T) * ξ) * (ZMod.dft Q ξ).1.coeff j else 0) ≠ 0 := by
    by_contra hn
    push Not at hn
    apply hsum
    exact Finset.sum_eq_zero (fun ξ _ => hn ξ)
  rcases hex with ⟨ξ, hterm⟩
  have hfreq : (m : ZMod T) * ξ = zout.1 := by
    by_contra hf
    simp [hf] at hterm
  have hcoeff : (ZMod.dft Q ξ).1.coeff j ≠ 0 := by
    intro hc
    simp [hfreq, hc] at hterm
  have hpoly : (ZMod.dft Q ξ).1 ≠ 0 := by
    intro hp
    apply hcoeff
    rw [hp, Polynomial.coeff_zero]
  have hnatdeg : (ZMod.dft Q ξ).1.natDegree < d + 1 := by
    exact (Polynomial.natDegree_lt_iff_degree_lt hpoly).2 (Polynomial.mem_degreeLT.mp (ZMod.dft Q ξ).2)
  have hjlt : j < d + 1 :=
    (Polynomial.le_natDegree_of_ne_zero hcoeff).trans_lt hnatdeg
  let jin : Fin (d + 1) := ⟨j, hjlt⟩
  let zin : FreqJetIdx T d := ⟨ξ, jin⟩
  have hzincoord : profileFourierJetEquiv T d Q zin ≠ 0 := by
    simpa [zin, jin, profileFourierJetEquiv_apply] using hcoeff
  have hzinS : freqJetShellLabel hT zin ∈ S := by
    by_contra hnot
    have hmask := hQ
    change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT S at hmask
    exact hzincoord (hmask zin hnot)
  refine ⟨zin, hzinS, ?_, ?_⟩
  · exact hfreq
  · simpa [zin, jin] using hqj

/-- Shell-level corollary: every nonzero output coordinate lies in the explicit upward/downward
closure of the input mask. -/
theorem nonzero_section_coord_label_mem_explicitClosure
    [NeZero T] (hT : 0 < T) (S : Set (ShellJetIdx T d))
    (m r : ℕ) (hm : 0 < m) (Q : DegreeBoundedProfile T d)
    (hQ : Q ∈ ShellJetMaskSubmodule hT S)
    (zout : FreqJetIdx T d)
    (hout : profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d m r hm Q) zout ≠ 0) :
    freqJetShellLabel hT zout ∈ ExplicitShellJetClosure S := by
  rcases nonzero_section_coord_has_source hT S m r hm Q hQ zout hout with
    ⟨zin, hzinS, hfreq, hjet⟩
  refine ⟨freqJetShellLabel hT zin, hzinS, ?_, hjet⟩
  change (frequencyShellIdx hT zin.1).1 ∣ (frequencyShellIdx hT zout.1).1
  rw [← hfreq]
  exact frequencyShellIdx_dvd_mul hT (m : ZMod T) zin.1

/-- The explicit upward/downward closure mask is stable under every positive affine section. -/
theorem ExplicitShellJetClosure_mask_invariant
    [NeZero T] (hT : 0 < T) (S : Set (ShellJetIdx T d)) :
    ShellJetMaskSectionInvariant hT (ExplicitShellJetClosure S) := by
  intro m r hm Q hQ
  change profileFourierJetEquiv T d (quasiPolynomialSectionProfile T d m r hm Q) ∈
    ShellJetCoordinateMask hT (ExplicitShellJetClosure S)
  intro zout hzout
  by_contra hout
  apply hzout
  rcases nonzero_section_coord_has_source hT (ExplicitShellJetClosure S)
      m r hm Q hQ zout hout with ⟨zin, hzin, hfreq, hjet⟩
  apply ExplicitShellJetClosure_trans hzin
  · change (frequencyShellIdx hT zin.1).1 ∣ (frequencyShellIdx hT zout.1).1
    rw [← hfreq]
    exact frequencyShellIdx_dvd_mul hT (m : ZMod T) zin.1
  · exact hjet

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.frequencyShellIdx_dvd_mul
#print axioms KomorebiCrossRadix.nonzero_section_coord_has_source
#print axioms KomorebiCrossRadix.ExplicitShellJetClosure_mask_invariant
