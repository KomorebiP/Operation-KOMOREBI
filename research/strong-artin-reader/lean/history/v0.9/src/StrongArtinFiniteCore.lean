module

public import Mathlib.Data.ZMod.Basic
public import Mathlib.Algebra.CharP.Reduced
public import Mathlib.Algebra.Polynomial.Eval.Coeff
public import Mathlib.Algebra.Polynomial.Roots
public import Mathlib.Data.Sym.Card
public import Mathlib.Analysis.Fourier.ZMod
public import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar
public import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff
public import Mathlib.LinearAlgebra.Charpoly.ToMatrix
public import Mathlib.LinearAlgebra.Matrix.Charpoly.FiniteField
public import Mathlib.LinearAlgebra.Determinant
public import Mathlib.LinearAlgebra.Matrix.Trace
public import Mathlib.LinearAlgebra.Eigenspace.Charpoly
public import Mathlib.LinearAlgebra.BilinearMap
public import Mathlib.LinearAlgebra.Basis.Basic
public import Mathlib.LinearAlgebra.Basis.VectorSpace
public import Mathlib.RingTheory.SimpleModule.IsAlgClosed
public import Mathlib.RingTheory.Morita.Matrix
public import Mathlib.LinearAlgebra.Trace
public import Mathlib.LinearAlgebra.StdBasis
public import Mathlib.LinearAlgebra.Projection
public import Mathlib.Tactic
public import Mathlib.GroupTheory.QuotientGroup.Finite
public import Mathlib.GroupTheory.Index
public import Mathlib.GroupTheory.OrderOfElement
public import Mathlib.RingTheory.DedekindDomain.Ideal.Lemmas
public import Mathlib.RingTheory.Ideal.Quotient.Basic
public import Mathlib.RepresentationTheory.Irreducible
public import Mathlib.RepresentationTheory.Character
public import Mathlib.RepresentationTheory.FinGroupCharZero
public import Mathlib.GroupTheory.GroupAction.Quotient
public import Mathlib.LinearAlgebra.Dimension.Free
public import Mathlib.RepresentationTheory.Semisimple
public import Mathlib.RepresentationTheory.Induced
public import Mathlib.RepresentationTheory.FiniteIndex
public import Mathlib.RingTheory.Jacobson.Semiprimary
public import Mathlib.RingTheory.Nilpotent.Lemmas
public import Mathlib.RingTheory.KrullDimension.Basic
public import Mathlib.Algebra.CharP.Algebra
public import Mathlib.RingTheory.Artinian.Module
public import Mathlib.Algebra.Module.Torsion.Basic
public import Mathlib.Algebra.MonoidAlgebra.MapDomain
public import Mathlib.GroupTheory.GroupAction.ConjAct

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.StrongArtin.FiniteCore

/-!
# Finite cyclic-label core for the Strong Artin papers

This file deliberately formalizes only the finite exact algebra that occurs at a
prime cyclic Clifford step.  It does not encode automorphic base change,
Chebotarev, local Langlands, or a global Strong Artin attachment theorem.
-/

universe u

variable (p : ℕ) [Fact p.Prime]

/-- The quotient-character label group at a prime cyclic step. -/
abbrev Label := ZMod p

/-- Multiplicity spectrum of one stable type. -/
abbrev Spectrum := Label p → ℕ

/-- Quotient twisting rotates the cyclic multiplicity spectrum. -/
def rotate (j : Label p) (P : Spectrum p) : Spectrum p :=
  fun a => P (a - j)

@[simp] theorem rotate_zero (P : Spectrum p) :
    rotate p 0 P = P := by
  funext a
  simp [rotate]

@[simp] theorem rotate_add (j k : Label p) (P : Spectrum p) :
    rotate p j (rotate p k P) = rotate p (j + k) P := by
  funext a
  simp [rotate]
  congr 1
  abel

@[simp] theorem rotate_neg_cancel (j : Label p) (P : Spectrum p) :
    rotate p (-j) (rotate p j P) = P := by
  rw [rotate_add]
  simp

/-- Rotation by a fixed quotient character is a bijection on spectra. -/
def rotateEquiv (j : Label p) : Spectrum p ≃ Spectrum p where
  toFun := rotate p j
  invFun := rotate p (-j)
  left_inv P := rotate_neg_cancel p j P
  right_inv P := by
    rw [rotate_add]
    simp

/-- A family indexed by stable irreducible types. -/
abbrev SpectrumFamily (α : Type u) := α → Spectrum p

/-- One common quotient twist aligns all stable-type spectra. -/
def Aligned {α : Type u}
    (V W : SpectrumFamily p α) (j : Label p) : Prop :=
  ∀ τ, W τ = rotate p j (V τ)

/-- A quotient rotation stabilizes every stable-type spectrum. -/
def Stabilizes {α : Type u}
    (V : SpectrumFamily p α) (s : Label p) : Prop :=
  ∀ τ, rotate p s (V τ) = V τ

@[simp] theorem stabilizes_zero {α : Type u} (V : SpectrumFamily p α) :
    Stabilizes p V 0 := by
  intro τ
  exact rotate_zero p (V τ)

/-- Stabilizers are closed under addition. -/
theorem stabilizes_add {α : Type u} (V : SpectrumFamily p α)
    {s t : Label p} (hs : Stabilizes p V s) (ht : Stabilizes p V t) :
    Stabilizes p V (s + t) := by
  intro τ
  rw [← rotate_add]
  rw [ht τ, hs τ]

/-- Stabilizers are closed under negation. -/
theorem stabilizes_neg {α : Type u} (V : SpectrumFamily p α)
    {s : Label p} (hs : Stabilizes p V s) :
    Stabilizes p V (-s) := by
  intro τ
  have h := congrArg (rotate p (-s)) (hs τ)
  simpa using h.symm

/-- Once one alignment index exists, translating it by any common stabilizer
produces another alignment index. -/
theorem aligned_add_stabilizer {α : Type u}
    (V W : SpectrumFamily p α) {j s : Label p}
    (hj : Aligned p V W j) (hs : Stabilizes p V s) :
    Aligned p V W (j + s) := by
  intro τ
  rw [hj τ, ← rotate_add, hs τ]

/-- Two alignment indices differ by a common rotational stabilizer. -/
theorem aligned_difference_stabilizes {α : Type u}
    (V W : SpectrumFamily p α) {j₁ j₂ : Label p}
    (h₁ : Aligned p V W j₁) (h₂ : Aligned p V W j₂) :
    Stabilizes p V (j₂ - j₁) := by
  intro τ
  have h : rotate p j₁ (V τ) = rotate p j₂ (V τ) := by
    rw [← h₁ τ, ← h₂ τ]
  have h' := congrArg (rotate p (-j₁)) h
  simpa [sub_eq_add_neg, add_comm, add_left_comm, add_assoc] using h'.symm

/-- A spectrum is aperiodic when no nonzero quotient rotation fixes it. -/
def Aperiodic (P : Spectrum p) : Prop :=
  ∀ s : Label p, rotate p s P = P → s = 0

/-- One aperiodic stable type makes a global alignment index unique. -/
theorem aligned_unique_of_aperiodic {α : Type u}
    (V W : SpectrumFamily p α) (τ₀ : α)
    (haper : Aperiodic p (V τ₀))
    {j₁ j₂ : Label p}
    (h₁ : Aligned p V W j₁) (h₂ : Aligned p V W j₂) :
    j₁ = j₂ := by
  have hs := aligned_difference_stabilizes p V W h₁ h₂
  have hz : j₂ - j₁ = 0 := haper (j₂ - j₁) (hs τ₀)
  exact sub_eq_zero.mp hz |>.symm

/-- The alignment set of two stable-type spectrum families. -/
def alignmentSet {α : Type u}
    (V W : SpectrumFamily p α) : Set (Label p) :=
  {j | Aligned p V W j}

/-- The common rotational stabilizer set. -/
def stabilizerSet {α : Type u}
    (V : SpectrumFamily p α) : Set (Label p) :=
  {s | Stabilizes p V s}

/-- Exact coset description around any known alignment index. -/
theorem mem_alignmentSet_iff_difference_stabilizes {α : Type u}
    (V W : SpectrumFamily p α) {j₀ : Label p}
    (h₀ : Aligned p V W j₀) (j : Label p) :
    j ∈ alignmentSet p V W ↔ j - j₀ ∈ stabilizerSet p V := by
  constructor
  · intro hj
    exact aligned_difference_stabilizes p V W h₀ hj
  · intro hs
    change Stabilizes p V (j - j₀) at hs
    change Aligned p V W j
    have hsum := aligned_add_stabilizer p V W h₀ hs
    have hj : j₀ + (j - j₀) = j := by abel
    rw [← hj]
    exact hsum



/-! ## Torsor blindness of total cyclic aggregation -/

/-- The full cyclic orbit of one extension spectrum. -/
def spectrumOrbit (P : Spectrum p) : Set (Spectrum p) :=
  Set.range (fun j : Label p => rotate p j P)

/-- Replacing an extension by any quotient twist only permutes its full cyclic
orbit. This is the spectrum-level exact core of "total induction is torsor
blind". -/
theorem spectrumOrbit_rotate (s : Label p) (P : Spectrum p) :
    spectrumOrbit p (rotate p s P) = spectrumOrbit p P := by
  ext Q
  constructor
  · rintro ⟨j, rfl⟩
    refine ⟨j + s, ?_⟩
    exact (rotate_add p j s P).symm
  · rintro ⟨k, rfl⟩
    refine ⟨k - s, ?_⟩
    change rotate p (k - s) (rotate p s P) = rotate p k P
    rw [rotate_add]
    have h : k - s + s = k := by abel
    rw [h]

/-- Total stable-type multiplicity, the augmentation of the cyclic spectrum. -/
def augmentation (P : Spectrum p) : ℕ :=
  ∑ a : Label p, P a

/-- Quotient twisting preserves the augmentation. At the spectrum level this
is precisely the information that remains when all cyclic labels are forgotten. -/
theorem augmentation_rotate (j : Label p) (P : Spectrum p) :
    augmentation p (rotate p j P) = augmentation p P := by
  unfold augmentation rotate
  let e : Label p ≃ Label p := Equiv.addRight (-j)
  simpa [e, sub_eq_add_neg] using Equiv.sum_comp e P

/-- All members of one cyclic extension orbit have identical augmentation. -/
theorem augmentation_eq_of_mem_orbit (P Q : Spectrum p)
    (hQ : Q ∈ spectrumOrbit p P) :
    augmentation p Q = augmentation p P := by
  rcases hQ with ⟨j, rfl⟩
  exact augmentation_rotate p j P


/-! ## Actual complex Fourier coordinates of cyclic extension spectra -/

section SpectrumFourier

open scoped ZMod

/-- Embed a multiplicity spectrum into complex-valued functions. -/
def spectrumComplex (P : Spectrum p) : Label p → ℂ :=
  fun a => (P a : ℂ)

/-- Fourier coordinate in the sign convention of the Strong Artin manuscript.
Mathlib's `ZMod.dft` uses the negative exponential; evaluating it at `-r`
produces the positive phase `ζ^(ar)` convention used in the paper. -/
def spectrumFourier (P : Spectrum p) (r : Label p) : ℂ :=
  ZMod.dft (spectrumComplex p P) (-r)

/-- The Fourier transform of a quotient-twisted spectrum acquires exactly the
corresponding cyclic phase factor. -/
theorem spectrumFourier_rotate (j r : Label p) (P : Spectrum p) :
    spectrumFourier p (rotate p j P) r =
      ZMod.stdAddChar (j * r) * spectrumFourier p P r := by
  classical
  unfold spectrumFourier spectrumComplex rotate
  rw [ZMod.dft_apply, ZMod.dft_apply]
  simp only [smul_eq_mul]
  let e : Label p ≃ Label p := Equiv.addRight j
  have hs := Equiv.sum_comp e
    (fun a : Label p =>
      ZMod.stdAddChar (- (a * (-r))) * (P (a - j) : ℂ))
  rw [← hs]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro a ha
  change ZMod.stdAddChar (-((a + j) * (-r))) * (P (a + j - j) : ℂ) =
    ZMod.stdAddChar (j * r) *
      (ZMod.stdAddChar (-(a * (-r))) * (P a : ℂ))
  have hsub : a + j - j = a := by abel
  rw [hsub]
  have hphase : -((a + j) * (-r)) = j * r + (-(a * (-r))) := by ring
  rw [hphase, AddChar.map_add_eq_mul]
  ring

/-- Equality of all Fourier coordinates determines the original spectrum. -/
theorem spectrumFourier_injective :
    Function.Injective (fun P : Spectrum p => fun r => spectrumFourier p P r) := by
  intro P Q h
  have hdft : ZMod.dft (spectrumComplex p P) = ZMod.dft (spectrumComplex p Q) := by
    funext r
    have hr := congrFun h (-r)
    simpa [spectrumFourier] using hr
  have hc : spectrumComplex p P = spectrumComplex p Q := ZMod.dft.injective hdft
  funext a
  have ha := congrFun hc a
  simp only [spectrumComplex] at ha
  exact_mod_cast ha

/-- Fourier attachment criterion, exact finite version: a common cyclic shift of
all Fourier coordinates is equivalent to rotation of the underlying spectrum. -/
theorem spectrum_eq_rotate_iff_fourier
    (V W : Spectrum p) (j : Label p) :
    W = rotate p j V ↔
      ∀ r : Label p,
        spectrumFourier p W r =
          ZMod.stdAddChar (j * r) * spectrumFourier p V r := by
  constructor
  · rintro rfl r
    exact spectrumFourier_rotate p j r V
  · intro h
    apply spectrumFourier_injective p
    funext r
    change spectrumFourier p W r = spectrumFourier p (rotate p j V) r
    rw [spectrumFourier_rotate]
    exact h r

/-- Family version of the exact Fourier attachment criterion used in the
cyclic extension-spectrum theorem. -/
theorem aligned_iff_fourier {α : Type u}
    (V W : SpectrumFamily p α) (j : Label p) :
    Aligned p V W j ↔
      ∀ τ r,
        spectrumFourier p (W τ) r =
          ZMod.stdAddChar (j * r) * spectrumFourier p (V τ) r := by
  constructor
  · intro h τ r
    exact (spectrum_eq_rotate_iff_fourier p (V τ) (W τ) j).mp (h τ) r
  · intro h τ
    exact (spectrum_eq_rotate_iff_fourier p (V τ) (W τ) j).mpr (h τ)

end SpectrumFourier

/-! ## Rank-prime selector algebra -/

/-- Abstract label transformation induced by taking an `n`th determinant power
on a cyclic quotient character. In additive `ZMod p` notation this is
multiplication by `n`. -/
def powerLabel (n : ℕ) (j : Label p) : Label p := (n : ZMod p) * j

/-- If the rank is nonzero modulo the quotient prime, the determinant-power
label map is injective. -/
theorem powerLabel_injective (n : ℕ) (hn : (n : ZMod p) ≠ 0) :
    Function.Injective (powerLabel p n) := by
  intro a b hab
  unfold powerLabel at hab
  exact mul_left_cancel₀ hn hab

/-- If the rank is nonzero modulo the quotient prime, every target determinant
label has a unique cyclic twist preimage. -/
theorem existsUnique_powerLabel_eq (n : ℕ) (hn : (n : ZMod p) ≠ 0)
    (δ : Label p) :
    ∃! j : Label p, powerLabel p n j = δ := by
  refine ⟨(n : ZMod p)⁻¹ * δ, ?_, ?_⟩
  · simp [powerLabel, hn]
  · intro y hy
    apply powerLabel_injective p n hn
    rw [hy]
    simp [powerLabel, hn]



/-- The manuscript hypothesis `p ∤ n` is exactly the nonvanishing condition
needed by the rank-power selector in `ZMod p`. -/
theorem rank_nonzero_mod_prime (n : ℕ) (hn : ¬ p ∣ n) :
    (n : ZMod p) ≠ 0 := by
  rw [Ne, ZMod.natCast_eq_zero_iff]
  exact hn

/-- Rank-prime sieve, injective form. -/
theorem powerLabel_injective_of_not_dvd (n : ℕ) (hn : ¬ p ∣ n) :
    Function.Injective (powerLabel p n) :=
  powerLabel_injective p n (rank_nonzero_mod_prime p n hn)

/-- Rank-prime sieve, unique-preimage form. -/
theorem existsUnique_powerLabel_eq_of_not_dvd
    (n : ℕ) (hn : ¬ p ∣ n) (δ : Label p) :
    ∃! j : Label p, powerLabel p n j = δ :=
  existsUnique_powerLabel_eq p n (rank_nonzero_mod_prime p n hn) δ

/-! ## Nonzero Fourier-mode selector algebra -/

/-- Exponent label appearing in the Fourier twist factor `ζ^(jr)`. -/
def modeLabel (r j : Label p) : Label p := j * r

/-- Every nonzero Fourier mode is an injective cyclic-label probe. -/
theorem modeLabel_injective (r : Label p) (hr : r ≠ 0) :
    Function.Injective (modeLabel p r) := by
  intro j₁ j₂ h
  unfold modeLabel at h
  exact mul_right_cancel₀ hr h

/-- If a primitive phase encoding is injective, one nonzero Fourier phase
`phase (j*r)` uniquely determines the cyclic attachment label `j`. -/
theorem one_nonzero_fourier_phase_selects
    {β : Type*} (phase : Label p → β) (hphase : Function.Injective phase)
    (r : Label p) (hr : r ≠ 0) {j₁ j₂ : Label p}
    (h : phase (modeLabel p r j₁) = phase (modeLabel p r j₂)) :
    j₁ = j₂ := by
  apply modeLabel_injective p r hr
  exact hphase h

/-- Ratio-form abstraction of the manuscript's one-nonzero-Fourier-mode test:
if two candidate labels produce the same primitive phase ratio at a nonzero
mode, they are equal. -/
theorem fourier_ratio_candidate_unique
    {β : Type*} (phase : Label p → β) (hphase : Function.Injective phase)
    (r : Label p) (hr : r ≠ 0) (ratio : β)
    {j₁ j₂ : Label p}
    (h₁ : ratio = phase (modeLabel p r j₁))
    (h₂ : ratio = phase (modeLabel p r j₂)) :
    j₁ = j₂ := by
  apply one_nonzero_fourier_phase_selects p phase hphase r hr
  exact h₁.symm.trans h₂

/-- A determinant-like observable transforming equivariantly by the rank-power
map selects at most one cyclic label whenever the rank is nonzero mod `p`. -/
theorem equivariant_selector_unique
    {A : Type*} [SMul (Label p) A]
    (n : ℕ) (hn : (n : ZMod p) ≠ 0)
    (obs : A → Label p)
    (hobs : ∀ (x : A) (j : Label p),
      obs (j • x) = obs x + powerLabel p n j)
    (x : A) (target : Label p)
    {j₁ j₂ : Label p}
    (h₁ : obs (j₁ • x) = target)
    (h₂ : obs (j₂ • x) = target) :
    j₁ = j₂ := by
  apply powerLabel_injective p n hn
  have e₁ := hobs x j₁
  have e₂ := hobs x j₂
  rw [h₁] at e₁
  rw [h₂] at e₂
  exact add_left_cancel (e₁.symm.trans e₂)


/-- Determinant/central-character selector with the literal manuscript
hypothesis `p ∤ n`. -/
theorem equivariant_selector_unique_of_not_dvd
    {A : Type*} [SMul (Label p) A]
    (n : ℕ) (hn : ¬ p ∣ n)
    (obs : A → Label p)
    (hobs : ∀ (x : A) (j : Label p),
      obs (j • x) = obs x + powerLabel p n j)
    (x : A) (target : Label p)
    {j₁ j₂ : Label p}
    (h₁ : obs (j₁ • x) = target)
    (h₂ : obs (j₂ • x) = target) :
    j₁ = j₂ :=
  equivariant_selector_unique p n (rank_nonzero_mod_prime p n hn)
    obs hobs x target h₁ h₂


/-! ## Quotient-prime Frobenius cancellation core -/

section FrobeniusCancellation

variable {k : Type*} [CommRing k] [IsReduced k] [ExpChar k p]

/-- Coefficientwise Frobenius on a residue-field polynomial. This is the
reduced polynomial operation appearing after the manuscript's root-power
Frobenius transform. -/
def coeffFrobenius (P : Polynomial k) : Polynomial k :=
  P.map (frobenius k p)

omit [Fact p.Prime] in
/-- Frobenius on coefficients is injective over every reduced ring of
exponential characteristic `p`; in particular over a residue field. -/
theorem coeffFrobenius_injective :
    Function.Injective (coeffFrobenius (p := p) : Polynomial k → Polynomial k) := by
  exact Polynomial.map_injective (frobenius k p) (frobenius_inj k p)

omit [Fact p.Prime] in
/-- Equality after coefficient Frobenius can be cancelled. This is the exact
finite algebraic cancellation used in the nonsplit quotient-prime comparison. -/
theorem eq_of_coeffFrobenius_eq {P Q : Polynomial k}
    (h : coeffFrobenius (p := p) P = coeffFrobenius (p := p) Q) :
    P = Q :=
  coeffFrobenius_injective (p := p) h

universe uβ
variable {β : Type uβ} [Fintype β]

/-- A monic split polynomial from a finite indexed multiset of roots. -/
def splitPolynomial (roots : β → k) : Polynomial k :=
  ∏ i, (Polynomial.X - Polynomial.C (roots i))

/-- The manuscript's root-power transform on a supplied splitting: raise every
root to the `p`th power and rebuild the monic polynomial. -/
def rootPowerPolynomial (roots : β → k) : Polynomial k :=
  ∏ i, (Polynomial.X - Polynomial.C ((roots i) ^ p))

omit [Fact p.Prime] [IsReduced k] in
/-- In exponential characteristic `p`, the root-power transform is exactly
coefficientwise Frobenius on a split polynomial. -/
theorem coeffFrobenius_splitPolynomial (roots : β → k) :
    coeffFrobenius (p := p) (splitPolynomial roots) =
      rootPowerPolynomial (p := p) roots := by
  classical
  unfold coeffFrobenius splitPolynomial rootPowerPolynomial
  change Polynomial.mapRingHom (frobenius k p)
      (∏ i, (Polynomial.X - Polynomial.C (roots i))) = _
  rw [map_prod]
  apply Finset.prod_congr rfl
  intro i hi
  simp [frobenius_def]

omit [Fact p.Prime] in
/-- Root-power cancellation after reduction: equality of the `p`th-root-power
transforms forces equality of the original split polynomials over any reduced
ring of exponential characteristic `p`. -/
theorem eq_splitPolynomial_of_rootPowerPolynomial_eq
    {roots₁ roots₂ : β → k}
    (h : rootPowerPolynomial (p := p) roots₁ =
      rootPowerPolynomial (p := p) roots₂) :
    splitPolynomial roots₁ = splitPolynomial roots₂ := by
  apply eq_of_coeffFrobenius_eq (p := p)
  rw [coeffFrobenius_splitPolynomial, coeffFrobenius_splitPolynomial]
  exact h

end FrobeniusCancellation


/-! ## Finite trace-alphabet counting core -/

section TraceAlphabetCounting

universe uΓ uT

variable {Γ : Type uΓ} {T : Type uT} [Fintype Γ] [Fintype T]

/-- Once a finite object embeds in `d` coordinates drawn from an alphabet `T`,
its cardinality is at most `|T|^d`. -/
theorem card_le_alphabet_pow_of_injective
    (d : ℕ) (Φ : Γ → (Fin d → T)) (hΦ : Function.Injective Φ) :
    Fintype.card Γ ≤ Fintype.card T ^ d := by
  have hcard := Fintype.card_le_of_injective Φ hΦ
  simpa only [Fintype.card_pi_const] using hcard

/-- The precise counting step in the paper's finite trace image theorem: if the
trace-coordinate embedding uses at most `n^2` coordinates, then the image has
size at most `t^(n^2)`. -/
theorem finite_trace_bound_from_coordinate_embedding
    (n d : ℕ) (Φ : Γ → (Fin d → T))
    (hΦ : Function.Injective Φ)
    (hT : 0 < Fintype.card T)
    (hd : d ≤ n ^ 2) :
    Fintype.card Γ ≤ Fintype.card T ^ (n ^ 2) := by
  exact (card_le_alphabet_pow_of_injective d Φ hΦ).trans
    (Nat.pow_le_pow_right hT hd)

section GroupCoordinates

variable [Group Γ]

/-- Trace-coordinate map associated with a finite list of group test elements.
The codomain `T` is an abstract finite trace alphabet. -/
def traceCoordinates (d : ℕ) (tr : Γ → T) (test : Fin d → Γ) :
    Γ → (Fin d → T) :=
  fun γ i => tr (γ * test i)

/-- If nondegeneracy/separation of the trace pairing has already supplied
injectivity of the trace-coordinate map, the stated `t^(n^2)` bound follows
purely finitely. -/
theorem finite_trace_image_bound_certificate
    (n d : ℕ) (tr : Γ → T) (test : Fin d → Γ)
    (hsep : Function.Injective (traceCoordinates d tr test))
    (hT : 0 < Fintype.card T)
    (hd : d ≤ n ^ 2) :
    Fintype.card Γ ≤ Fintype.card T ^ (n ^ 2) :=
  finite_trace_bound_from_coordinate_embedding n d
    (traceCoordinates d tr test) hsep hT hd

end GroupCoordinates

/-! ### Nondegenerate trace-pairing certificate -/

section PairingCoordinates

universe uK uA
variable {K : Type uK} [Field K]
variable {A : Type uA} [AddCommGroup A] [Module K A]
variable [Group Γ]

omit [Fintype Γ] [Fintype T] in
/-- Abstract finite-image-algebra certificate matching the core of the paper's
trace-bound proof. A basis of the image algebra is represented by group
elements, and a nondegenerate bilinear trace pairing evaluates on group pairs
through the finite trace alphabet `T`. These hypotheses force the trace
coordinate map to separate group elements. -/
theorem traceCoordinates_injective_of_nondegenerate_pairing
    (d : ℕ)
    (ρ : Γ → A) (hρ : Function.Injective ρ)
    (test : Fin d → Γ)
    (b : Module.Basis (Fin d) K A)
    (hb : ∀ i, b i = ρ (test i))
    (B : A →ₗ[K] A →ₗ[K] K)
    (hnondeg : ∀ x : A, B x = 0 → x = 0)
    (tr : Γ → T) (val : T → K)
    (htrace : ∀ γ δ : Γ, B (ρ γ) (ρ δ) = val (tr (γ * δ))) :
    Function.Injective (traceCoordinates d tr test) := by
  intro γ γ' hcoord
  apply hρ
  have hB : B (ρ γ - ρ γ') = 0 := by
    apply b.ext
    intro i
    simp only [LinearMap.zero_apply]
    rw [hb i]
    simp only [map_sub]
    change B (ρ γ) (ρ (test i)) - B (ρ γ') (ρ (test i)) = 0
    rw [htrace, htrace]
    have hc := congrFun hcoord i
    exact sub_eq_zero.mpr (congrArg val hc)
  exact sub_eq_zero.mp (hnondeg (ρ γ - ρ γ') hB)

/-- The full cardinality conclusion from a nondegenerate trace-pairing
certificate. This removes the raw injectivity assumption from the earlier
counting theorem and derives it from the image-algebra basis and pairing data. -/
theorem finite_trace_image_bound_from_pairing
    (n d : ℕ)
    (ρ : Γ → A) (hρ : Function.Injective ρ)
    (test : Fin d → Γ)
    (b : Module.Basis (Fin d) K A)
    (hb : ∀ i, b i = ρ (test i))
    (B : A →ₗ[K] A →ₗ[K] K)
    (hnondeg : ∀ x : A, B x = 0 → x = 0)
    (tr : Γ → T) (val : T → K)
    (htrace : ∀ γ δ : Γ, B (ρ γ) (ρ δ) = val (tr (γ * δ)))
    (hd : d ≤ n ^ 2) :
    Fintype.card Γ ≤ Fintype.card T ^ (n ^ 2) := by
  have hsep := traceCoordinates_injective_of_nondegenerate_pairing
    (Γ := Γ) (T := T) d ρ hρ test b hb B hnondeg tr val htrace
  have hT : 0 < Fintype.card T := by
    exact Fintype.card_pos_iff.mpr ⟨tr 1⟩
  exact finite_trace_bound_from_coordinate_embedding n d
    (traceCoordinates d tr test) hsep hT hd


omit [Fintype Γ] [Group Γ] in
/-- If the group-image vectors span the finite image algebra, one can choose a
basis consisting entirely of actual group-image vectors.  This formalizes the
manuscript step “choose a basis `γ₁,…,γ_d ∈ Γ` of the image algebra”. -/
theorem exists_group_image_basis_of_span
    (ρ : Γ → A)
    (hspan : Submodule.span K (Set.range ρ) = ⊤) :
    ∃ (S : Set A) (b : Module.Basis S K A) (test : S → Γ),
      ∀ i, b i = ρ (test i) := by
  let htop : (⊤ : Submodule K A) ≤ Submodule.span K (Set.range ρ) := by
    rw [hspan]
  let b0 := Module.Basis.ofSpan htop
  let S : Set A :=
    (linearIndepOn_empty K id).extend (Set.empty_subset (Set.range ρ))
  have hbsub : Set.range b0 ⊆ Set.range ρ :=
    Module.Basis.ofSpan_subset htop
  have heq : S = Set.range b0 := by
    symm
    exact Module.Basis.range_ofSpan htop
  have hmem : ∀ i : S, (i : A) ∈ Set.range ρ := by
    intro i
    apply hbsub
    rw [← heq]
    exact i.property
  choose test htest using hmem
  refine ⟨S, ?_, test, ?_⟩
  · exact b0
  · intro i
    have hbi : b0 i = (i : A) := Module.Basis.ofSpan_apply_self htop i
    rw [hbi]
    exact (htest i).symm


omit [Fintype Γ] [Group Γ] in
set_option linter.style.haveILetI false in
/-- Finite reindexing of the preceding group-image basis. Its length is exactly
the vector-space dimension of the image algebra. -/
theorem exists_fin_group_image_basis_of_span
    [FiniteDimensional K A]
    (ρ : Γ → A)
    (hspan : Submodule.span K (Set.range ρ) = ⊤) :
    ∃ (d : ℕ) (test : Fin d → Γ) (b : Module.Basis (Fin d) K A),
      (∀ i, b i = ρ (test i)) ∧ d = Module.finrank K A := by
  rcases exists_group_image_basis_of_span (K := K) ρ hspan with
    ⟨S, b, test, hb⟩
  letI : Fintype S := FiniteDimensional.fintypeBasisIndex b
  let e : S ≃ Fin (Fintype.card S) := Fintype.equivFin S
  let b' : Module.Basis (Fin (Fintype.card S)) K A := b.reindex e
  let test' : Fin (Fintype.card S) → Γ := fun i => test (e.symm i)
  refine ⟨Fintype.card S, test', b', ?_, ?_⟩
  · intro i
    simpa [b', test', Module.Basis.reindex_apply] using hb (e.symm i)
  · exact (Module.finrank_eq_card_basis b).symm


/-- Trace-alphabet cardinality bound with the basis/test list eliminated.
Spanning by actual group images supplies the required basis automatically. -/
theorem finite_trace_image_bound_from_spanning_pairing
    [FiniteDimensional K A]
    (n : ℕ)
    (ρ : Γ → A) (hρ : Function.Injective ρ)
    (hspan : Submodule.span K (Set.range ρ) = ⊤)
    (B : A →ₗ[K] A →ₗ[K] K)
    (hnondeg : ∀ x : A, B x = 0 → x = 0)
    (tr : Γ → T) (val : T → K)
    (htrace : ∀ γ δ : Γ, B (ρ γ) (ρ δ) = val (tr (γ * δ)))
    (hdim : Module.finrank K A ≤ n ^ 2) :
    Fintype.card Γ ≤ Fintype.card T ^ (n ^ 2) := by
  rcases exists_fin_group_image_basis_of_span (K := K) ρ hspan with
    ⟨d, test, b, hb, hd⟩
  apply finite_trace_image_bound_from_pairing
    (Γ := Γ) (T := T) (K := K) (A := A)
    n d ρ hρ test b hb B hnondeg tr val htrace
  simpa [hd] using hdim

end PairingCoordinates

section MatrixTracePairing

universe uI uKmat
variable {I : Type uI} [Fintype I] [DecidableEq I]
variable {Kmat : Type uKmat} [Field Kmat]

/-- Standard trace pairing on a full matrix algebra. -/
def matrixTracePairing :
    Matrix I I Kmat →ₗ[Kmat] Matrix I I Kmat →ₗ[Kmat] Kmat :=
  LinearMap.mk₂ Kmat (fun A B => (A * B).trace)
    (by intro A A' B; simp [add_mul])
    (by intro c A B; simp)
    (by intro A B B'; simp [mul_add])
    (by intro c A B; simp)

@[simp] theorem matrixTracePairing_apply (A B : Matrix I I Kmat) :
    matrixTracePairing A B = (A * B).trace := rfl

/-- The manuscript's blockwise trace form `Tr(XY)` is nondegenerate on every
full matrix algebra. -/
theorem matrixTracePairing_nondegenerate :
    ∀ A : Matrix I I Kmat, matrixTracePairing A = 0 → A = 0 := by
  intro A hA
  apply (Matrix.ext_iff_trace_mul_right).2
  intro X
  have hx : matrixTracePairing A X = 0 := by
    have h := congrArg (fun f : Matrix I I Kmat →ₗ[Kmat] Kmat => f X) hA
    simpa using h
  simpa [matrixTracePairing] using hx

/-- Multiplicity-scaled trace pairing on one simple matrix block. -/
def scaledMatrixTracePairing (m : Kmat) :
    Matrix I I Kmat →ₗ[Kmat] Matrix I I Kmat →ₗ[Kmat] Kmat :=
  m • matrixTracePairing

@[simp] theorem scaledMatrixTracePairing_apply
    (m : Kmat) (A B : Matrix I I Kmat) :
    scaledMatrixTracePairing m A B = m * (A * B).trace := by
  simp [scaledMatrixTracePairing, matrixTracePairing]

/-- If the multiplicity scalar is nonzero, the block form `m · Tr(XY)` remains
nondegenerate. This is the exact local step used in the semisimple image-algebra
proof when each multiplicity `m_i` is nonzero in the residue field. -/
theorem scaledMatrixTracePairing_nondegenerate
    (m : Kmat) (hm : m ≠ 0) :
    ∀ A : Matrix I I Kmat, scaledMatrixTracePairing m A = 0 → A = 0 := by
  intro A hA
  apply matrixTracePairing_nondegenerate
  apply LinearMap.ext
  intro X
  have hx := congrArg (fun f : Matrix I I Kmat →ₗ[Kmat] Kmat => f X) hA
  have hmx : m * matrixTracePairing A X = 0 := by
    simpa [scaledMatrixTracePairing] using hx
  exact (mul_eq_zero.mp hmx).resolve_left hm

end MatrixTracePairing

section DirectSumTracePairing

universe uSigma uKsum uV
variable {SigmaIdx : Type uSigma} [Fintype SigmaIdx] [DecidableEq SigmaIdx]
variable {Ksum : Type uKsum} [Field Ksum]
variable {V : SigmaIdx → Type uV}
variable [∀ i, AddCommGroup (V i)] [∀ i, Module Ksum (V i)]

/-- A finite direct sum of nondegenerate block pairings is nondegenerate. The
statement is phrased on the finite dependent product, which is canonically the
finite direct sum in this setting. -/
theorem finite_block_pairing_nondegenerate
    (B : ∀ i, V i →ₗ[Ksum] V i →ₗ[Ksum] Ksum)
    (hnondeg : ∀ i x, B i x = 0 → x = 0)
    (x : ∀ i, V i)
    (hx : ∀ y : ∀ i, V i, ∑ i, B i (x i) (y i) = 0) :
    x = 0 := by
  funext i
  apply hnondeg i (x i)
  apply LinearMap.ext
  intro z
  have h := hx (Pi.single i z)
  rw [Finset.sum_eq_single i] at h
  · simpa [Pi.single_apply] using h
  · intro j hj hji
    simp [hji]
  · simp

/-- In characteristic `ell`, a positive multiplicity strictly below `ell`
is a nonzero scalar. This is the elementary characteristic step behind the
manuscript's hypothesis `1 ≤ m_i ≤ n < ell`. -/
theorem natCast_ne_zero_of_pos_lt_char
    {Kchar : Type*} [Field Kchar]
    (ell m : ℕ) [CharP Kchar ell]
    (hmpos : 0 < m) (hmlt : m < ell) :
    (m : Kchar) ≠ 0 := by
  intro hm0
  have hd : ell ∣ m := (CharP.cast_eq_zero_iff Kchar ell m).mp hm0
  exact (not_le_of_gt hmlt) (Nat.le_of_dvd hmpos hd)

/-- Literal rank/characteristic form: `1 ≤ m ≤ n < ell` implies that the
multiplicity scalar is nonzero in characteristic `ell`. -/
theorem multiplicity_scalar_ne_zero_of_le_rank_lt_char
    {Kchar : Type*} [Field Kchar]
    (ell n m : ℕ) [CharP Kchar ell]
    (hmpos : 0 < m) (hmle : m ≤ n) (hnell : n < ell) :
    (m : Kchar) ≠ 0 :=
  natCast_ne_zero_of_pos_lt_char ell m hmpos (lt_of_le_of_lt hmle hnell)

/-- The exact semisimple-block trace form used in the manuscript is
nondegenerate once every block multiplicity is nonzero in the field. -/
theorem finite_matrix_block_trace_pairing_nondegenerate
    (d : SigmaIdx → ℕ) (m : SigmaIdx → Ksum) (hm : ∀ i, m i ≠ 0)
    (x : ∀ i, Matrix (Fin (d i)) (Fin (d i)) Ksum)
    (hx : ∀ y : ∀ i, Matrix (Fin (d i)) (Fin (d i)) Ksum,
      ∑ i, scaledMatrixTracePairing (I := Fin (d i)) (m i) (x i) (y i) = 0) :
    x = 0 := by
  apply finite_block_pairing_nondegenerate
    (B := fun i => scaledMatrixTracePairing (I := Fin (d i)) (m i))
    (hnondeg := fun i => scaledMatrixTracePairing_nondegenerate (I := Fin (d i)) (m i) (hm i))
    x hx


/-- Manuscript form of the semisimple block pairing: in characteristic `ell`,
if every natural multiplicity satisfies `0 < m_i ≤ n < ell`, then the direct
sum pairing `Σ_i m_i Tr(X_i Y_i)` is nondegenerate. -/
theorem finite_matrix_block_trace_pairing_nondegenerate_of_rank_lt_char
    {Kchar : Type*} [Field Kchar]
    (ell n : ℕ) [CharP Kchar ell]
    (d mult : SigmaIdx → ℕ)
    (hmpos : ∀ i, 0 < mult i)
    (hmle : ∀ i, mult i ≤ n)
    (hnell : n < ell)
    (x : ∀ i, Matrix (Fin (d i)) (Fin (d i)) Kchar)
    (hx : ∀ y : ∀ i, Matrix (Fin (d i)) (Fin (d i)) Kchar,
      ∑ i, scaledMatrixTracePairing (I := Fin (d i)) ((mult i : Kchar))
        (x i) (y i) = 0) :
    x = 0 := by
  apply finite_matrix_block_trace_pairing_nondegenerate
    (d := d) (m := fun i => (mult i : Kchar))
  · intro i
    exact multiplicity_scalar_ne_zero_of_le_rank_lt_char
      ell n (mult i) (hmpos i) (hmle i) hnell
  · exact hx

end DirectSumTracePairing

section MatrixImageAlgebra

universe uG uKim
variable {Gim : Type uG} [Group Gim]
variable {Kim : Type uKim} [Field Kim]

/-- The algebra generated by a matrix representation of a group. Because the
range is already multiplicatively closed, its underlying vector space is just
the linear span of the group matrices. -/
def matrixImageAlgebra (n : ℕ)
    (ρ : Gim →* Matrix (Fin n) (Fin n) Kim) :
    Subalgebra Kim (Matrix (Fin n) (Fin n) Kim) :=
  Algebra.adjoin Kim (Set.range ρ)

/-- The algebra generated by a group representation has underlying submodule
equal to the linear span of the group-image matrices. -/
theorem matrixImageAlgebra_toSubmodule_eq_span
    (n : ℕ) (ρ : Gim →* Matrix (Fin n) (Fin n) Kim) :
    (matrixImageAlgebra n ρ).toSubmodule =
      Submodule.span Kim (Set.range ρ) := by
  unfold matrixImageAlgebra
  rw [Algebra.adjoin_eq_span, MonoidHom.mclosure_range]
  exact congrArg (Submodule.span Kim) (MonoidHom.coe_mrange ρ)

/-- A group element viewed inside its generated image algebra. -/
def matrixImageElement (n : ℕ)
    (ρ : Gim →* Matrix (Fin n) (Fin n) Kim) (g : Gim) :
    matrixImageAlgebra n ρ :=
  ⟨ρ g, Algebra.subset_adjoin (Set.mem_range_self g)⟩

/-- Actual group elements span the generated image algebra as a vector space. -/
theorem matrixImageElement_span_eq_top
    (n : ℕ) (ρ : Gim →* Matrix (Fin n) (Fin n) Kim) :
    Submodule.span Kim (Set.range (matrixImageElement n ρ)) = ⊤ := by
  let A := matrixImageAlgebra n ρ
  have hs : ∀ g : Gim, ρ g ∈ A.toSubmodule := by
    intro g
    exact Algebra.subset_adjoin (Set.mem_range_self g)
  apply (Submodule.span_range_subtype_eq_top_iff A.toSubmodule hs).2
  exact (matrixImageAlgebra_toSubmodule_eq_span n ρ).symm

/-- Injectivity of the original matrix representation is inherited by the map
into the generated image algebra. -/
theorem matrixImageElement_injective
    (n : ℕ) (ρ : Gim →* Matrix (Fin n) (Fin n) Kim)
    (hρ : Function.Injective ρ) :
    Function.Injective (matrixImageElement n ρ) := by
  intro g h hgh
  apply hρ
  exact congrArg Subtype.val hgh

end MatrixImageAlgebra

section MatrixImageDimension

/-- Any matrix image algebra inside `M_n(K)` has vector-space dimension at
most `n²`. This discharges the dimension bound used by the finite trace
alphabet argument. -/
theorem matrix_subalgebra_finrank_le_square
    {Kdim : Type*} [Field Kdim]
    (n : ℕ) (A : Subalgebra Kdim (Matrix (Fin n) (Fin n) Kdim)) :
    Module.finrank Kdim A ≤ n ^ 2 := by
  calc
    Module.finrank Kdim A ≤
        Module.finrank Kdim (Matrix (Fin n) (Fin n) Kdim) :=
      A.toSubmodule.finrank_le
    _ = n ^ 2 := by
      simp [Module.finrank_matrix, pow_two]

end MatrixImageDimension

section ConcreteTraceAlphabetBound

universe uGtr uKtr
variable {Gtr : Type uGtr} [Group Gtr]
variable {Ktr : Type uKtr} [Field Ktr]

/-- The actual trace alphabet of a finite matrix representation. -/
def matrixTraceAlphabet (n : ℕ)
    (ρ : Gtr →* Matrix (Fin n) (Fin n) Ktr) : Set Ktr :=
  Set.range (fun g => (ρ g).trace)

/-- The trace of a group element, packaged as an element of its finite trace
alphabet. -/
def matrixTraceLabel (n : ℕ)
    (ρ : Gtr →* Matrix (Fin n) (Fin n) Ktr) (g : Gtr) :
    matrixTraceAlphabet n ρ :=
  ⟨(ρ g).trace, Set.mem_range_self g⟩

/-- The representation trace pairing restricted to the generated image
algebra. -/
def imageTracePairing (n : ℕ)
    (ρ : Gtr →* Matrix (Fin n) (Fin n) Ktr) :
    matrixImageAlgebra n ρ →ₗ[Ktr]
      matrixImageAlgebra n ρ →ₗ[Ktr] Ktr :=
  LinearMap.mk₂ Ktr
    (fun A B => (((A : Matrix (Fin n) (Fin n) Ktr)) *
      (B : Matrix (Fin n) (Fin n) Ktr)).trace)
    (by intro A A' B; simp [add_mul])
    (by intro c A B; simp)
    (by intro A B B'; simp [mul_add])
    (by intro c A B; simp)

@[simp] theorem imageTracePairing_on_group_elements
    (n : ℕ) (ρ : Gtr →* Matrix (Fin n) (Fin n) Ktr)
    (g h : Gtr) :
    imageTracePairing n ρ (matrixImageElement n ρ g)
        (matrixImageElement n ρ h) =
      (matrixTraceLabel n ρ (g * h) : Ktr) := by
  simp [imageTracePairing, matrixImageElement, matrixTraceLabel]

set_option linter.style.haveILetI false in
/-- The manuscript's finite trace-alphabet bound with all counting, basis, span,
and dimension bookkeeping discharged. The only remaining hypothesis is the
mathematically substantive nondegeneracy of the representation trace pairing
on the image algebra. -/
theorem finite_trace_image_bound_of_nondegenerate_image_pairing
    [Fintype Gtr]
    (n : ℕ) (ρ : Gtr →* Matrix (Fin n) (Fin n) Ktr)
    (hρ : Function.Injective ρ)
    (hnondeg : ∀ x : matrixImageAlgebra n ρ,
      imageTracePairing n ρ x = 0 → x = 0) :
    Fintype.card Gtr ≤
      (matrixTraceAlphabet n ρ).ncard ^ (n ^ 2) := by
  letI : Fintype (matrixTraceAlphabet n ρ) :=
    Set.Finite.fintype (Set.finite_range (fun g : Gtr => (ρ g).trace))
  have hbound := finite_trace_image_bound_from_spanning_pairing
    (Γ := Gtr) (T := matrixTraceAlphabet n ρ)
    (K := Ktr) (A := matrixImageAlgebra n ρ)
    n (matrixImageElement n ρ)
    (matrixImageElement_injective n ρ hρ)
    (matrixImageElement_span_eq_top n ρ)
    (imageTracePairing n ρ) hnondeg
    (matrixTraceLabel n ρ) Subtype.val
    (by
      intro g h
      exact imageTracePairing_on_group_elements n ρ g h)
    (matrix_subalgebra_finrank_le_square n (matrixImageAlgebra n ρ))
  simpa only [Set.fintypeCard_eq_ncard] using hbound

end ConcreteTraceAlphabetBound

section WedderburnBridge

universe uF uAlg
variable {Falg : Type uF} [Field Falg] [IsAlgClosed Falg]
variable {Aalg : Type uAlg} [Ring Aalg] [Algebra Falg Aalg]

set_option linter.style.haveILetI false in
/-- A faithful semisimple module over a finite-dimensional algebra forces the
acting algebra itself to be semisimple. The proof is exactly the Jacobson-
radical argument used implicitly in the manuscript: the radical annihilates a
semisimple module, faithfulness makes the annihilator zero, and finite
dimensionality makes the algebra Artinian. -/
theorem isSemisimpleRing_of_faithful_semisimple_module
    {F : Type*} [Field F]
    {A : Type*} [Ring A] [Algebra F A]
    {M : Type*} [AddCommGroup M] [Module A M]
    [IsSemisimpleModule A M] [FaithfulSMul A M]
    [FiniteDimensional F A] :
    IsSemisimpleRing A := by
  letI : IsArtinianRing A := IsArtinianRing.of_finite F A
  rw [IsArtinianRing.isSemisimpleRing_iff_jacobson]
  apply le_antisymm
  · calc
      Ring.jacobson A ≤ Module.annihilator A M :=
        IsSemisimpleModule.jacobson_le_annihilator A M
      _ = ⊥ := (Module.annihilator_eq_bot).2 inferInstance
  · exact bot_le

/-- The exact Wedderburn–Artin decomposition used in the manuscript: a finite-
dimensional semisimple algebra over an algebraically closed field is a finite
product of full matrix algebras over that field. This delegates the classical
structure theorem to Mathlib rather than treating it as a new Strong Artin
claim. -/
theorem semisimple_algebra_exists_matrix_block_decomposition
    [IsSemisimpleRing Aalg] [FiniteDimensional Falg Aalg] :
    ∃ (r : ℕ) (d : Fin r → ℕ), (∀ i, NeZero (d i)) ∧
      Nonempty (Aalg ≃ₐ[Falg] ∀ i, Matrix (Fin (d i)) (Fin (d i)) Falg) := by
  exact IsSemisimpleRing.exists_algEquiv_pi_matrix_of_isAlgClosed Falg Aalg


set_option linter.style.haveILetI false in
/-- Combined manuscript bridge: a finite-dimensional algebra over an
algebraically closed field that acts faithfully and semisimply on one module
already admits a finite product-of-matrix-algebras decomposition. -/
theorem faithful_semisimple_action_exists_matrix_block_decomposition
    {F : Type*} [Field F] [IsAlgClosed F]
    {A : Type*} [Ring A] [Algebra F A]
    {M : Type*} [AddCommGroup M] [Module A M]
    [IsSemisimpleModule A M] [FaithfulSMul A M]
    [FiniteDimensional F A] :
    ∃ (r : ℕ) (d : Fin r → ℕ), (∀ i, NeZero (d i)) ∧
      Nonempty (A ≃ₐ[F] ∀ i, Matrix (Fin (d i)) (Fin (d i)) F) := by
  letI : IsSemisimpleRing A :=
    isSemisimpleRing_of_faithful_semisimple_module (F := F) (A := A) (M := M)
  exact semisimple_algebra_exists_matrix_block_decomposition (Falg := F) (Aalg := A)

end WedderburnBridge


section MoritaTraceBridge

open Matrix
open scoped Matrix.Module BigOperators

universe uKm uMm uIm
variable {Kmor : Type uKm} [Field Kmor]
variable {Imor : Type uIm} [Fintype Imor] [DecidableEq Imor]

/-- Coordinate matrix action on `Imor → N`. -/
def moritaCoordinateAction {N : Type uMm} [AddCommGroup N] [Module Kmor N]
    (A : Matrix Imor Imor Kmor) : (Imor → N) →ₗ[Kmor] (Imor → N) where
  toFun v := A • v
  map_add' x y := by simp [smul_add]
  map_smul' c x := by
    ext i
    simp only [Matrix.Module.smul_apply, Pi.smul_apply]
    rw [Finset.smul_sum]
    apply Finset.sum_congr rfl
    intro j hj
    simp [smul_smul, mul_comm]

@[simp] theorem moritaCoordinateAction_apply {N : Type uMm}
    [AddCommGroup N] [Module Kmor N]
    (A : Matrix Imor Imor Kmor) (v : Imor → N) :
    moritaCoordinateAction A v = A • v := rfl

/-- On the concrete Morita model `K^d ⊗ N ≃ d → N`, matrix action has trace
`dim(N) * matrixTrace(A)`. -/
theorem moritaCoordinateAction_trace {N : Type uMm}
    [AddCommGroup N] [Module Kmor N] [FiniteDimensional Kmor N]
    (A : Matrix Imor Imor Kmor) :
    LinearMap.trace Kmor (Imor → N) (moritaCoordinateAction A) =
      (Module.finrank Kmor N : Kmor) * Matrix.trace A := by
  let bN : Module.Basis (Fin (Module.finrank Kmor N)) Kmor N := Module.finBasis Kmor N
  let b : Module.Basis (Σ _ : Imor, Fin (Module.finrank Kmor N)) Kmor (Imor → N) :=
    Pi.basis (fun _ : Imor => bN)
  have hdiag : ∀ q : Σ _ : Imor, Fin (Module.finrank Kmor N),
      LinearMap.toMatrix b b (moritaCoordinateAction A) q q = A q.1 q.1 := by
    intro q
    rw [LinearMap.toMatrix_apply, Pi.basis_repr]
    have hbq : b q = Pi.single q.1 (bN q.2) := by simp [b]
    rw [hbq]
    simp only [moritaCoordinateAction_apply, Matrix.Module.smul_apply]
    rw [Finset.sum_eq_single q.1]
    · simp [bN]
    · intro x hx hne
      simp [hne]
    · simp
  rw [LinearMap.trace_eq_matrix_trace Kmor b]
  simp only [Matrix.trace, Matrix.diag_apply, hdiag]
  rw [Fintype.sum_sigma]
  simp only [Finset.sum_const, nsmul_eq_mul]
  rw [Finset.mul_sum]
  simp

/-- The action of a full-matrix-ring element, regarded as a linear map over its
central scalar field. -/
noncomputable def moritaModuleActionLinear
    {M : Type uMm} [AddCommGroup M] [Module (Matrix Imor Imor Kmor) M]
    (A : Matrix Imor Imor Kmor) :
    letI : Module Kmor M := Module.compHom M (Matrix.scalar (α := Kmor) Imor)
    M →ₗ[Kmor] M := by
  letI : Module Kmor M := Module.compHom M (Matrix.scalar (α := Kmor) Imor)
  exact {
    toFun := fun m => A • m
    map_add' := fun x y => by simp
    map_smul' := fun c x => by
      change A • ((Matrix.scalar Imor c) • x) = (Matrix.scalar Imor c) • (A • x)
      rw [← mul_smul, ← mul_smul]
      exact congrArg (fun C : Matrix Imor Imor Kmor => C • x)
        (Matrix.scalar_commute c (fun _ => Commute.all _ _) A).eq.symm }

set_option linter.style.haveILetI false in
/-- Canonical Morita trace formula for an arbitrary finite module over a full
matrix algebra. The multiplicity is the dimension of the matrix corner
`E_jj M`. -/
theorem moduleAction_trace_via_morita
    {M : Type uMm} [AddCommGroup M] [Module (Matrix Imor Imor Kmor) M]
    [Module.Finite (Matrix Imor Imor Kmor) M]
    (j : Imor) (A : Matrix Imor Imor Kmor) :
    letI : Module Kmor M := Module.compHom M (Matrix.scalar (α := Kmor) Imor)
    letI : IsScalarTower Kmor (Matrix Imor Imor Kmor) M :=
      MatrixModCat.isScalarTower_toModuleCat Kmor
        (ModuleCat.of (Matrix Imor Imor Kmor) M)
    LinearMap.trace Kmor M (moritaModuleActionLinear (M := M) A) =
      (Module.finrank Kmor (MatrixModCat.toModuleCatObj Kmor M j) : Kmor) *
        Matrix.trace A := by
  letI : Module Kmor M := Module.compHom M (Matrix.scalar (α := Kmor) Imor)
  letI : IsScalarTower Kmor (Matrix Imor Imor Kmor) M :=
    MatrixModCat.isScalarTower_toModuleCat Kmor
      (ModuleCat.of (Matrix Imor Imor Kmor) M)
  letI : Module.Finite Kmor M := Module.Finite.trans (Matrix Imor Imor Kmor) M
  let N := MatrixModCat.toModuleCatObj Kmor M j
  let eM := toModuleCatFromModuleCatLinearEquiv Kmor
    (ModuleCat.of (Matrix Imor Imor Kmor) M) j
  let eK : M ≃ₗ[Kmor] (Imor → N) := eM.restrictScalars Kmor
  let fM : M →ₗ[Kmor] M := moritaModuleActionLinear (M := M) A
  have hconj : eK.conj fM = moritaCoordinateAction (N := N) A := by
    apply LinearMap.ext
    intro y
    change eM (A • eM.symm y) = A • y
    rw [eM.map_smul, eM.apply_symm_apply]
  have htr := LinearMap.trace_conj' fM eK
  rw [hconj, moritaCoordinateAction_trace] at htr
  exact htr.symm

end MoritaTraceBridge

section ProjectorTraceLocalization

open LinearMap Submodule

universe uKt uMt
variable {Ktrc : Type uKt} [Field Ktrc]
variable {Mtrc : Type uMt} [AddCommGroup Mtrc] [Module Ktrc Mtrc]
  [FiniteDimensional Ktrc Mtrc]

/-- If an endomorphism commutes with an idempotent projector and vanishes on
its complementary kernel, its ambient trace is exactly the trace on the
projector range. -/
theorem trace_eq_trace_range_of_proj
    (P T : Module.End Ktrc Mtrc)
    (hP : IsIdempotentElem P)
    (hcomm : Commute P T)
    (hker : ker P ≤ ker T) :
    LinearMap.trace Ktrc Mtrc T =
      LinearMap.trace Ktrc (range P)
        (T.restrict ((Module.End.mem_invtSubmodule_iff_forall_mem_of_mem T).1
          ((hP.commute_iff).1 hcomm).1)) := by
  let p := range P
  let q := ker P
  have hpInv : p ∈ Module.End.invtSubmodule T := ((hP.commute_iff).1 hcomm).1
  have hqInv : q ∈ Module.End.invtSubmodule T := ((hP.commute_iff).1 hcomm).2
  let Tp : p →ₗ[Ktrc] p :=
    T.restrict ((Module.End.mem_invtSubmodule_iff_forall_mem_of_mem T).1 hpInv)
  let Tq : q →ₗ[Ktrc] q :=
    T.restrict ((Module.End.mem_invtSubmodule_iff_forall_mem_of_mem T).1 hqInv)
  have hTq : Tq = 0 := by
    apply LinearMap.ext
    intro x
    apply Subtype.ext
    change T (x : Mtrc) = 0
    exact hker x.2
  let e := p.prodEquivOfIsCompl q hP.isProj_range.isCompl
  have hconj : e.conj (LinearMap.prodMap Tp Tq) = T := by
    apply LinearMap.ext
    intro x
    rcases e.surjective x with ⟨⟨xp, xq⟩, rfl⟩
    rw [LinearEquiv.conj_apply]
    simp only [LinearMap.coe_comp, Function.comp_apply, LinearMap.prodMap_apply]
    change e (Tp ((e.symm (e (xp, xq))).1), Tq ((e.symm (e (xp, xq))).2)) =
      T (e (xp, xq))
    rw [e.symm_apply_apply]
    change e (Tp xp, Tq xq) = T (e (xp, xq))
    simp only [e]
    change (Tp xp : Mtrc) + (Tq xq : Mtrc) =
      T ((xp : Mtrc) + (xq : Mtrc))
    simp [Tp, Tq, map_add]
  calc
    LinearMap.trace Ktrc Mtrc T =
        LinearMap.trace Ktrc Mtrc (e.conj (LinearMap.prodMap Tp Tq)) := by rw [hconj]
    _ = LinearMap.trace Ktrc (p × q) (LinearMap.prodMap Tp Tq) :=
      LinearMap.trace_conj' (LinearMap.prodMap Tp Tq) e
    _ = LinearMap.trace Ktrc p Tp + LinearMap.trace Ktrc q Tq :=
      LinearMap.trace_prodMap' Tp Tq
    _ = LinearMap.trace Ktrc p Tp := by rw [hTq]; simp
    _ = LinearMap.trace Ktrc (range P)
        (T.restrict ((Module.End.mem_invtSubmodule_iff_forall_mem_of_mem T).1
          ((hP.commute_iff).1 hcomm).1)) := by rfl

end ProjectorTraceLocalization


section WedderburnTraceFormulaBridge

universe uKw uAw uIw
variable {Kwed : Type uKw} [Field Kwed]
variable {Awed : Type uAw} [Ring Awed] [Algebra Kwed Awed]
variable {Iwed : Type uIw} [Fintype Iwed] [DecidableEq Iwed]

/-- Once the representation trace is expressed in Wedderburn coordinates as
`Σ_i m_i Tr(-)`, the manuscript's characteristic/rank hypotheses force its
multiplication pairing to be nondegenerate. This theorem deliberately isolates
that exact trace-formula bridge from the already certified block algebra. -/
theorem trace_pairing_nondegenerate_of_wedderburn_formula
    (ell n : ℕ) [CharP Kwed ell]
    (d mult : Iwed → ℕ)
    (hmpos : ∀ i, 0 < mult i)
    (hmle : ∀ i, mult i ≤ n)
    (hnell : n < ell)
    (e : Awed ≃ₐ[Kwed] ∀ i, Matrix (Fin (d i)) (Fin (d i)) Kwed)
    (trA : Awed →ₗ[Kwed] Kwed)
    (htrace : ∀ a : Awed,
      trA a = ∑ i, (mult i : Kwed) * Matrix.trace (e a i))
    (x : Awed)
    (hx : ∀ y : Awed, trA (x * y) = 0) :
    x = 0 := by
  have hblock : e x = 0 := by
    apply finite_matrix_block_trace_pairing_nondegenerate_of_rank_lt_char
      (SigmaIdx := Iwed) ell n d mult hmpos hmle hnell
    intro y
    let yA : Awed := e.symm y
    have hxy := hx yA
    rw [htrace] at hxy
    simpa [yA, map_mul, scaledMatrixTracePairing_apply] using hxy
  exact e.injective (by simpa using hblock)

/-- Bilinear-map packaging of the same bridge. -/
def algebraTracePairing
    (trA : Awed →ₗ[Kwed] Kwed) : Awed →ₗ[Kwed] Awed →ₗ[Kwed] Kwed :=
  LinearMap.mk₂ Kwed (fun x y => trA (x * y))
    (fun _ _ _ => by simp [add_mul])
    (fun c x y => by simp)
    (fun _ _ _ => by simp [mul_add])
    (fun c x y => by simp)

@[simp] theorem algebraTracePairing_apply
    (trA : Awed →ₗ[Kwed] Kwed) (x y : Awed) :
    algebraTracePairing trA x y = trA (x * y) := rfl

/-- Nondegeneracy in the linear-map form consumed by the concrete trace
alphabet bound. -/
theorem algebraTracePairing_nondegenerate_of_wedderburn_formula
    (ell n : ℕ) [CharP Kwed ell]
    (d mult : Iwed → ℕ)
    (hmpos : ∀ i, 0 < mult i)
    (hmle : ∀ i, mult i ≤ n)
    (hnell : n < ell)
    (e : Awed ≃ₐ[Kwed] ∀ i, Matrix (Fin (d i)) (Fin (d i)) Kwed)
    (trA : Awed →ₗ[Kwed] Kwed)
    (htrace : ∀ a : Awed,
      trA a = ∑ i, (mult i : Kwed) * Matrix.trace (e a i)) :
    ∀ x : Awed, algebraTracePairing trA x = 0 → x = 0 := by
  intro x hx
  apply trace_pairing_nondegenerate_of_wedderburn_formula
    ell n d mult hmpos hmle hnell e trA htrace x
  intro y
  have h := LinearMap.congr_fun hx y
  simpa using h

end WedderburnTraceFormulaBridge

end TraceAlphabetCounting


/-! ## Finite Satake / cyclotomic algebra -/

section FiniteSatake

/-- If an `f`th power has order dividing `M` and `f ∣ d`, then the original
 element has order dividing `d*M`. This is the algebraic core of the finite
 Satake-root theorem. -/
theorem torsion_of_power_torsion
    {G : Type*} [Monoid G] (α : G) (f d M : ℕ)
    (hfd : f ∣ d) (h : (α ^ f) ^ M = 1) :
    α ^ (d * M) = 1 := by
  rcases hfd with ⟨q, rfl⟩
  have hq := congrArg (fun x : G => x ^ q) h
  simpa [pow_mul, mul_assoc, mul_comm, mul_left_comm] using hq

/-- In particular, an `f`th-power Satake root lying in `μ_M` lies in `μ_{dM}`
whenever the residue degree `f` divides the global extension degree `d`. -/
theorem satake_root_order_divides
    {G : Type*} [Monoid G] (α : G) (f d M : ℕ)
    (hfd : f ∣ d) (hfinite : (α ^ f) ^ M = 1) :
    α ^ (d * M) = 1 :=
  torsion_of_power_torsion α f d M hfd hfinite

/-- Exact stars-and-bars count for multisets of `n` roots drawn from a finite
cyclotomic alphabet. -/
theorem root_multiset_count
    (Ω : Type*) [Fintype Ω] (n : ℕ) [Fintype (Sym Ω n)] :
    Fintype.card (Sym Ω n) =
      (Fintype.card Ω + n - 1).choose n :=
  Sym.card_sym_eq_choose n

/-- If the available root alphabet has exactly `N` elements, there are exactly
`choose (N+n-1) n` root multisets of degree `n`. A monic split polynomial is
determined by such a multiset, giving the manuscript's finite-polynomial
alphabet bound once the root-to-polynomial map is invoked. -/
theorem root_multiset_count_of_card
    (Ω : Type*) [Fintype Ω] (n N : ℕ) [Fintype (Sym Ω n)]
    (hΩ : Fintype.card Ω = N) :
    Fintype.card (Sym Ω n) = (N + n - 1).choose n := by
  rw [root_multiset_count, hΩ]

end FiniteSatake



/-! ## Matrix coefficient rotation and one-polynomial separators -/

section MatrixCoefficientRotation

universe uι uR
variable {ι : Type uι} [Fintype ι] [DecidableEq ι]
variable {R : Type uR} [CommRing R]

/-- The degree-`k` elementary matrix coefficient, realized as the sum of all
`k × k` principal minors. This is the `e_k(A)` appearing in the manuscript. -/
def elementaryCoeff (A : Matrix ι ι R) (k : ℕ) : R :=
  ∑ s ∈ Finset.univ.powersetCard k,
    (A.submatrix (Subtype.val : s → ι) (Subtype.val : s → ι)).det

/-- Scalar multiplication rotates the degree-`k` coefficient by the `k`th
power, exactly `e_k(cA) = c^k e_k(A)`. -/
theorem elementaryCoeff_smul (c : R) (A : Matrix ι ι R) (k : ℕ) :
    elementaryCoeff (c • A) k = c ^ k * elementaryCoeff A k := by
  classical
  unfold elementaryCoeff
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro s hs
  have hh : s.card = k := (Finset.mem_powersetCard.mp hs).2
  simp only [Matrix.submatrix_smul, Pi.smul_apply, Matrix.det_smul,
    Fintype.card_coe, hh]

/-- The principal-minor coefficient agrees with the usual signed
characteristic-polynomial coefficient. -/
theorem elementaryCoeff_eq_signed_charpoly_coeff
    (A : Matrix ι ι R) (k : ℕ) (hk : k ≤ Fintype.card ι) :
    A.charpoly.coeff (Fintype.card ι - k) = (-1 : R) ^ k * elementaryCoeff A k := by
  exact Matrix.charpoly_coeff_eq_sum_minors A k hk

/-- Abstract one-polynomial separator: if one active coefficient degree `k`
has nonzero value and the cyclic scalar phase at degree `k` distinguishes two
labels, then the corresponding scalar-twisted matrices cannot have identical
`k`th coefficients. -/
theorem coefficient_separates_scalar_twists [IsDomain R]
    (A : Matrix ι ι R) (k : ℕ) (hA : elementaryCoeff A k ≠ 0)
    {c d : R} (hphase : c ^ k ≠ d ^ k) :
    elementaryCoeff (c • A) k ≠ elementaryCoeff (d • A) k := by
  rw [elementaryCoeff_smul, elementaryCoeff_smul]
  intro h
  apply hphase
  exact mul_right_cancel₀ hA h

end MatrixCoefficientRotation

section CyclicPolynomialSeparator

universe uι
variable {ι : Type uι} [Fintype ι] [DecidableEq ι]

/-- The canonical complex scalar attached to a cyclic quotient-character label. -/
def cyclicScalar (j : Label p) : ℂ := ZMod.stdAddChar j

/-- Taking the `k`th power of the cyclic scalar corresponds exactly to applying
the additive rank/degree map on `ZMod p`. -/
theorem cyclicScalar_pow (k : ℕ) (j : Label p) :
    cyclicScalar p j ^ k = cyclicScalar p (powerLabel p k j) := by
  unfold cyclicScalar powerLabel
  rw [← AddChar.map_nsmul_eq_pow]
  congr 1
  simp [nsmul_eq_mul]

/-- If `p ∤ k`, the `k`th-power cyclic phase distinguishes every quotient
character label. -/
theorem cyclicScalar_pow_injective_of_not_dvd
    (k : ℕ) (hk : ¬ p ∣ k) :
    Function.Injective (fun j : Label p => cyclicScalar p j ^ k) := by
  intro a b h
  change cyclicScalar p a ^ k = cyclicScalar p b ^ k at h
  rw [cyclicScalar_pow, cyclicScalar_pow] at h
  apply powerLabel_injective_of_not_dvd p k hk
  exact ZMod.injective_stdAddChar h

/-- One active characteristic-polynomial degree not divisible by `p` separates
all cyclic scalar twists at the coefficient level. -/
theorem one_active_degree_coefficient_separator
    (A : Matrix ι ι ℂ) (k : ℕ)
    (hA : elementaryCoeff A k ≠ 0) (hk : ¬ p ∣ k) :
    Function.Injective
      (fun j : Label p => elementaryCoeff (cyclicScalar p j • A) k) := by
  intro a b h
  change elementaryCoeff (cyclicScalar p a • A) k =
    elementaryCoeff (cyclicScalar p b • A) k at h
  rw [elementaryCoeff_smul, elementaryCoeff_smul] at h
  apply cyclicScalar_pow_injective_of_not_dvd p k hk
  exact mul_right_cancel₀ hA h

/-- Manuscript one-polynomial separator, exact matrix form: if one active
coefficient degree `k ≤ n` is not divisible by the quotient prime, then the
characteristic polynomials of all cyclic scalar twists are pairwise distinct. -/
theorem one_active_degree_charpoly_separator
    (A : Matrix ι ι ℂ) (k : ℕ)
    (hkdim : k ≤ Fintype.card ι)
    (hA : elementaryCoeff A k ≠ 0) (hk : ¬ p ∣ k) :
    Function.Injective (fun j : Label p => (cyclicScalar p j • A).charpoly) := by
  intro a b hpoly
  have hc := congrArg
    (fun P : Polynomial ℂ => P.coeff (Fintype.card ι - k)) hpoly
  rw [elementaryCoeff_eq_signed_charpoly_coeff,
      elementaryCoeff_eq_signed_charpoly_coeff] at hc
  · have he : elementaryCoeff (cyclicScalar p a • A) k =
        elementaryCoeff (cyclicScalar p b • A) k := by
      exact mul_left_cancel₀ (by simp : (-1 : ℂ) ^ k ≠ 0) hc
    exact one_active_degree_coefficient_separator p A k hA hk he
  · exact hkdim
  · exact hkdim

end CyclicPolynomialSeparator

/-! ## Sharp finite boundary certificates -/

/-- When the quotient prime divides the rank, the determinant-power label map
can genuinely lose injectivity: at `p = 2`, rank `n = 2`, every label maps to
zero. -/
theorem rank_prime_selector_failure_example :
    ¬ Function.Injective (powerLabel 2 2) := by
  intro hinj
  have hsame : powerLabel 2 2 (0 : ZMod 2) = powerLabel 2 2 (1 : ZMod 2) := by
    decide +kernel
  have h01 := hinj hsame
  norm_num at h01

/-- The nonzero-mode hypothesis in the one-Fourier-mode selector is also
necessary: the zero mode cannot distinguish cyclic labels even for `p = 2`. -/
theorem zero_fourier_mode_failure_example :
    ¬ Function.Injective (modeLabel 2 0) := by
  intro hinj
  have hsame : modeLabel 2 0 (0 : ZMod 2) = modeLabel 2 0 (1 : ZMod 2) := by
    decide +kernel
  have h01 := hinj hsame
  norm_num at h01


/-! ## Concrete Wedderburn-to-trace-alphabet closure -/

section ConcreteWedderburnTraceBound

universe uGcw uKcw uIcw
variable {Gcw : Type uGcw} [Group Gcw]
variable {Kcw : Type uKcw} [Field Kcw]
variable {Icw : Type uIcw} [Fintype Icw] [DecidableEq Icw]

/-- Ordinary matrix trace restricted to the generated image algebra. -/
def imageTraceLinear (n : ℕ)
    (ρ : Gcw →* Matrix (Fin n) (Fin n) Kcw) :
    matrixImageAlgebra n ρ →ₗ[Kcw] Kcw :=
  (Matrix.traceLinearMap (Fin n) Kcw Kcw).comp
    (matrixImageAlgebra n ρ).toSubmodule.subtype

@[simp] theorem imageTraceLinear_apply
    (n : ℕ) (ρ : Gcw →* Matrix (Fin n) (Fin n) Kcw)
    (a : matrixImageAlgebra n ρ) :
    imageTraceLinear n ρ a =
      (a : Matrix (Fin n) (Fin n) Kcw).trace := rfl

/-- The concrete image-algebra pairing is exactly multiplication followed by
its representation trace. -/
theorem imageTracePairing_eq_algebraTracePairing
    (n : ℕ) (ρ : Gcw →* Matrix (Fin n) (Fin n) Kcw) :
    imageTracePairing n ρ = algebraTracePairing (imageTraceLinear n ρ) := by
  ext x y
  rfl

/-- Concrete closure of the finite trace-alphabet count from a certified
Wedderburn multiplicity trace formula.  This removes the abstract
nondegeneracy hypothesis from `finite_trace_image_bound_of_nondegenerate_image_pairing`:
the manuscript's rank/characteristic inequalities and the trace formula imply
nondegeneracy internally. -/
theorem finite_trace_image_bound_of_wedderburn_trace_formula
    [Fintype Gcw]
    (ell n : ℕ) [CharP Kcw ell]
    (ρ : Gcw →* Matrix (Fin n) (Fin n) Kcw)
    (hρ : Function.Injective ρ)
    (d mult : Icw → ℕ)
    (hmpos : ∀ i, 0 < mult i)
    (hmle : ∀ i, mult i ≤ n)
    (hnell : n < ell)
    (e : matrixImageAlgebra n ρ ≃ₐ[Kcw]
      ∀ i, Matrix (Fin (d i)) (Fin (d i)) Kcw)
    (htrace : ∀ a : matrixImageAlgebra n ρ,
      imageTraceLinear n ρ a =
        ∑ i, (mult i : Kcw) * Matrix.trace (e a i)) :
    Fintype.card Gcw ≤
      (matrixTraceAlphabet n ρ).ncard ^ (n ^ 2) := by
  apply finite_trace_image_bound_of_nondegenerate_image_pairing n ρ hρ
  have hnondeg := algebraTracePairing_nondegenerate_of_wedderburn_formula
    (Kwed := Kcw) (Awed := matrixImageAlgebra n ρ) (Iwed := Icw)
    ell n d mult hmpos hmle hnell e (imageTraceLinear n ρ) htrace
  intro x hx
  apply hnondeg x
  rw [← imageTracePairing_eq_algebraTracePairing n ρ]
  exact hx

end ConcreteWedderburnTraceBound

/-! ## Concrete semisimple image-algebra bridge -/

section ConcreteSemisimpleImageBridge

universe uGsi uKsi
variable {Gsi : Type uGsi} [Group Gsi]
variable {Ksi : Type uKsi} [Field Ksi] [IsAlgClosed Ksi]

set_option linter.style.haveILetI false in
omit [IsAlgClosed Ksi] in
/-- The generated matrix image algebra acts faithfully on the defining column
module.  No extra faithfulness certificate is needed: equality of actions on all
vectors implies equality of the underlying matrices. -/
theorem matrixImageAlgebra_defining_action_faithful
    (n : ℕ) (ρ : Gsi →* Matrix (Fin n) (Fin n) Ksi) :
    let A := matrixImageAlgebra n ρ
    letI : Module (Matrix (Fin n) (Fin n) Ksi) (Fin n → Ksi) :=
      Matrix.Module.matrixModule
    letI : Module A (Fin n → Ksi) :=
      Module.compHom (Fin n → Ksi) (SubsemiringClass.subtype A)
    FaithfulSMul A (Fin n → Ksi) := by
  let A := matrixImageAlgebra n ρ
  letI : Module (Matrix (Fin n) (Fin n) Ksi) (Fin n → Ksi) :=
    Matrix.Module.matrixModule
  letI : Module A (Fin n → Ksi) :=
    Module.compHom (Fin n → Ksi) (SubsemiringClass.subtype A)
  refine ⟨?_⟩
  intro a b h
  apply Subtype.ext
  apply Matrix.ext_iff_smul.2
  intro v
  have hv := h v
  change (a.1 : Matrix (Fin n) (Fin n) Ksi) • v =
    (b.1 : Matrix (Fin n) (Fin n) Ksi) • v at hv
  exact hv

set_option linter.style.haveILetI false in
/-- Concrete Wedderburn closure from the manuscript's semisimple defining-module
hypothesis.  The image algebra is finite-dimensional and its defining action is
faithful automatically, so semisimplicity of that module forces a finite product
of full matrix blocks over the algebraically closed coefficient field. -/
theorem matrixImageAlgebra_exists_block_decomposition_of_semisimple
    (n : ℕ) (ρ : Gsi →* Matrix (Fin n) (Fin n) Ksi)
    (hsem :
      let A := matrixImageAlgebra n ρ
      letI : Module (Matrix (Fin n) (Fin n) Ksi) (Fin n → Ksi) :=
        Matrix.Module.matrixModule
      letI : Module A (Fin n → Ksi) :=
        Module.compHom (Fin n → Ksi) (SubsemiringClass.subtype A)
      IsSemisimpleModule A (Fin n → Ksi)) :
    ∃ (r : ℕ) (d : Fin r → ℕ), (∀ i, NeZero (d i)) ∧
      Nonempty (matrixImageAlgebra n ρ ≃ₐ[Ksi]
        ∀ i, Matrix (Fin (d i)) (Fin (d i)) Ksi) := by
  let A := matrixImageAlgebra n ρ
  letI : Module (Matrix (Fin n) (Fin n) Ksi) (Fin n → Ksi) :=
    Matrix.Module.matrixModule
  letI : Module A (Fin n → Ksi) :=
    Module.compHom (Fin n → Ksi) (SubsemiringClass.subtype A)
  letI : IsSemisimpleModule A (Fin n → Ksi) := hsem
  letI : FaithfulSMul A (Fin n → Ksi) := ⟨by
    intro a b h
    apply Subtype.ext
    apply Matrix.ext_iff_smul.2
    intro v
    have hv := h v
    change (a.1 : Matrix (Fin n) (Fin n) Ksi) • v =
      (b.1 : Matrix (Fin n) (Fin n) Ksi) • v at hv
    exact hv⟩
  have hfaith : FaithfulSMul A (Fin n → Ksi) := inferInstance
  have hsemi : IsSemisimpleModule A (Fin n → Ksi) := inferInstance
  exact @faithful_semisimple_action_exists_matrix_block_decomposition
    Ksi _ _ A _ _ (Fin n → Ksi) _ _ hsemi hfaith _

end ConcreteSemisimpleImageBridge

/-! ## Exact split-polynomial encoding of finite root alphabets -/

section SplitPolynomialAlphabet

universe uΩ uKs
variable {Ω : Type uΩ}
variable {Ks : Type uKs} [Field Ks]

/-- Turn an unordered degree-`n` multiset of abstract roots into its monic split
polynomial after embedding the root alphabet into the coefficient field. -/
def splitPolynomialOfSym (n : ℕ) (root : Ω → Ks) (s : Sym Ω n) : Polynomial Ks :=
  ((((s : Multiset Ω).map root).map fun a => Polynomial.X - Polynomial.C a).prod)

/-- The root multiset of the encoded polynomial is exactly the embedded root
multiset. -/
theorem roots_splitPolynomialOfSym
    (n : ℕ) (root : Ω → Ks) (s : Sym Ω n) :
    (splitPolynomialOfSym n root s).roots = (s : Multiset Ω).map root := by
  unfold splitPolynomialOfSym
  exact Polynomial.roots_multiset_prod_X_sub_C ((s : Multiset Ω).map root)

/-- Distinct unordered root multisets give distinct monic split polynomials as
soon as the root alphabet embeds injectively in the coefficient field. -/
theorem splitPolynomialOfSym_injective
    (n : ℕ) (root : Ω → Ks) (hroot : Function.Injective root) :
    Function.Injective (splitPolynomialOfSym n root) := by
  intro s t hpoly
  apply Sym.coe_injective
  apply Multiset.map_injective hroot
  rw [← roots_splitPolynomialOfSym n root s,
      ← roots_splitPolynomialOfSym n root t, hpoly]

/-- Therefore the number of degree-`n` monic split polynomials built from an
`N`-element injectively embedded root alphabet is exactly the symmetric-power
count `choose (N+n-1) n`. -/
theorem splitPolynomial_image_card
    [Fintype Ω] (n N : ℕ) [Fintype (Sym Ω n)]
    (root : Ω → Ks) (hroot : Function.Injective root)
    (hΩ : Fintype.card Ω = N) :
    Set.ncard (Set.range (splitPolynomialOfSym n root)) =
      (N + n - 1).choose n := by
  rw [Set.ncard_range_of_injective (splitPolynomialOfSym_injective n root hroot)]
  simpa only [Nat.card_eq_fintype_card] using
    (root_multiset_count_of_card Ω n N hΩ)

end SplitPolynomialAlphabet

/-! ## Quotient-prime scalar collapse -/

section QuotientPrimeScalarCollapse

universe uRc
variable {Rc : Type uRc} [Field Rc] [CharP Rc p]

/-- In reduced characteristic `p`, there is no nontrivial scalar `p`-torsion:
`x^p = 1` forces `x = 1`.  This is the scalar algebra behind the collapse of
order-`p` quotient-character labels at a place above `p`. -/
theorem p_torsion_scalar_eq_one (x : Rc) (hx : x ^ p = 1) : x = 1 := by
  have hnil : (x - 1) ^ p = 0 := by
    rw [sub_pow_char, hx, one_pow, sub_self]
  have hz : x - 1 = 0 := eq_zero_of_pow_eq_zero hnil
  exact sub_eq_zero.mp hz

/-- Consequently any two scalar labels whose ratio is `p`-torsion coincide in
reduced characteristic `p`. -/
theorem eq_of_ratio_p_torsion
    {x y : Rc} (hy : y ≠ 0) (h : (x / y) ^ p = 1) : x = y := by
  have hxy : x / y = 1 := p_torsion_scalar_eq_one p (x / y) h
  exact (div_eq_one_iff_eq hy).mp hxy

end QuotientPrimeScalarCollapse

end Komorebi.StrongArtin.FiniteCore


namespace Komorebi.StrongArtin.BlockTrace

open LinearMap Submodule
open scoped BigOperators

universe uK uA uI uM

section CyclicFunctional
variable {K : Type uK} [Field K]
variable {J : Type*} [Fintype J] [DecidableEq J] [Nonempty J]

theorem cyclic_linearFunctional_eq_smul_trace
    (L : Matrix J J K →ₗ[K] K)
    (hcyc : ∀ A B : Matrix J J K, L (A * B) = L (B * A)) :
    ∃ c : K, L = c • Matrix.traceLinearMap J K K := by
  classical
  let j0 : J := Classical.choice (inferInstance : Nonempty J)
  let c : K := L (Matrix.single j0 j0 1)
  refine ⟨c, ?_⟩
  apply (Matrix.stdBasis K J J).ext
  intro ij
  rcases ij with ⟨i, j⟩
  rw [Matrix.stdBasis_eq_single]
  by_cases hij : i = j
  · subst j
    have hd : L (Matrix.single i i 1) = c := by
      unfold c
      have h := hcyc (Matrix.single j0 i 1) (Matrix.single i j0 1)
      simpa using h.symm
    rw [hd]
    simp
  · have hoff : L (Matrix.single i j 1) = 0 := by
      have h := hcyc (Matrix.single i i 1) (Matrix.single i j 1)
      have hji : j ≠ i := Ne.symm hij
      simpa [Matrix.single_mul_single_of_ne, hij, hji] using h
    rw [hoff]
    simp [Matrix.trace_single_eq_of_ne, hij]

end CyclicFunctional

section IdempotentTrace
variable {K : Type uK} [Field K]
variable {M : Type uM} [AddCommGroup M] [Module K M] [FiniteDimensional K M]
variable {p : ℕ} [CharP K p]

theorem trace_ne_zero_of_idempotent_ne_zero_of_finrank_lt_char
    (P : Module.End K M) (hP : IsIdempotentElem P) (hP0 : P ≠ 0)
    (hchar : Module.finrank K M < p) :
    LinearMap.trace K M P ≠ 0 := by
  rw [hP.isProj_range.trace]
  intro hzero
  have hdvd : p ∣ Module.finrank K (range P) :=
    (CharP.cast_eq_zero_iff K p _).mp hzero
  have hrpos : 0 < Module.finrank K (range P) := by
    rw [Module.finrank_pos_iff]
    exact Submodule.nontrivial_iff_ne_bot.mpr (by
      intro hrbot
      exact hP0 (range_eq_bot.mp hrbot))
  have hrle : Module.finrank K (range P) ≤ Module.finrank K M :=
    Submodule.finrank_le (range P)
  have hrlt : Module.finrank K (range P) < p := lt_of_le_of_lt hrle hchar
  have hp_le : p ≤ Module.finrank K (range P) := Nat.le_of_dvd hrpos hdvd
  exact (not_lt_of_ge hp_le) hrlt

end IdempotentTrace


section WedderburnBlocksViaActionHom

variable {K : Type uK} [Field K]
variable {A : Type uA} [Ring A] [Algebra K A]
variable {I : Type uI} [Fintype I] [DecidableEq I]
variable (d : I → ℕ)
variable (e : A ≃ₐ[K] ∀ i, Matrix (Fin (d i)) (Fin (d i)) K)
variable {M : Type uM} [AddCommGroup M] [Module K M] [FiniteDimensional K M]
variable (act : A →ₐ[K] Module.End K M)

/-- Insert one matrix into a Wedderburn coordinate and transport it back to A. -/
def blockElem' (i : I) (B : Matrix (Fin (d i)) (Fin (d i)) K) : A :=
  e.symm ((LinearMap.single K (fun i => Matrix (Fin (d i)) (Fin (d i)) K) i) B)

omit [Fintype I] in
@[simp] theorem blockElem'_toPi (i : I) (B : Matrix (Fin (d i)) (Fin (d i)) K) :
    e (blockElem' d e i B) = Pi.single i B := by
  simp [blockElem']

omit [Fintype I] in
/-- Multiplication inside one inserted block is ordinary matrix multiplication. -/
theorem blockElem'_mul (i : I)
    (B C : Matrix (Fin (d i)) (Fin (d i)) K) :
    blockElem' d e i B * blockElem' d e i C = blockElem' d e i (B * C) := by
  apply e.injective
  rw [map_mul, blockElem'_toPi, blockElem'_toPi, blockElem'_toPi]
  ext j
  by_cases hji : j = i
  · subst j
    simp
  · simp [hji]

omit [Fintype I] in
/-- Right multiplication by a block-supported element keeps only that block. -/
theorem mul_blockElem' (a : A) (i : I)
    (B : Matrix (Fin (d i)) (Fin (d i)) K) :
    a * blockElem' d e i B = blockElem' d e i (e a i * B) := by
  apply e.injective
  rw [map_mul, blockElem'_toPi, blockElem'_toPi]
  ext j
  by_cases hji : j = i
  · subst j
    simp
  · simp [hji]

omit [Fintype I] in
/-- Block insertion is additive. -/
theorem blockElem'_add (i : I)
    (B C : Matrix (Fin (d i)) (Fin (d i)) K) :
    blockElem' d e i (B + C) = blockElem' d e i B + blockElem' d e i C := by
  let s := LinearMap.single K (fun i => Matrix (Fin (d i)) (Fin (d i)) K) i
  calc
    blockElem' d e i (B + C) = e.symm (s (B + C)) := rfl
    _ = e.symm (s B + s C) := by rw [s.map_add]
    _ = e.symm (s B) + e.symm (s C) := e.symm.map_add _ _
    _ = blockElem' d e i B + blockElem' d e i C := rfl

omit [Fintype I] in
/-- Block insertion is K-linear. -/
theorem blockElem'_smul (i : I) (c : K)
    (B : Matrix (Fin (d i)) (Fin (d i)) K) :
    blockElem' d e i (c • B) = c • blockElem' d e i B := by
  let s := LinearMap.single K (fun i => Matrix (Fin (d i)) (Fin (d i)) K) i
  calc
    blockElem' d e i (c • B) = e.symm (s (c • B)) := rfl
    _ = e.symm (c • s B) := by rw [s.map_smul]
    _ = c • e.symm (s B) := e.symm.toLinearEquiv.map_smul c (s B)
    _ = c • blockElem' d e i B := rfl

/-- Trace of a faithful representation restricted to one Wedderburn block. -/
noncomputable def blockTraceFunctional' (i : I) :
    Matrix (Fin (d i)) (Fin (d i)) K →ₗ[K] K where
  toFun B := LinearMap.trace K M (act (blockElem' d e i B))
  map_add' B C := by
    rw [blockElem'_add, map_add]
    simp
  map_smul' c B := by
    rw [blockElem'_smul, map_smul]
    simp

omit [Fintype I] [FiniteDimensional K M] in
/-- The block trace functional is cyclic. -/
theorem blockTraceFunctional'_cyclic (i : I)
    (B C : Matrix (Fin (d i)) (Fin (d i)) K) :
    blockTraceFunctional' (M := M) d e act i (B * C) =
      blockTraceFunctional' (M := M) d e act i (C * B) := by
  change LinearMap.trace K M (act (blockElem' d e i (B * C))) =
    LinearMap.trace K M (act (blockElem' d e i (C * B)))
  have hBC : act (blockElem' d e i (B * C)) =
      act (blockElem' d e i B) * act (blockElem' d e i C) := by
    rw [← blockElem'_mul]
    exact act.map_mul _ _
  have hCB : act (blockElem' d e i (C * B)) =
      act (blockElem' d e i C) * act (blockElem' d e i B) := by
    rw [← blockElem'_mul]
    exact act.map_mul _ _
  rw [hBC, hCB]
  exact LinearMap.trace_mul_comm K _ _

omit [Fintype I] [FiniteDimensional K M] in
set_option linter.style.haveILetI false in
/-- Each Wedderburn block trace is a scalar multiple of ordinary matrix trace. -/
theorem exists_blockTrace_scalar'
    (hd : ∀ i, 0 < d i) (i : I) :
    ∃ c : K, ∀ B : Matrix (Fin (d i)) (Fin (d i)) K,
      blockTraceFunctional' (M := M) d e act i B = c * Matrix.trace B := by
  let hnon : Nonempty (Fin (d i)) := Fin.pos_iff_nonempty.mp (hd i)
  letI : Nonempty (Fin (d i)) := hnon
  rcases cyclic_linearFunctional_eq_smul_trace
      (blockTraceFunctional' (M := M) d e act i)
      (blockTraceFunctional'_cyclic (M := M) d e act i) with ⟨c, hc⟩
  refine ⟨c, fun B => ?_⟩
  rw [hc]
  simp

omit [Fintype I] in
/-- A matrix unit inserted into a Wedderburn block is nonzero. -/
theorem blockElem'_single_ne_zero (i : I) (j : Fin (d i)) :
    blockElem' d e i (Matrix.single j j 1) ≠ 0 := by
  intro hzero
  have heq := congrArg e hzero
  have hi := congrFun heq i
  have hij := congrFun (congrFun hi j) j
  simp [blockElem'] at hij

omit [Fintype I] [FiniteDimensional K M] in
/-- Injectivity of the algebra action makes the diagonal block action nonzero. -/
theorem block_single_action'_ne_zero
    (hact : Function.Injective act) (i : I) (j : Fin (d i)) :
    act (blockElem' d e i (Matrix.single j j 1)) ≠ 0 := by
  intro hzero
  apply blockElem'_single_ne_zero d e i j
  apply hact
  simpa using hzero

omit [Fintype I] [FiniteDimensional K M] in
/-- The action of a diagonal block matrix unit is idempotent. -/
theorem block_single_action'_idempotent (i : I) (j : Fin (d i)) :
    IsIdempotentElem (act (blockElem' d e i (Matrix.single j j 1))) := by
  rw [IsIdempotentElem]
  let x : A := blockElem' d e i (Matrix.single j j 1)
  have hx : x * x = x := by
    dsimp [x]
    rw [blockElem'_mul]
    simp
  calc
    act x * act x = act (x * x) := (act.map_mul x x).symm
    _ = act x := congrArg act hx

omit [Fintype I] in
/-- In cross characteristic, every block-trace scalar is nonzero. -/
theorem exists_ne_zero_blockTrace_scalar'
    (hact : Function.Injective act)
    (hd : ∀ i, 0 < d i) {p : ℕ} [CharP K p]
    (hchar : Module.finrank K M < p) (i : I) :
    ∃ c : K, c ≠ 0 ∧ ∀ B : Matrix (Fin (d i)) (Fin (d i)) K,
      blockTraceFunctional' (M := M) d e act i B = c * Matrix.trace B := by
  let j : Fin (d i) := ⟨0, hd i⟩
  rcases exists_blockTrace_scalar' (M := M) d e act hd i with ⟨c, hc⟩
  have htrace : blockTraceFunctional' (M := M) d e act i (Matrix.single j j 1) ≠ 0 := by
    exact trace_ne_zero_of_idempotent_ne_zero_of_finrank_lt_char
      (act (blockElem' d e i (Matrix.single j j 1)))
      (block_single_action'_idempotent d e act i j)
      (block_single_action'_ne_zero d e act hact i j) hchar
  have hc0 : c ≠ 0 := by
    intro hcz
    apply htrace
    rw [hc (Matrix.single j j 1), hcz, zero_mul]
  exact ⟨c, hc0, hc⟩

omit [Fintype I] in
/-- The representation trace pairing is nondegenerate on a faithfully represented
Wedderburn algebra in cross characteristic. -/
theorem representation_trace_pairing_nondegenerate'
    (e : A ≃ₐ[K] ∀ i, Matrix (Fin (d i)) (Fin (d i)) K)
    (hact : Function.Injective act)
    (hd : ∀ i, 0 < d i) {p : ℕ} [CharP K p]
    (hchar : Module.finrank K M < p) :
    ∀ a : A,
      (∀ b : A, LinearMap.trace K M (act (a * b)) = 0) → a = 0 := by
  intro a hall
  by_contra ha
  have hcomp : ∃ i : I, e a i ≠ 0 := by
    by_contra hnone
    have hnone' : ∀ i : I, e a i = 0 := by
      simpa only [not_exists, not_ne_iff] using hnone
    have hea : e a = 0 := by funext i; exact hnone' i
    exact ha (e.injective (by simpa using hea))
  rcases hcomp with ⟨i, hai⟩
  have htest : ∃ B : Matrix (Fin (d i)) (Fin (d i)) K,
      Matrix.trace (e a i * B) ≠ 0 := by
    by_contra hnone
    have hnone' : ∀ B : Matrix (Fin (d i)) (Fin (d i)) K,
        Matrix.trace (e a i * B) = 0 := by
      simpa only [not_exists, not_ne_iff] using hnone
    have hz : e a i = 0 := (Matrix.ext_iff_trace_mul_right).2 (fun B => by
      simpa using hnone' B)
    exact hai hz
  rcases htest with ⟨B, hB⟩
  rcases exists_ne_zero_blockTrace_scalar' (M := M) d e act hact hd hchar i with
    ⟨c, hc, hformula⟩
  let b : A := blockElem' d e i B
  have hzero := hall b
  have hab : a * b = blockElem' d e i (e a i * B) := by
    simpa [b] using mul_blockElem' d e a i B
  have hzero' : blockTraceFunctional' (M := M) d e act i (e a i * B) = 0 := by
    change LinearMap.trace K M (act (blockElem' d e i (e a i * B))) = 0
    rw [← hab]
    exact hzero
  rw [hformula (e a i * B)] at hzero'
  exact (mul_ne_zero hc hB) hzero'

end WedderburnBlocksViaActionHom


end Komorebi.StrongArtin.BlockTrace

namespace Komorebi.StrongArtin.FiniteCore

open Komorebi.StrongArtin.BlockTrace

section FullFiniteTraceClosure

universe uGfull uKfull
variable {Gfull : Type uGfull} [Group Gfull]
variable {Kfull : Type uKfull} [Field Kfull] [IsAlgClosed Kfull]

/-- Canonical faithful linear action of the generated matrix image algebra on K^n. -/
noncomputable def matrixImageAction (n : ℕ)
    (ρ : Gfull →* Matrix (Fin n) (Fin n) Kfull) :
    matrixImageAlgebra n ρ →ₐ[Kfull] Module.End Kfull (Fin n → Kfull) :=
  (Matrix.toLinAlgEquiv' : Matrix (Fin n) (Fin n) Kfull ≃ₐ[Kfull]
      Module.End Kfull (Fin n → Kfull)).toAlgHom.comp
    (Subalgebra.val (matrixImageAlgebra n ρ))

omit [IsAlgClosed Kfull] in
/-- The canonical image-algebra action is injective. -/
theorem matrixImageAction_injective (n : ℕ)
    (ρ : Gfull →* Matrix (Fin n) (Fin n) Kfull) :
    Function.Injective (matrixImageAction n ρ) := by
  intro a b hab
  apply Subtype.ext
  apply (Matrix.toLinAlgEquiv' : Matrix (Fin n) (Fin n) Kfull ≃ₐ[Kfull]
      Module.End Kfull (Fin n → Kfull)).injective
  exact hab

omit [IsAlgClosed Kfull] in
/-- Trace of the canonical action is exactly ordinary matrix trace. -/
theorem matrixImageAction_trace (n : ℕ)
    (ρ : Gfull →* Matrix (Fin n) (Fin n) Kfull)
    (a : matrixImageAlgebra n ρ) :
    LinearMap.trace Kfull (Fin n → Kfull) (matrixImageAction n ρ a) =
      (a : Matrix (Fin n) (Fin n) Kfull).trace := by
  change LinearMap.trace Kfull (Fin n → Kfull)
      (Matrix.toLinAlgEquiv' (a : Matrix (Fin n) (Fin n) Kfull)) = _
  exact Matrix.trace_toLin'_eq _

set_option linter.style.haveILetI false in
/-- Full finite trace-image theorem in the manuscript's hypotheses.  The defining
module is assumed semisimple, the coefficient field is algebraically closed of
characteristic ell, and ell > n.  Lean derives the Wedderburn decomposition,
nondegenerate representation trace pairing, and the t^(n^2) count internally. -/
theorem finite_trace_image_bound_semisimple
    [Fintype Gfull]
    (ell n : ℕ) [CharP Kfull ell]
    (ρ : Gfull →* Matrix (Fin n) (Fin n) Kfull)
    (hρ : Function.Injective ρ)
    (hnell : n < ell)
    (hsem :
      let A := matrixImageAlgebra n ρ
      letI : Module (Matrix (Fin n) (Fin n) Kfull) (Fin n → Kfull) :=
        Matrix.Module.matrixModule
      letI : Module A (Fin n → Kfull) :=
        Module.compHom (Fin n → Kfull) (SubsemiringClass.subtype A)
      IsSemisimpleModule A (Fin n → Kfull)) :
    Fintype.card Gfull ≤
      (matrixTraceAlphabet n ρ).ncard ^ (n ^ 2) := by
  rcases matrixImageAlgebra_exists_block_decomposition_of_semisimple
      (Ksi := Kfull) n ρ hsem with ⟨r, d, hdNZ, ⟨e⟩⟩
  have hd : ∀ i : Fin r, 0 < d i := by
    intro i
    exact Nat.pos_of_ne_zero (NeZero.ne (d i))
  have hdim : Module.finrank Kfull (Fin n → Kfull) < ell := by
    simpa using hnell
  have hrep := representation_trace_pairing_nondegenerate'
    (M := Fin n → Kfull) (d := d) (e := e)
    (act := matrixImageAction n ρ)
    (matrixImageAction_injective n ρ) hd hdim
  apply finite_trace_image_bound_of_nondegenerate_image_pairing n ρ hρ
  intro x hx
  apply hrep x
  intro y
  have hxy : imageTracePairing n ρ x y = 0 := by
    have := congrArg (fun f => f y) hx
    simpa using this
  change (((x : Matrix (Fin n) (Fin n) Kfull) *
    (y : Matrix (Fin n) (Fin n) Kfull)).trace) = 0 at hxy
  rw [matrixImageAction_trace n ρ (x * y)]
  exact hxy

end FullFiniteTraceClosure

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.BlockTrace.cyclic_linearFunctional_eq_smul_trace
#print axioms Komorebi.StrongArtin.BlockTrace.exists_ne_zero_blockTrace_scalar'
#print axioms Komorebi.StrongArtin.BlockTrace.representation_trace_pairing_nondegenerate'
#print axioms Komorebi.StrongArtin.FiniteCore.matrixImageAction_trace

namespace Komorebi.StrongArtin.FiniteCore

section CrossCharacteristicThreshold

universe uGcc uKcc
variable {Gcc : Type uGcc} [Group Gcc] [Fintype Gcc]
variable {Kcc : Type uKcc} [Field Kcc] [IsAlgClosed Kcc]

/-- Pure finite arithmetic: a positive finite group order bounded strictly below
`ell` cannot be divisible by `ell`. -/
theorem not_dvd_card_of_card_lt
    (ell : ℕ) (hcard : Fintype.card Gcc < ell) :
    ¬ ell ∣ Fintype.card Gcc := by
  intro hdvd
  have hpos : 0 < Fintype.card Gcc := Fintype.card_pos
  have hle : ell ≤ Fintype.card Gcc := Nat.le_of_dvd hpos hdvd
  exact (not_lt_of_ge hle) hcard

/-- The checked trace bound forces the residual image into cross characteristic
as soon as `ell` exceeds the universal trace-alphabet bound. -/
theorem residual_image_cross_characteristic
    (ell n : ℕ) [CharP Kcc ell]
    (ρ : Gcc →* Matrix (Fin n) (Fin n) Kcc)
    (hρ : Function.Injective ρ)
    (hnell : n < ell)
    (hsem :
      let A := matrixImageAlgebra n ρ
      letI : Module (Matrix (Fin n) (Fin n) Kcc) (Fin n → Kcc) :=
        Matrix.Module.matrixModule
      letI : Module A (Fin n → Kcc) :=
        Module.compHom (Fin n → Kcc) (SubsemiringClass.subtype A)
      IsSemisimpleModule A (Fin n → Kcc))
    (hlarge : (matrixTraceAlphabet n ρ).ncard ^ (n ^ 2) < ell) :
    ¬ ell ∣ Fintype.card Gcc := by
  have hbound := finite_trace_image_bound_semisimple ell n ρ hρ hnell hsem
  have hcard : Fintype.card Gcc < ell := lt_of_le_of_lt hbound hlarge
  exact not_dvd_card_of_card_lt (Gcc := Gcc) ell hcard

/-- A finite alphabet is separating for a reduction map exactly when that map
is injective on the alphabet.  This packages the coefficient-prime step without
assuming any number-theoretic existence theorem. -/
def SeparatingOn {P Q : Type*} (A : Set P) (red : P → Q) : Prop :=
  Set.InjOn red A

/-- At a separating reduction, equality after reduction forces equality in
characteristic zero for members of the declared finite alphabet. -/
theorem eq_of_reduction_eq_of_separating
    {P Q : Type*} {A : Set P} {red : P → Q}
    (hsep : SeparatingOn A red)
    {P₁ P₂ : P} (hP₁ : P₁ ∈ A) (hP₂ : P₂ ∈ A)
    (hred : red P₁ = red P₂) :
    P₁ = P₂ :=
  hsep hP₁ hP₂ hred

/-- Finite one-prime funnel: if both the target and candidate local data belong
to one separating alphabet, residual equality determines the characteristic-zero
label exactly. -/
theorem one_prime_finite_alphabet_funnel
    {V Q : Type*} {A : Set V} {red : V → Q}
    (hsep : SeparatingOn A red)
    {target candidate : V}
    (ht : target ∈ A) (hc : candidate ∈ A)
    (hmod : red candidate = red target) :
    candidate = target := by
  exact hsep hc ht hmod

end CrossCharacteristicThreshold

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.finite_trace_image_bound_semisimple

namespace Komorebi.StrongArtin.FiniteCore

/-! ## Universal bounded cyclotomic alphabet -/

section BoundedCyclotomicAlphabet

universe uKba
variable {Kba : Type uKba} [Field Kba]

/-- All roots of unity whose order is at most `B`, represented as a finite union
of the root sets of `X^m - 1` for `1 ≤ m ≤ B`. -/
noncomputable def boundedRootsOfUnity (B : ℕ) : Finset Kba := by
  classical
  exact (Finset.range B).biUnion (fun i => Polynomial.nthRootsFinset (i + 1) (1 : Kba))

/-- Membership in the bounded root alphabet is exactly bounded torsion. -/
theorem mem_boundedRootsOfUnity_iff (B : ℕ) (z : Kba) :
    z ∈ boundedRootsOfUnity (Kba := Kba) B ↔
      ∃ m : ℕ, 0 < m ∧ m ≤ B ∧ z ^ m = 1 := by
  classical
  constructor
  · intro hz
    rcases Finset.mem_biUnion.mp hz with ⟨i, hi, hzi⟩
    refine ⟨i + 1, Nat.succ_pos i, ?_, ?_⟩
    · exact Nat.succ_le_iff.mpr (Finset.mem_range.mp hi)
    · exact (Polynomial.mem_nthRootsFinset (Nat.succ_pos i) (1 : Kba)).mp hzi
  · rintro ⟨m, hmpos, hmB, hzm⟩
    obtain ⟨i, rfl⟩ := Nat.exists_eq_succ_of_ne_zero (Nat.ne_of_gt hmpos)
    apply Finset.mem_biUnion.mpr
    refine ⟨i, ?_, ?_⟩
    · exact Finset.mem_range.mpr (Nat.lt_of_succ_le hmB)
    · exact (Polynomial.mem_nthRootsFinset (Nat.succ_pos i) (1 : Kba)).mpr hzm

/-- The abstract finite type of bounded roots of unity. -/
abbrev BoundedRoot (B : ℕ) := ↥(boundedRootsOfUnity (Kba := Kba) B)

/-- The universal degree-`n` bounded cyclotomic polynomial alphabet: all monic
split polynomials whose roots have order at most `B`. -/
noncomputable def boundedCyclotomicAlphabet (B n : ℕ) : Finset (Polynomial Kba) := by
  classical
  let Ω := BoundedRoot (Kba := Kba) B
  exact (Finset.univ : Finset (Sym Ω n)).image
    (splitPolynomialOfSym n (fun z : Ω => (z : Kba)))

/-- The bounded cyclotomic alphabet has the exact symmetric-power cardinality. -/
theorem card_boundedCyclotomicAlphabet (B n : ℕ) :
    (boundedCyclotomicAlphabet (Kba := Kba) B n).card =
      ((boundedRootsOfUnity (Kba := Kba) B).card + n - 1).choose n := by
  classical
  let Ω := BoundedRoot (Kba := Kba) B
  let encode : Sym Ω n → Polynomial Kba :=
    splitPolynomialOfSym n (fun z : Ω => (z : Kba))
  have henc : Function.Injective encode := by
    exact splitPolynomialOfSym_injective n (fun z : Ω => (z : Kba)) Subtype.val_injective
  change ((Finset.univ : Finset (Sym Ω n)).image encode).card = _
  rw [Finset.card_image_of_injective _ henc]
  simp only [Finset.card_univ]
  rw [root_multiset_count]
  simp [Ω]

/-- In particular the universal bounded cyclotomic alphabet is finite, with an
explicit manuscript-compatible cardinal bound. -/
theorem finite_boundedCyclotomicAlphabet (B n : ℕ) :
    Set.Finite (↑(boundedCyclotomicAlphabet (Kba := Kba) B n) : Set (Polynomial Kba)) :=
  (boundedCyclotomicAlphabet (Kba := Kba) B n).finite_toSet

end BoundedCyclotomicAlphabet

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.mem_boundedRootsOfUnity_iff
#print axioms Komorebi.StrongArtin.FiniteCore.card_boundedCyclotomicAlphabet


namespace Komorebi.StrongArtin.FiniteCore

/-! ## Finite-image matrices land in the bounded cyclotomic alphabet -/

section FiniteImageCyclotomicAlphabet

universe uKfi uGfi
variable {Kfi : Type uKfi} [Field Kfi]

/-- Every characteristic-polynomial root of a finite-order matrix has the same
bounded torsion order. -/
theorem charpoly_root_pow_eq_one_of_matrix_pow_eq_one
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (A : Matrix ι ι Kfi) (m : ℕ) (hA : A ^ m = 1)
    {z : Kfi} (hz : z ∈ A.charpoly.roots) :
    z ^ m = 1 := by
  have hroot : A.charpoly.IsRoot z :=
    (Polynomial.mem_roots A.charpoly_monic.ne_zero).mp hz
  have hrootLin : (Matrix.toLin' A).charpoly.IsRoot z := by
    rw [Matrix.charpoly_toLin']
    exact hroot
  have hev : Module.End.HasEigenvalue (Matrix.toLin' A) z :=
    (Module.End.hasEigenvalue_iff_isRoot_charpoly _ _).mpr hrootLin
  rcases hev.exists_hasEigenvector with ⟨v, hv⟩
  have hp := hv.pow_apply m
  have hlin : (Matrix.toLin' A) ^ m = LinearMap.id := by
    rw [← Matrix.toLin'_pow, hA, Matrix.toLin'_one]
  rw [hlin] at hp
  simp only [LinearMap.id_apply] at hp
  have hzero : (z ^ m - 1) • v = 0 := by
    rw [sub_smul, one_smul, ← hp, sub_self]
  have hs : z ^ m - 1 = 0 ∨ v = 0 := (smul_eq_zero.mp hzero)
  exact sub_eq_zero.mp (hs.resolve_right hv.2)

/-- The image of any element of a finite group has exponent dividing the group
cardinality. -/
theorem finite_group_matrix_pow_card_eq_one
    {G : Type uGfi} [Group G] [Fintype G]
    (n : ℕ) (ρ : G →* Matrix (Fin n) (Fin n) Kfi) (g : G) :
    (ρ g) ^ Fintype.card G = 1 := by
  rw [← map_pow, pow_card_eq_one, map_one]

/-- If `|G| ≤ B`, every root of every characteristic polynomial in a finite
matrix image belongs to the universal bounded root alphabet `Ω_B`. -/
theorem finite_image_charpoly_roots_bounded
    {G : Type uGfi} [Group G] [Fintype G]
    (B n : ℕ) (ρ : G →* Matrix (Fin n) (Fin n) Kfi)
    (hcard : Fintype.card G ≤ B) (g : G) :
    ∀ z ∈ (ρ g).charpoly.roots,
      z ∈ boundedRootsOfUnity (Kba := Kfi) B := by
  intro z hz
  rw [mem_boundedRootsOfUnity_iff]
  refine ⟨Fintype.card G, Fintype.card_pos, hcard, ?_⟩
  exact charpoly_root_pow_eq_one_of_matrix_pow_eq_one
    (ρ g) (Fintype.card G) (finite_group_matrix_pow_card_eq_one n ρ g) hz

end FiniteImageCyclotomicAlphabet

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.charpoly_root_pow_eq_one_of_matrix_pow_eq_one
#print axioms Komorebi.StrongArtin.FiniteCore.finite_image_charpoly_roots_bounded

namespace Komorebi.StrongArtin.FiniteCore

section FiniteImagePolynomialAlphabet

universe uKfp uGfp
variable {Kfp : Type uKfp} [Field Kfp] [IsAlgClosed Kfp]
variable {Gfp : Type uGfp} [Group Gfp] [Fintype Gfp]

/-- A characteristic polynomial of a finite image of order at most `B` is a
member of the universal degree-`n` bounded cyclotomic alphabet. -/
theorem finite_image_charpoly_mem_boundedCyclotomicAlphabet
    (B n : ℕ) (ρ : Gfp →* Matrix (Fin n) (Fin n) Kfp)
    (hcard : Fintype.card Gfp ≤ B) (g : Gfp) :
    (ρ g).charpoly ∈ boundedCyclotomicAlphabet (Kba := Kfp) B n := by
  classical
  let Ω := BoundedRoot (Kba := Kfp) B
  have hall : ∀ z ∈ (ρ g).charpoly.roots,
      z ∈ boundedRootsOfUnity (Kba := Kfp) B :=
    finite_image_charpoly_roots_bounded B n ρ hcard g
  let rootsΩ : Multiset Ω :=
    Multiset.pmap (fun z hz => (⟨z, hz⟩ : Ω)) (ρ g).charpoly.roots hall
  have hsplit : (ρ g).charpoly.Splits := IsAlgClosed.splits _
  have hcardroots : (ρ g).charpoly.roots.card = n := by
    have hs := hsplit.natDegree_eq_card_roots
    rw [Matrix.charpoly_natDegree_eq_dim] at hs
    simpa using hs.symm
  have hcardΩ : rootsΩ.card = n := by
    simpa [rootsΩ] using hcardroots
  let s : Sym Ω n := Sym.mk rootsΩ hcardΩ
  have hmap : rootsΩ.map (fun z : Ω => (z : Kfp)) = (ρ g).charpoly.roots := by
    unfold rootsΩ
    rw [Multiset.map_pmap]
    rw [Multiset.pmap_eq_map]
    simp
  have hencode :
      splitPolynomialOfSym n (fun z : Ω => (z : Kfp)) s = (ρ g).charpoly := by
    unfold splitPolynomialOfSym s
    change (((rootsΩ.map (fun z : Ω => (z : Kfp))).map
      (fun a => Polynomial.X - Polynomial.C a)).prod) = (ρ g).charpoly
    rw [hmap]
    exact Polynomial.prod_multiset_X_sub_C_of_monic_of_roots_card_eq
      (ρ g).charpoly_monic hsplit.natDegree_eq_card_roots.symm
  unfold boundedCyclotomicAlphabet
  apply Finset.mem_image.mpr
  refine ⟨s, Finset.mem_univ s, ?_⟩
  exact hencode

end FiniteImagePolynomialAlphabet

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.finite_image_charpoly_mem_boundedCyclotomicAlphabet

namespace Komorebi.StrongArtin.FiniteCore

/-! ## Post-Brauer finite-alphabet funnel -/

section PostBrauerFunnel

universe uKpb uGpb uQpb
variable {Kpb : Type uKpb} [Field Kpb] [IsAlgClosed Kpb]
variable {Gpb : Type uGpb} [Group Gpb] [Fintype Gpb]

/-- The finite alphabet used after cross-characteristic lifting: the declared
target polynomial alphabet together with all bounded finite-image lift
polynomials. -/
noncomputable def enlargedLiftAlphabet
    (targetAlphabet : Finset (Polynomial Kpb)) (B n : ℕ) :
    Finset (Polynomial Kpb) := by
  classical
  exact targetAlphabet ∪ boundedCyclotomicAlphabet (Kba := Kpb) B n

omit [IsAlgClosed Kpb] in
@[simp] theorem target_mem_enlargedLiftAlphabet
    (targetAlphabet : Finset (Polynomial Kpb)) (B n : ℕ)
    {P : Polynomial Kpb} (hP : P ∈ targetAlphabet) :
    P ∈ enlargedLiftAlphabet targetAlphabet B n := by
  classical
  simp [enlargedLiftAlphabet, hP]

/-- A characteristic polynomial from a finite lift of order at most `B` belongs
to the enlarged finite alphabet. -/
theorem lifted_charpoly_mem_enlargedLiftAlphabet
    (targetAlphabet : Finset (Polynomial Kpb)) (B n : ℕ)
    (ρ : Gpb →* Matrix (Fin n) (Fin n) Kpb)
    (hcard : Fintype.card Gpb ≤ B) (g : Gpb) :
    (ρ g).charpoly ∈ enlargedLiftAlphabet targetAlphabet B n := by
  classical
  simp only [enlargedLiftAlphabet, Finset.mem_union]
  exact Or.inr (finite_image_charpoly_mem_boundedCyclotomicAlphabet B n ρ hcard g)

/-- Post-Brauer one-prime funnel.  Once a characteristic-zero lift is supplied,
the finite image bound places its local polynomial in the bounded alphabet; a
coefficient reduction that is injective on the enlarged finite alphabet then
forces residual equality to be exact characteristic-zero equality. -/
theorem post_brauer_separating_funnel
    (targetAlphabet : Finset (Polynomial Kpb)) (B n : ℕ)
    (ρ : Gpb →* Matrix (Fin n) (Fin n) Kpb)
    (hcard : Fintype.card Gpb ≤ B) (g : Gpb)
    {target : Polynomial Kpb} (htarget : target ∈ targetAlphabet)
    {Qpb : Type uQpb} (red : Polynomial Kpb → Qpb)
    (hsep : SeparatingOn
      (↑(enlargedLiftAlphabet targetAlphabet B n) : Set (Polynomial Kpb)) red)
    (hmod : red (ρ g).charpoly = red target) :
    (ρ g).charpoly = target := by
  apply eq_of_reduction_eq_of_separating hsep
  · exact lifted_charpoly_mem_enlargedLiftAlphabet targetAlphabet B n ρ hcard g
  · exact target_mem_enlargedLiftAlphabet targetAlphabet B n htarget
  · exact hmod

end PostBrauerFunnel

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.post_brauer_separating_funnel

namespace Komorebi.StrongArtin.FiniteCore

/-! ## Conditional large-residual realization funnel -/

section LargeResidualConditional

universe uGlar uKres uKlift uQlar
variable {Glar : Type uGlar} [Group Glar] [Fintype Glar]
variable {Kres : Type uKres} [Field Kres] [IsAlgClosed Kres]
variable {Klift : Type uKlift} [Field Klift] [IsAlgClosed Klift]

/-- Finite algebraic content of the manuscript's large-residual realization
argument.  Lean proves the image-order bound, cross-characteristic conclusion,
bounded cyclotomic alphabet for any supplied characteristic-zero lift, and the
separating-prime upgrade.  The existence/reduction compatibility of the lift and
the separating reduction itself remain explicit inputs. -/
theorem large_residual_post_lift_exact
    (ell n : ℕ) [CharP Kres ell] [CharZero Klift]
    (ρres : Glar →* Matrix (Fin n) (Fin n) Kres)
    (hρres : Function.Injective ρres)
    (hnell : n < ell)
    (hsem :
      let A := matrixImageAlgebra n ρres
      letI : Module (Matrix (Fin n) (Fin n) Kres) (Fin n → Kres) :=
        Matrix.Module.matrixModule
      letI : Module A (Fin n → Kres) :=
        Module.compHom (Fin n → Kres) (SubsemiringClass.subtype A)
      IsSemisimpleModule A (Fin n → Kres))
    (hlarge : (matrixTraceAlphabet n ρres).ncard ^ (n ^ 2) < ell)
    (lift : Glar →* Matrix (Fin n) (Fin n) Klift)
    (targetAlphabet : Finset (Polynomial Klift))
    (target : Glar → Polynomial Klift)
    (htarget : ∀ g, target g ∈ targetAlphabet)
    {Qlar : Type uQlar} (red : Polynomial Klift → Qlar)
    (hsep : SeparatingOn
      (↑(enlargedLiftAlphabet targetAlphabet
        ((matrixTraceAlphabet n ρres).ncard ^ (n ^ 2)) n) : Set (Polynomial Klift)) red)
    (hmod : ∀ g, red (lift g).charpoly = red (target g)) :
    (¬ ell ∣ Fintype.card Glar) ∧
      ∀ g, (lift g).charpoly = target g := by
  let B := (matrixTraceAlphabet n ρres).ncard ^ (n ^ 2)
  have hbound : Fintype.card Glar ≤ B :=
    finite_trace_image_bound_semisimple ell n ρres hρres hnell hsem
  have hcross : ¬ ell ∣ Fintype.card Glar :=
    not_dvd_card_of_card_lt ell (lt_of_le_of_lt hbound hlarge)
  refine ⟨hcross, ?_⟩
  intro g
  exact post_brauer_separating_funnel
    targetAlphabet B n lift hbound g (htarget g) red hsep (hmod g)

end LargeResidualConditional

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.large_residual_post_lift_exact

namespace Komorebi.StrongArtin.FiniteCore

/-! ## Finite-index local Artin descent core -/

section FiniteIndexImage

universe uGidx uRidx
variable {Gidx : Type uGidx} [Group Gidx]
variable {Ridx : Type uRidx} [Group Ridx]

set_option linter.style.haveILetI false in
/-- Pure group-theoretic core of local Artin descent: if the image of a
finite-index subgroup is finite, then the full homomorphism image is finite. -/
theorem finite_range_of_finite_index_subgroup_image
    (H : Subgroup Gidx) [H.FiniteIndex]
    (ρ : Gidx →* Ridx)
    (hfinite : Finite (H.map ρ.rangeRestrict)) :
    Set.Finite (Set.range ρ) := by
  let f : Gidx →* ρ.range := ρ.rangeRestrict
  let K : Subgroup ρ.range := H.map f
  have hf : Function.Surjective f := by
    simpa [f] using ρ.rangeRestrict_surjective
  have hdiv : K.index ∣ H.index :=
    H.index_map_dvd hf
  letI : Finite K := hfinite
  letI : K.FiniteIndex := ⟨by
    intro hKzero
    apply Subgroup.FiniteIndex.index_ne_zero (H := H)
    rcases hdiv with ⟨c, hc⟩
    rw [hc, hKzero, zero_mul]
  ⟩
  letI : Finite ρ.range := Finite.of_subgroup_quotient K
  have hrange : (ρ.range : Set Ridx).Finite := Set.toFinite _
  simpa only [MonoidHom.coe_range] using hrange

end FiniteIndexImage

end Komorebi.StrongArtin.FiniteCore

#print axioms Komorebi.StrongArtin.FiniteCore.finite_range_of_finite_index_subgroup_image


namespace Komorebi.StrongArtin.Separating

open UniqueFactorizationMonoid

universe uR
variable {R : Type uR} [CommRing R] [IsDedekindDomain R]

/-- A nonzero element of a Dedekind domain belongs to only finitely many prime ideals. -/
theorem primeIdealsContaining_nonzero_finite (x : R) (hx : x ≠ 0) :
    Set.Finite {P : Ideal R | P.IsPrime ∧ x ∈ P} := by
  let I : Ideal R := Ideal.span {x}
  have hI : I ≠ ⊥ := by
    simpa [I, Ideal.span_singleton_eq_bot] using hx
  have hsub : {P : Ideal R | P.IsPrime ∧ x ∈ P} ⊆
      (↑((normalizedFactors I).toFinset) : Set (Ideal R)) := by
    intro P hP
    have hle : I ≤ P := by
      change Ideal.span {x} ≤ P
      rw [Ideal.span_singleton_le_iff_mem]
      exact hP.2
    have hm : P ∈ normalizedFactors I :=
      (Ideal.mem_normalizedFactors_iff hI).2 ⟨hP.1, hle⟩
    simpa using hm
  exact (Set.finite_mem_finset ((normalizedFactors I).toFinset)).subset hsub

end Komorebi.StrongArtin.Separating

namespace Komorebi.StrongArtin.Separating

universe uR
variable {R : Type uR} [CommRing R] [IsDedekindDomain R]

/-- Two distinct polynomials over a Dedekind domain collide after quotient reduction
at only finitely many prime ideals. -/
theorem polynomial_collision_primes_finite
    (P Q : Polynomial R) (hPQ : P ≠ Q) :
    Set.Finite {I : Ideal R |
      I.IsPrime ∧ P.map (Ideal.Quotient.mk I) = Q.map (Ideal.Quotient.mk I)} := by
  classical
  obtain ⟨n, hn⟩ : ∃ n : ℕ, P.coeff n ≠ Q.coeff n := by
    by_contra h
    push Not at h
    apply hPQ
    ext m
    exact h m
  let d : R := P.coeff n - Q.coeff n
  have hd : d ≠ 0 := sub_ne_zero.mpr hn
  have hfinite := primeIdealsContaining_nonzero_finite d hd
  apply hfinite.subset
  intro I hI
  refine ⟨hI.1, ?_⟩
  have hc := congrArg (fun f : Polynomial (R ⧸ I) => f.coeff n) hI.2
  simp only [Polynomial.coeff_map] at hc
  have hz : Ideal.Quotient.mk I d = 0 := by
    change Ideal.Quotient.mk I (P.coeff n - Q.coeff n) = 0
    rw [map_sub, hc, sub_self]
  exact Ideal.Quotient.eq_zero_iff_mem.mp hz

end Komorebi.StrongArtin.Separating

namespace Komorebi.StrongArtin.Separating

universe uR
variable {R : Type uR} [CommRing R] [IsDedekindDomain R]

/-- Prime ideals at which two distinct members of a finite polynomial alphabet
become equal after coefficientwise quotient reduction form a finite set. -/
theorem finite_alphabet_bad_reduction_primes_finite
    (A : Finset (Polynomial R)) :
    Set.Finite {I : Ideal R |
      I.IsPrime ∧ ∃ P ∈ A, ∃ Q ∈ A, P ≠ Q ∧
        P.map (Ideal.Quotient.mk I) = Q.map (Ideal.Quotient.mk I)} := by
  classical
  let PairBad : Polynomial R → Polynomial R → Set (Ideal R) :=
    fun P Q => {I : Ideal R |
      I.IsPrime ∧ P ≠ Q ∧
        P.map (Ideal.Quotient.mk I) = Q.map (Ideal.Quotient.mk I)}
  have hPair : ∀ P Q : Polynomial R, (PairBad P Q).Finite := by
    intro P Q
    by_cases hPQ : P = Q
    · subst Q
      simp [PairBad]
    · exact (polynomial_collision_primes_finite P Q hPQ).subset (by
        intro I hI
        exact ⟨hI.1, hI.2.2⟩)
  let S : Set (Ideal R) :=
    ⋃ P : {P : Polynomial R // P ∈ A},
      ⋃ Q : {Q : Polynomial R // Q ∈ A}, PairBad P.1 Q.1
  have hS : S.Finite := by
    unfold S
    exact Set.finite_iUnion (fun P => Set.finite_iUnion (fun Q => hPair P.1 Q.1))
  apply hS.subset
  intro I hI
  rcases hI with ⟨hprime, P, hPA, Q, hQA, hPQ, hred⟩
  unfold S
  apply Set.mem_iUnion.mpr
  refine ⟨⟨P, hPA⟩, ?_⟩
  apply Set.mem_iUnion.mpr
  refine ⟨⟨Q, hQA⟩, ?_⟩
  exact ⟨hprime, hPQ, hred⟩

end Komorebi.StrongArtin.Separating

namespace Komorebi.StrongArtin.Separating

universe uR
variable {R : Type uR} [CommRing R] [IsDedekindDomain R]

/-- Separating-prime theorem for a finite integral polynomial alphabet over a
Dedekind domain: outside a finite exceptional set of prime ideals, quotient
reduction is injective on the alphabet. -/
theorem finite_alphabet_separating_primes
    (A : Finset (Polynomial R)) :
    ∃ Bad : Set (Ideal R), Bad.Finite ∧
      ∀ I : Ideal R, I.IsPrime → I ∉ Bad →
        Set.InjOn (fun P : Polynomial R => P.map (Ideal.Quotient.mk I)) (↑A : Set (Polynomial R)) := by
  classical
  let Bad : Set (Ideal R) := {I : Ideal R |
    I.IsPrime ∧ ∃ P ∈ A, ∃ Q ∈ A, P ≠ Q ∧
      P.map (Ideal.Quotient.mk I) = Q.map (Ideal.Quotient.mk I)}
  refine ⟨Bad, ?_, ?_⟩
  · exact finite_alphabet_bad_reduction_primes_finite A
  · intro I hprime hIbad P hPA Q hQA hred
    by_contra hPQ
    apply hIbad
    exact ⟨hprime, P, hPA, Q, hQA, hPQ, hred⟩

end Komorebi.StrongArtin.Separating



namespace Komorebi.StrongArtin.CyclicSimple

open scoped MonoidAlgebra
open MonoidAlgebra

universe uKcp uVcp

/-- A multiplicative model of the cyclic quotient of order `p`. -/
abbrev Cp (p : ℕ) := Multiplicative (ZMod p)

lemma cp_pow_prime_eq_one (p : ℕ) (g : Cp p) : g ^ p = 1 := by
  apply Multiplicative.toAdd.injective
  change p • g.toAdd = 0
  exact ZModModule.char_nsmul_eq_zero p g.toAdd

section DimensionOne

variable (p : ℕ)
variable {Kcp : Type uKcp} [Field Kcp] [IsAlgClosed Kcp]
variable {Vcp : Type uVcp} [AddCommGroup Vcp] [Module Kcp Vcp] [FiniteDimensional Kcp Vcp]

/-- Irreducibility for a representation of the abelian group `C_p` over an
algebraically closed field forces one-dimensionality. -/
theorem irreducible_cp_finrank_one
    (ρ : Representation Kcp (Cp p) Vcp) [Representation.IsIrreducible ρ] :
    Module.finrank Kcp Vcp = 1 := by
  exact Representation.IsIrreducible.finrank_eq_one_of_isMulCommutative ρ

end DimensionOne

section CharacteristicP

variable (p : ℕ) [Fact p.Prime]
variable {Kcp : Type uKcp} [Field Kcp] [IsAlgClosed Kcp] [CharP Kcp p]
variable {Vcp : Type uVcp} [AddCommGroup Vcp] [Module Kcp Vcp] [FiniteDimensional Kcp Vcp]

/-- Quotient-prime simple-module collapse: every irreducible representation of
`C_p` over an algebraically closed field of characteristic `p` is trivial. -/
theorem irreducible_cp_trivial
    (ρ : Representation Kcp (Cp p) Vcp) [Representation.IsIrreducible ρ] :
    ∀ g : Cp p, ρ g = LinearMap.id := by
  intro g
  have d1 : Module.finrank Kcp Vcp = 1 := irreducible_cp_finrank_one p ρ
  obtain ⟨c, hc, _⟩ := LinearMap.existsUnique_eq_smul_id_of_finrank_eq_one d1 (ρ g)
  have hgp : g ^ p = 1 := cp_pow_prime_eq_one p g
  have hpow : (ρ g) ^ p = 1 := by
    rw [← map_pow, hgp, map_one]
  have hscalarpow : (c ^ p) • LinearMap.id = (1 : Module.End Kcp Vcp) := by
    rw [← hpow, hc]
    simp [smul_pow]
  rw [Module.End.one_eq_id] at hscalarpow
  let e := LinearEquiv.smul_id_of_finrank_eq_one d1
  have hcp : c ^ p = 1 := by
    apply e.injective
    simpa [e] using hscalarpow
  have hc1 : c = 1 :=
    Komorebi.StrongArtin.FiniteCore.p_torsion_scalar_eq_one p c hcp
  simpa [hc1] using hc

/-- Class-valued form of the same theorem. -/
theorem irreducible_cp_isTrivial
    (ρ : Representation Kcp (Cp p) Vcp) [Representation.IsIrreducible ρ] :
    Representation.IsTrivial ρ :=
  ⟨irreducible_cp_trivial p ρ⟩

end CharacteristicP

section SemisimpleCharacteristicP

variable (p : ℕ) [Fact p.Prime]
variable {Kcp : Type uKcp} [Field Kcp] [CharP Kcp p]
variable {Vcp : Type uVcp} [AddCommGroup Vcp] [Module Kcp Vcp]

set_option linter.style.haveILetI false in
/-- In characteristic `p`, the group-algebra element `[g]-1` is nilpotent for
`g` in the prime cyclic quotient `C_p`. -/
theorem cp_groupAlgebra_sub_one_nilpotent (g : Cp p) :
    IsNilpotent ((MonoidAlgebra.single g (1 : Kcp)) - 1 : Kcp[Cp p]) := by
  letI : CharP Kcp[Cp p] p := charP_of_injective_algebraMap' Kcp p
  refine ⟨p, ?_⟩
  rw [sub_pow_char]
  have hgp : g ^ p = 1 := cp_pow_prime_eq_one p g
  simp [MonoidAlgebra.single_pow, hgp]
  rw [← MonoidAlgebra.one_def]
  exact sub_self 1

set_option linter.style.haveILetI false in
/-- Full quotient-prime semisimple collapse: every semisimple representation of
`C_p` over a field of characteristic `p` is trivial. -/
theorem semisimple_cp_trivial
    (ρ : Representation Kcp (Cp p) Vcp) [Representation.IsSemisimpleRepresentation ρ] :
    ∀ g : Cp p, ρ g = LinearMap.id := by
  letI : IsSemisimpleModule Kcp[Cp p] ρ.asModule :=
    (Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule ρ).mp inferInstance
  intro g
  apply LinearMap.ext
  intro v
  let u : Kcp[Cp p] := MonoidAlgebra.single g (1 : Kcp) - 1
  have hnil : IsNilpotent u := cp_groupAlgebra_sub_one_nilpotent p g
  have hnilrad : u ∈ nilradical Kcp[Cp p] := (mem_nilradical).2 hnil
  have hjac : u ∈ Ring.jacobson Kcp[Cp p] := (nilradical_le_jacobson Kcp[Cp p]) hnilrad
  have hann : u ∈ Module.annihilator Kcp[Cp p] ρ.asModule :=
    IsSemisimpleModule.jacobson_le_annihilator Kcp[Cp p] ρ.asModule hjac
  have huv : u • (ρ.asModuleEquiv.symm v) = 0 := (Module.mem_annihilator.mp hann) _
  change ρ g v = v
  have hsub : ρ g v - v = 0 := by
    simpa [u, Representation.single_smul] using congrArg ρ.asModuleEquiv huv
  exact sub_eq_zero.mp hsub

/-- Any two semisimple `C_p` representations on the same module coincide in
characteristic `p`. -/
theorem semisimple_cp_unique_on_module
    (ρ σ : Representation Kcp (Cp p) Vcp)
    [Representation.IsSemisimpleRepresentation ρ]
    [Representation.IsSemisimpleRepresentation σ] :
    ρ = σ := by
  apply MonoidHom.ext
  intro g
  rw [semisimple_cp_trivial p ρ g, semisimple_cp_trivial p σ g]

end SemisimpleCharacteristicP

section SemisimpleComparison

universe uWcp
variable (p : ℕ) [Fact p.Prime]
variable {Kcp : Type uKcp} [Field Kcp] [CharP Kcp p]
variable {Vcp : Type uVcp} [AddCommGroup Vcp] [Module Kcp Vcp] [FiniteDimensional Kcp Vcp]
variable {Wcp : Type uWcp} [AddCommGroup Wcp] [Module Kcp Wcp] [FiniteDimensional Kcp Wcp]

/-- Same-dimension form of quotient-prime residual collapse: any two semisimple
`C_p` representations of the same dimension are linearly isomorphic, and every
linear equivalence intertwines after the actions have collapsed to the identity. -/
theorem semisimple_cp_equiv_of_finrank_eq
    (ρ : Representation Kcp (Cp p) Vcp)
    (σ : Representation Kcp (Cp p) Wcp)
    [Representation.IsSemisimpleRepresentation ρ]
    [Representation.IsSemisimpleRepresentation σ]
    (hdim : Module.finrank Kcp Vcp = Module.finrank Kcp Wcp) :
    ∃ e : Vcp ≃ₗ[Kcp] Wcp, ∀ g v, e (ρ g v) = σ g (e v) := by
  let e : Vcp ≃ₗ[Kcp] Wcp := LinearEquiv.ofFinrankEq Vcp Wcp hdim
  refine ⟨e, ?_⟩
  intro g v
  rw [semisimple_cp_trivial p ρ g, semisimple_cp_trivial p σ g]
  simp

end SemisimpleComparison

end Komorebi.StrongArtin.CyclicSimple

#print axioms Komorebi.StrongArtin.Separating.finite_alphabet_separating_primes
#print axioms Komorebi.StrongArtin.CyclicSimple.irreducible_cp_trivial
#print axioms Komorebi.StrongArtin.CyclicSimple.semisimple_cp_trivial
#print axioms Komorebi.StrongArtin.CyclicSimple.semisimple_cp_unique_on_module
#print axioms Komorebi.StrongArtin.CyclicSimple.semisimple_cp_equiv_of_finrank_eq

namespace Komorebi.StrongArtin.CliffordAssembly

universe uK uG uH uI uV uW uT uVs uWs

section Generic

variable {K : Type uK} [CommSemiring K]
variable {G : Type uG} [Monoid G]
variable {I : Type uI}
variable {V : I → Type uV} {W : I → Type uW}
variable [∀ i, AddCommMonoid (V i)] [∀ i, Module K (V i)]
variable [∀ i, AddCommMonoid (W i)] [∀ i, Module K (W i)]

/-- Componentwise representation equivalences assemble to an equivalence of
the full direct-sum representations. -/
noncomputable def directSumEquiv
    (ρ : ∀ i, Representation K G (V i))
    (σ : ∀ i, Representation K G (W i))
    (e : ∀ i, (ρ i).Equiv (σ i)) :
    (Representation.directSum ρ).Equiv (Representation.directSum σ) :=
  Representation.Equiv.mk (DirectSum.congrLinearEquiv (fun i => (e i).toLinearEquiv)) (by
    classical
    intro g
    apply DirectSum.linearMap_ext
    intro i
    apply LinearMap.ext
    intro v
    simp only [LinearMap.comp_apply, Representation.directSum_apply,
      DirectSum.congrLinearEquiv_toLinearMap, DirectSum.lmap_lof]
    exact congrArg (fun w => DirectSum.lof K I W i w)
      (Representation.IntertwiningMap.isIntertwining (ρ i) (σ i) (e i).toIntertwiningMap g v))

/-- If every component equivalence merely exists, classical choice plus
`directSumEquiv` assembles the total equivalence. -/
noncomputable def directSumEquivOfNonempty
    (ρ : ∀ i, Representation K G (V i))
    (σ : ∀ i, Representation K G (W i))
    (h : ∀ i, Nonempty ((ρ i).Equiv (σ i))) :
    (Representation.directSum ρ).Equiv (Representation.directSum σ) := by
  classical
  exact directSumEquiv ρ σ (fun i => Classical.choice (h i))

end Generic

section Functoriality

variable {K : Type uK} [CommSemiring K]
variable {G : Type uG} [Monoid G]
variable {H : Type uH} [Monoid H]
variable {T : Type uT} [AddCommMonoid T] [Module K T]
variable {M : Type uV} [AddCommMonoid M] [Module K M]
variable {N : Type uW} [AddCommMonoid N] [Module K N]

/-- Representation equivalences pull back along a monoid homomorphism. -/
noncomputable def compEquiv
    {ρ : Representation K H M} {σ : Representation K H N}
    (e : ρ.Equiv σ) (q : G →* H) :
    (show Representation K G M from ρ.comp q).Equiv
      (show Representation K G N from σ.comp q) :=
  Representation.Equiv.mk e.toLinearEquiv (by
    intro g
    exact e.toIntertwiningMap.isIntertwining' (q g))

/-- Tensoring a representation equivalence on the right with a fixed left
representation preserves equivalence. -/
noncomputable def lTensorEquiv
    (τ : Representation K G T)
    {ρ : Representation K G M} {σ : Representation K G N}
    (e : ρ.Equiv σ) :
    (τ.tprod ρ).Equiv (τ.tprod σ) :=
  Representation.Equiv.mk (e.toLinearEquiv.lTensor T) (by
    intro g
    exact (e.toIntertwiningMap.lTensor τ).isIntertwining' g)

end Functoriality

section StableBlock

variable (p : ℕ) [Fact p.Prime]
variable {Kp : Type uK} [Field Kp] [CharP Kp p]
variable {Gp : Type uG} [Group Gp]
variable {Tp : Type uT} [AddCommGroup Tp] [Module Kp Tp]
variable {Vs : Type uVs} [AddCommGroup Vs] [Module Kp Vs] [FiniteDimensional Kp Vs]
variable {Ws : Type uWs} [AddCommGroup Ws] [Module Kp Ws] [FiniteDimensional Kp Ws]

/-- Same-dimension semisimple quotient multiplicity spaces have an actual
representation equivalence of `C_p`. -/
theorem cpSemisimpleEquiv_nonempty
    (ρ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Vs)
    (σ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Ws)
    [Representation.IsSemisimpleRepresentation ρ]
    [Representation.IsSemisimpleRepresentation σ]
    (hdim : Module.finrank Kp Vs = Module.finrank Kp Ws) :
    Nonempty (ρ.Equiv σ) := by
  obtain ⟨e, he⟩ :=
    Komorebi.StrongArtin.CyclicSimple.semisimple_cp_equiv_of_finrank_eq p ρ σ hdim
  refine ⟨Representation.Equiv.mk e ?_⟩
  intro g
  apply LinearMap.ext
  intro v
  exact he g v

/-- Chosen form of `cpSemisimpleEquiv_nonempty`. -/
noncomputable def cpSemisimpleEquiv
    (ρ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Vs)
    (σ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Ws)
    [Representation.IsSemisimpleRepresentation ρ]
    [Representation.IsSemisimpleRepresentation σ]
    (hdim : Module.finrank Kp Vs = Module.finrank Kp Ws) :
    ρ.Equiv σ :=
  Classical.choice (cpSemisimpleEquiv_nonempty p ρ σ hdim)

/-- Stable Clifford block assembly: after quotient-prime semisimple collapse of
multiplicity spaces, tensoring with the common stable type gives equivalent
ambient `G`-blocks. -/
noncomputable def stableBlockEquiv
    (q : Gp →* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (τ : Representation Kp Gp Tp)
    (ρ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Vs)
    (σ : Representation Kp (Komorebi.StrongArtin.CyclicSimple.Cp p) Ws)
    [Representation.IsSemisimpleRepresentation ρ]
    [Representation.IsSemisimpleRepresentation σ]
    (hdim : Module.finrank Kp Vs = Module.finrank Kp Ws) :
    (τ.tprod (show Representation Kp Gp Vs from ρ.comp q)).Equiv
      (τ.tprod (show Representation Kp Gp Ws from σ.comp q)) :=
  lTensorEquiv τ (compEquiv (cpSemisimpleEquiv p ρ σ hdim) q)

end StableBlock

end Komorebi.StrongArtin.CliffordAssembly

namespace Komorebi.StrongArtin.CliffordAssembly

section StableMovingAssembly

universe uS uMidx uK4 uG4 uB

variable (p : ℕ) [Fact p.Prime]
variable {K : Type uK4} [Field K] [CharP K p]
variable {G : Type uG4} [Group G]
variable {S : Type uS} {J : Type uMidx}

variable {T : S → Type uB}
variable [∀ s, AddCommGroup (T s)] [∀ s, Module K (T s)]
variable {Vs : S → Type uB} {Ws : S → Type uB}
variable [∀ s, AddCommGroup (Vs s)] [∀ s, Module K (Vs s)]
variable [∀ s, FiniteDimensional K (Vs s)]
variable [∀ s, AddCommGroup (Ws s)] [∀ s, Module K (Ws s)]
variable [∀ s, FiniteDimensional K (Ws s)]

variable {MV : J → Type uB} {MW : J → Type uB}
variable [∀ j, AddCommMonoid (MV j)] [∀ j, Module K (MV j)]
variable [∀ j, AddCommMonoid (MW j)] [∀ j, Module K (MW j)]

/-- Underlying space family for a mixed stable/moving Clifford block
resolution. -/
abbrev blockSpace
    (K : Type uK4) [Field K]
    (T : S → Type uB) (MulSpace : S → Type uB) (MoveSpace : J → Type uB)
    [∀ s, AddCommGroup (T s)] [∀ s, Module K (T s)]
    [∀ s, AddCommGroup (MulSpace s)] [∀ s, Module K (MulSpace s)] :
    Sum S J → Type uB :=
  Sum.rec (fun s => TensorProduct K (T s) (MulSpace s)) (fun j => MoveSpace j)

instance blockSpaceAddCommMonoid
    (K : Type uK4) [Field K]
    (T : S → Type uB) (MulSpace : S → Type uB) (MoveSpace : J → Type uB)
    [∀ s, AddCommGroup (T s)] [∀ s, Module K (T s)]
    [∀ s, AddCommGroup (MulSpace s)] [∀ s, Module K (MulSpace s)]
    [∀ j, AddCommMonoid (MoveSpace j)]
    (i : Sum S J) : AddCommMonoid (blockSpace K T MulSpace MoveSpace i) := by
  cases i <;> infer_instance

instance blockSpaceModule
    (K : Type uK4) [Field K]
    (T : S → Type uB) (MulSpace : S → Type uB) (MoveSpace : J → Type uB)
    [∀ s, AddCommGroup (T s)] [∀ s, Module K (T s)]
    [∀ s, AddCommGroup (MulSpace s)] [∀ s, Module K (MulSpace s)]
    [∀ j, AddCommMonoid (MoveSpace j)] [∀ j, Module K (MoveSpace j)]
    (i : Sum S J) : Module K (blockSpace K T MulSpace MoveSpace i) := by
  cases i <;> infer_instance

/-- Representation family associated to a stable/moving Clifford block
resolution. -/
noncomputable def blockRepresentation
    (q : G →* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (τ : ∀ s, Representation K G (T s))
    {MulSpace : S → Type uB}
    [∀ s, AddCommGroup (MulSpace s)] [∀ s, Module K (MulSpace s)]
    (μ : ∀ s, Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) (MulSpace s))
    {MoveSpace : J → Type uB}
    [∀ j, AddCommMonoid (MoveSpace j)] [∀ j, Module K (MoveSpace j)]
    (move : ∀ j, Representation K G (MoveSpace j)) :
    (i : Sum S J) → Representation K G (blockSpace K T MulSpace MoveSpace i)
  | .inl s => (τ s).tprod
      (show Representation K G (MulSpace s) from (μ s).comp q)
  | .inr j => move j

/-- Abstract Clifford residual assembly interface.  Stable blocks have a common
`G`-type tensored with semisimple quotient multiplicity spaces; moving blocks
are supplied with their already-established equivalences.  Equal stable
multiplicity dimensions plus characteristic-`p` `C_p` collapse then imply an
equivalence of the complete block direct sums. -/
noncomputable def residualBlockAssemblyEquiv
    (q : G →* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (τ : ∀ s, Representation K G (T s))
    (μV : ∀ s, Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) (Vs s))
    (μW : ∀ s, Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) (Ws s))
    [∀ s, Representation.IsSemisimpleRepresentation (μV s)]
    [∀ s, Representation.IsSemisimpleRepresentation (μW s)]
    (hdim : ∀ s, Module.finrank K (Vs s) = Module.finrank K (Ws s))
    (moveV : ∀ j, Representation K G (MV j))
    (moveW : ∀ j, Representation K G (MW j))
    (hmove : ∀ j, Nonempty ((moveV j).Equiv (moveW j))) :
    (Representation.directSum (blockRepresentation p q τ μV moveV)).Equiv
      (Representation.directSum (blockRepresentation p q τ μW moveW)) := by
  apply directSumEquivOfNonempty
    (blockRepresentation p q τ μV moveV)
    (blockRepresentation p q τ μW moveW)
  intro i
  cases i with
  | inl s =>
      exact ⟨stableBlockEquiv p q (τ s) (μV s) (μW s) (hdim s)⟩
  | inr j =>
      exact hmove j

end StableMovingAssembly

end Komorebi.StrongArtin.CliffordAssembly

namespace Komorebi.StrongArtin.InducedTwist

open scoped MonoidAlgebra

universe uKi uHi uGi uAi
variable {k : Type uKi} [CommRing k]
variable {H : Type uHi} [Group H]
variable {G : Type uGi} [Group G]
variable {A : Type uAi} [AddCommGroup A] [Module k A]

/-- Scalar character twist of a representation, on the same underlying module. -/
noncomputable def scalarTwist (χ : G →* kˣ) (ρ : Representation k G A) :
    Representation k G A where
  toFun g := (χ g : k) • ρ g
  map_one' := by ext; simp
  map_mul' g h := by
    ext a
    simp only [map_mul, LinearMap.smul_apply, Module.End.mul_apply, map_smul]
    rw [Units.val_mul]
    calc
      ((χ g : k) * (χ h : k)) • (ρ g) ((ρ h) a) =
          ((χ h : k) * (χ g : k)) • (ρ g) ((ρ h) a) := by rw [mul_comm]
      _ = (χ h : k) • (χ g : k) • (ρ g) ((ρ h) a) := (smul_smul _ _ _).symm

@[simp] theorem scalarTwist_apply (χ : G →* kˣ) (ρ : Representation k G A)
    (g : G) (a : A) :
    scalarTwist χ ρ g a = (χ g : k) • ρ g a := rfl

end Komorebi.StrongArtin.InducedTwist


namespace Komorebi.StrongArtin.InducedTwist

open CategoryTheory

universe uK2 uH2 uG2 uA2
variable {k : Type uK2} [CommRing k]
variable {H : Type uH2} [Group H]
variable {G : Type uG2} [Group G]
variable {A : Type uA2} [AddCommGroup A] [Module k A]

/-- Diagonal rescaling on the coinduced function space. -/
noncomputable def coindScaleEquiv
    (φ : H →* G) (ρ : Representation k H A)
    (χ : G →* kˣ) (hχ : ∀ h : H, χ (φ h) = 1) :
    Representation.coindV φ ρ ≃ₗ[k] Representation.coindV φ ρ where
  toFun f := ⟨fun g => (↑((χ g)⁻¹) : k) • f.1 g, by
    intro h g
    change (↑((χ (φ h * g))⁻¹) : k) • f.1 (φ h * g) =
      ρ h ((↑((χ g)⁻¹) : k) • f.1 g)
    rw [f.2 h g, map_smul, map_mul, hχ h]
    simp
    ⟩
  invFun f := ⟨fun g => (χ g : k) • f.1 g, by
    intro h g
    change (χ (φ h * g) : k) • f.1 (φ h * g) =
      ρ h ((χ g : k) • f.1 g)
    rw [f.2 h g, map_smul, map_mul, hχ h]
    simp
    ⟩
  left_inv f := by
    apply Subtype.ext
    funext g
    dsimp
    rw [smul_smul]
    simp
  right_inv f := by
    apply Subtype.ext
    funext g
    dsimp
    rw [smul_smul]
    simp
  map_add' f g := by
    apply Subtype.ext
    funext x
    exact smul_add _ _ _
  map_smul' c f := by
    apply Subtype.ext
    funext x
    change (↑((χ x)⁻¹) : k) • (c • f.1 x) = c • ((↑((χ x)⁻¹) : k) • f.1 x)
    exact smul_comm _ _ _

/-- Twist invariance of coinduction when the character is trivial on the source. -/
noncomputable def coindTwistEquiv
    (φ : H →* G) (ρ : Representation k H A)
    (χ : G →* kˣ) (hχ : ∀ h : H, χ (φ h) = 1) :
    (Representation.coind φ ρ).Equiv (scalarTwist χ (Representation.coind φ ρ)) :=
  Representation.Equiv.mk (coindScaleEquiv φ ρ χ hχ) (by
    intro g
    apply LinearMap.ext
    intro f
    apply Subtype.ext
    funext x
    dsimp only [LinearMap.comp_apply, coindScaleEquiv, scalarTwist, Representation.coind,
      LinearMap.funLeft, LinearMap.restrict, Function.comp_apply]
    change (↑((χ x)⁻¹) : k) • f.1 (x * g) =
      (χ g : k) • ((↑((χ (x * g))⁻¹) : k) • f.1 (x * g))
    rw [map_mul]
    simp [smul_smul, mul_comm]
  )

/-- Twisting preserves representation equivalences. -/
noncomputable def scalarTwistEquiv
    {V W : Type*} [AddCommGroup V] [Module k V]
    [AddCommGroup W] [Module k W]
    (χ : G →* kˣ)
    {ρ : Representation k G V} {σ : Representation k G W}
    (e : ρ.Equiv σ) :
    (scalarTwist χ ρ).Equiv (scalarTwist χ σ) :=
  Representation.Equiv.mk e.toLinearEquiv (by
    intro g
    apply LinearMap.ext
    intro v
    change e.toLinearEquiv ((χ g : k) • ρ g v) =
      (χ g : k) • σ g (e.toLinearEquiv v)
    rw [map_smul]
    exact congrArg (fun w => (χ g : k) • w)
      (LinearMap.ext_iff.mp (e.toIntertwiningMap.isIntertwining' g) v)
  )

section FiniteIndexSubgroup

universe u
variable {k0 G0 A0 : Type u} [CommRing k0] [Group G0]
variable [AddCommGroup A0] [Module k0 A0]
variable (S : Subgroup G0) [S.FiniteIndex]
variable [DecidableRel (QuotientGroup.rightRel S)]
variable (ρ : Representation k0 S A0)

/-- Finite-index induced blocks are invariant under twisting by a character
trivial on the inducing subgroup. -/
noncomputable def inducedTwistEquiv
    (χ : G0 →* k0ˣ) (hχ : ∀ h : S, χ h.1 = 1) :
    (Representation.ind S.subtype ρ).Equiv
      (scalarTwist χ (Representation.ind S.subtype ρ)) := by
  let eIC : (Representation.ind S.subtype ρ).Equiv
      (Representation.coind S.subtype ρ) :=
    Representation.equivOfIso (Rep.indCoindIso (k := k0) (S := S) (Rep.of ρ))
  let eC : (Representation.coind S.subtype ρ).Equiv
      (scalarTwist χ (Representation.coind S.subtype ρ)) :=
    coindTwistEquiv S.subtype ρ χ hχ
  let eTI : (scalarTwist χ (Representation.coind S.subtype ρ)).Equiv
      (scalarTwist χ (Representation.ind S.subtype ρ)) :=
    scalarTwistEquiv χ eIC.symm
  exact eIC.trans (eC.trans eTI)

/-- Proposition-level form: a finite-index induced block is unchanged up to
representation equivalence by any scalar character trivial on the inducing subgroup. -/
theorem induced_twist_invariant
    (χ : G0 →* k0ˣ) (hχ : ∀ h : S, χ h.1 = 1) :
    Nonempty ((Representation.ind S.subtype ρ).Equiv
      (scalarTwist χ (Representation.ind S.subtype ρ))) :=
  ⟨inducedTwistEquiv S ρ χ hχ⟩

end FiniteIndexSubgroup

end Komorebi.StrongArtin.InducedTwist

#print axioms Komorebi.StrongArtin.InducedTwist.coindTwistEquiv
#print axioms Komorebi.StrongArtin.InducedTwist.inducedTwistEquiv
#print axioms Komorebi.StrongArtin.InducedTwist.induced_twist_invariant


namespace Komorebi.StrongArtin.CliffordOrbit

universe uX

set_option linter.style.haveILetI false in
/-- Every orbit under the prime cyclic quotient `C_p` has cardinality exactly
`1` or `p`.  This is the finite group-action core of the stable/moving
Clifford dichotomy. -/
theorem orbit_card_one_or_p
    (p : ℕ) [Fact p.Prime]
    {X : Type uX} [MulAction (Komorebi.StrongArtin.CyclicSimple.Cp p) X]
    (x : X)
    [Fintype (MulAction.orbit (Komorebi.StrongArtin.CyclicSimple.Cp p) x)] :
    Fintype.card (MulAction.orbit (Komorebi.StrongArtin.CyclicSimple.Cp p) x) = 1 ∨
      Fintype.card (MulAction.orbit (Komorebi.StrongArtin.CyclicSimple.Cp p) x) = p := by
  letI : NeZero p := ⟨(Fact.out : p.Prime).ne_zero⟩
  letI : Fintype (Komorebi.StrongArtin.CyclicSimple.Cp p) :=
    Fintype.ofEquiv (ZMod p) Multiplicative.ofAdd
  letI : Fintype (MulAction.stabilizer (Komorebi.StrongArtin.CyclicSimple.Cp p) x) :=
    Fintype.ofFinite _
  have hmul :=
    MulAction.card_orbit_mul_card_stabilizer_eq_card_group
      (Komorebi.StrongArtin.CyclicSimple.Cp p) x
  have hcardG : Fintype.card (Komorebi.StrongArtin.CyclicSimple.Cp p) = p := by
    calc
      Fintype.card (Komorebi.StrongArtin.CyclicSimple.Cp p) = Fintype.card (ZMod p) :=
        Fintype.card_congr Multiplicative.toAdd
      _ = p := ZMod.card p
  rw [hcardG] at hmul
  have hdvd : Fintype.card (MulAction.orbit (Komorebi.StrongArtin.CyclicSimple.Cp p) x) ∣ p := by
    exact ⟨Fintype.card (MulAction.stabilizer (Komorebi.StrongArtin.CyclicSimple.Cp p) x),
      hmul.symm⟩
  exact (Fact.out : p.Prime).eq_one_or_self_of_dvd _ hdvd

end Komorebi.StrongArtin.CliffordOrbit

namespace Komorebi.StrongArtin.TraceSeparator

open Representation
open scoped MonoidAlgebra

universe uKts uGts uHts uVts
variable {K : Type uKts} [Field K]
variable {G : Type uGts} [Group G]
variable {H : Type uHts} [Group H]
variable {V : Type uVts} [AddCommGroup V] [Module K V]

/-- Scalar twisting preserves the lattice of invariant subspaces. -/
noncomputable def twistSubrepresentationOrderIso
    (χ : G →* Kˣ) (ρ : Representation K G V) :
    Subrepresentation ρ ≃o
      Subrepresentation (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ) where
  toFun S :=
    { toSubmodule := S.toSubmodule
      apply_mem_toSubmodule := by
        intro g v hv
        exact S.toSubmodule.smul_mem (χ g : K) (S.apply_mem_toSubmodule g hv) }
  invFun T :=
    { toSubmodule := T.toSubmodule
      apply_mem_toSubmodule := by
        intro g v hv
        have ht := T.apply_mem_toSubmodule g hv
        have hs := T.toSubmodule.smul_mem ((χ g)⁻¹ : K) ht
        simpa [Komorebi.StrongArtin.InducedTwist.scalarTwist, smul_smul] using hs }
  left_inv S := by ext v; rfl
  right_inv T := by ext v; rfl
  map_rel_iff' := by intro S T; rfl

/-- Twisting by a scalar character preserves irreducibility. -/
theorem scalarTwist_irreducible_iff
    (χ : G →* Kˣ) (ρ : Representation K G V) :
    Representation.IsIrreducible
        (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ) ↔
      Representation.IsIrreducible ρ := by
  exact (twistSubrepresentationOrderIso χ ρ).isSimpleOrder_iff.symm

section FiniteDimensional

variable [FiniteDimensional K V]

omit [FiniteDimensional K V] in
/-- Character of a scalar twist. -/
@[simp] theorem scalarTwist_character
    (χ : G →* Kˣ) (ρ : Representation K G V) (g : G) :
    (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ).character g =
      (χ g : K) * ρ.character g := by
  simp [Representation.character, Komorebi.StrongArtin.InducedTwist.scalarTwist]

variable [IsAlgClosed K]

set_option linter.style.haveILetI false in
/-- A nontrivial quotient character cannot fix an extension whose restriction
is irreducible.  This is the Schur-lemma obstruction underlying the trace
separator. -/
theorem no_self_twist_of_irreducible_restriction
    (ι : H →* G)
    (ρ : Representation K G V)
    (χ : G →* Kˣ)
    (hχH : ∀ h : H, χ (ι h) = 1)
    (g0 : G) (hχ0 : χ g0 ≠ 1)
    [Representation.IsIrreducible (ρ.comp ι)] :
    IsEmpty (ρ.Equiv
      (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ)) := by
  refine ⟨fun e => ?_⟩
  let fH : Representation.IntertwiningMap (ρ.comp ι) (ρ.comp ι) :=
    ⟨e.toLinearEquiv.toLinearMap, by
      intro h
      apply LinearMap.ext
      intro v
      have he := e.toIntertwiningMap.isIntertwining' (ι h)
      have hv := LinearMap.congr_fun he v
      simpa [Komorebi.StrongArtin.InducedTwist.scalarTwist, hχH h] using hv⟩
  have hbij :=
    Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
      (ρ := ρ.comp ι)
  obtain ⟨c, hc⟩ := hbij.2 fH
  have hf_scalar : fH.toLinearMap = c • LinearMap.id := by
    apply LinearMap.ext
    intro v
    have hv := LinearMap.congr_fun
      (congrArg Representation.IntertwiningMap.toLinearMap hc) v
    simpa using hv.symm
  letI : Nontrivial V := by
    exact IsSimpleModule.nontrivial K[H]
      (show Representation K H V from ρ.comp ι).asModule
  have hc_ne : c ≠ 0 := by
    intro hc0
    have hz : fH.toLinearMap = 0 := by simpa [hc0] using hf_scalar
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hev0 : e.toLinearEquiv v = 0 := by
      change fH.toLinearMap v = 0
      rw [hz]
      rfl
    have : v = 0 := e.toLinearEquiv.injective (by simpa using hev0)
    exact hv this
  have he0 := e.toIntertwiningMap.isIntertwining' g0
  have hev : ∀ v, e.toLinearEquiv (ρ g0 v) =
      (χ g0 : K) • ρ g0 (e.toLinearEquiv v) := by
    intro v
    simpa [Komorebi.StrongArtin.InducedTwist.scalarTwist] using
      LinearMap.congr_fun he0 v
  have hscalar_point : ∀ v, e.toLinearEquiv v = c • v := by
    intro v
    change fH.toLinearMap v = c • v
    rw [hf_scalar]
    simp
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  have hρv : ρ g0 v ≠ 0 := by
    intro hz
    have hh := congrArg (fun w => ρ g0⁻¹ w) hz
    exact hv (by simpa using hh)
  have hEq : c • ρ g0 v = ((χ g0 : K) * c) • ρ g0 v := by
    calc
      c • ρ g0 v = e.toLinearEquiv (ρ g0 v) :=
        (hscalar_point (ρ g0 v)).symm
      _ = (χ g0 : K) • ρ g0 (e.toLinearEquiv v) := hev v
      _ = (χ g0 : K) • ρ g0 (c • v) := by rw [hscalar_point v]
      _ = (χ g0 : K) • (c • ρ g0 v) := by rw [map_smul]
      _ = ((χ g0 : K) * c) • ρ g0 v := by rw [smul_smul]
  have hs : c = (χ g0 : K) * c :=
    (smul_left_injective K hρv) hEq
  have hχval : (χ g0 : K) = 1 := by
    apply mul_right_cancel₀ hc_ne
    simpa using hs.symm
  exact hχ0 (Units.ext hχval)

end FiniteDimensional

section CharacterSeparator

variable [FiniteDimensional K V] [IsAlgClosed K] [CharZero K]
variable [Fintype G]

set_option linter.style.haveILetI false in
/-- Galois trace separator, finite-group form.  If an irreducible extension has
irreducible restriction and admits a nontrivial quotient character trivial on
`H`, then some element outside `H` has nonzero trace. -/
theorem trace_separator
    (ι : H →* G)
    (ρ : Representation K G V)
    (χ : G →* Kˣ)
    (hχH : ∀ h : H, χ (ι h) = 1)
    (g0 : G) (hχ0 : χ g0 ≠ 1)
    [Representation.IsIrreducible ρ]
    [Representation.IsIrreducible (ρ.comp ι)] :
    ∃ g : G, g ∉ Set.range ι ∧ ρ.character g ≠ 0 := by
  haveI : Representation.IsIrreducible
      (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ) :=
    (scalarTwist_irreducible_iff χ ρ).2 inferInstance
  letI : Invertible (Nat.card G : K) := invertibleOfNonzero <|
    Nat.cast_ne_zero.mpr ((Nat.card_ne_zero).mpr ⟨inferInstance, inferInstance⟩)
  have hno : IsEmpty (ρ.Equiv
      (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ)) :=
    no_self_twist_of_irreducible_restriction ι ρ χ hχH g0 hχ0
  letI : IsEmpty
      ((Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ).Equiv ρ) :=
    ⟨fun e => hno.false e.symm⟩
  by_contra hsep
  push Not at hsep
  have hchar :
      (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ).character =
        ρ.character := by
    funext g
    by_cases hgH : g ∈ Set.range ι
    · rcases hgH with ⟨h, rfl⟩
      simp [scalarTwist_character, hχH h]
    · have hz : ρ.character g = 0 := hsep g hgH
      simp [scalarTwist_character, hz]
  have hcross := Representation.char_orthonormal ρ
    (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ)
  have hself := Representation.char_orthonormal ρ ρ
  have hEqL :
      (Nat.card G : K)⁻¹ * ∑ g : G, ρ.character g *
        (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ).character g⁻¹ =
      (Nat.card G : K)⁻¹ * ∑ g : G, ρ.character g * ρ.character g⁻¹ := by
    simp_rw [hchar]
  rw [hcross, hself] at hEqL
  have hnot_tw : ¬ Nonempty
      ((Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ).Equiv ρ) :=
    not_nonempty_iff.mpr inferInstance
  have hyes_self : Nonempty (ρ.Equiv ρ) := ⟨Representation.Equiv.refl ρ⟩
  simp [hnot_tw, hyes_self] at hEqL

end CharacterSeparator

end Komorebi.StrongArtin.TraceSeparator

#print axioms Komorebi.StrongArtin.CliffordOrbit.orbit_card_one_or_p
#print axioms Komorebi.StrongArtin.TraceSeparator.no_self_twist_of_irreducible_restriction
#print axioms Komorebi.StrongArtin.TraceSeparator.trace_separator


namespace Komorebi.StrongArtin.ExtensionTorsor

open Representation
open scoped MonoidAlgebra

universe uKet uGet uVet uWet
variable {K : Type uKet} [Field K] [IsAlgClosed K]
variable {G : Type uGet} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uVet} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

set_option linter.style.haveILetI false in
/-- Pointwise Schur normalization: two extensions which agree on the normal
subgroup differ at each `g` by one unique scalar. -/
theorem existsUnique_scalar_ratio
    (ρ σ : Representation K G V)
    (hres : ∀ h : S, ρ h.1 = σ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)]
    (g : G) :
    ∃! c : K, σ g = c • ρ g := by
  let D : V →ₗ[K] V := (σ g).comp (ρ g⁻¹)
  let DH : Representation.IntertwiningMap (ρ.comp S.subtype) (ρ.comp S.subtype) :=
    LinearMap.intertwiningMap_of_isIntertwiningMap
      (ρ.comp S.subtype) (ρ.comp S.subtype) D (by
        intro h v
        let hc : S := ⟨g⁻¹ * h.1 * g,
          Subgroup.Normal.conj_mem' inferInstance h.1 h.2 g⟩
        change σ g (ρ g⁻¹ (ρ h.1 v)) = ρ h.1 (σ g (ρ g⁻¹ v))
        calc
          σ g (ρ g⁻¹ (ρ h.1 v)) =
              σ g (ρ (g⁻¹ * h.1 * g) (ρ g⁻¹ v)) := by
                simp [map_mul, mul_assoc]
          _ = σ g (σ (g⁻¹ * h.1 * g) (ρ g⁻¹ v)) := by
                rw [← hres hc]
          _ = σ h.1 (σ g (ρ g⁻¹ v)) := by
                simp [map_mul, mul_assoc]
          _ = ρ h.1 (σ g (ρ g⁻¹ v)) := by rw [hres h])
  have hbij :=
    Representation.IsIrreducible.algebraMap_intertwiningMap_bijective_of_isAlgClosed
      (ρ := ρ.comp S.subtype)
  obtain ⟨c, hc⟩ := hbij.2 DH
  refine ⟨c, ?_, ?_⟩
  · apply LinearMap.ext
    intro v
    have hcv := LinearMap.congr_fun
      (congrArg Representation.IntertwiningMap.toLinearMap hc) (ρ g v)
    change σ g v = c • ρ g v
    have hD : DH.toLinearMap (ρ g v) = σ g v := by
      simp [DH, D]
    rw [← hD]
    simpa using hcv.symm
  · intro d hd
    letI : Nontrivial V := by
      exact IsSimpleModule.nontrivial K[S]
        (show Representation K S V from ρ.comp S.subtype).asModule
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hρv : ρ g v ≠ 0 := by
      intro hz
      have hh := congrArg (fun w => ρ g⁻¹ w) hz
      exact hv (by simpa using hh)
    have hcmap : σ g = c • ρ g := by
      apply LinearMap.ext
      intro w
      have hcw := LinearMap.congr_fun
        (congrArg Representation.IntertwiningMap.toLinearMap hc) (ρ g w)
      have hD : DH.toLinearMap (ρ g w) = σ g w := by simp [DH, D]
      change σ g w = c • ρ g w
      rw [← hD]
      simpa using hcw.symm
    have hcv := LinearMap.congr_fun hcmap v
    have hdv := LinearMap.congr_fun hd v
    exact (smul_left_injective K hρv) (hdv.symm.trans hcv)

set_option linter.style.haveILetI false in
/-- Same-space extension theorem: the scalar ratios form a character trivial on
`S`, and this character twists one extension to the other. -/
theorem exists_scalar_character
    (ρ σ : Representation K G V)
    (hres : ∀ h : S, ρ h.1 = σ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃ χ : G →* Kˣ,
      σ = Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ ∧
      ∀ h : S, χ h.1 = 1 := by
  let hcData := fun g : G => existsUnique_scalar_ratio S ρ σ hres g
  let c : G → K := fun g => Classical.choose (hcData g)
  have hc_eq : ∀ g : G, σ g = c g • ρ g := by
    intro g
    exact (Classical.choose_spec (hcData g)).1
  letI : Nontrivial V := by
    exact IsSimpleModule.nontrivial K[S]
      (show Representation K S V from ρ.comp S.subtype).asModule
  have hc_ne : ∀ g : G, c g ≠ 0 := by
    intro g hcg0
    obtain ⟨v, hv⟩ := exists_ne (0 : V)
    have hσv : σ g v ≠ 0 := by
      intro hz
      have hh := congrArg (fun w => σ g⁻¹ w) hz
      exact hv (by simpa using hh)
    have hg := LinearMap.congr_fun (hc_eq g) v
    rw [hcg0] at hg
    simp at hg
    exact hσv hg
  have hc_one : c 1 = 1 := by
    have hu := (Classical.choose_spec (hcData 1)).2 (1 : K) (by simp)
    exact hu.symm
  have hc_mul : ∀ g h : G, c (g * h) = c g * c h := by
    intro g h
    have hcand : σ (g * h) = (c g * c h) • ρ (g * h) := by
      rw [map_mul, hc_eq g, hc_eq h, map_mul]
      ext v
      simp [smul_smul, mul_comm]
    have hu := (Classical.choose_spec (hcData (g * h))).2 (c g * c h) hcand
    exact hu.symm
  let χ : G →* Kˣ :=
    { toFun := fun g => Units.mk0 (c g) (hc_ne g)
      map_one' := by exact Units.ext hc_one
      map_mul' := by
        intro g h
        exact Units.ext (hc_mul g h) }
  refine ⟨χ, ?_, ?_⟩
  · apply MonoidHom.ext
    intro g
    apply LinearMap.ext
    intro v
    change σ g v = (χ g : K) • ρ g v
    exact LinearMap.congr_fun (hc_eq g) v
  · intro h
    have hcandidate : σ h.1 = (1 : K) • ρ h.1 := by
      rw [← hres h]
      simp
    have hu := (Classical.choose_spec (hcData h.1)).2 (1 : K) hcandidate
    apply Units.ext
    exact hu.symm

/-- The character in `exists_scalar_character` factors through the quotient. -/
theorem exists_quotient_character
    (ρ σ : Representation K G V)
    (hres : ∀ h : S, ρ h.1 = σ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃ χbar : (G ⧸ S) →* Kˣ,
      σ = Komorebi.StrongArtin.InducedTwist.scalarTwist
        (χbar.comp (QuotientGroup.mk' S)) ρ := by
  obtain ⟨χ, hσ, hχS⟩ := exists_scalar_character S ρ σ hres
  have hker : S ≤ χ.ker := by
    intro g hg
    exact hχS ⟨g, hg⟩
  let χbar : (G ⧸ S) →* Kˣ := QuotientGroup.lift S χ hker
  refine ⟨χbar, ?_⟩
  rw [hσ]
  apply MonoidHom.ext
  intro g
  apply LinearMap.ext
  intro v
  simp [Komorebi.StrongArtin.InducedTwist.scalarTwist, χbar]

/-- Freeness of the quotient-character action in the same-space normalization. -/
theorem quotient_character_unique
    (ρ σ : Representation K G V)
    (hres : ∀ h : S, ρ h.1 = σ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)]
    {χ ψ : (G ⧸ S) →* Kˣ}
    (hχ : σ = Komorebi.StrongArtin.InducedTwist.scalarTwist
      (χ.comp (QuotientGroup.mk' S)) ρ)
    (hψ : σ = Komorebi.StrongArtin.InducedTwist.scalarTwist
      (ψ.comp (QuotientGroup.mk' S)) ρ) :
    χ = ψ := by
  apply MonoidHom.ext
  intro x
  obtain ⟨g, rfl⟩ := QuotientGroup.mk'_surjective S x
  apply Units.ext
  let q := QuotientGroup.mk' S
  have hχg : σ g = ((χ.comp q) g : K) • ρ g := by
    rw [hχ]
    rfl
  have hψg : σ g = ((ψ.comp q) g : K) • ρ g := by
    rw [hψ]
    rfl
  exact ExistsUnique.unique (existsUnique_scalar_ratio S ρ σ hres g) hχg hψg

/-- Literal quotient-character torsor statement after fixing one realization of
the common restriction. -/
theorem existsUnique_quotient_character
    (ρ σ : Representation K G V)
    (hres : ∀ h : S, ρ h.1 = σ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃! χ : (G ⧸ S) →* Kˣ,
      σ = Komorebi.StrongArtin.InducedTwist.scalarTwist
        (χ.comp (QuotientGroup.mk' S)) ρ := by
  obtain ⟨χ, hχ⟩ := exists_quotient_character S ρ σ hres
  exact ⟨χ, hχ, fun ψ hψ => quotient_character_unique S ρ σ hres hψ hχ⟩

universe uWet2
variable {W : Type uWet2} [AddCommGroup W] [Module K W]

/-- Transport a representation across a linear equivalence. -/
noncomputable def transportRep (e : V ≃ₗ[K] W) (σ : Representation K G W) :
    Representation K G V where
  toFun g := e.symm.toLinearMap.comp ((σ g).comp e.toLinearMap)
  map_one' := by
    apply LinearMap.ext
    intro v
    simp
  map_mul' g h := by
    apply LinearMap.ext
    intro v
    simp [map_mul]

/-- The transport equivalence back to the original representation. -/
noncomputable def transportEquiv (e : V ≃ₗ[K] W) (σ : Representation K G W) :
    (transportRep e σ).Equiv σ :=
  Representation.Equiv.mk e (by
    intro g
    apply LinearMap.ext
    intro v
    simp [transportRep])

omit [IsAlgClosed K] [FiniteDimensional K V] in
/-- An equivalence of restrictions makes them literally equal after transport. -/
theorem transportRep_restriction_eq
    {H : Type*} [Group H]
    (ι : H →* G)
    (ρ : Representation K G V) (σ : Representation K G W)
    (e : Representation.Equiv
      (show Representation K H V from ρ.comp ι)
      (show Representation K H W from σ.comp ι)) :
    ∀ h : H, ρ (ι h) = transportRep e.toLinearEquiv σ (ι h) := by
  intro h
  apply LinearMap.ext
  intro v
  have he := e.toIntertwiningMap.isIntertwining' h
  have hev := LinearMap.congr_fun he v
  change ρ (ι h) v = e.toLinearEquiv.symm (σ (ι h) (e.toLinearEquiv v))
  have hev' := hev
  change e.toLinearEquiv.toLinearMap (ρ (ι h) v) =
    σ (ι h) (e.toLinearEquiv.toLinearMap v) at hev'
  calc
    ρ (ι h) v = e.toLinearEquiv.symm (e.toLinearEquiv (ρ (ι h) v)) :=
      (e.toLinearEquiv.symm_apply_apply _).symm
    _ = e.toLinearEquiv.symm (σ (ι h) (e.toLinearEquiv v)) :=
      congrArg e.toLinearEquiv.symm hev'

/-- Full extension-torsor transitivity on possibly different realization
spaces: equivalent irreducible restrictions imply quotient-twist equivalence. -/
theorem extensions_differ_by_quotient_character
    (ρ : Representation K G V)
    (σ : Representation K G W)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃ χbar : (G ⧸ S) →* Kˣ,
      Nonempty ((Komorebi.StrongArtin.InducedTwist.scalarTwist
        (χbar.comp (QuotientGroup.mk' S)) ρ).Equiv σ) := by
  let σV : Representation K G V := transportRep eH.toLinearEquiv σ
  have hres : ∀ h : S, ρ h.1 = σV h.1 := by
    exact transportRep_restriction_eq S.subtype ρ σ eH
  obtain ⟨χbar, hχ⟩ := exists_quotient_character S ρ σV hres
  let eV : σV.Equiv σ := transportEquiv eH.toLinearEquiv σ
  rw [hχ] at eV
  exact ⟨χbar, ⟨eV⟩⟩

end Komorebi.StrongArtin.ExtensionTorsor

#print axioms Komorebi.StrongArtin.ExtensionTorsor.existsUnique_scalar_ratio
#print axioms Komorebi.StrongArtin.ExtensionTorsor.existsUnique_quotient_character
#print axioms Komorebi.StrongArtin.ExtensionTorsor.extensions_differ_by_quotient_character

namespace Komorebi.StrongArtin.DeterminantSelector

open Representation

universe uKdet uGdet uQdet uVdet
variable {K : Type uKdet} [Field K]
variable {G : Type uGdet} [Group G]
variable {Q : Type uQdet} [Group Q]
variable {V : Type uVdet} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

abbrev Cp (p : ℕ) := Komorebi.StrongArtin.CyclicSimple.Cp p

/-- Every element of the concrete prime cyclic group has exponent dividing `p`. -/
theorem cp_pow (p : ℕ) (q : Cp p) : q ^ p = 1 := by
  change Multiplicative.ofAdd (p • Multiplicative.toAdd q) = 1
  simp

/-- A group identified with `C_p` has exponent dividing `p`. -/
theorem exponent_of_equiv_cp (p : ℕ) (e : Q ≃* Cp p) (q : Q) : q ^ p = 1 := by
  apply e.injective
  simpa using cp_pow p (e q)

/-- On a group of prime exponent `p`, the `n`th-power map on multiplicative
characters is injective whenever `p ∤ n`. -/
theorem character_pow_injective_of_prime_exponent
    (p n : ℕ) (hp : p.Prime) (hpn : ¬ p ∣ n)
    (hexp : ∀ q : Q, q ^ p = 1) :
    Function.Injective (fun χ : Q →* Kˣ => χ ^ n) := by
  intro χ ψ hpow
  apply MonoidHom.ext
  intro q
  have hn : (χ q) ^ n = (ψ q) ^ n := by
    have h := congrArg (fun f : Q →* Kˣ => f q) hpow
    simpa using h
  let δ : Kˣ := χ q * (ψ q)⁻¹
  have hδn : δ ^ n = 1 := by
    dsimp [δ]
    rw [mul_pow, inv_pow, hn]
    simp
  have hχp : (χ q) ^ p = 1 := by
    rw [← map_pow, hexp q, map_one]
  have hψp : (ψ q) ^ p = 1 := by
    rw [← map_pow, hexp q, map_one]
  have hδp : δ ^ p = 1 := by
    dsimp [δ]
    rw [mul_pow, inv_pow, hχp, hψp]
    simp
  have hd_p : orderOf δ ∣ p := orderOf_dvd_of_pow_eq_one hδp
  have hd_n : orderOf δ ∣ n := orderOf_dvd_of_pow_eq_one hδn
  have hd1 : orderOf δ = 1 :=
    Nat.eq_one_of_dvd_coprimes ((hp.coprime_iff_not_dvd).2 hpn) hd_p hd_n
  have hδ1 : δ = 1 := orderOf_eq_one_iff.mp hd1
  dsimp [δ] at hδ1
  exact mul_inv_eq_one.mp hδ1

omit [FiniteDimensional K V] in
/-- Literal determinant transformation law under a scalar character twist. -/
theorem det_scalarTwist
    (χ : G →* Kˣ) (ρ : Representation K G V) (g : G) :
    LinearMap.det (Komorebi.StrongArtin.InducedTwist.scalarTwist χ ρ g) =
      (χ g : K) ^ Module.finrank K V * LinearMap.det (ρ g) := by
  simp [Komorebi.StrongArtin.InducedTwist.scalarTwist, LinearMap.det_smul]

omit [FiniteDimensional K V] in
/-- Representation matrices have nonzero determinant because the inverse group
element gives an inverse linear map. -/
theorem det_rep_ne_zero (ρ : Representation K G V) (g : G) :
    LinearMap.det (ρ g) ≠ 0 := by
  intro hz
  have hmul : LinearMap.det (ρ g) * LinearMap.det (ρ g⁻¹) = 1 := by
    rw [← LinearMap.det_comp, ← Module.End.mul_eq_comp]
    rw [← ρ.map_mul]
    simp
  rw [hz, zero_mul] at hmul
  exact zero_ne_one hmul

omit [FiniteDimensional K V] in
/-- Representation-level rank-prime selector.  If `Q ≃ C_p` and `p` does not
divide the rank, two quotient twists with the same determinant function use the
same quotient character. -/
theorem determinant_twists_injective
    (p : ℕ) (hp : p.Prime) (eQ : Q ≃* Cp p)
    (qmap : G →* Q) (hq : Function.Surjective qmap)
    (ρ : Representation K G V)
    (hpn : ¬ p ∣ Module.finrank K V) :
    Function.Injective (fun χ : Q →* Kˣ =>
      fun g : G => LinearMap.det
        (Komorebi.StrongArtin.InducedTwist.scalarTwist (χ.comp qmap) ρ g)) := by
  intro χ ψ hdet
  have hpow : χ ^ Module.finrank K V = ψ ^ Module.finrank K V := by
    apply MonoidHom.ext
    intro x
    obtain ⟨g, rfl⟩ := hq x
    have hd := congrFun hdet g
    change LinearMap.det
        (Komorebi.StrongArtin.InducedTwist.scalarTwist (χ.comp qmap) ρ g) =
      LinearMap.det
        (Komorebi.StrongArtin.InducedTwist.scalarTwist (ψ.comp qmap) ρ g) at hd
    rw [det_scalarTwist, det_scalarTwist] at hd
    have hbase : LinearMap.det (ρ g) ≠ 0 := det_rep_ne_zero ρ g
    have hpowsK : ((χ (qmap g) : K) ^ Module.finrank K V) =
        ((ψ (qmap g) : K) ^ Module.finrank K V) :=
      mul_right_cancel₀ hbase hd
    change χ (qmap g) ^ Module.finrank K V =
      ψ (qmap g) ^ Module.finrank K V
    exact Units.ext hpowsK
  exact character_pow_injective_of_prime_exponent
    p (Module.finrank K V) hp hpn (exponent_of_equiv_cp p eQ) hpow

section Torsor

variable [IsAlgClosed K]
variable (S : Subgroup G) [S.Normal]

/-- Actual determinant selector on an extension torsor.  For a prime cyclic
quotient and rank coprime to the quotient prime, two extensions of the same
irreducible restriction with identical determinant functions are equal in the
fixed-space normalization. -/
theorem determinant_distinguishes_extensions
    (p : ℕ) (hp : p.Prime) (eQ : (G ⧸ S) ≃* Cp p)
    (ρ σ τ : Representation K G V)
    (hσ : ∀ h : S, ρ h.1 = σ h.1)
    (hτ : ∀ h : S, ρ h.1 = τ h.1)
    [Representation.IsIrreducible (ρ.comp S.subtype)]
    (hpn : ¬ p ∣ Module.finrank K V)
    (hdet : ∀ g : G, LinearMap.det (σ g) = LinearMap.det (τ g)) :
    σ = τ := by
  obtain ⟨χ, hσχ⟩ :=
    Komorebi.StrongArtin.ExtensionTorsor.exists_quotient_character S ρ σ hσ
  obtain ⟨ψ, hτψ⟩ :=
    Komorebi.StrongArtin.ExtensionTorsor.exists_quotient_character S ρ τ hτ
  have hχψ : χ = ψ := by
    apply determinant_twists_injective p hp eQ
      (QuotientGroup.mk' S) (QuotientGroup.mk'_surjective S) ρ hpn
    funext g
    change LinearMap.det
        (Komorebi.StrongArtin.InducedTwist.scalarTwist
          (χ.comp (QuotientGroup.mk' S)) ρ g) =
      LinearMap.det
        (Komorebi.StrongArtin.InducedTwist.scalarTwist
          (ψ.comp (QuotientGroup.mk' S)) ρ g)
    rw [← hσχ, ← hτψ]
    exact hdet g
  rw [hσχ, hτψ, hχψ]

end Torsor

end Komorebi.StrongArtin.DeterminantSelector

#print axioms Komorebi.StrongArtin.DeterminantSelector.character_pow_injective_of_prime_exponent
#print axioms Komorebi.StrongArtin.DeterminantSelector.det_scalarTwist
#print axioms Komorebi.StrongArtin.DeterminantSelector.determinant_twists_injective
#print axioms Komorebi.StrongArtin.DeterminantSelector.determinant_distinguishes_extensions

namespace Komorebi.StrongArtin.DeterminantSelector

universe uKdet2 uGdet2 uVdet2 uWdet uUdet
variable {K : Type uKdet2} [Field K]
variable {G : Type uGdet2} [Group G]
variable {V : Type uVdet2} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {Wdet : Type uWdet} [AddCommGroup Wdet] [Module K Wdet] [FiniteDimensional K Wdet]
variable {Udet : Type uUdet} [AddCommGroup Udet] [Module K Udet] [FiniteDimensional K Udet]

/-- A group element acts by a genuine linear equivalence. -/
noncomputable def repLinearEquiv (ρ : Representation K G Wdet) (g : G) :
    Wdet ≃ₗ[K] Wdet where
  toLinearMap := ρ g
  invFun := ρ g⁻¹
  left_inv v := by simp
  right_inv v := by simp

omit [FiniteDimensional K V] [FiniteDimensional K Wdet] in
/-- Transporting a representation across a linear equivalence preserves its
determinant function pointwise. -/
theorem det_transportRep
    (e : V ≃ₗ[K] Wdet) (σ : Representation K G Wdet) (g : G) :
    LinearMap.det (Komorebi.StrongArtin.ExtensionTorsor.transportRep e σ g) =
      LinearMap.det (σ g) := by
  let f : Wdet ≃ₗ[K] Wdet := repLinearEquiv σ g
  have hc := LinearEquiv.det_conj f e.symm
  have hmap :
      (e.symm.symm ≪≫ₗ f ≪≫ₗ e.symm).toLinearMap =
        Komorebi.StrongArtin.ExtensionTorsor.transportRep e σ g := by
    apply LinearMap.ext
    intro v
    rfl
  have hk := congrArg Units.val hc
  rw [LinearEquiv.coe_det, LinearEquiv.coe_det] at hk
  rw [hmap] at hk
  simpa [f, repLinearEquiv] using hk

section NaturalTorsor

variable [IsAlgClosed K]
variable (S : Subgroup G) [S.Normal]

omit [FiniteDimensional K Wdet] [FiniteDimensional K Udet] in
/-- Natural isomorphism-class form of the determinant selector.  Equivalent
irreducible restrictions and equal determinant functions force the two
extensions to be equivalent when the quotient is prime cyclic and its prime
does not divide the rank. -/
theorem determinant_distinguishes_extension_classes
    (p : ℕ) (hp : p.Prime) (eQ : (G ⧸ S) ≃* Cp p)
    (ρ : Representation K G V)
    (σ : Representation K G Wdet)
    (τ : Representation K G Udet)
    (eσH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S Wdet from σ.comp S.subtype))
    (eτH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S Udet from τ.comp S.subtype))
    [Representation.IsIrreducible (ρ.comp S.subtype)]
    (hpn : ¬ p ∣ Module.finrank K V)
    (hdet : ∀ g : G, LinearMap.det (σ g) = LinearMap.det (τ g)) :
    Nonempty (σ.Equiv τ) := by
  let σV : Representation K G V :=
    Komorebi.StrongArtin.ExtensionTorsor.transportRep eσH.toLinearEquiv σ
  let τV : Representation K G V :=
    Komorebi.StrongArtin.ExtensionTorsor.transportRep eτH.toLinearEquiv τ
  have hσres : ∀ h : S, ρ h.1 = σV h.1 := by
    exact Komorebi.StrongArtin.ExtensionTorsor.transportRep_restriction_eq
      S.subtype ρ σ eσH
  have hτres : ∀ h : S, ρ h.1 = τV h.1 := by
    exact Komorebi.StrongArtin.ExtensionTorsor.transportRep_restriction_eq
      S.subtype ρ τ eτH
  have hdetV : ∀ g : G, LinearMap.det (σV g) = LinearMap.det (τV g) := by
    intro g
    calc
      LinearMap.det (σV g) = LinearMap.det (σ g) :=
        det_transportRep eσH.toLinearEquiv σ g
      _ = LinearMap.det (τ g) := hdet g
      _ = LinearMap.det (τV g) :=
        (det_transportRep eτH.toLinearEquiv τ g).symm
  have heq : σV = τV :=
    determinant_distinguishes_extensions S p hp eQ ρ σV τV hσres hτres hpn hdetV
  let eσ : σV.Equiv σ :=
    Komorebi.StrongArtin.ExtensionTorsor.transportEquiv eσH.toLinearEquiv σ
  let eτ : τV.Equiv τ :=
    Komorebi.StrongArtin.ExtensionTorsor.transportEquiv eτH.toLinearEquiv τ
  have eτ' : σV.Equiv τ := by
    rw [heq]
    exact eτ
  exact ⟨eσ.symm.trans eτ'⟩

end NaturalTorsor

end Komorebi.StrongArtin.DeterminantSelector

#print axioms Komorebi.StrongArtin.DeterminantSelector.det_transportRep
#print axioms Komorebi.StrongArtin.DeterminantSelector.determinant_distinguishes_extension_classes


namespace Komorebi.StrongArtin.TraceSeparator

universe uKtf uGtf uVtf
variable {K : Type uKtf} [Field K]
variable {G : Type uGtf} [Group G]
variable {V : Type uVtf} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

omit [FiniteDimensional K V] in
/-- A single nonzero trace value separates all powers of a character whose
value at that element has exact order `p`. -/
theorem trace_twist_fibre_injective_at
    (p : ℕ) (χ : G →* Kˣ) (ρ : Representation K G V) (g : G)
    (htr : ρ.character g ≠ 0)
    (hord : orderOf (χ g) = p) :
    Function.Injective (fun j : Fin p =>
      (Komorebi.StrongArtin.InducedTwist.scalarTwist (χ ^ (j : ℕ)) ρ).character g) := by
  intro i j hij
  have hpowsK : (((χ g) ^ (i : ℕ) : Kˣ) : K) =
      (((χ g) ^ (j : ℕ) : Kˣ) : K) := by
    simp only [scalarTwist_character, MonoidHom.pow_apply] at hij
    exact mul_right_cancel₀ htr hij
  have hpows : (χ g) ^ (i : ℕ) = (χ g) ^ (j : ℕ) := Units.ext hpowsK
  apply Fin.ext
  apply pow_injOn_Iio_orderOf (x := χ g)
  · rw [hord]
    exact i.isLt
  · rw [hord]
    exact j.isLt
  · exact hpows

/-- Prime-order criterion: a nontrivial element whose `p`th power is one has
exact order `p`. -/
theorem orderOf_eq_prime_of_pow_eq_one_of_ne_one
    {x : Kˣ} (p : ℕ) (hp : p.Prime) (hxp : x ^ p = 1) (hx1 : x ≠ 1) :
    orderOf x = p := by
  have hd : orderOf x ∣ p := orderOf_dvd_of_pow_eq_one hxp
  rcases (hp.eq_one_or_self_of_dvd (orderOf x) hd) with h1 | hpord
  · exact False.elim (hx1 (orderOf_eq_one_iff.mp h1))
  · exact hpord

omit [FiniteDimensional K V] in
/-- Practical prime-cyclic trace separator: nonzero base trace plus a nontrivial
`p`-torsion quotient value separates the entire `p`-element twist fibre. -/
theorem trace_twist_fibre_injective_of_prime_torsion
    (p : ℕ) (hp : p.Prime) (χ : G →* Kˣ) (ρ : Representation K G V) (g : G)
    (htr : ρ.character g ≠ 0)
    (hxp : (χ g) ^ p = 1) (hx1 : χ g ≠ 1) :
    Function.Injective (fun j : Fin p =>
      (Komorebi.StrongArtin.InducedTwist.scalarTwist (χ ^ (j : ℕ)) ρ).character g) := by
  exact trace_twist_fibre_injective_at p χ ρ g htr
    (orderOf_eq_prime_of_pow_eq_one_of_ne_one p hp hxp hx1)

end Komorebi.StrongArtin.TraceSeparator

#print axioms Komorebi.StrongArtin.TraceSeparator.trace_twist_fibre_injective_at
#print axioms Komorebi.StrongArtin.TraceSeparator.trace_twist_fibre_injective_of_prime_torsion


namespace Komorebi.StrongArtin.TraceSeparator

abbrev CpC (p : ℕ) := Komorebi.StrongArtin.CyclicSimple.Cp p

/-- Canonical faithful complex character of the standard cyclic model. -/
noncomputable def canonicalCpChar (p : ℕ) (hp0 : p ≠ 0) : CpC p →* ℂˣ := by
  letI : NeZero p := ⟨hp0⟩
  exact Circle.toUnits.comp ZMod.toCircle.toMonoidHom

set_option linter.style.haveILetI false in
/-- The canonical cyclic character is faithful. -/
theorem canonicalCpChar_injective (p : ℕ) (hp0 : p ≠ 0) :
    Function.Injective (canonicalCpChar p hp0) := by
  letI : NeZero p := ⟨hp0⟩
  intro a b hab
  apply Multiplicative.toAdd.injective
  apply ZMod.injective_toCircle
  apply Subtype.ext
  have hval := congrArg (fun u : ℂˣ => (u : ℂ)) hab
  simpa [canonicalCpChar] using hval

/-- Pull back the canonical `C_p` character through a quotient identification. -/
noncomputable def canonicalQuotientChar
    {G : Type*} [Group G] (S : Subgroup G) [S.Normal]
    (p : ℕ) (hp0 : p ≠ 0) (eQ : (G ⧸ S) ≃* CpC p) : G →* ℂˣ :=
  (canonicalCpChar p hp0).comp (eQ.toMonoidHom.comp (QuotientGroup.mk' S))

/-- Its kernel is exactly the subgroup defining the quotient. -/
theorem canonicalQuotientChar_eq_one_iff
    {G : Type*} [Group G] (S : Subgroup G) [S.Normal]
    (p : ℕ) (hp0 : p ≠ 0) (eQ : (G ⧸ S) ≃* CpC p) (g : G) :
    canonicalQuotientChar S p hp0 eQ g = 1 ↔ g ∈ S := by
  constructor
  · intro h
    have hq : (QuotientGroup.mk' S) g = 1 := by
      apply eQ.injective
      apply canonicalCpChar_injective p hp0
      simpa [canonicalQuotientChar] using h
    exact (QuotientGroup.eq_one_iff g).1 hq
  · intro hg
    have hq : (g : G ⧸ S) = 1 :=
      (QuotientGroup.eq_one_iff g).2 hg
    simp [canonicalQuotientChar, hq]

set_option linter.style.haveILetI false in
/-- End-to-end degree-one separator for an irreducible extension across a
prime-cyclic quotient. One off-subgroup trace separates all `p` quotient twists. -/
theorem prime_cyclic_trace_separator_full_fibre
    {G : Type*} [Group G] [Fintype G]
    (S : Subgroup G) [S.Normal]
    (p : ℕ) (hp : p.Prime) (eQ : (G ⧸ S) ≃* CpC p)
    {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
    (ρ : Representation ℂ G V)
    [Representation.IsIrreducible ρ]
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃ g : G, g ∉ S ∧ ρ.character g ≠ 0 ∧
      Function.Injective (fun j : Fin p =>
        (Komorebi.StrongArtin.InducedTwist.scalarTwist
          ((canonicalQuotientChar S p hp.ne_zero eQ) ^ (j : ℕ)) ρ).character g) := by
  letI : NeZero p := ⟨hp.ne_zero⟩
  letI : Nontrivial (ZMod p) := ZMod.nontrivial_iff.mpr hp.ne_one
  let χ : G →* ℂˣ := canonicalQuotientChar S p hp.ne_zero eQ
  have hχS : ∀ h : S, χ h.1 = 1 := by
    intro h
    exact (canonicalQuotientChar_eq_one_iff S p hp.ne_zero eQ h.1).2 h.2
  let q0 : G ⧸ S := eQ.symm (Multiplicative.ofAdd (1 : ZMod p))
  have hq0 : q0 ≠ 1 := by
    intro h
    have he := congrArg eQ h
    simp [q0] at he
  obtain ⟨g0, hg0⟩ := QuotientGroup.mk'_surjective S q0
  have hg0_notS : g0 ∉ S := by
    intro hgS
    have hqone : (g0 : G ⧸ S) = 1 :=
      (QuotientGroup.eq_one_iff g0).2 hgS
    have hqmk : (QuotientGroup.mk' S) g0 = 1 := by
      simpa using hqone
    exact hq0 (hg0.symm.trans hqmk)
  have hχ0 : χ g0 ≠ 1 := by
    change canonicalQuotientChar S p hp.ne_zero eQ g0 ≠ 1
    exact fun h => hg0_notS ((canonicalQuotientChar_eq_one_iff S p hp.ne_zero eQ g0).1 h)
  obtain ⟨g, hgRange, htr⟩ := trace_separator S.subtype ρ χ hχS g0 hχ0
  have hgS : g ∉ S := by
    intro hg
    exact hgRange ⟨⟨g, hg⟩, rfl⟩
  have hgp : (χ g) ^ p = 1 := by
    rw [← map_pow]
    apply (canonicalQuotientChar_eq_one_iff S p hp.ne_zero eQ (g ^ p)).2
    apply (QuotientGroup.eq_one_iff (g ^ p)).1
    have hqp : (g : G ⧸ S) ^ p = 1 :=
      Komorebi.StrongArtin.DeterminantSelector.exponent_of_equiv_cp p eQ (g : G ⧸ S)
    simpa using hqp
  have hχ1 : χ g ≠ 1 := by
    change canonicalQuotientChar S p hp.ne_zero eQ g ≠ 1
    exact fun h => hgS ((canonicalQuotientChar_eq_one_iff S p hp.ne_zero eQ g).1 h)
  refine ⟨g, hgS, htr, ?_⟩
  change Function.Injective (fun j : Fin p =>
    (Komorebi.StrongArtin.InducedTwist.scalarTwist (χ ^ (j : ℕ)) ρ).character g)
  exact trace_twist_fibre_injective_of_prime_torsion p hp χ ρ g htr hgp hχ1

end Komorebi.StrongArtin.TraceSeparator

#print axioms Komorebi.StrongArtin.TraceSeparator.canonicalCpChar_injective
#print axioms Komorebi.StrongArtin.TraceSeparator.prime_cyclic_trace_separator_full_fibre
namespace Komorebi.StrongArtin.CyclicSimple

set_option linter.style.haveILetI false in
theorem exists_nonzero_fixed_vector_cp
    (p : ℕ) [Fact p.Prime]
    {K : Type*} [Field K] [CharP K p]
    {U : Type*} [AddCommGroup U] [Module K U] [FiniteDimensional K U] [Nontrivial U]
    (θ : Representation K (Cp p) U) :
    ∃ u : U, u ≠ 0 ∧ ∀ g : Cp p, θ g u = u := by
  let c : Cp p := Multiplicative.ofAdd (1 : ZMod p)
  let T : Module.End K U := θ c - 1
  letI : CharP (Module.End K U) p := charP_of_injective_algebraMap' K p
  have hTp : T ^ p = 0 := by
    dsimp [T]
    rw [sub_pow_char_of_commute p (Commute.one_right (θ c))]
    have hcp : c ^ p = 1 := cp_pow_prime_eq_one p c
    rw [← map_pow, hcp, map_one]
    simp
  have hdetpow : (LinearMap.det T) ^ p = 0 := by
    calc
      (LinearMap.det T) ^ p = LinearMap.det (T ^ p) := (map_pow LinearMap.det T p).symm
      _ = LinearMap.det 0 := by rw [hTp]
      _ = 0 := by
        rw [LinearMap.det_zero]
        exact zero_pow (Module.finrank_pos (R := K) (M := U)).ne'
  have hdet : LinearMap.det T = 0 :=
    (pow_eq_zero_iff (Fact.out : p.Prime).ne_zero).mp hdetpow
  have hker : T.ker ≠ ⊥ := (LinearMap.det_eq_zero_iff_ker_ne_bot).1 hdet
  obtain ⟨u, huT, hu0⟩ := (T.ker).ne_bot_iff.mp hker
  refine ⟨u, hu0, ?_⟩
  intro g
  have hcgen : ∃ n : ℕ, c ^ n = g := by
    refine ⟨(Multiplicative.toAdd g).val, ?_⟩
    apply Multiplicative.toAdd.injective
    simp [c]
  rcases hcgen with ⟨n, rfl⟩
  have hcu : θ c u = u := by
    have hzero : T u = 0 := huT
    simpa [T, sub_eq_zero] using hzero
  rw [map_pow]
  induction n with
  | zero => simp
  | succ n ih =>
      simp [pow_succ, ih, hcu]

end Komorebi.StrongArtin.CyclicSimple

#print axioms Komorebi.StrongArtin.CyclicSimple.exists_nonzero_fixed_vector_cp

namespace Komorebi.StrongArtin.QuotientRestriction

universe uKri uGri uVri uWri
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uKri} [Field K] [CharP K p]
variable {G : Type uGri} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uVri} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uWri} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

set_option linter.style.haveILetI false in
/-- In characteristic `p`, restriction across a prime-cyclic quotient is
injective on irreducible representation classes. -/
theorem irreducible_equiv_of_restriction_equiv
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype)) :
    Nonempty (ρ.Equiv σ) := by
  let L : Representation K G (V →ₗ[K] W) := Representation.linHom ρ σ
  let U : Submodule K (V →ₗ[K] W) :=
    Representation.invariants (show Representation K S (V →ₗ[K] W) from L.comp S.subtype)
  let qRep : Representation K (G ⧸ S) U := Representation.quotientToInvariants L S
  let θ : Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) U :=
    qRep.comp eQ.symm.toMonoidHom
  let fHU : U := by
    refine ⟨eH.toLinearEquiv.toLinearMap, ?_⟩
    have hint : (show Representation K S V from ρ.comp S.subtype).IsIntertwiningMap
        (show Representation K S W from σ.comp S.subtype)
        eH.toLinearEquiv.toLinearMap :=
      ⟨fun h v => Representation.IntertwiningMap.isIntertwining
        (ρ := (show Representation K S V from ρ.comp S.subtype))
        (σ := (show Representation K S W from σ.comp S.subtype))
        eH.toIntertwiningMap h v⟩
    have hmem := (Representation.mem_linHom_invariants_iff_isIntertwining
      (ρ := (show Representation K S V from ρ.comp S.subtype))
      (σ := (show Representation K S W from σ.comp S.subtype))
      eH.toLinearEquiv.toLinearMap).2 hint
    simpa [U, L] using hmem
  have hfHU_ne : fHU ≠ 0 := by
    intro hz
    haveI : IsSimpleModule (MonoidAlgebra K G) ρ.asModule :=
      (Representation.irreducible_iff_isSimpleModule_asModule ρ).mp inferInstance
    haveI : Nontrivial ρ.asModule :=
      IsSimpleModule.nontrivial (MonoidAlgebra K G) ρ.asModule
    letI : Nontrivial V := ρ.asModuleEquiv.toEquiv.symm.nontrivial
    obtain ⟨v, hv⟩ : ∃ v : V, v ≠ 0 := exists_ne 0
    have hzval := congrArg Subtype.val hz
    have hzv : eH.toLinearEquiv v = 0 := by
      have hfun : eH.toLinearEquiv.toLinearMap = 0 := by
        simpa [fHU] using hzval
      have hvz := congrArg (fun f : V →ₗ[K] W => f v) hfun
      simpa using hvz
    exact hv (eH.toLinearEquiv.injective (by simpa using hzv))
  letI : Nontrivial U := ⟨⟨fHU, 0, hfHU_ne⟩⟩
  obtain ⟨u, hu0, hufix⟩ :=
    Komorebi.StrongArtin.CyclicSimple.exists_nonzero_fixed_vector_cp p θ
  have huG : ∀ g : G, L g u.1 = u.1 := by
    intro g
    have hqfix : qRep ((QuotientGroup.mk' S) g) u = u := by
      have hcp := hufix (eQ ((QuotientGroup.mk' S) g))
      simpa [θ] using hcp
    have hqfix' : ((qRep.comp (QuotientGroup.mk' S)) g) u = u := by
      simpa using hqfix
    have hlift := Representation.IntertwiningMap.isIntertwining
      (show Representation K G U from qRep.comp (QuotientGroup.mk' S)) L
      (Representation.quotientToInvariants_lift L S) g u
    rw [hqfix'] at hlift
    exact hlift.symm
  have huInv : u.1 ∈ Representation.invariants L := huG
  let xG : Representation.invariants L := ⟨u.1, huInv⟩
  let EG := Representation.invariantsEquivIntertwiningMap ρ σ
  let fG : ρ.IntertwiningMap σ := EG xG
  have hfG_ne : fG ≠ 0 := by
    intro hz
    have hx0 : xG = 0 := by
      apply EG.injective
      simpa [fG, EG] using hz
    apply hu0
    apply Subtype.ext
    have hxv := congrArg Subtype.val hx0
    simpa [xG] using hxv
  have hbij : Function.Bijective fG :=
    (Representation.IsIrreducible.bijective_or_eq_zero fG).resolve_right hfG_ne
  exact ⟨fG.ofBijective hbij⟩

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.irreducible_equiv_of_restriction_equiv


namespace Komorebi.StrongArtin.QuotientRestriction

open scoped MonoidAlgebra Pointwise

universe uKr uGr uVr
variable {Kr : Type uKr} [Field Kr]
variable {Gr : Type uGr} [Group Gr]
variable (Hr : Subgroup Gr) [Hr.Normal]
variable {Vr : Type uVr} [AddCommGroup Vr] [Module Kr Vr]

/-- Conjugation of a normal subgroup induces a ring automorphism of its group algebra. -/
noncomputable def conjugateGroupAlgebra (g : Gr) : Kr[Hr] ≃+* Kr[Hr] :=
  MonoidAlgebra.mapDomainRingEquiv Kr (MulAut.conjNormal g)

/-- The Jacobson radical of the subgroup algebra is invariant under ambient conjugation. -/
theorem conjugateGroupAlgebra_map_jacobson (g : Gr) :
    Ideal.map (conjugateGroupAlgebra (Kr:=Kr) Hr g).toRingHom
        ((⊥ : Ideal Kr[Hr]).jacobson) =
      ((⊥ : Ideal Kr[Hr]).jacobson) := by
  let e := conjugateGroupAlgebra (Kr:=Kr) Hr g
  have h := Ideal.map_jacobson_of_bijective
    (I := (⊥ : Ideal Kr[Hr])) e.bijective
  simpa only [conjugateGroupAlgebra,
    MonoidAlgebra.toRingHom_mapDomainRingEquiv, Ideal.map_bot] using h

/-- Ambient conjugation preserves membership in the subgroup-algebra Jacobson radical. -/
theorem conjugateGroupAlgebra_mem_jacobson {g : Gr} {a : Kr[Hr]}
    (ha : a ∈ Ring.jacobson Kr[Hr]) :
    conjugateGroupAlgebra (Kr:=Kr) Hr g a ∈ Ring.jacobson Kr[Hr] := by
  have hm : conjugateGroupAlgebra (Kr:=Kr) Hr g a ∈
      Ideal.map (conjugateGroupAlgebra (Kr:=Kr) Hr g).toRingHom
        (Ring.jacobson Kr[Hr]) :=
    Ideal.mem_map_of_mem (conjugateGroupAlgebra (Kr:=Kr) Hr g).toRingHom ha
  have hj := conjugateGroupAlgebra_map_jacobson (Kr:=Kr) Hr g
  rw [Ideal.jacobson_bot] at hj
  rwa [hj] at hm

/-- Conjugation compatibility between the ambient representation action and the
subgroup group-algebra action. -/
theorem subgroupAlgebra_action_conj
    (ρ : Representation Kr Gr Vr) (g : Gr) (a : Kr[Hr]) (v : Vr) :
    ρ g ((show Representation Kr Hr Vr from ρ.comp Hr.subtype).asAlgebraHom a v) =
      (show Representation Kr Hr Vr from ρ.comp Hr.subtype).asAlgebraHom
        (conjugateGroupAlgebra (Kr:=Kr) Hr g a) (ρ g v) := by
  apply MonoidAlgebra.induction_on a
  · intro h
    simp only [MonoidAlgebra.of_apply, Representation.asAlgebraHom_single,
      one_smul, conjugateGroupAlgebra, MonoidAlgebra.mapDomainRingEquiv_single]
    change ρ g (ρ (h:Gr) v) = ρ ((MulAut.conjNormal g h : Hr) : Gr) (ρ g v)
    rw [← Module.End.mul_apply, ← ρ.map_mul,
      ← Module.End.mul_apply, ← ρ.map_mul]
    simp [MulAut.conjNormal_apply, mul_assoc]
  · intro a b ha hb
    simp [ha, hb]
  · intro r a ha
    have hmap : conjugateGroupAlgebra (Kr:=Kr) Hr g (r • a) =
        r • conjugateGroupAlgebra (Kr:=Kr) Hr g a := by
      ext h
      simp [conjugateGroupAlgebra]
    rw [hmap]
    simp [ha]

set_option linter.unusedSimpArgs false in
/-- The part generated by the subgroup-algebra Jacobson radical is stable under
all ambient group elements when the subgroup is normal. -/
theorem radical_generated_stable
    (ρ : Representation Kr Gr Vr) (g : Gr)
    {x : (show Representation Kr Hr Vr from ρ.comp Hr.subtype).asModule}
    (hx : x ∈ Ring.jacobson Kr[Hr] •
      (⊤ : Submodule Kr[Hr]
        (show Representation Kr Hr Vr from ρ.comp Hr.subtype).asModule)) :
    (show Representation Kr Hr Vr from ρ.comp Hr.subtype).asModuleEquiv.symm
      (ρ g ((show Representation Kr Hr Vr from ρ.comp Hr.subtype).asModuleEquiv x)) ∈
      Ring.jacobson Kr[Hr] •
        (⊤ : Submodule Kr[Hr]
          (show Representation Kr Hr Vr from ρ.comp Hr.subtype).asModule) := by
  let ρH : Representation Kr Hr Vr := ρ.comp Hr.subtype
  change ρH.asModuleEquiv.symm (ρ g (ρH.asModuleEquiv x)) ∈
    Ring.jacobson Kr[Hr] • (⊤ : Submodule Kr[Hr] ρH.asModule)
  change x ∈ Ring.jacobson Kr[Hr] • (⊤ : Submodule Kr[Hr] ρH.asModule) at hx
  refine Submodule.smul_induction_on hx ?_ ?_
  · intro a ha y hy
    have hca : conjugateGroupAlgebra (Kr:=Kr) Hr g a ∈ Ring.jacobson Kr[Hr] :=
      conjugateGroupAlgebra_mem_jacobson (Kr:=Kr) Hr ha
    have hact := subgroupAlgebra_action_conj (Kr:=Kr) Hr ρ g a (ρH.asModuleEquiv y)
    have hleft : ρH.asModuleEquiv (a • y) =
        ρH.asAlgebraHom a (ρH.asModuleEquiv y) :=
      ρH.asModuleEquiv_map_smul a y
    rw [hleft]
    rw [hact]
    have hright : ρH.asModuleEquiv.symm
        (ρH.asAlgebraHom (conjugateGroupAlgebra (Kr:=Kr) Hr g a)
          (ρ g (ρH.asModuleEquiv y))) =
        (conjugateGroupAlgebra (Kr:=Kr) Hr g a) •
          ρH.asModuleEquiv.symm (ρ g (ρH.asModuleEquiv y)) := by
      apply ρH.asModuleEquiv.injective
      simp
    rw [hright]
    exact Submodule.smul_mem_smul hca (by trivial)
  · intro x y hx' hy'
    simp only [map_add, LinearEquiv.map_add]
    exact Submodule.add_mem _ hx' hy'

set_option linter.style.haveILetI false in
/-- Modular Clifford semisimplicity: an irreducible finite-dimensional
representation restricts semisimply to every normal subgroup. -/
theorem irreducible_restrict_normal_semisimple
    {Kr : Type*} [Field Kr]
    {Gr : Type*} [Group Gr] [Fintype Gr]
    (Hr : Subgroup Gr) [Hr.Normal]
    {Vr : Type*} [AddCommGroup Vr] [Module Kr Vr] [FiniteDimensional Kr Vr]
    (ρ : Representation Kr Gr Vr)
    [Representation.IsIrreducible ρ] :
    Representation.IsSemisimpleRepresentation
      (show Representation Kr Hr Vr from ρ.comp Hr.subtype) := by
  let ρH : Representation Kr Hr Vr := ρ.comp Hr.subtype
  let NH : Submodule Kr[Hr] ρH.asModule :=
    Ring.jacobson Kr[Hr] • (⊤ : Submodule Kr[Hr] ρH.asModule)
  let NK0 : Submodule Kr ρH.asModule := NH.restrictScalars Kr
  let NK : Submodule Kr Vr := NK0.map ρH.asModuleEquiv.toLinearMap
  have hNKstable : ∀ (g : Gr) {x : Vr}, x ∈ NK → ρ g x ∈ NK := by
    intro g x hx
    rcases hx with ⟨y, hy, rfl⟩
    have hyNH : y ∈ NH := by
      exact (Submodule.restrictScalars_mem Kr NH y).mp hy
    have hzNH := radical_generated_stable (Kr:=Kr) Hr ρ g hyNH
    have hzNK0 : ρH.asModuleEquiv.symm (ρ g (ρH.asModuleEquiv y)) ∈ NK0 := by
      exact (Submodule.restrictScalars_mem Kr NH _).2 hzNH
    refine ⟨ρH.asModuleEquiv.symm (ρ g (ρH.asModuleEquiv y)), hzNK0, ?_⟩
    simp
  let NI : Subrepresentation ρ :=
    { toSubmodule := NK
      apply_mem_toSubmodule := hNKstable }
  haveI : IsSimpleModule Kr[Gr] ρ.asModule :=
    (Representation.irreducible_iff_isSimpleModule_asModule ρ).mp inferInstance
  letI : Nontrivial ρ.asModule := IsSimpleModule.nontrivial Kr[Gr] ρ.asModule
  letI : Nontrivial Vr := ρ.asModuleEquiv.toEquiv.symm.nontrivial
  letI : Nontrivial ρH.asModule := ρH.asModuleEquiv.toEquiv.nontrivial
  have hcases : NI = ⊥ ∨ NI = ⊤ := IsSimpleOrder.eq_bot_or_eq_top NI
  have hnotTop : NI ≠ ⊤ := by
    intro htop
    have hNKtop : NK = ⊤ := by
      apply top_unique
      intro x hx
      have hxNI : x ∈ NI := by
        rw [htop]
        trivial
      exact hxNI
    have hNHtop : NH = ⊤ := by
      apply top_unique
      intro y hy
      have hyNK0 : y ∈ NK0 := by
        have hyV : ρH.asModuleEquiv y ∈ NK := by rw [hNKtop]; trivial
        rcases hyV with ⟨z, hz, heq⟩
        have hzy : z = y := by
          apply ρH.asModuleEquiv.injective
          simpa using heq
        simpa [hzy] using hz
      exact (Submodule.restrictScalars_mem Kr NH y).mp hyNK0
    haveI : Module.Finite Kr[Hr] ρH.asModule := by
      exact Module.Finite.of_restrictScalars_finite Kr Kr[Hr] ρH.asModule
    have hfg : (⊤ : Submodule Kr[Hr] ρH.asModule).FG :=
      (Module.Finite.iff_fg).mp inferInstance
    have heqbot : (⊤ : Submodule Kr[Hr] ρH.asModule) = ⊥ := by
      apply hfg.eq_bot_of_le_jacobson_smul
      change (⊤ : Submodule Kr[Hr] ρH.asModule) ≤ NH
      simp [hNHtop]
    exact top_ne_bot heqbot
  have hNIbot : NI = ⊥ := hcases.resolve_right hnotTop
  have hNKbot : NK = ⊥ := by
    apply bot_unique
    intro x hx
    have hxNI : x ∈ NI := hx
    rw [hNIbot] at hxNI
    exact hxNI
  have hNHbot : NH = ⊥ := by
    apply bot_unique
    intro y hy
    have hyNK0 : y ∈ NK0 := (Submodule.restrictScalars_mem Kr NH y).2 hy
    have hyNK : ρH.asModuleEquiv y ∈ NK := ⟨y, hyNK0, rfl⟩
    rw [hNKbot] at hyNK
    have hy0 : ρH.asModuleEquiv y = 0 := hyNK
    exact ρH.asModuleEquiv.injective (by simpa using hy0)
  have hjann : Ring.jacobson Kr[Hr] ≤ Module.annihilator Kr[Hr] ρH.asModule := by
    intro a ha
    apply Module.mem_annihilator.mpr
    intro y
    have hmem : a • y ∈ NH := Submodule.smul_mem_smul ha (by trivial)
    rw [hNHbot] at hmem
    exact hmem
  letI : IsArtinianRing Kr[Hr] := IsArtinianRing.of_finite Kr Kr[Hr]
  have hringSemi : IsSemisimpleRing (Kr[Hr] ⧸ Ring.jacobson Kr[Hr]) := by
    infer_instance
  have htors : Module.IsTorsionBySet Kr[Hr] ρH.asModule
      (Ring.jacobson Kr[Hr] : Set Kr[Hr]) := by
    rw [Module.isTorsionBySet_iff_subset_annihilator Kr[Hr] ρH.asModule]
    exact hjann
  rw [Representation.isSemisimpleRepresentation_iff_isSemisimpleModule_asModule]
  letI : Module (Kr[Hr] ⧸ Ring.jacobson Kr[Hr]) ρH.asModule := htors.module
  letI : IsSemisimpleRing (Kr[Hr] ⧸ Ring.jacobson Kr[Hr]) := hringSemi
  exact (htors.isSemisimpleModule_iff).mp inferInstance

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.irreducible_restrict_normal_semisimple

namespace Komorebi.StrongArtin.QuotientRestriction

universe uKri2 uGri2 uVri2 uWri2
variable (p : ℕ) [Fact p.Prime]
variable {K : Type uKri2} [Field K] [CharP K p]
variable {G : Type uGri2} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uVri2} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uWri2} [AddCommGroup W] [Module K W] [FiniteDimensional K W]

set_option linter.style.haveILetI false in
/-- A nonzero intertwiner after restriction across a prime-cyclic quotient already
forces equivalence of irreducible ambient representations in characteristic `p`. -/
theorem irreducible_equiv_of_nonzero_restriction_intertwiner
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    (ρ : Representation K G V) (σ : Representation K G W)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (fH : Representation.IntertwiningMap
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    (hfH : fH ≠ 0) :
    Nonempty (ρ.Equiv σ) := by
  let L : Representation K G (V →ₗ[K] W) := Representation.linHom ρ σ
  let U : Submodule K (V →ₗ[K] W) :=
    Representation.invariants (show Representation K S (V →ₗ[K] W) from L.comp S.subtype)
  let qRep : Representation K (G ⧸ S) U := Representation.quotientToInvariants L S
  let θ : Representation K (Komorebi.StrongArtin.CyclicSimple.Cp p) U :=
    qRep.comp eQ.symm.toMonoidHom
  let u0 : U := by
    refine ⟨fH.toLinearMap, ?_⟩
    have hint : Representation.IsIntertwiningMap
        (show Representation K S V from ρ.comp S.subtype)
        (show Representation K S W from σ.comp S.subtype)
        fH.toLinearMap :=
      ⟨fun h v => Representation.IntertwiningMap.isIntertwining
        (ρ := (show Representation K S V from ρ.comp S.subtype))
        (σ := (show Representation K S W from σ.comp S.subtype))
        fH h v⟩
    exact (Representation.mem_linHom_invariants_iff_isIntertwining
      (ρ := (show Representation K S V from ρ.comp S.subtype))
      (σ := (show Representation K S W from σ.comp S.subtype))
      fH.toLinearMap).2 hint
  have hu0_ne : u0 ≠ 0 := by
    intro hz
    apply hfH
    apply Representation.IntertwiningMap.ext
    have hv := congrArg Subtype.val hz
    simpa [u0] using hv
  letI : Nontrivial U := ⟨⟨u0, 0, hu0_ne⟩⟩
  obtain ⟨u, hu0, hufix⟩ :=
    Komorebi.StrongArtin.CyclicSimple.exists_nonzero_fixed_vector_cp p θ
  have huG : ∀ g : G, L g u.1 = u.1 := by
    intro g
    have hqfix : qRep ((QuotientGroup.mk' S) g) u = u := by
      have hcp := hufix (eQ ((QuotientGroup.mk' S) g))
      simpa [θ] using hcp
    have hqfix' : ((qRep.comp (QuotientGroup.mk' S)) g) u = u := by
      simpa using hqfix
    have hlift := Representation.IntertwiningMap.isIntertwining
      (show Representation K G U from qRep.comp (QuotientGroup.mk' S)) L
      (Representation.quotientToInvariants_lift L S) g u
    rw [hqfix'] at hlift
    exact hlift.symm
  have huInv : u.1 ∈ Representation.invariants L := huG
  let xG : Representation.invariants L := ⟨u.1, huInv⟩
  let EG := Representation.invariantsEquivIntertwiningMap ρ σ
  let fG : ρ.IntertwiningMap σ := EG xG
  have hfG_ne : fG ≠ 0 := by
    intro hz
    have hx0 : xG = 0 := by
      apply EG.injective
      simpa [fG, EG] using hz
    apply hu0
    apply Subtype.ext
    have hxv := congrArg Subtype.val hx0
    simpa [xG] using hxv
  have hbij : Function.Bijective fG :=
    (Representation.IsIrreducible.bijective_or_eq_zero fG).resolve_right hfG_ne
  exact ⟨fG.ofBijective hbij⟩

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.irreducible_equiv_of_nonzero_restriction_intertwiner

namespace Komorebi.StrongArtin.ExtensionTorsor

open Representation

universe uKfree uGfree uVfree
variable {K : Type uKfree} [Field K] [IsAlgClosed K]
variable {G : Type uGfree} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uVfree} [AddCommGroup V] [Module K V] [FiniteDimensional K V]

set_option linter.style.haveILetI false in
/-- Freeness of the quotient-character action on representation isomorphism
classes, without choosing a common realization of the target extension. -/
theorem quotient_character_unique_up_to_equiv
    (ρ : Representation K G V)
    [Representation.IsIrreducible (ρ.comp S.subtype)]
    {χ ψ : (G ⧸ S) →* Kˣ}
    (e : Nonempty
      ((Komorebi.StrongArtin.InducedTwist.scalarTwist
          (χ.comp (QuotientGroup.mk' S)) ρ).Equiv
        (Komorebi.StrongArtin.InducedTwist.scalarTwist
          (ψ.comp (QuotientGroup.mk' S)) ρ))) :
    χ = ψ := by
  classical
  rcases e with ⟨e⟩
  let δ : G →* Kˣ :=
    (ψ.comp (QuotientGroup.mk' S)) * (χ.comp (QuotientGroup.mk' S))⁻¹
  have hδS : ∀ h : S, δ h.1 = 1 := by
    intro h
    have hq : (QuotientGroup.mk' S) h.1 = 1 :=
      (QuotientGroup.eq_one_iff h.1).2 h.property
    change ψ ((QuotientGroup.mk' S) h.1) *
      (χ ((QuotientGroup.mk' S) h.1))⁻¹ = 1
    rw [hq]
    simp
  by_contra hχψ
  obtain ⟨x, hx⟩ : ∃ x : G ⧸ S, ψ x * (χ x)⁻¹ ≠ 1 := by
    by_contra hn
    push Not at hn
    apply hχψ
    apply MonoidHom.ext
    intro x
    have hh := hn x
    have hm := congrArg (fun u : Kˣ => u * χ x) hh
    exact (by simpa [mul_assoc] using hm.symm)
  obtain ⟨g, rfl⟩ := QuotientGroup.mk'_surjective S x
  have hδg : δ g ≠ 1 := by
    simpa [δ] using hx
  have eδ : ρ.Equiv (Komorebi.StrongArtin.InducedTwist.scalarTwist δ ρ) := by
    refine Representation.Equiv.mk e.toLinearEquiv ?_
    intro g
    apply LinearMap.ext
    intro v
    have he := e.toIntertwiningMap.isIntertwining' g
    have hev := LinearMap.congr_fun he v
    have hev' : ((χ.comp (QuotientGroup.mk' S)) g : K) •
          e.toLinearEquiv (ρ g v) =
        ((ψ.comp (QuotientGroup.mk' S)) g : K) •
          ρ g (e.toLinearEquiv v) := by
      simpa [map_smul] using hev
    calc
      e.toLinearEquiv (ρ g v) =
          (((χ.comp (QuotientGroup.mk' S)) g : K)⁻¹) •
            (((χ.comp (QuotientGroup.mk' S)) g : K) • e.toLinearEquiv (ρ g v)) := by
        rw [smul_smul,
          inv_mul_cancel₀ (Units.ne_zero ((χ.comp (QuotientGroup.mk' S)) g)), one_smul]
      _ = (((χ.comp (QuotientGroup.mk' S)) g : K)⁻¹) •
            (((ψ.comp (QuotientGroup.mk' S)) g : K) • ρ g (e.toLinearEquiv v)) := by
        rw [hev']
      _ = (δ g : K) • ρ g (e.toLinearEquiv v) := by
        simp [δ, smul_smul, mul_comm]
  have hno : IsEmpty (ρ.Equiv
      (Komorebi.StrongArtin.InducedTwist.scalarTwist δ ρ)) :=
    Komorebi.StrongArtin.TraceSeparator.no_self_twist_of_irreducible_restriction
      S.subtype ρ δ hδS g hδg
  exact hno.false eδ

end Komorebi.StrongArtin.ExtensionTorsor

#print axioms Komorebi.StrongArtin.ExtensionTorsor.quotient_character_unique_up_to_equiv

namespace Komorebi.StrongArtin.ExtensionTorsor

universe uKfree2 uGfree2 uVfree2 uWfree2
variable {K : Type uKfree2} [Field K] [IsAlgClosed K]
variable {G : Type uGfree2} [Group G]
variable (S : Subgroup G) [S.Normal]
variable {V : Type uVfree2} [AddCommGroup V] [Module K V] [FiniteDimensional K V]
variable {W : Type uWfree2} [AddCommGroup W] [Module K W]

/-- Full quotient-character torsor statement on representation isomorphism
classes: the character carrying one irreducible extension to another is unique. -/
theorem existsUnique_quotient_character_up_to_equiv
    (ρ : Representation K G V)
    (σ : Representation K G W)
    (eH : Representation.Equiv
      (show Representation K S V from ρ.comp S.subtype)
      (show Representation K S W from σ.comp S.subtype))
    [Representation.IsIrreducible (ρ.comp S.subtype)] :
    ∃! χbar : (G ⧸ S) →* Kˣ,
      Nonempty ((Komorebi.StrongArtin.InducedTwist.scalarTwist
        (χbar.comp (QuotientGroup.mk' S)) ρ).Equiv σ) := by
  obtain ⟨χ, eχ⟩ := extensions_differ_by_quotient_character S ρ σ eH
  refine ⟨χ, eχ, ?_⟩
  intro ψ eψ
  rcases eχ with ⟨eχ⟩
  rcases eψ with ⟨eψ⟩
  exact (quotient_character_unique_up_to_equiv S ρ
    (χ := χ) (ψ := ψ) ⟨eχ.trans eψ.symm⟩).symm

end Komorebi.StrongArtin.ExtensionTorsor

#print axioms Komorebi.StrongArtin.ExtensionTorsor.existsUnique_quotient_character_up_to_equiv

namespace Komorebi.StrongArtin.QuotientRestriction

universe uGcp uVcp uWcp
variable (p : ℕ) [Fact p.Prime]

/-- Over the prime field `F_p`, taking the `p`th power of an endomorphism does
not change its characteristic polynomial. -/
theorem linearMap_charpoly_pow_prime
    {V : Type uVcp} [AddCommGroup V] [Module (ZMod p) V]
    [FiniteDimensional (ZMod p) V]
    (f : Module.End (ZMod p) V) :
    (f ^ p).charpoly = f.charpoly := by
  let b := Module.Free.chooseBasis (ZMod p) V
  rw [← LinearMap.charpoly_toMatrix (f ^ p) b,
      ← LinearMap.charpoly_toMatrix f b,
      ← LinearMap.toMatrix_pow]
  exact ZMod.charpoly_pow_card (LinearMap.toMatrix b b f)

/-- Characteristic-polynomial propagation from a prime-cyclic restriction.
If two representations over `F_p` become equivalent on a normal subgroup whose
quotient is `C_p`, then their characteristic polynomials agree on every group
element.  This is the finite-field Frobenius-cancellation core of residual
label collapse. -/
theorem charpoly_eq_of_restriction_equiv_cp
    {G : Type uGcp} [Group G]
    (S : Subgroup G) [S.Normal]
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    {V : Type uVcp} [AddCommGroup V] [Module (ZMod p) V]
    {W : Type uWcp} [AddCommGroup W] [Module (ZMod p) W]
    [FiniteDimensional (ZMod p) V] [FiniteDimensional (ZMod p) W]
    (ρ : Representation (ZMod p) G V)
    (σ : Representation (ZMod p) G W)
    (eH : Representation.Equiv
      (show Representation (ZMod p) S V from ρ.comp S.subtype)
      (show Representation (ZMod p) S W from σ.comp S.subtype)) :
    ∀ g : G, (ρ g).charpoly = (σ g).charpoly := by
  intro g
  have hpow : g ^ p ∈ S := by
    apply (QuotientGroup.eq_one_iff (g ^ p)).1
    have hqp : (g : G ⧸ S) ^ p = 1 :=
      Komorebi.StrongArtin.DeterminantSelector.exponent_of_equiv_cp
        p eQ (g : G ⧸ S)
    simpa using hqp
  let h : S := ⟨g ^ p, hpow⟩
  have hconj : eH.toLinearEquiv.conj (ρ.comp S.subtype h) = σ.comp S.subtype h :=
    eH.conj_apply_self h
  have hcp : (ρ (g ^ p)).charpoly = (σ (g ^ p)).charpoly := by
    change (ρ.comp S.subtype h).charpoly = (σ.comp S.subtype h).charpoly
    rw [← hconj, LinearEquiv.charpoly_conj]
  have hrpow : ρ (g ^ p) = (ρ g) ^ p := by simp
  have hspow : σ (g ^ p) = (σ g) ^ p := by simp
  rw [hrpow, hspow] at hcp
  simpa only [linearMap_charpoly_pow_prime (p := p)] using hcp

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.linearMap_charpoly_pow_prime
#print axioms Komorebi.StrongArtin.QuotientRestriction.charpoly_eq_of_restriction_equiv_cp

namespace Komorebi.StrongArtin.QuotientRestriction

universe uGbn uVbn uWbn

/-- The precise remaining semisimple Brauer--Nesbitt interface over the prime
field: semisimple finite-group representations with the same characteristic
polynomial on every group element are equivalent.  This is stated as a
property, not assumed globally or encoded as an axiom. -/
def SemisimpleCharpolyRigidityFp (p : ℕ) [Fact p.Prime] : Prop :=
  ∀ {G : Type uGbn} [Group G] [Fintype G]
    {V : Type uVbn} [AddCommGroup V] [Module (ZMod p) V]
    {W : Type uWbn} [AddCommGroup W] [Module (ZMod p) W]
    [FiniteDimensional (ZMod p) V] [FiniteDimensional (ZMod p) W]
    (ρ : Representation (ZMod p) G V)
    (σ : Representation (ZMod p) G W),
    Representation.IsSemisimpleRepresentation ρ →
    Representation.IsSemisimpleRepresentation σ →
    (∀ g : G, (ρ g).charpoly = (σ g).charpoly) →
    Nonempty (ρ.Equiv σ)

/-- End-to-end residual-collapse reduction over `F_p`: after the checked
prime-cyclic Frobenius propagation, the only remaining ingredient is the
semisimple characteristic-polynomial rigidity principle above. -/
theorem semisimple_residual_collapse_of_charpoly_rigidity
    (p : ℕ) [Fact p.Prime]
    (hBN : SemisimpleCharpolyRigidityFp.{uGbn, uVbn, uWbn} p)
    {G : Type uGbn} [Group G] [Fintype G]
    (S : Subgroup G) [S.Normal]
    (eQ : (G ⧸ S) ≃* Komorebi.StrongArtin.CyclicSimple.Cp p)
    {V : Type uVbn} [AddCommGroup V] [Module (ZMod p) V]
    {W : Type uWbn} [AddCommGroup W] [Module (ZMod p) W]
    [FiniteDimensional (ZMod p) V] [FiniteDimensional (ZMod p) W]
    (ρ : Representation (ZMod p) G V)
    (σ : Representation (ZMod p) G W)
    (hρ : Representation.IsSemisimpleRepresentation ρ)
    (hσ : Representation.IsSemisimpleRepresentation σ)
    (eH : Representation.Equiv
      (show Representation (ZMod p) S V from ρ.comp S.subtype)
      (show Representation (ZMod p) S W from σ.comp S.subtype)) :
    Nonempty (ρ.Equiv σ) := by
  apply hBN ρ σ hρ hσ
  exact charpoly_eq_of_restriction_equiv_cp p S eQ ρ σ eH

end Komorebi.StrongArtin.QuotientRestriction

#print axioms Komorebi.StrongArtin.QuotientRestriction.semisimple_residual_collapse_of_charpoly_rigidity
