import RealizationBoundaries.SelectorClassification
import RealizationBoundaries.NormalForms

/-! # Exact coordinate transport under finite selector changes -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The section difference is genuinely finite, without a nonzero-rational hypothesis. -/
theorem section_difference_finite (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (r : ℚ) :
    rationalSection (pairedSelector a) r - rationalSection (pairedSelector b) r ∈ finiteSupport := by
  classical
  obtain ⟨E, hE, he⟩ := pairedSelectors_agree_off_finite a b h
  apply hE.subset
  intro p hp
  by_contra hn
  apply hp
  change rationalSection (pairedSelector a) r p - rationalSection (pairedSelector b) r p = 0
  simp [rationalSection, he p hn]

/-- Finite correction converting the source normal-form section into the target section. -/
def selectorCorrection (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (r : ℚ) : finiteSupport :=
  ⟨rationalSection (pairedSelector a) r - rationalSection (pairedSelector b) r,
    section_difference_finite a b h r⟩

/-- The coordinate formula is typed in the twisted normal-form groups, not split products. -/
def normalFormTransport (a b : ℕ → Bool) (h : {n : ℕ | a n ≠ b n}.Finite)
    (x : NormalForm (pairedSelector a)) : NormalForm (pairedSelector b) :=
  ⟨x.rational, x.finite + selectorCorrection a b h x.rational⟩

@[simp] theorem normalFormTransport_rational (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (normalFormTransport a b h x).rational = x.rational := rfl

@[simp] theorem normalFormTransport_finite (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (normalFormTransport a b h x).finite = x.finite + selectorCorrection a b h x.rational := rfl

/-- Transport fixes the represented ambient vector exactly, not merely its tail class. -/
theorem normalFormTransport_realization (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    (NormalForm.realizationEquiv (pairedSelector_infinite b)
      (normalFormTransport a b h x)).val =
    (NormalForm.realizationEquiv (pairedSelector_infinite a) x).val := by
  simp only [NormalForm.realizationEquiv_coe, normalFormTransport_rational,
    normalFormTransport_finite]
  change rationalSection (pairedSelector b) x.rational +
    (x.finite.val + (rationalSection (pairedSelector a) x.rational -
      rationalSection (pairedSelector b) x.rational)) = _
  abel

/-- The same coordinate transformation as an actual additive equivalence. -/
def normalFormTransportEquiv (a b : ℕ → Bool) (h : {n : ℕ | a n ≠ b n}.Finite) :
    NormalForm (pairedSelector a) ≃+ NormalForm (pairedSelector b) :=
  ((NormalForm.realizationEquiv (pairedSelector_infinite a)).trans
    (pairedEquivOfFiniteDisagreement a b h)).trans
      (NormalForm.realizationEquiv (pairedSelector_infinite b)).symm

/-- The abstractly composed equivalence has precisely the finite-correction formula. -/
theorem normalFormTransportEquiv_apply (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x : NormalForm (pairedSelector a)) :
    normalFormTransportEquiv a b h x = normalFormTransport a b h x := by
  apply (NormalForm.realizationEquiv (pairedSelector_infinite b)).injective
  apply Subtype.ext
  change (NormalForm.realizationEquiv (pairedSelector_infinite b)
    ((NormalForm.realizationEquiv (pairedSelector_infinite b)).symm
      (pairedEquivOfFiniteDisagreement a b h
        (NormalForm.realizationEquiv (pairedSelector_infinite a) x)))).val = _
  rw [AddEquiv.apply_symm_apply, pairedEquivOfFiniteDisagreement_val]
  exact (normalFormTransport_realization a b h x).symm

/-- Addition is preserved for the actual twisted laws. -/
theorem normalFormTransport_add (a b : ℕ → Bool)
    (h : {n : ℕ | a n ≠ b n}.Finite) (x y : NormalForm (pairedSelector a)) :
    normalFormTransport a b h (x+y) =
      normalFormTransport a b h x + normalFormTransport a b h y := by
  simpa only [normalFormTransportEquiv_apply] using (normalFormTransportEquiv a b h).map_add x y

end RealizationBoundaries
