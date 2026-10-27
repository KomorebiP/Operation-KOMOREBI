import CrossRadixShellJetTransition
import Mathlib.Data.Nat.Choose.Basic

noncomputable section
open Polynomial
open scoped BigOperators

namespace KomorebiCrossRadix

local instance propDecidableShellJetNecessity (p : Prop) : Decidable p := Classical.propDecidable p

variable {T d : ℕ}

/-- The degree-bounded monomial occupying exactly jet `j`. -/
def boundedJetMonomial (d : ℕ) (j : Fin (d + 1)) : DegreeBoundedPolynomial d :=
  ⟨Polynomial.monomial j 1, Polynomial.monomial_coe_mem_degreeLT j 1⟩

/-- A profile whose DFT has exactly one frequency and one monomial jet. -/
def FourierJetAtomProfile [NeZero T] (d : ℕ) (ξ : ZMod T) (j : Fin (d + 1)) :
    DegreeBoundedProfile T d :=
  (ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)).symm
    (fun η => if η = ξ then boundedJetMonomial d j else 0)

@[simp] theorem dft_FourierJetAtomProfile [NeZero T]
    (d : ℕ) (ξ η : ZMod T) (j : Fin (d + 1)) :
    ZMod.dft (FourierJetAtomProfile d ξ j) η =
      if η = ξ then boundedJetMonomial d j else 0 := by
  have h := (ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)).apply_symm_apply
    (fun η : ZMod T => if η = ξ then boundedJetMonomial d j else 0)
  exact congrFun h η

@[simp] theorem FourierJetAtomProfile_coord [NeZero T]
    (d : ℕ) (ξ η : ZMod T) (j q : Fin (d + 1)) :
    profileFourierJetEquiv T d (FourierJetAtomProfile d ξ j) ⟨η, q⟩ =
      if η = ξ ∧ q = j then 1 else 0 := by
  rw [profileFourierJetEquiv_apply, dft_FourierJetAtomProfile]
  by_cases hη : η = ξ
  · subst η
    simp only [true_and]
    by_cases hq : q = j
    · subst q
      simp [boundedJetMonomial]
    · have hval : j.val ≠ q.val := by
        intro hv
        exact hq (Fin.ext hv.symm)
      simp only [hq]
      change (Polynomial.monomial j.val (1 : ℂ)).coeff q.val = 0
      rw [Polynomial.coeff_monomial]
      simp [hval]
  · simp [hη]

/-- A shell/jet mask containing the shell label also contains a pure atom in any frequency of that shell. -/
theorem FourierJetAtomProfile_mem_mask [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) (ξ : ZMod T) (j : Fin (d + 1))
    (hlabel : (frequencyShellIdx hT ξ, j) ∈ S) :
    FourierJetAtomProfile d ξ j ∈ ShellJetMaskSubmodule hT S := by
  change profileFourierJetEquiv T d (FourierJetAtomProfile d ξ j) ∈
    ShellJetCoordinateMask hT S
  intro z hz
  rw [FourierJetAtomProfile_coord]
  by_cases h : z.1 = ξ ∧ z.2 = j
  · rcases h with ⟨rfl, rfl⟩
    exact False.elim (hz hlabel)
  · simp [h]

/-- Canonical Fourier representative of a divisor shell. -/
def shellRepresentative (g : DivIdx T) : ZMod T := (g.1 : ZMod T)

@[simp] theorem frequencyShellIdx_shellRepresentative [NeZero T] (hT : 0 < T)
    (g : DivIdx T) :
    frequencyShellIdx hT (shellRepresentative g) = g := by
  apply Subtype.ext
  rw [frequencyShellIdx_val]
  have hgT : g.1 ∣ T := (Nat.mem_divisors.mp g.2).1
  have hgle : g.1 ≤ T := Nat.le_of_dvd hT hgT
  rcases hgle.eq_or_lt with hEq | hlt
  · simp [shellRepresentative, hEq]
  · rw [shellRepresentative, ZMod.val_natCast_of_lt hlt]
    exact Nat.gcd_eq_right_iff_dvd.mpr hgT

/-- If shell `g` divides shell `g'`, one positive multiplier sends their canonical representatives exactly. -/
theorem shellRepresentative_reachable [NeZero T] (hT : 0 < T)
    (g g' : DivIdx T) (hgg' : g.1 ∣ g'.1) :
    ∃ m : ℕ, 0 < m ∧ (m : ZMod T) * shellRepresentative g = shellRepresentative g' := by
  have hg'T : g'.1 ∣ T := (Nat.mem_divisors.mp g'.2).1
  have hg'pos : 0 < g'.1 := Nat.pos_of_dvd_of_pos hg'T hT
  have hgpos : 0 < g.1 := Nat.pos_of_dvd_of_pos hgg' hg'pos
  let m := g'.1 / g.1
  have hm : 0 < m := Nat.div_pos (Nat.le_of_dvd hg'pos hgg') hgpos
  refine ⟨m, hm, ?_⟩
  change ((m : ℕ) : ZMod T) * ((g.1 : ℕ) : ZMod T) = ((g'.1 : ℕ) : ZMod T)
  rw [← Nat.cast_mul]
  congr 1
  exact Nat.div_mul_cancel hgg'


/-- With zero translation, a pure Fourier/jet atom survives at the multiplied frequency and the same jet. -/
theorem FourierJetAtomProfile_shell_transport_nonzero [NeZero T]
    (d m : ℕ) (hm : 0 < m) (ξ η : ZMod T) (j : Fin (d + 1))
    (hfreq : (m : ZMod T) * ξ = η) :
    profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d m 0 hm (FourierJetAtomProfile d ξ j)) ⟨η, j⟩ ≠ 0 := by
  rw [profileFourierJetEquiv_apply, dft_quasiPolynomialSectionProfile]
  simp only [Nat.cast_zero, zero_mul]
  have hchar0 : ZMod.stdAddChar (0 : ZMod T) = (1 : ℂ) := by
    exact (ZMod.stdAddChar (N := T)).map_zero_eq_one
  simp only [hchar0, one_smul]
  have hsum :
      (∑ ζ : ZMod T, if (m : ZMod T) * ζ = η then
          ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0) =
        boundedJetMonomial d j := by
    classical
    let F : ZMod T → DegreeBoundedPolynomial d := fun ζ =>
      if (m : ZMod T) * ζ = η then ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0
    calc
      (∑ ζ : ZMod T, if (m : ZMod T) * ζ = η then
          ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0) = ∑ ζ : ZMod T, F ζ := rfl
      _ = F ξ := by
        apply Finset.sum_eq_single ξ
        · intro ζ _ hζ
          simp [F, dft_FourierJetAtomProfile, hζ]
        · intro hnot
          exact False.elim (hnot (Finset.mem_univ ξ))
      _ = boundedJetMonomial d j := by
        simp [F, dft_FourierJetAtomProfile, hfreq]
  rw [hsum, boundedAffinePolynomialEquiv_coeff_hasse]
  have hmC : (m : ℂ) ≠ 0 := natCast_complex_ne_zero_of_pos hm
  simp [boundedJetMonomial, Polynomial.hasseDeriv_monomial, hmC]



/-- Necessity of divisor-upward shell closure for every section-invariant shell/jet mask. -/
theorem invariant_mask_shell_upward [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) (hInv : ShellJetMaskSectionInvariant hT S)
    (g g' : DivIdx T) (j : Fin (d + 1))
    (hgj : (g, j) ∈ S) (hgg' : g.1 ∣ g'.1) :
    (g', j) ∈ S := by
  rcases shellRepresentative_reachable hT g g' hgg' with ⟨m, hm, hfreq⟩
  let ξ := shellRepresentative g
  let η := shellRepresentative g'
  let Q := FourierJetAtomProfile d ξ j
  have hQ : Q ∈ ShellJetMaskSubmodule hT S := by
    apply FourierJetAtomProfile_mem_mask hT
    simpa [ξ, frequencyShellIdx_shellRepresentative hT] using hgj
  have hsec := hInv m 0 hm Q hQ
  change profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d m 0 hm Q) ∈ ShellJetCoordinateMask hT S at hsec
  have hnz : profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d m 0 hm Q) ⟨η, j⟩ ≠ 0 := by
    apply FourierJetAtomProfile_shell_transport_nonzero d m hm ξ η j
    exact hfreq
  by_contra hnot
  have hznot : freqJetShellLabel hT (⟨η, j⟩ : FreqJetIdx T d) ∉ S := by
    simpa [η, freqJetShellLabel, frequencyShellIdx_shellRepresentative hT] using hnot
  exact hnz (hsec ⟨η, j⟩ hznot)


/-- Translation by one of a pure Fourier/jet atom creates every lower jet at the same frequency. -/
theorem FourierJetAtomProfile_jet_transport_nonzero [NeZero T]
    (d : ℕ) (ξ : ZMod T) (j q : Fin (d + 1)) (hqj : q.val ≤ j.val) :
    profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d 1 1 (by decide)
        (FourierJetAtomProfile d ξ j)) ⟨ξ, q⟩ ≠ 0 := by
  rw [profileFourierJetEquiv_apply, dft_quasiPolynomialSectionProfile]
  have hsum :
      (∑ ζ : ZMod T, if ((1 : ℕ) : ZMod T) * ζ = ξ then
          ZMod.stdAddChar (((1 : ℕ) : ZMod T) * ζ) •
            ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0) =
        ZMod.stdAddChar ξ • boundedJetMonomial d j := by
    classical
    let F : ZMod T → DegreeBoundedPolynomial d := fun ζ =>
      if ((1 : ℕ) : ZMod T) * ζ = ξ then
        ZMod.stdAddChar (((1 : ℕ) : ZMod T) * ζ) •
          ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0
    calc
      (∑ ζ : ZMod T, if ((1 : ℕ) : ZMod T) * ζ = ξ then
          ZMod.stdAddChar (((1 : ℕ) : ZMod T) * ζ) •
            ZMod.dft (FourierJetAtomProfile d ξ j) ζ else 0) = ∑ ζ : ZMod T, F ζ := rfl
      _ = F ξ := by
        apply Finset.sum_eq_single ξ
        · intro ζ _ hζ
          simp [F, dft_FourierJetAtomProfile, hζ]
        · intro hnot
          exact False.elim (hnot (Finset.mem_univ ξ))
      _ = ZMod.stdAddChar ξ • boundedJetMonomial d j := by
        simp [F, dft_FourierJetAtomProfile]
  rw [hsum, boundedAffinePolynomialEquiv_coeff_hasse]
  have hphase : ZMod.stdAddChar ξ ≠ (0 : ℂ) := by
    rw [ZMod.stdAddChar_apply]
    exact Circle.coe_ne_zero _
  have hchoose : (j.val.choose q.val : ℂ) ≠ 0 := by
    exact_mod_cast (Nat.choose_pos hqj).ne'
  simp [boundedJetMonomial, Polynomial.hasseDeriv_monomial, hphase, hchoose]

/-- Necessity of jet-downward closure for every section-invariant shell/jet mask. -/
theorem invariant_mask_jet_downward [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) (hInv : ShellJetMaskSectionInvariant hT S)
    (g : DivIdx T) (j q : Fin (d + 1))
    (hgj : (g, j) ∈ S) (hqj : q.val ≤ j.val) :
    (g, q) ∈ S := by
  let ξ := shellRepresentative g
  let Q := FourierJetAtomProfile d ξ j
  have hQ : Q ∈ ShellJetMaskSubmodule hT S := by
    apply FourierJetAtomProfile_mem_mask hT
    simpa [ξ, frequencyShellIdx_shellRepresentative hT] using hgj
  have hsec := hInv 1 1 (by decide) Q hQ
  change profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d 1 1 (by decide) Q) ∈ ShellJetCoordinateMask hT S at hsec
  have hnz : profileFourierJetEquiv T d
      (quasiPolynomialSectionProfile T d 1 1 (by decide) Q) ⟨ξ, q⟩ ≠ 0 := by
    exact FourierJetAtomProfile_jet_transport_nonzero d ξ j q hqj
  by_contra hnot
  have hznot : freqJetShellLabel hT (⟨ξ, q⟩ : FreqJetIdx T d) ∉ S := by
    simpa [ξ, freqJetShellLabel, frequencyShellIdx_shellRepresentative hT] using hnot
  exact hnz (hsec ⟨ξ, q⟩ hznot)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.FourierJetAtomProfile_mem_mask
#print axioms KomorebiCrossRadix.shellRepresentative_reachable
#print axioms KomorebiCrossRadix.FourierJetAtomProfile_shell_transport_nonzero
#print axioms KomorebiCrossRadix.invariant_mask_shell_upward
#print axioms KomorebiCrossRadix.FourierJetAtomProfile_jet_transport_nonzero
#print axioms KomorebiCrossRadix.invariant_mask_jet_downward
