import KomorebiPadic.SupportExamples
open KomorebiPadic
noncomputable section
example {R I A : Type*} [CommRing R] [Fintype I] [DecidableEq I]
    (M : CoordinateSupport.System R I A) :
    CoordinateSupport.step M (CoordinateSupport.iterate M (Fintype.card I)) =
      CoordinateSupport.iterate M (Fintype.card I) := CoordinateSupport.iterate_stabilizes M
example {R I A : Type*} [CommRing R] [Fintype I] [DecidableEq I]
    (M : CoordinateSupport.System R I A) (s : Finset I)
    (hi : CoordinateSupport.Supported s M.initial)
    (ht : ∀ d x, CoordinateSupport.Supported s x → CoordinateSupport.Supported s (M.transition d x)) :
    CoordinateSupport.least M ⊆ s := CoordinateSupport.least_minimal_invariant M s hi ht
example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    SupportCanonicalMaskCertificate p r A B hp hr hB := supportCanonicalMaskCertificate p r A B hp hr hB hAB
example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬(p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    supportMaskOutput p r A B hp hr hB
      (supportMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (supportMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) :=
    supportMask_output_canonical_coefficient p r A B hp hr hB hAB n
end
